# coding=utf-8

import pytest
from mock import MagicMock
from requests import HTTPError

from fakturownia import core
from fakturownia.exceptions import HttpException


def test_default_headers(offline_client):
    headers = offline_client.build_headers()
    assert headers['Accept'] == 'application/json'
    assert headers['Content-Type'] == 'application/json'
    assert set(headers.keys()) == {'accept', 'user-agent', 'content-type'}


def test_get_additional_headers(offline_client):
    headers = offline_client.build_headers({'foo': 'bar'})
    assert headers['foo'] == 'bar'


def test_override_headers(offline_client):
    headers = offline_client.build_headers({'Accept': 'bar'})
    assert headers['Accept'] == 'bar'
    assert headers['accept'] == 'bar'


def test_default_payload(offline_client):
    payload = offline_client.build_payload()
    assert payload['api_token'] == 'fake-key'


def test_build_payload(offline_client):
    data = {'foo': 'bar'}
    payload = offline_client.build_payload(data)
    assert payload['foo'] == 'bar'


def test_base_url_validation():
    with pytest.raises(ValueError, match='Invalid url: foo'):
        core.ApiClient(base_url='foo', api_token='')


def test_base_url_from_key():
    offline_client = core.ApiClient(api_token='abc/example.com')
    assert offline_client.base_url == "https://example.com.fakturownia.pl/"


def test_error_message_collection(offline_client, mocker):
    factory = mocker.patch('fakturownia.core.ApiClient.request_factory')
    response = MagicMock()
    response.raise_for_status.side_effect = HTTPError('foo')
    response.json.return_value = {"code": "error", "message": 'bad things'}
    factory.return_value = response
    with pytest.raises(HttpException) as ex:
        offline_client.request(None, 'api')
    assert """foo - bad things""" == str(ex.value)


def test_error_exception_chaining(offline_client, mocker):
    factory = mocker.patch('fakturownia.core.ApiClient.request_factory')
    response = MagicMock()
    response.raise_for_status.side_effect = HTTPError('foo')
    response.json.return_value = {"foo": "bar"}
    factory.return_value = response
    with pytest.raises(HttpException) as ex:
        offline_client.request(None, 'api')
    assert """foo""" == str(ex.value)


def test_get(offline_client, mocker):
    request = mocker.patch('fakturownia.core.ApiClient.request')
    offline_client.get('foo')
    request.assert_called_with('GET', 'foo', headers=None, params={'api_token': 'fake-key'})


def test_put(offline_client, mocker):
    request = mocker.patch('fakturownia.core.ApiClient.request')
    offline_client.put('foo')
    request.assert_called_with('PUT', 'foo', headers=None, payload='{"api_token": "fake-key"}')


def test_delete(offline_client, mocker):
    request = mocker.patch('fakturownia.core.ApiClient.request')
    offline_client.delete('foo')
    request.assert_called_with('DELETE', 'foo', headers=None, params={'api_token': 'fake-key'})
