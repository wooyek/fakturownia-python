# coding=utf-8
import json
import logging
import sys

import requests
import six
from requests import HTTPError
from requests.structures import CaseInsensitiveDict
from urllib3.util import parse_url

from fakturownia import endpoints
from fakturownia.exceptions import FakturowniaException, HttpException

log = logging.getLogger(__file__)


class ApiClient(object):
    """ Fakturownia API client

    Here is an example of how to crete an invoice.
    But first make sure you have set  `FAKTUROWNIA_API_TOKEN` environment variable.

    >>> import os
    >>> os.environ.get('FAKTUROWNIA_API_TOKEN', 'Missing key')  # doctest: +ELLIPSIS
    '...'
    >>> from fakturownia import get_default_client
    >>> api = get_default_client()
    >>> invoice = api.invoices.create(
    ...     seller_name='Kabaret Starszych Panów',
    ...     buyer_name='Odrażający drab',
    ...     positions=[{
    ...         'name': 'Smolna szczapa',
    ...         'quantity': 5,
    ...         'total_price_gross': 7.33,
    ...     }],
    ... )

    This instance is only partially updated as create returns only subset of
    data properties, to get all we need to update our instance.

    This shows payment_url but only if you have payments enabled.

    >>> invoice.get() # doctest: +ELLIPSIS
    <fakturownia.endpoints.Invoice object at 0x...>
    >>> invoice.payment_url # doctest: +ELLIPSIS
    u'...'

    We can mark this invoice as paid.

    >>> invoice.mark_paid() # doctest: +ELLIPSIS
    <fakturownia.endpoints.Invoice object at 0x...>

    You can chain your calls

    >>> invoice.put(buyer_email='kominek@niepodam.pl').send_by_email() # doctest: +ELLIPSIS
    <fakturownia.endpoints.Invoice object at 0x...>

    """

    def __init__(self, api_token, base_url=None):
        self.api_token = api_token
        if base_url is not None:
            self.base_url = base_url
        else:
            self.base_url = 'https://{}.fakturownia.pl/'.format(self.api_token.split('/')[1])
        from . import __version__ as version
        self.default_headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'user-agent': "Fakturownia Python/" + version
        }

        log.info("Fakturownia: base_url: %s api_token: ***%s", self.base_url, self.api_token[self.api_token.index('/'):] if '/' in self.api_token else '')
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

    def put(self, endpoint, data=None, headers=None):
        payload = self.build_payload(data)
        payload = json.dumps(payload)
        return self.request('PUT', endpoint, payload=payload, headers=headers)

    def delete(self, endpoint, data=None, headers=None):
        params = self.build_payload(data)
        return self.request('DELETE', endpoint, params=params, headers=headers)

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

    :return: ApiClient instance
    """
    import os
    from fakturownia import settings
    api_token = os.environ.get('FAKTUROWNIA_API_TOKEN', None)
    if api_token is None:
        api_token = settings.get_key_from_file()
    if api_token is None:
        raise FakturowniaException('Please set FAKTUROWNIA_API_TOKEN environment variable')
    base_url = os.environ.get('FAKTUROWNIA_BASE_URL', None)
    return ApiClient(api_token=api_token, base_url=base_url)
