# coding=utf-8
from datetime import datetime

import six

from fakturownia import vat
from fakturownia.base import BaseEndpoint, BaseModel


class DateProperty(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def __get__(self, instance, owner):
        # noinspection PyProtectedMember
        value = instance._data.get(self.name)
        return datetime.strptime(value, '%Y-%m-%d').date() if value and isinstance(value, six.string_types) else value

    def __set__(self, instance, value):
        if not isinstance(value, six.string_types):
            value = value.strftime('%Y-%m-%d')
        # noinspection PyProtectedMember
        instance._data[self.name] = value


class Invoice(BaseModel):
    _endpoint = 'invoices'
    _data_wrap = 'invoice'
    sell_date = DateProperty('sell_date')
    issue_date = DateProperty('issue_date')
    payment_to = DateProperty('payment_to')

    def send_by_email(self):
        assert self.id, 'Cannot send invoice without id'
        endpoint = self.get_endpoint('/send_by_email')
        self._api_client.post(endpoint)
        return self

    def mark_paid(self):
        return self.put(status='paid')

    def normalize_vat(self, default_rate=None, intra_eu_vat_rate='np'):
        """This is a common business logic that maybe helpful in handling EU to EU invoicing"""
        eu_member_states = vat.eu_member_state_vat.keys()
        default_rate = default_rate or vat.get_standard_vat_rate(self.seller_country)
        if self.buyer_country not in eu_member_states:
            # Outside EU
            self.set_tax_on_positions(default_rate)
        else:
            if self.buyer_tax_no is not None:
                # EU company, country
                self.set_tax_on_positions(intra_eu_vat_rate)
                self.description = "VAT reverse charge"
            else:
                # EU citizen, member state VAT rate applies
                vat_rate = vat.get_standard_vat_rate(self.buyer_country)
                self.set_tax_on_positions(vat_rate)
        return self

    def set_tax_on_positions(self, rate):
        for position in self.positions:
            position['tax'] = rate


class Invoices(BaseEndpoint):
    model = Invoice


class Client(BaseModel):
    _endpoint = 'clients'
    _data_wrap = 'client'

    def create_invoice(self, **kwargs):
        assert self.id
        kwargs['client_id'] = self.id
        return self._api_client.invoices.create(**kwargs)

    def prepare_post_data(self, **kwargs):
        payload = super(Client, self).prepare_post_data(**kwargs)
        pop_data = ['balance']
        data = payload[self._data_wrap]
        for key in pop_data:
            if key in data:
                data.pop('balance')
        return payload


class Clients(BaseEndpoint):
    model = Client
