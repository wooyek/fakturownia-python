# coding=utf-8
import datetime
import logging
import os

import pytest
import six
from mock import MagicMock

from . import test_data
from fakturownia import base, factories, endpoints
from fakturownia.exceptions import HttpException

log = logging.getLogger(__name__)

# noinspection PyUnresolvedReferences
CLIENT_CREATE = test_data.CLIENT_CREATE
# noinspection PyUnresolvedReferences
INVOICE_CREATE = test_data.INVOICE_CREATE


@pytest.fixture(params=["invoices", "clients"])
def endpoint(request, offline_client):
    return getattr(offline_client, request.param)


# noinspection PyUnresolvedReferences
@pytest.fixture(params=[
    test_data.CLIENT_GET,
    factories.ClientFactory().get_raw_data(),
])
def client_raw_data(request):
    return request.param


@pytest.fixture
def existing_product_id(secrets):
    if 'FAKTUROWNIA_EXISTING_PRODUCT_ID' not in secrets:
        pytest.skip('Requires an environment FAKTUROWNIA_EXISTING_PRODUCT_ID setting')
    return secrets['FAKTUROWNIA_EXISTING_PRODUCT_ID']


# noinspection PyShadowingNames
def test_create_invoice(endpoint, mocker):
    request = mocker.patch('requests.request')
    request.return_value = MagicMock()
    request.json.return_value = {}
    endpoint.create()
    assert request.called


@pytest.mark.parametrize("data", [
    INVOICE_CREATE,
    factories.InvoiceFactory().get_raw_data(),
])
def test_create_refresh_send_invoice_sandbox(api_client, data):
    invoice = api_client.invoices.create(**data)
    assert invoice
    invoice.get()
    log.debug("id: %s", invoice.id)
    log.debug("payment_url: %s", invoice.payment_url)
    assert invoice.id
    assert invoice.payment_url


@pytest.mark.parametrize("buyer_email", ['fakturownia@niepodam.pl', os.environ.get('FAKTUROWNIA_SANDBOX_EMAIL', 'dummy@niepodam.pl')])
def test_send_invoice(api_client, buyer_email):
    invoice = factories.InvoiceFactory(api_client=api_client, buyer_email=buyer_email)
    invoice.post()
    invoice.send_by_email()


# noinspection PyMethodMayBeStatic
class ClientTests(object):
    @pytest.mark.parametrize("data", [
        CLIENT_CREATE,
        factories.ClientFactory().get_raw_data(),
    ])
    def test_create_refresh_client_sandbox(self, api_client, data):
        item = api_client.clients.create(**data)
        assert item
        item.get()
        log.debug("id: %s", item.id)
        assert item.id

    def test_client_create_invoice(self, mocker):
        invoices_create = mocker.patch('fakturownia.endpoints.Invoices.create')
        client = factories.ClientFactory(id=777)
        client.create_invoice()
        assert invoices_create.called

    def test_client_create_invoice_no_id(self, ):
        client = factories.ClientFactory()
        with pytest.raises(AssertionError):
            client.create_invoice()

    # noinspection PyShadowingNames
    @pytest.mark.parametrize("data", [
        CLIENT_CREATE,
        factories.ClientFactory().get_raw_data(),
    ])
    def test_client_create_invoice_sandbox(self, api_client, data, existing_product_id):
        client = api_client.clients.create(**data)
        invoice = client.create_invoice(positions=[{'product_id': existing_product_id, 'quantity': 100}])
        invoice.get()
        log.debug("id: %s", client.id)
        assert invoice.id
        assert invoice.payment_url

    def test_get_client(self, api_client):
        with pytest.raises(HttpException, match='404 Client Error: Not Found for url') as ex:
            # noinspection PyStatementEffect
            api_client.clients[123]
        assert ex.value.status_code == 404

    # noinspection PyShadowingNames
    def test_invalid_data(self, client_raw_data):
        api = MagicMock()
        api.return_value = {}
        client = endpoints.Client(api, **client_raw_data)
        client.put()
        data = api.put.call_args[1]['data']
        assert 'balance' not in data


