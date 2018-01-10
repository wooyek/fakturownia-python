# coding=utf-8
"""Top-level package for Fakturownia."""
from __future__ import absolute_import

from .core import get_api_client  # noqa F401
from .endpoints import Client, Invoice  # noqa F401

__author__ = """Janusz Skonieczny"""
__email__ = 'js+pypi@bravelabs.pl'
__version__ = '0.1.2'
