# coding=utf-8
import json
import sys

import six

if six.PY3:
    from pathlib import Path
else:
    from pathlib2 import Path

FIXTURES = Path(__file__).parent / 'fixtures'
for p in FIXTURES.glob('*.json'):

    try:
        globals()[p.stem.upper()] = json.loads(p.read_text())
    except ValueError as ex:
        msg = str(ex.msg) + " in " + str(p)
        raise six.reraise(ValueError, ValueError(msg, ex.doc, ex.pos), sys.exc_info()[2])
