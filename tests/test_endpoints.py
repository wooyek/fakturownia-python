# coding=utf-8
import datetime
import logging
import os

import pytest
import six
from mock import MagicMock

from . import test_data
from fakturownia import base, factories

log = logging.getLogger(__name__)


@pytest.fixture(params=["invoices", "clients"])
def endpoint(request, client):
    return getattr(client, request.param)


def test_create_invioce(endpoint, mocker):
    request = mocker.patch('requests.request')
    request.return_value = MagicMock()
    request.json.return_value = {}
    endpoint.create()
    assert request.called


@pytest.mark.parametrize("data", [
    test_data.INVOICE_CREATE_DATA,
    factories.InvoiceFactory()._data,
])
def test_create_refresh_send_invoice_sandbox(sandbox_client, data):
    invoice = sandbox_client.invoices.create(**data)
    assert invoice
    invoice.get()
    log.debug("id: %s", invoice.id)
    log.debug("payment_url: %s", invoice.payment_url)
    assert invoice.id
    assert invoice.payment_url


@pytest.mark.parametrize("buyer_email", ['fakturownia@niepodam.pl', os.environ.get('FAKTUROWNIA_SANDBOX_EMAIL', 'dummy@niepodam.pl')])
def test_send_invoice(sandbox_client, buyer_email):
    invoice = factories.InvoiceFactory(client=sandbox_client, buyer_email=buyer_email)
    invoice.post()
    invoice.send_by_email()


@pytest.mark.parametrize("data", [
    test_data.CLIENT_CREATE_DATA,
    factories.ClientFactory()._data,
])
def test_create_refresh_client_sandbox(sandbox_client, data):
    item = sandbox_client.clients.create(**data)
    assert item
    item.get()
    log.debug("id: %s", item.id)
    assert item.id


def test_client_create_invoice(mocker):
    invoices_create = mocker.patch('fakturownia.endpoints.Invoices.create')
    client = factories.ClientFactory(id=777)
    client.create_invoice()
    assert invoices_create.called


def test_client_create_invoice_no_id():
    client = factories.ClientFactory()
    with pytest.raises(AssertionError):
        client.create_invoice()


@pytest.mark.parametrize("data", [
    test_data.CLIENT_CREATE_DATA,
    factories.ClientFactory()._data,
])
def test_client_create_invoice_sandbox(sandbox_client, data):
    client = sandbox_client.clients.create(**data)
    invoice = client.create_invoice(positions=[{'product_id': 11912912, 'quantity': 100}])
    invoice.get()
    log.debug("id: %s", client.id)
    assert invoice.id
    assert invoice.payment_url


# noinspection PyMethodMayBeStatic
class InvoiceTests(object):

    # noinspection PyProtectedMember
    def test_dates_on_invoice(self):
        invoice = factories.InvoiceFactory()
        assert isinstance(invoice.sell_date, datetime.date)
        assert isinstance(invoice.issue_date, datetime.date)
        assert isinstance(invoice.payment_to, datetime.date)
        assert isinstance(invoice._data['sell_date'], six.string_types)
        assert isinstance(invoice._data['issue_date'], six.string_types)
        assert isinstance(invoice._data['payment_to'], six.string_types)

    def test_set_datetime_str(self):
        invoice = factories.InvoiceFactory()
        invoice.sell_date = '1980-08-14'
        assert invoice.sell_date == datetime.date(1980, 8, 14)
        # noinspection PyProtectedMember
        assert invoice._data['sell_date'] == '1980-08-14'

    def test_send_by_email(self, mocker):
        post = mocker.patch('fakturownia.core.Client.post')
        invoice = factories.InvoiceFactory(id='666')
        invoice.send_by_email()
        post.assert_called_with('invoices/666/send_by_email.json')

    def test_send_by_email_failed_no_id(self):
        invoice = factories.InvoiceFactory()
        with pytest.raises(AssertionError, match='Cannot send invoice without id'):
            invoice.send_by_email()


# noinspection PyMethodMayBeStatic
class BaseModelTests(object):

    def test_get(self, client, mocker):
        client_get = mocker.patch('fakturownia.core.Client.get')
        client_get.return_value = {'foo': 'bar'}
        item = base.BaseModel(client, _endpoint='api')
        item.get()
        assert client_get.called
        assert item.foo == 'bar'

    def test_missing_attribute(self):
        item = base.BaseModel(None)
        with pytest.raises(AttributeError, match='BaseModel instance does not have foo_bar key in data dictionary'):
            item.foo_bar

    def test_update_data(self):
        item = base.BaseModel(None, id=333)
        with pytest.raises(AssertionError, match='Existing id does not match update data 333!=777'):
            # noinspection PyProtectedMember
            item._update_data({'id': 777})
