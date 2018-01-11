# coding=utf-8
import random

import factory
from factory import DictFactory
from faker import providers

from . import endpoints
from fakturownia.core import ApiClient


class TestEmailProvider(providers.BaseProvider):
    def niepodam_email(self):
        return '{}@niepodam.pl'.format(self.generator.user_name())


factory.Faker.add_provider(TestEmailProvider)
api_client = ApiClient(api_token='invalid-token', base_url='http://invalid.example.com')


class InvoiceFactory(factory.Factory):
    class Meta:
        model = endpoints.Invoice

    api_client = api_client
    kind = 'vat'
    number = None
    currency = 'EUR'
    show_discount = '1'
    discount_kind = 'amount'
    sell_date = factory.Faker('future_date')
    issue_date = factory.Faker('future_date')
    payment_to = factory.Faker('future_date')
    seller_name = factory.Faker('company')
    seller_tax_no = factory.Faker('company_vat', locale='pl_PL')
    seller_bank_account = factory.Faker('iban')
    seller_post_code = factory.Faker('postalcode')
    seller_city = factory.Faker('city')
    seller_street = factory.Faker('street_name')
    seller_country = factory.Faker('country_code')
    buyer_name = factory.Faker('company')
    buyer_tax_no = factory.Faker('company_vat', locale='pl_PL')
    buyer_post_code = factory.Faker('postalcode')
    buyer_city = factory.Faker('city')
    buyer_street = factory.Faker('street_name')
    buyer_first_name = factory.Faker('first_name')
    buyer_last_name = factory.Faker('last_name')
    buyer_country = factory.Faker('country_code')
    buyer_email = factory.Faker('niepodam_email')

    # noinspection PyUnusedLocal
    @factory.post_generation
    def positions(self, create, extracted, **kwargs):
        if extracted is None:  # pragma: no branch
            extracted = InvoicePosition.create_batch(random.randint(1, 10))
        # noinspection PyAttributeOutsideInit
        self.positions = extracted


class InvoicePosition(DictFactory):
    name = factory.Faker('bs')
    # tax = 23
    total_price_gross = factory.LazyFunction(lambda: round(random.random() * 30, 2) + 3)
    quantity = factory.LazyFunction(lambda: random.randint(1, 30))
    discount = factory.LazyFunction(lambda: round(random.random() * 3, 2))
    code = factory.Faker('ean8')


class ClientFactory(factory.Factory):
    class Meta:
        model = endpoints.Client

    api_client = api_client
    name = factory.Faker('company')
    tax_no = factory.Faker('company_vat', locale='pl_PL')
    post_code = factory.Faker('postalcode')
    city = factory.Faker('city')
    street = factory.Faker('street_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    country = factory.Faker('country')
    email = factory.Faker('niepodam_email')
