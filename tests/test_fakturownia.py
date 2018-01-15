#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fakturownia-python` package."""
import logging
import os

import pytest

import fakturownia
from fakturownia.core import get_api_client
from fakturownia.exceptions import FakturowniaException

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


@pytest.fixture
def no_api_token_env():
    if 'FAKTUROWNIA_API_TOKEN' not in os.environ:
        yield
        return

    initial_value, clear = None, True
    if 'FAKTUROWNIA_API_TOKEN' in os.environ:
        initial_value = os.environ.get('FAKTUROWNIA_API_TOKEN', None)
        clear = False
    del os.environ['FAKTUROWNIA_API_TOKEN']
    yield
    if clear:
        del os.environ['FAKTUROWNIA_API_TOKEN']
    else:
        os.environ['FAKTUROWNIA_API_TOKEN'] = initial_value


def test_client_factory(api_token):
    api_client = get_api_client()
    assert api_client is not None
    assert api_client.api_token
    log.debug("api_client.base_url: %s", api_client.base_url)
    assert api_client.base_url


def test_client_factory_no_environment(mocker, no_api_token_env):
    get_env_from_file = mocker.patch('fakturownia.settings.get_env_from_file')
    get_env_from_file.return_value = {}
    with pytest.raises(FakturowniaException, match='Please set FAKTUROWNIA_API_TOKEN environment variable'):
        get_api_client()


def test_client_factory_timeout(mocker):
    mocker.patch.dict('os.environ', {'FAKTUROWNIA_TIMEOUT': '0.1'})
    api = get_api_client()
    assert 0.1 == api.request_timeout


def test_client_factory_default_timeout():
    api = get_api_client()
    assert api.request_timeout is None
