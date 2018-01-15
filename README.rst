===========
Fakturownia
===========

Python client library for the Fakturownia API


.. image:: https://img.shields.io/pypi/v/fakturownia.svg
        :target: https://pypi.python.org/pypi/fakturownia

.. image:: https://img.shields.io/travis/wooyek/fakturownia-python.svg
        :target: https://travis-ci.org/wooyek/fakturownia-python

.. image:: https://readthedocs.org/projects/fakturownia/badge/?version=latest
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

If you don't know it yet be sure to check it out:

.. image:: //app.fakturownia.pl/polecam-fakturownie-niebieski.png
    :target: http://fakturownia.pl
    :alt: Polecam Fakturownia.pl - prosty program do fakturowania online


.. contents:: Table of Contents

Features
--------

* ☑ Invoice CRUD plus `send_by_email` and 'mark_paid`
* ☑ EU member states VAT rate helpers for B2C transactions
* ☑ ApiClient CRUD
* ☐ Payments CRUD
* ☐ Products CRUD
* ☐ Warehouse documents CRUD
* ☐ Accounts management

Please refer to the `fakturownia APIs`_ for full API features

Quickstart
----------

Install Fakturownia

    pip install fakturownia
    python

Play with `fakturownia APIs`_ in python interpreter::

    >>> import os
    >>> os.environ.get('FAKTUROWNIA_API_TOKEN', 'Missing key')
    '...'
    >>> from fakturownia import get_api_client
    >>> api = get_api_client()
    >>> invoice = api.invoices.create(
    ...     seller_name='Kabaret Starszych Panów',
    ...     buyer_name='Odrażający drab',
    ...     positions=[{
    ...         'name': 'Smolna szczapa',
    ...         'quantity': 5,
    ...         'total_price_gross': 7.33,
    ...     }],
    ... )
    >>> invoice.view_url
    '...'

This instance is only partially updated as create returns only subset of
data properties, to get all we need to update our instance.

If you have payments enabled you can call get to fetch all data and check payment_url::

    >>> invoice.get()
    <fakturownia.endpoints.Invoice object at 0x...>
    >>> invoice.payment_url
    '...'

We can mark this invoice as paid::

    >>> invoice.mark_paid()
    <fakturownia.endpoints.Invoice object at 0x...>

You can chain your calls::

    >>> invoice.put(buyer_email='kominek@niepodam.pl').send_by_email()
    <fakturownia.endpoints.Invoice object at 0x...>

You can play and test your scenarios wih factories::

    pip install fakturownia[factories]
    python

Now you can do this::

    >>> from fakturownia.factories import InvoiceFactory
    >>> InvoiceFactory(api_client='<your api key here>', kind='proforma').post().get().payment_url # doctest: +SKIP
    '...'

Also checkout VAT tax normalization based on
`EU country specific VAT rates <https://ec.europa.eu/taxation_customs/business/vat/eu-country-specific-information-vat_en>`_::

    >>> InvoiceFactory(
    ...     api_client=api,
    ...     seller_country='PL',
    ...     buyer_country='DE',
    ...     buyer_tax_no=None,
    ... ).normalize_vat().post().view_url
    '...'

Neat! :)


Running Tests
-------------

Does the code actually work?

.. code-block:: sh

    pipenv install --dev
    pipenv shell
    tox


We recommend using pipenv_ but a legacy approach to creating virtualenv and installing requirements should also work.
Please install `requirements/base.txt` and `requirements/development.txt` to setup virtual env for testing and development.

Help wanted
-----------

This library is not yet complete. It does what was needed by up to date contributors, but more can be done.
You can implement new api endpoints and write test for them, it's actually straightforward and new classes will be simple,
but tests need some effort. We are lazy test writers and because we don't want to compromise coverage so we
postponed new apis until someone would want to write test.

If want to help please refer to the
`contributing section <https://fakturownia.readthedocs.io/en/latest/contributing.html>`_ in the docs for more info.

Credits
-------

This package was created with Cookiecutter_ and the `wooyek/cookiecutter-pylib`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`wooyek/cookiecutter-pylib`: https://github.com/wooyek/cookiecutter-pylib
.. _`pipenv`: https://docs.pipenv.org/install#fancy-installation-of-pipenv
.. _`fakturownia APIs`: https://github.com/fakturownia/api
