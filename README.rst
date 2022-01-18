.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: python-bulk-email-verifier license
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/pypi/v/bulk-email-verifier.svg
    :alt: python-bulk-email-verifier release
    :target: https://pypi.org/project/bulk-email-verifier

.. image:: https://github.com/whois-api-llc/python-bulk-email-verifier/workflows/Build/badge.svg
    :alt: python-bulk-email-verifier build
    :target: https://github.com/whois-api-llc/python-bulk-email-verifier/actions

========
Overview
========

The client library for
`Bulk Email Verification API <https://emailverification.whoisxmlapi.com/bulk-api>`_
in Python language.

The minimum Python version is 3.6.

Installation
============

.. code-block:: shell

    pip install bulk-email-verifier

Examples
========

Full API documentation available `here <https://emailverification.whoisxmlapi.com/bulk-api/documentation/making-requests>`_

Create a new client
-------------------

.. code-block:: python

    from bulkemailverifier import *

    client = Client('Your API key')

Create bulk request
-------------------

.. code-block:: python

    emails = [
        'example@example.com',
        'test@example.org',
        'test'
    ]

    request_id = client.create_request(emails=emails)

Get request status
-------------------

.. code-block:: python

    result = client.get_status(request_ids=[request_id])

    # Finished once result.data[i].ready == True
    print(result)

Get email records
-------------------

.. code-block:: python

    completed = client.get_records(request_id=request_id)

    # Invalid and failed emails
    failed = client.get_records(request_id=request_id, return_failed=True)

List your requests
-------------------

.. code-block:: python

    result = client.get_requests()

Download CSV result
-------------------

.. code-block:: python

    client.download(filename='emails.csv', request_id=request_id)

Extras
-------------------

.. code-block:: python

    # Paginate over request IDs in descending order and get results in XML
    result = client.get_requests_raw(
        only_ids=True,
        page=2,
        per_page=20,
        sort=Client.SORT_DESC,
        output_format=Client.XML_FORMAT
    )

Response model overview
-----------------------

.. code-block:: python

    ResponseRecords:
        - data: [Record]
            - email_address: str
            - format_check: bool
            - smtp_check: bool
            - dns_check: bool
            - free_check: bool
            - disposable_check: bool
            - catch_all_check: bool
            - result: str
            - error: str
            - mx_records: [str]

    ResponseRequests:
        - current_page: int
        - from_requests: int
        - last_page: int
        - per_page: int
        - to_requests: int
        - total: int
        - data: [BulkRequest]
            - id: int
            - date_start: datetime.datetime
            - total_emails: int
            - invalid_emails: int
            - processed_emails: int
            - failed_emails: int
            - ready: bool

    ResponseStatus:
        - data: [BulkRequest]

