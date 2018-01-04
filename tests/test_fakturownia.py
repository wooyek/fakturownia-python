#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fakturownia-python` package."""
import logging

import fakturownia
import pytest
from envparse import env
from faker import Faker
from fakturownia.core import get_default_client

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
def settings():
    env.read_envfile()


def test_client_factory(settings):
    client = get_default_client()
    assert client is not None
    assert client.api_token
    log.debug("client.base_url: %s", client.base_url)
    assert client.base_url
