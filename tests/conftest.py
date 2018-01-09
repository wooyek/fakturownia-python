# coding=utf-8
import logging
import os

import pytest
import six

from fakturownia.core import ApiClient
from fakturownia.settings import get_env_from_file

if six.PY3:
    from pathlib import Path
else:
    from pathlib2 import Path

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)
logging.getLogger('environ').setLevel(logging.INFO)

log = logging.getLogger(__name__)


@pytest.fixture
def client():
    return ApiClient('fake-key', 'https://fakturownia.example.com')


@pytest.fixture
def secrets():
    env_file = Path(__file__).parents[1] / 'secrets.env'
    if not env_file.exists:
        pytest.skip('Requires an environment file with secret settings: {}'.format(env_file))

    return get_env_from_file(env_file)


@pytest.fixture
def sandbox_client(request, secrets):
    sandbox_enabled = bool(secrets.get('FAKTUROWNIA_SANDBOX_ENABLED', False))
    if not sandbox_enabled:
        pytest.skip('Sandbox calls are disabled')

    api_token = secrets.get('FAKTUROWNIA_API_TOKEN', None) or os.environ.get('FAKTUROWNIA_API_TOKEN')
    base_url = secrets.get('FAKTUROWNIA_BASE_URL', None)
    return ApiClient(api_token, base_url)
