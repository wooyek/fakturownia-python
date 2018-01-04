# coding=utf-8
import datetime
import logging
import os

import pytest
import six
from mock import MagicMock

from . import test_data
from fakturownia import factories

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
    assert item.payment_url


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


def test_dates_on_invoice():
    invoice = factories.InvoiceFactory()
    assert isinstance(invoice.sell_date, datetime.date)
    assert isinstance(invoice.issue_date, datetime.date)
    assert isinstance(invoice.payment_to, datetime.date)
    assert isinstance(invoice._data['sell_date'], six.string_types)
    assert isinstance(invoice._data['issue_date'], six.string_types)
    assert isinstance(invoice._data['payment_to'], six.string_types)
