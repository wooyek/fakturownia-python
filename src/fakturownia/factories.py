# coding=utf-8
import factory
from factory import DictFactory
from faker import providers

from . import endpoints
from fakturownia.core import Client


class TestEmailProvider(providers.BaseProvider):
    def niepodam_email(self):
        return '{}@niepodam.pl'.format(self.generator.user_name())


factory.Faker.add_provider(TestEmailProvider)
client = Client(api_token='invalid-token', base_url='http://invalid.example.com')


class InvoiceFactory(factory.Factory):
    class Meta:
        model = endpoints.Invoice

    client = client
    kind = 'vat'
    number = None
    currency = 'EUR'
    sell_date = factory.Faker('future_date')
    issue_date = factory.Faker('future_date')
    payment_to = factory.Faker('future_date')
    seller_name = factory.Faker('company')
    seller_tax_no = factory.Faker('company_vat', locale='pl_PL')
    seller_bank_account = factory.Faker('iban')
    seller_post_code = factory.Faker('postalcode')
    seller_city = factory.Faker('city')
    seller_street = factory.Faker('street_name')
    seller_country = factory.Faker('country')
    buyer_name = factory.Faker('company')
    buyer_tax_no = factory.Faker('company_vat', locale='pl_PL')
    buyer_post_code = factory.Faker('postalcode')
    buyer_city = factory.Faker('city')
    buyer_street = factory.Faker('street_name')
    buyer_first_name = factory.Faker('first_name')
    buyer_last_name = factory.Faker('last_name')
    buyer_country = factory.Faker('country')
    buyer_email = factory.Faker('niepodam_email')

    @factory.post_generation
    def positions(self, create, extracted, **kwargs):
        if extracted is None:
            extracted = InvoicePosition.create_batch(3)
        self.positions = extracted


class InvoicePosition(DictFactory):
    name = factory.Faker('bs')
    # tax = 23
    total_price_gross = 113.33
    quantity = 13
    discount = 1.33


class ClientFactory(factory.Factory):
    class Meta:
        model = endpoints.Client

    client = client
    name = factory.Faker('company')
    tax_no = factory.Faker('company_vat', locale='pl_PL')
    post_code = factory.Faker('postalcode')
    city = factory.Faker('city')
    street = factory.Faker('street_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    country = factory.Faker('country')
    email = factory.Faker('niepodam_email')
