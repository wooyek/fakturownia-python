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

# INVOICE_CREATE_DATA = json.loads((FIXTURES / 'invoice_create.json').read_text())
# INVOICE_CREATED = json.loads((FIXTURES / 'invoice_created.json').read_text())
# INVOICE_GET = json.loads((FIXTURES / 'invoice_get.json').read_text())
# CLIENT_CREATE_DATA = json.loads((FIXTURES / 'client_create.json').read_text())
# CLIENT_GET = json.loads((FIXTURES / 'client_get.json').read_text())
# CLIENT_CREATED = json.loads((FIXTURES / 'client_created.json').read_text())
