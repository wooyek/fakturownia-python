# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging

import pytest

from fakturownia import factories, vat

log = logging.getLogger(__name__)


@pytest.mark.parametrize("country, vat", [('DE', 19), ('ES', 21), ('UK', 20)])
def test_eu_normalize_vat(country, vat):
    invoice = factories.InvoiceFactory(seller_country='PL', buyer_country=country, buyer_tax_no=None)
    invoice.normalize_vat()
    for position in invoice.positions:
        assert vat == position['tax']


def test_eu_normalize_vat_company():
    invoice = factories.InvoiceFactory(seller_country='PL', buyer_country='DE')
    invoice.normalize_vat(23)
    for position in invoice.positions:
        assert 0 == position['tax']


def test_normalize_vat_world():
    invoice = factories.InvoiceFactory(seller_country='PL', buyer_country='US')
    invoice.normalize_vat(23)
    for position in invoice.positions:
        assert 23 == position['tax']


def test_eu_member_state_validation():
    with pytest.raises(ValueError, match='US not found in eu member state vat table'):
        vat.get_standard_vat_rate('us')


def test_invalid_tax_no_is_not_restricted(sandbox_api):
    i = factories.InvoiceFactory(
        api_client=sandbox_api,
        kind='proforma',
        use_moss=True,
        seller_country='PL',
        buyer_country='DE',
        buyer_tax_no='lorem',
    )
    i.normalize_vat().post()
    logging.debug("i.view_url: %s", i.view_url)