# noinspection PyMethodMayBeStatic
class InvoiceTests(object):

    # noinspection PyProtectedMember,PyMethodMayBeStatic
    def test_dates_on_invoice(self):
        invoice = factories.InvoiceFactory()
        assert isinstance(invoice.sell_date, datetime.date)
        assert isinstance(invoice.issue_date, datetime.date)
        assert isinstance(invoice.payment_to, datetime.date)
        assert isinstance(invoice.get_raw_data()['sell_date'], six.string_types)
        assert isinstance(invoice.get_raw_data()['issue_date'], six.string_types)
        assert isinstance(invoice.get_raw_data()['payment_to'], six.string_types)

    def test_set_datetime_str(self):
        invoice = factories.InvoiceFactory()
        invoice.sell_date = '1980-08-14'
        assert invoice.sell_date == datetime.date(1980, 8, 14)
        # noinspection PyProtectedMember
        assert invoice.get_raw_data()['sell_date'] == '1980-08-14'

    def test_send_by_email(self, mocker):
        post = mocker.patch('fakturownia.core.ApiClient.post')
        invoice = factories.InvoiceFactory(id='666')
        invoice.send_by_email()
        post.assert_called_with('invoices/666/send_by_email.json')

    def test_send_by_email_failed_no_id(self):
        invoice = factories.InvoiceFactory()
        with pytest.raises(AssertionError, match='Cannot send invoice without id'):
            invoice.send_by_email()

    def test_mark_paid(self, api_client):
        invoice = factories.InvoiceFactory(api_client=api_client)
        invoice.post()
        assert invoice.status == 'issued'
        invoice.mark_paid()
        assert invoice.status == 'paid'

    def test_delete(self, api_client):
        invoice = factories.InvoiceFactory(api_client=api_client)
        invoice.post()
        assert invoice.status == 'issued'
        invoice.delete()
        assert invoice.id is not None
        with pytest.raises(HttpException, match='404 Client Error: Not Found for url'):
            # noinspection PyStatementEffect
            api_client.invoices[invoice.id]

    @pytest.mark.parametrize(
        "total_price_gross, total_price_net, total_price_tax, quantity, "
        "price_gross, price_net, price_tax, discount, discount_kind, final_price_gross, final_price_net, final_price_tax, tax",
        [
            ('100.0', '100.0', '0.0',  1, '100.0', '100.0', '0.0',  '5.0',   'amount',        '95.0',   '95.0',   '0.0',   '0.0'),  # noqa E241
            ('100.0', '100.0', '0.0',  1, '100.0', '100.0', '0.0',  '5.1',   'amount',        '94.9',   '94.9',   '0.0',   '0.0'),  # noqa E241
            ('100.0', '100.0', '0.0',  1, '100.0', '100.0', '0.0',  '33.33', 'amount',        '66.67',  '66.67',  '0.0',   '0.0'),  # noqa E241
            ('100.0', '100.0', '0.0',  1, '100.0', '100.0', '0.0',  '33.33', 'percent_unit',  '66.67',  '66.67',  '0.0',   '0.0'),  # noqa E241
            ('100.0', '100.0', '0.0',  1, '100.0', '100.0', '0.0',  '33.33', 'percent_total', '66.67',  '66.67',  '0.0',   '0.0'),  # noqa E241
            ('300.0', '300.0', '0.0',  3, '100.0', '100.0', '0.0',  '5.0',   'amount',        '295.0',  '295.0',  '0.0',   '0.0'),  # noqa E241
            ('300.0', '300.0', '0.0',  3, '100.0', '100.0', '0.0',  '5.1',   'amount',        '294.9',  '294.9',  '0.0',   '0.0'),  # noqa E241
            ('300.0', '300.0', '0.0',  3, '100.0', '100.0', '0.0',  '33.33', 'amount',        '266.67', '266.67', '0.0',   '0.0'),  # noqa E241
            ('300.0', '300.0', '0.0',  3, '100.0', '100.0', '0.0',  '33.33', 'percent_unit',  '200.01', '200.01', '0.0',   '0.0'),  # noqa E241
            ('300.0', '300.0', '0.0',  3, '100.0', '100.0', '0.0',  '33.33', 'percent_total', '200.01', '200.01', '0.0',   '0.0'),  # noqa E241
            ('100.0', '81.3',  '18.7', 1, '100.0', '81.3',  '18.7', '5.0',   'amount',        '95.0',   '77.24',  '17.76', '23.0'),  # noqa E241
            ('123.0', '100.0', '23.0', 1, '123.0', '100.0', '23.0', '33.33', 'amount',        '89.67',  '72.9',   '16.77', '23.0'),  # noqa E241
            ('123.0', '100.0', '23.0', 1, '123.0', '100.0', '23.0', '33.33', 'percent_unit',  '82.0',   '66.67',  '15.33', '23.0'),  # noqa E241
            ('123.0', '100.0', '23.0', 1, '123.0', '100.0', '23.0', '33.33', 'percent_total', '82.0',   '66.67',  '15.33', '23.0'),  # noqa E241
            ('369.0', '300.0', '69.0', 3, '123.0', '100.0', '23.0', '33.33', 'percent_unit',  '246.01', '200.01', '46.0',  '23.0'),  # noqa E241
            ('369.0', '300.0', '69.0', 3, '123.0', '100.0', '23.0', '33.33', 'percent_total', '246.01', '200.01', '46.0',  '23.0'),  # noqa E241
        ]
    )
    def test_discount_amount(self, sandbox_api,
                             total_price_gross, total_price_net, total_price_tax, quantity,
                             price_gross, price_net, price_tax, discount, discount_kind,
                             final_price_gross, final_price_net, final_price_tax, tax):
        """This more an expectation validation test an actual unit test"""

        position = factories.InvoicePosition(
            total_price_gross=total_price_gross,
            tax=tax,
            quantity=quantity,
            discount=discount,
            discount_percent=discount,
        )
        invoice = factories.InvoiceFactory(
            api_client=sandbox_api,
            show_discount=1,
            discount_kind=discount_kind,
            positions=[position]
        )
        invoice.post().get()
        position = invoice.positions[0]

        # Has discount
        if discount_kind == 'amount':
            assert discount == position['discount']
        else:
            assert discount == position['discount_percent']

        # No discount shown in totals of position
        assert total_price_gross == position['total_price_gross']
        assert total_price_net == position['total_price_net']
        assert total_price_tax == position['total_price_tax']

        # Quantity quantity * price == total_price
        assert price_gross == position['price_gross']
        assert price_net == position['price_net']
        assert price_tax == position['price_tax']
        assert tax == position['tax']

        # With discount
        assert final_price_gross == invoice.price_gross
        assert final_price_net == invoice.price_net
        assert final_price_tax == invoice.price_tax


# noinspection PyMethodMayBeStatic
class BaseModelTests(object):
    def test_get(self, offline_client, mocker):
        client_get = mocker.patch('fakturownia.core.ApiClient.get')
        client_get.return_value = {'foo': 'bar'}
        item = base.BaseModel(offline_client, _endpoint='api')
        item.get()
        assert client_get.called
        assert item.foo == 'bar'

    def test_missing_attribute(self):
        item = base.BaseModel(None)
        with pytest.raises(AttributeError, match='BaseModel instance does not have foo_bar key in data dictionary'):
            # noinspection PyStatementEffect
            item.foo_bar

    def test_update_data(self):
        item = base.BaseModel(None, id=333)
        with pytest.raises(AssertionError, match='Existing id does not match update data 333!=777'):
            # noinspection PyProtectedMember
            item._update_data({'id': 777})

    # noinspection PyProtectedMember
    def test_api_client_by_string_key(self):
        item = base.BaseModel('adios/pomidory')
        assert item._api_client.base_url == 'https://pomidory.fakturownia.pl/'
        assert item._api_client.api_token == 'adios/pomidory'

    def test_update_data(self):
        item = base.BaseModel('adios/pomidory')
        item.update_data(tanie='dranie')
        assert item.tanie == 'dranie'
