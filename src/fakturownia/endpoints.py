# coding=utf-8
from datetime import datetime

import six

from fakturownia.base import BaseEndpoint, BaseModel


class DateProperty(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def __get__(self, instance, owner):
        value = instance._data.get(self.name)
        return datetime.strptime(value, '%Y-%m-%d').date() if value and isinstance(value, six.string_types) else value

    def __set__(self, instance, value):
        if not isinstance(value, six.string_types):
            value = value.strftime('%Y-%m-%d')
        # noinspection PyProtectedMember
        instance._data[self.name] = value


class Invoices(BaseEndpoint):

    def create(self, **kwargs):
        return Invoice(self.client, **kwargs).post()


class Invoice(BaseModel):
    endpoint = 'invoices'
    data_wrap = 'invoice'
    sell_date = DateProperty('sell_date')
    issue_date = DateProperty('issue_date')
    payment_to = DateProperty('payment_to')

    def send_by_email(self):
        endpoint = self.get_endpoint('/send_by_email')
        self._client.post(endpoint)


class Clients(BaseEndpoint):

    def create(self, **kwargs):
        return Client(self.client, **kwargs).post()


class Client(BaseModel):
    endpoint = 'clients'
    data_wrap = 'client'

    def create_invoice(self, **kwargs):
        assert self.id
        kwargs['client_id'] = self.id
        return self._client.invoices.create(**kwargs)
