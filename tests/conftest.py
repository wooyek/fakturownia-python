# coding=utf-8
import json
import logging
import os

import envparse
import pytest
import six
from faker import Faker
from mock import MagicMock
from pytest_lazyfixture import lazy_fixture

from fakturownia.core import ApiClient
from fakturownia.exceptions import HttpException
from fakturownia.settings import get_env_from_file

if six.PY3:
    from pathlib import Path
else:
    from pathlib2 import Path

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
# logging.disable(logging.NOTSET)
logging.getLogger('environ').setLevel(logging.INFO)

log = logging.getLogger(__name__)
fake = Faker()


class MockedApiClient(ApiClient):

    def __init__(self):
        super(MockedApiClient, self).__init__('invalid-key/invalid-api-url')
        super(ApiClient, self).__setattr__('_storage', {})
        super(ApiClient, self).__setattr__('_ids', (i for i in range(999, 9999)))

    def request(self, method, endpoint, params=None, payload=None, headers=None):
        if endpoint.count('/') > 1:
            return
        payload = json.loads(payload)
        kind = endpoint.replace('.json', '')[:-1]
        data = payload[kind].copy()
        if 'id' not in data or data['id'] is None:
            data['id'] = self._ids.__next__()
        self._storage.setdefault(kind, {})[data['id']] = data
        if kind == 'invoice':
            data['payment_url'] = fake.url()
            data['status'] = 'issued'
        return data

    def delete(self, endpoint, data=None, headers=None):
        model_id, model_name = self.parse_endpoint(endpoint)
        del self._storage[model_name][model_id]
        return

    def get(self, endpoint, data=None, headers=None):
        model_id, model_name = self.parse_endpoint(endpoint)
        return self._get_model_data(model_name, model_id)

    def _get_model_data(self, model_name, model_id):
        models = self._storage.setdefault(model_name, {})
        if model_id not in models:
            response = MagicMock()
            response.status_code = 404
            raise HttpException('404 Client Error: Not Found for url', response, None)
        return models[model_id]

    def put(self, endpoint, data=None, headers=None):
        model_id, model_name = self.parse_endpoint(endpoint)
        model_data = self._get_model_data(model_name, model_id)
        model_data.update(data[model_name])
        return model_data.copy()

    @staticmethod
    def parse_endpoint(endpoint):
        logging.debug("endpoint: %s", endpoint)
        if "/" not in endpoint:
            return None, endpoint.replace('.json', '')

        endpoint, model_id = endpoint.split('/')
        model_id = int(model_id.replace('.json', ''))
        model_name = endpoint[:-1]
        return model_id, model_name

    def request_factory(self, *args, **kwargs):
        raise Exception('{} should not try to make requests'.format(self.__class__.__name__))

    # def __getattr__(self, key):
    #     if key not in self._storage:
    #         msg = '{} instance does not have {} key in _storage dictionary'
    #         raise AttributeError(msg.format(self.__class__.__name__, key))
    #     return self._storage[key]


@pytest.fixture
def mocked_client():
    return MockedApiClient()


@pytest.fixture
def offline_client():
    return ApiClient('fake-key', 'https://fakturownia.example.com')


@pytest.fixture
def secrets():
    env_file = Path(__file__).parents[1] / 'secrets.env'
    if not env_file.exists():
        pytest.skip('Requires an environment file with secret settings: {}'.format(env_file))

    return get_env_from_file(env_file)


@pytest.fixture
def sandbox_client(request, secrets):
    sandbox_enabled = secrets.get('FAKTUROWNIA_SANDBOX_ENABLED', None) or os.environ.get('FAKTUROWNIA_SANDBOX_ENABLED', None)
    sandbox_enabled = envparse.Env.cast(sandbox_enabled, bool)
    if not sandbox_enabled:
        pytest.skip('Sandbox calls are disabled')

    api_token = secrets.get('FAKTUROWNIA_API_TOKEN', None) or os.environ.get('FAKTUROWNIA_API_TOKEN')
    base_url = secrets.get('FAKTUROWNIA_BASE_URL', None)
    return ApiClient(api_token, base_url)


@pytest.fixture(params=[
    lazy_fixture('mocked_client'),
    lazy_fixture('sandbox_client')
])
def api_client(request):
    return request.param
