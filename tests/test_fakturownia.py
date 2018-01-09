#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fakturownia-python` package."""
import logging
import os

import pytest
from faker import Faker

import fakturownia
from fakturownia.core import get_default_client
from fakturownia.exceptions import FakturowniaException

fake = Faker()
log = logging.getLogger(__name__)


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/wooyek/cookiecutter-pylib')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_version_exists():
    """This is a stupid test dummy validating import of fakturownia"""
    assert fakturownia.__version__


@pytest.fixture
def api_token():
    initial_value, clear = None, True
    if 'FAKTUROWNIA_API_TOKEN' in os.environ:
        initial_value = os.environ.get('FAKTUROWNIA_API_TOKEN', None)
        clear = False
    os.environ['FAKTUROWNIA_API_TOKEN'] = 'invalid-token/invalid-url'
    yield
    if clear:
        del os.environ['FAKTUROWNIA_API_TOKEN']
    else:
        os.environ['FAKTUROWNIA_API_TOKEN'] = initial_value


def test_client_factory():
    client = get_default_client()
    assert client is not None
    assert client.api_token
    log.debug("client.base_url: %s", client.base_url)
    assert client.base_url


def test_client_factory_no_environment(mocker):
    get_env_from_file = mocker.patch('fakturownia.settings.get_env_from_file')
    get_env_from_file.return_value = {}
    with pytest.raises(FakturowniaException, match='Please set FAKTUROWNIA_API_TOKEN environment variable'):
        get_default_client()
