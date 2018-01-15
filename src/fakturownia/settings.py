# coding=utf-8
"""
Utilities for settings loading

Since envparse modifies os.environ on while loading .env files we need and
alternate solution that wont't touch os.environ by default.
"""

import logging
import re
import shlex

import six

if six.PY3:  # pragma: no cover
    from pathlib import Path
else:
    from pathlib2 import Path  # pragma: no cover

log = logging.getLogger(__name__)


def parse_env(content):  # pragma: no cover
    # content = six.u(content)
    # This comes from evnparse.Env.read_envfile. Kudos!
    for line in content.splitlines():
        if line.startswith("#"):
            continue
        tokens = list(shlex.shlex(line, posix=True))
        # parses the assignment statement
        if len(tokens) < 3:
            continue
        name, op = tokens[:2]
        value = ''.join(tokens[2:])
        if op != '=':  # noqa
            continue
        if not re.match(r'[A-Za-z_][A-Za-z_0-9]*', name):  # noqa
            continue
        value = value.replace(r'\n', '\n').replace(r'\t', '\t')
        yield name, value


def get_env_from_file(path):
    if not isinstance(path, Path):  # pragma: no cover
        path = Path(str(path))
    return dict(parse_env(path.read_text()))


def get_key_from_file(env_file=None):
    """This is a utility to ease testing with secrets.env file present or not"""
    env_file = env_file or get_default_env_file()
    if not env_file.exists():
        return None
    return get_env_from_file(env_file).get('FAKTUROWNIA_API_TOKEN', None)


def get_default_env_file():
    """Returns secrets.env from project root, should not be used outside testing"""
    return Path(__file__).parents[2] / 'secrets.env'
