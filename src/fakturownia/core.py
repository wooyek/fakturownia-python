# coding=utf-8
import json
import logging
import sys

import envparse
import requests
import six
from requests import HTTPError
from requests.structures import CaseInsensitiveDict
from urllib3.util import parse_url

from . import __version__ as version
from fakturownia import endpoints
from fakturownia.exceptions import HttpException

log = logging.getLogger(__file__)


class Client(object):
    def __init__(self, api_token, base_url):
        self.base_url = base_url
        self.api_token = api_token
        self.default_headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'user-agent': "Fakturownia Python/" + version
        }
        self.invoices = endpoints.Invoices(self)
        self.clients = endpoints.Clients(self)

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, url):
        log.debug("url: %s", url)
        parsed = parse_url(url)
        if parsed.scheme is None or parsed.hostname is None:
            raise ValueError("Invalid url: {}".format(url))
        # noinspection PyAttributeOutsideInit
        self._base_url = url

    # noinspection PyMethodMayBeStatic
    def request_factory(self, *args, **kwargs):
        return requests.request(*args, **kwargs)

    def post(self, endpoint, data=None, headers=None):
        payload = self.build_payload(data)
        payload = json.dumps(payload)
        return self.request('POST', endpoint, payload=payload, headers=headers)

    def get(self, endpoint, data=None, headers=None):
        params = self.build_payload(data)
        return self.request('GET', endpoint, params=params, headers=headers)

    def request(self, method, endpoint, params=None, payload=None, headers=None):
        url = self.base_url + endpoint
        log.debug("url: %s", url)
        log.debug("payload: %s", payload)
        resp = self.request_factory(
            method=method,
            url=url,
            headers=self.build_headers(headers),
            data=payload,
            params=params,
        )
        log.debug("response: %s", resp)
        log.debug("response: %s", resp.text)
        self.validate_response(resp)
        return resp.json()

    def build_payload(self, data=None):
        payload = {
            'api_token': self.api_token,
        }
        if data:
            payload.update(data)
        return payload

    def build_headers(self, items=None):
        headers = CaseInsensitiveDict(self.default_headers)
        if items:
            headers.update(items)
        return headers

    # noinspection PyMethodMayBeStatic
    def validate_response(self, response):
        try:
            response.raise_for_status()
        except HTTPError as ex:
            data = response.json()
            if 'code' in data and data['code'] == 'error':
                msg = str(ex) + " - " + str(data['message'])
                six.reraise(HttpException, HttpException(msg, response), sys.exc_info()[2])
            raise six.reraise(HttpException, HttpException(ex, response), sys.exc_info()[2])


def get_default_client():
    """
    Factory function for Fakturownia API client with configuration options
    taken from environment

    :return: Client instance
    """
    env = envparse.Env()
    api_token = env('FAKTUROWNIA_API_TOKEN')
    base_url = env('FAKTUROWNIA_BASE_URL')
    return Client(api_token=api_token, base_url=base_url)
