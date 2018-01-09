# coding=utf-8
"""Top-level package for Fakturownia."""
from __future__ import absolute_import

__author__ = """Janusz Skonieczny"""
__email__ = 'js+pypi@bravelabs.pl'
__version__ = '0.1.1'

from .core import get_default_client
from .endpoints import Client, Invoice
