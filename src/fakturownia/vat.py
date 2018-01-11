# coding=utf-8
"""Utilities to get EU member state VAT values

These are not directly connected Fakturownia but since setting 'use_moss'
has no effect during invoice creation, this mapping maybe helpful

Based on
https://ec.europa.eu/taxation_customs/sites/taxation/files/resources/documents/taxation/vat/how_vat_works/rates/vat_rates_en.pdf
"""
import logging
from collections import namedtuple

log = logging.getLogger(__name__)

eu_member_state_vat_table_columns = ('country', 'country_code', 'super_reduced_rate', 'reduced_rate', 'standard_rate', 'parking_rate')
eu_member_state_vat_table = (
    ('Belgium', 'BE', None, (6, 12), 21, 12),
    ('Bulgaria', 'BG', None, 9, 20, None),
    ('Czech Republic', 'CZ', None, (10, 15), 21, None),
    ('Denmark', 'DK', None, None, 25, None),
    ('Germany', 'DE', None, 7, 19, None),
    ('Estonia', 'EE', None, 9, 20, None),
    ('Ireland', 'IE', 4.8, (9, 13), 5, 23, 13.5),
    ('Greece', 'EL', None, (6, 13), 24, None),
    ('Spain', 'ES', 4, 10, 21, None),
    ('France', 'FR', 2.1, 5, (5, 10), 20, None),
    ('Croatia', 'HR', None, (5, 13), 25, None),
    ('Italy', 'IT', 4, (5, 10), 22, None),
    ('Cyprus', 'CY', None, (5, 9), 19, None),
    ('Latvia', 'LV', None, 12, 21, None),
    ('Lithuania', 'LT', None, (5, 9), 21, None),
    ('Luxembourg', 'LU', 3, 8, 17, 14),
    ('Hungary', 'HU', None, (5, 18), 27, None),
    ('Malta', 'MT', None, (5, 7), 18, None),
    ('Netherlands', 'NL', None, 6, 21, None),
    ('Austria', 'AT', None, (10, 13), 20, 13),
    ('Poland', 'PL', None, (5, 8), 23, None),
    ('Portugal', 'PT', None, (6, 13), 23, 13),
    ('Romania', 'RO', None, (5, 9), 19, None),
    ('Slovenia', 'SI', None, 9.5, 22, None),
    ('Slovakia', 'SK', None, 10, 20, None),
    ('Finland', 'FI', None, (10, 14), 24, None),
    ('Sweden', 'SE', None, (6, 12), 25, None),
    ('United Kingdom', 'UK', None, 5, 20, None),
)

VAT = namedtuple('VAT', eu_member_state_vat_table_columns)

eu_member_state_vat = (VAT(**(dict(zip(eu_member_state_vat_table_columns, item)))) for item in eu_member_state_vat_table)
eu_member_state_vat = dict((item.country_code, item) for item in eu_member_state_vat)


def get_standard_vat_rate(country_code):
    country_code = country_code.upper()
    if country_code not in eu_member_state_vat:
        raise ValueError('{} not found in eu member state vat table'.format(country_code))
    vat = eu_member_state_vat[country_code.upper()]
    return vat.standard_rate
