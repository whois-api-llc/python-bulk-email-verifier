import datetime
from json import loads

import unittest

from bulkemailverifier import BulkRequest, ErrorMessage, Record, \
    ResponseRecords, ResponseRequests, ResponseStatus


_json_response_error = '''{
    "response": {
        "error": "Access denied"
    }
}'''

_json_response_records = '''{
    "response": [
        {
            "emailAddress": "foo@example.com",
            "formatCheck": "true",
            "smtpCheck": "false",
            "dnsCheck": "true",
            "freeCheck": "false",
            "disposableCheck": "false",
            "catchAllCheck": "false",
            "mxRecords": [
                "."
            ],
            "result": "smtp-failed"
        }
    ]
}'''

_json_response_records_failed = '''{
    "response": [
        {
            "error": "Invalid format",
            "emailAddress": "foo.bar"
        }
    ]
}'''

_json_response_requests = '''{
    "response": {
        "current_page": 1,
        "data": [
            {
                "id": 123,
                "date_start": "1642422382",
                "date_end": "1642422386",
                "total_emails": 1,
                "invalid_emails": 0,
                "processed_emails": 1,
                "failed_emails": 0,
                "ready": 1
            },
            {
                "id": 456,
                "date_start": "1642421810",
                "date_end": "1642421811",
                "total_emails": 1,
                "invalid_emails": 0,
                "processed_emails": 1,
                "failed_emails": 0,
                "ready": 1
            }
        ],
        "from": 1,
        "last_page": 1,
        "per_page": 10,
        "to": 2,
        "total": 2
    }
}'''

_json_response_requests_ids = '''{
    "response": {
        "current_page": 1,
        "data": [
            {
                "id": 123
            },
            {
                "id": 456
            }
        ],
        "from": 1,
        "last_page": 1,
        "per_page": 10,
        "to": 2,
        "total": 2
    }
}'''

_json_response_status = '''{
    "response": [
        {
            "id": 123,
            "date_start": "1642412278",
            "date_end": "1642422565",
            "total_emails": 3,
            "invalid_emails": 1,
            "processed_emails": 2,
            "failed_emails": 0,
            "ready": 1
        }
    ]
}'''


class TestModel(unittest.TestCase):

    def test_error_parsing(self):
        error = loads(_json_response_error)
        parsed_error = ErrorMessage(error, 403)
        self.assertEqual(parsed_error.code, 403)
        self.assertEqual(parsed_error.message[0], error['response']['error'])

    def test_response_records_parsing(self):
        response = loads(_json_response_records)
        parsed = ResponseRecords(response)

        self.assertEqual(parsed.data[0].email_address,
                         response['response'][0]['emailAddress'])

        self.assertIsInstance(parsed.data, list)
        self.assertIsInstance(parsed.data[0], Record)

    def test_response_records_failed_parsing(self):
        response = loads(_json_response_records_failed)
        parsed = ResponseRecords(response)

        self.assertEqual(
            parsed.data[0].error, response['response'][0]['error'])

        self.assertEqual(parsed.data[0].email_address,
                         response['response'][0]['emailAddress'])

        self.assertIsInstance(parsed.data, list)
        self.assertIsInstance(parsed.data[0], Record)

    def test_response_requests_parsing(self):
        response = loads(_json_response_requests)
        parsed = ResponseRequests(response)

        self.assertIsInstance(parsed.data, list)
        self.assertIsInstance(parsed.data[0], BulkRequest)

        self.assertEqual(parsed.current_page,
                         response['response']['current_page'])

        self.assertEqual(len(parsed.data),
                         len(response['response']['data']))

        self.assertEqual(parsed.data[1].id,
                         response['response']['data'][1]['id'])

        self.assertIsInstance(parsed.data[0].date_start, datetime.datetime)

    def test_response_requests_ids_parsing(self):
        response = loads(_json_response_requests_ids)
        parsed = ResponseRequests(response)

        self.assertIsInstance(parsed.data, list)
        self.assertIsInstance(parsed.data[0], BulkRequest)

        self.assertEqual(parsed.data[0].id,
                         response['response']['data'][0]['id'])

        self.assertEqual(len(parsed.data),
                         len(response['response']['data']))

        self.assertEqual(parsed.data[1].id,
                         response['response']['data'][1]['id'])

        self.assertIsNone(parsed.data[0].date_start)

    def test_response_status_parsing(self):
        response = loads(_json_response_status)
        parsed = ResponseStatus(response)

        self.assertIsInstance(parsed.data, list)
        self.assertIsInstance(parsed.data[0], BulkRequest)

        self.assertEqual(len(parsed.data), len(response['response']))

        self.assertEqual(parsed.data[0].invalid_emails,
                         response['response'][0]['invalid_emails'])

        self.assertIsInstance(parsed.data[0].date_start, datetime.datetime)
