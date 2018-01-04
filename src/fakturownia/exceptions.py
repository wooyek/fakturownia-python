# coding=utf-8
import inspect
import logging

import sys

log = logging.getLogger(__name__)


class FakturowniaException(Exception):
    pass


class ClientException(FakturowniaException):
    """Base client exception with data attribute"""

    def __init__(self, message, data=None, *args: object) -> None:
        super(ClientException, self).__init__(message, *args)
        self.data = data


class HttpException(ClientException):
    def __init__(self, message, response, *args) -> None:
        # noinspection PyUnresolvedReferences
        self.message = message
        self.status_code = response.status_code
        self.reason = response.reason
        self.response = response.reason
        super(HttpException, self).__init__(message, *args)

#
# class Http400BadRequest(HttpException):
#     status_code = 400
#     status_message = 'Bad Request'
#
#
# class Http422BadRequest(HttpException):
#     status_code = 422
#     status_message = 'Unprocessable Entity'
#
#
# http_exceptions = inspect.getmembers(sys.modules[__name__], inspect.isclass)
# http_exceptions = dict((c.status_code, c) for c in http_exceptions if isinstance(c, HttpException))

