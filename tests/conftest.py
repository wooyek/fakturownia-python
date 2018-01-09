# coding=utf-8
import logging
from pathlib import Path

import envparse
import pytest

from fakturownia.core import Client

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)
logging.getLogger('environ').setLevel(logging.INFO)

log = logging.getLogger(__name__)


@pytest.fixture
def client():
    return Client('fake-key', 'https://fakturownia.example.com')


# api_call = pytest.mark.skipif('TRAVIS' in os.environ, reason="Make an actual API call")


@pytest.fixture
def sandbox_client(request):
    secrets = Path(__file__).parent / 'secrets.env'
    if not secrets.exists:
        pytest.skip('Requires valid API token in: {}'.format(secrets))

    env = envparse.Env()
    env.read_envfile(str(secrets))
    if not env.bool('FAKTUROWNIA_SANDBOX_ENABLED', default=False):
        pytest.skip('Sandbox calls are disabled')

    api_token = env('FAKTUROWNIA_API_TOKEN')
    base_url = env('FAKTUROWNIA_BASE_URL')
    return Client(api_token=api_token, base_url=base_url)

# def pytest_configure(config):
#     env = envparse.Env()
#     env.read_envfile()
#     log.debug("FAKTUROWNIA_SANDBOX_ENABLED: %s", )
