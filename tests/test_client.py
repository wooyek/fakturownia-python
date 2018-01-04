# coding=utf-8


def test_default_headers(client):
    headers = client.build_headers()
    assert headers['Accept'] == 'application/json'
    assert headers['Content-Type'] == 'application/json'
    assert set(headers.keys()) == {'accept', 'user-agent', 'content-type'}


def test_get_additional_headers(client):
    headers = client.build_headers({'foo': 'bar'})
    assert headers['foo'] == 'bar'


def test_override_headers(client):
    headers = client.build_headers({'Accept': 'bar'})
    assert headers['Accept'] == 'bar'
    assert headers['accept'] == 'bar'


def test_default_payload(client):
    payload = client.build_payload()
    assert payload['api_token'] == 'fake-key'


def test_build_payload(client):
    data = {'foo': 'bar'}
    payload = client.build_payload(data)
    assert payload['foo'] == 'bar'
