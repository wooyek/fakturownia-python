# coding=utf-8
# Copyright 2015 Brave Labs sp. z o.o.
# All rights reserved.
#
# This source code and all resulting intermediate files are CONFIDENTIAL and
# PROPRIETY TRADE SECRETS of Brave Labs sp. z o.o.
# Use is subject to license terms. See NOTICE file of this project for details.

import logging

import six

from fakturownia import settings

log = logging.getLogger(__name__)

if six.PY3:
    from pathlib import Path
else:
    from pathlib2 import Path


def test_get_key_from_file(mocker):
    get_defafut_env_file = mocker.patch('fakturownia.settings.get_default_env_file')
    get_defafut_env_file.return_value = Path('file-that-does-not-exist')
    assert settings.get_key_from_file() is None
