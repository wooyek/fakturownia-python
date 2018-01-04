# coding=utf-8
import logging

log = logging.getLogger(__name__)


class FakturowniaException(Exception):
    pass


class ClientException(FakturowniaException):
    """Base client exception with data attribute"""

    def __init__(self, message, data=None, *args: object) -> None:
        super(ClientException, self).__init__(message, *args)
        self.data = data


class HttpException(ClientException):
    def __init__(self, message, response, data=None, *args) -> None:
        # noinspection PyUnresolvedReferences
        self.message = message
        self.status_code = response.status_code
        self.reason = response.reason
        self.response = response.reason
        super(HttpException, self).__init__(message, data=data, *args)
