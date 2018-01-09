# coding=utf-8
import logging
import re
import shlex

import six

if six.PY3:
    from pathlib import Path
else:
    from pathlib2 import Path

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
        path = Path(path)
    return dict(parse_env(path.read_text()))


def get_key_from_file(env_file=None):
    """This is a utili"""
    env_file = env_file or (Path(__file__).parents[2] / 'secrets.env')
    return get_env_from_file(env_file).get('FAKTUROWNIA_API_TOKEN', None)
