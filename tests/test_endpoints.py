# coding=utf-8
import datetime
import logging
import os

import pytest
import six
from mock import MagicMock

from . import test_data
from fakturownia import base, factories
from fakturownia.exceptions import HttpException

log = logging.getLogger(__name__)

# noinspection PyUnresolvedReferences
CLIENT_CREATE = test_data.CLIENT_CREATE
# noinspection PyUnresolvedReferences
INVOICE_CREATE = test_data.INVOICE_CREATE


@pytest.fixture(params=["invoices", "clients"])
def endpoint(request, offline_client):
    return getattr(offline_client, request.param)


@pytest.fixture
def existing_product_id(secrets):
    if not 'FAKTUROWNIA_EXISTING_PRODUCT_ID' in secrets:
        pytest.skip('Requires an environment FAKTUROWNIA_EXISTING_PRODUCT_ID setting')
    return secrets['FAKTUROWNIA_EXISTING_PRODUCT_ID']


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
    invoice = factories.InvoiceFactory(client=api_client, buyer_email=buyer_email)
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
        invoice = factories.InvoiceFactory(client=api_client)
        invoice.post()
        assert invoice.status == 'issued'
        invoice.mark_paid()
        assert invoice.status == 'paid'

    def test_delete(self, api_client):
        invoice = factories.InvoiceFactory(client=api_client)
        invoice.post()
        assert invoice.status == 'issued'
        invoice.delete()
        assert invoice.id is not None
        with pytest.raises(HttpException, match='404 Client Error: Not Found for url'):
            api_client.invoices[invoice.id]


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
