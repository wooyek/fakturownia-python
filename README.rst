===========
Fakturownia
===========

Python client library for the Fakturownia API


.. image:: https://img.shields.io/pypi/v/fakturownia-python.svg
        :target: https://pypi.python.org/pypi/fakturownia-python

.. image:: https://img.shields.io/travis/wooyek/fakturownia-python.svg
        :target: https://travis-ci.org/wooyek/fakturownia-python

.. image:: https://readthedocs.org/projects/fakturownia-python/badge/?version=latest
        :target: https://fakturownia.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/wooyek/fakturownia-python/badge.svg?branch=develop
        :target: https://coveralls.io/github/wooyek/fakturownia-python?branch=develop
        :alt: Coveralls.io coverage

.. image:: https://codecov.io/gh/wooyek/fakturownia-python/branch/develop/graph/badge.svg
        :target: https://codecov.io/gh/wooyek/fakturownia-python
        :alt: CodeCov coverage

.. image:: https://api.codeclimate.com/v1/badges/0e7992f6259bc7fd1a1a/maintainability
        :target: https://codeclimate.com/github/wooyek/fakturownia-python/maintainability
        :alt: Maintainability

.. image:: https://img.shields.io/github/license/wooyek/fakturownia-python.svg
        :target: https://github.com/wooyek/fakturownia-python/blob/develop/LICENSE
        :alt: License

.. image:: https://img.shields.io/twitter/url/https/github.com/wooyek/fakturownia-python.svg?style=social
        :target: https://twitter.com/intent/tweet?text=Wow:&url=https://github.com/wooyek/fakturownia-python
        :alt: Tweet about this project

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
        :target: https://saythanks.io/to/wooyek


* Free software: MIT license
* Documentation: https://fakturownia.readthedocs.io

Features
--------

* ☑ Invoice CRUD plus `send_by_email` and 'mark_paid`
* ☑ ApiClient CRUD
* ☐ Products CRUD
* ☐ Warehouse documents CRUD
* ☐ Accounts management

Please refer to the https://github.com/fakturownia/api_ for full API features

Quickstart
----------

Install Fakturownia::

    pip install fakturownia-python
    python


Play with `fakturownia APIs`_ in python interpreter::

    >>> import os
    >>> os.environ.get('FAKTUROWNIA_API_TOKEN', 'Missing key')
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

    >>> invoice.get()
    <fakturownia.endpoints.Invoice object at 0x...>
    >>> invoice.payment_url # doctest: +ELLIPSIS
    '...'

    We can mark this invoice as paid.

    >>> invoice.mark_paid()
    <fakturownia.endpoints.Invoice object at 0x...>

    You can chain your calls

    >>> invoice.put(buyer_email='kominek@niepodam.pl').send_by_email()
    <fakturownia.endpoints.Invoice object at 0x...>

Running Tests
-------------

Does the code actually work?

::

    $ pipenv install --dev
    $ pipenv shell
    $ tox


We recommend using pipenv_ but a legacy approach to creating virtualenv and installing requirements should also work.
Please install `requirements/base.txt` and `requirements/development.txt` to setup virtual env for testing and development.

Help wanted
-----------

If want to help please refer to

Credits
-------

This package was created with Cookiecutter_ and the `wooyek/cookiecutter-pylib`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`wooyek/cookiecutter-pylib`: https://github.com/wooyek/cookiecutter-pylib
.. _`pipenv`: https://docs.pipenv.org/install#fancy-installation-of-pipenv
.. _`fakturownia APIs`: https://github.com/fakturownia/api
