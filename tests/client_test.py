import os
from time import sleep
import unittest

from bulkemailverifier import BadRequestError, Client, FileError, \
    HttpApiError, ParameterError


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """

    client: Client
    correct_filename = 'bulk_email_verifier_lib_test_download.csv'
    correct_emails = ['foo@example.com', 'bar@example.org', 'test']
    correct_request_id: int

    incorrect_api_key = 'at_00000000000000000000000000000'
    incorrect_filename = 'src/does6/not257/exist5e7/8at/44all55'
    wrong_request_id = 123

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client(os.getenv('API_KEY'))

        cls.correct_request_id = \
            cls.client.create_request(emails=cls.correct_emails)

        sleep(10)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.correct_filename)

    def test_create_correct_data(self):
        request_id = self.client.create_request(emails=self.correct_emails)

        self.assertIsNotNone(request_id)

    def test_create_empty_emails(self):
        with self.assertRaises(ParameterError):
            self.client.create_request(emails=[])

    def test_download(self):
        self.client.download(
            filename=self.correct_filename,
            request_id=self.correct_request_id
        )

        self.assertGreater(os.path.getsize(self.correct_filename), 0)

    def test_empty_api_key_create(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.create_request(emails=self.correct_emails)

    def test_empty_api_key_download(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.download()

    def test_empty_api_key_get_requests(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.get_requests()

    def test_empty_api_key_get_status(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.get_status()

    def test_empty_api_key_get_records(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.get_records()

    def test_empty_filename(self):
        with self.assertRaises(ParameterError):
            self.client.download()

    def test_empty_request_id(self):
        with self.assertRaises(ParameterError):
            self.client.download()

    def test_get_records(self):
        response = self.client.get_records(request_id=self.correct_request_id)

        self.assertEqual(len(response.data), 2)
        self.assertIsNotNone(response.data[0].email_address)

    def test_get_records_failed(self):
        response = self.client.get_records(
            request_id=self.correct_request_id,
            return_failed=True
        )

        self.assertEqual(len(response.data), 1)
        self.assertIsNotNone(response.data[0].email_address)

    def test_get_requests(self):
        response = self.client.get_requests()

        self.assertGreater(len(response.data), 0)
        self.assertIsNotNone(response.data[0].date_start)

    def test_get_status(self):
        response = \
            self.client.get_status(request_ids=[self.correct_request_id])

        self.assertGreater(len(response.data), 0)
        self.assertIsNotNone(response.data[0].total_emails)

    def test_incorrect_api_key_create(self):
        with self.assertRaises(HttpApiError):
            client = Client(self.incorrect_api_key)
            client.create_request(emails=self.correct_emails)

    def test_incorrect_api_key_get_requests(self):
        with self.assertRaises(HttpApiError):
            client = Client(self.incorrect_api_key)
            client.get_requests()

    def test_incorrect_api_key_get_records(self):
        with self.assertRaises(HttpApiError):
            client = Client(self.incorrect_api_key)
            client.get_records(request_id=self.correct_request_id)

    def test_incorrect_api_key_get_status(self):
        with self.assertRaises(HttpApiError):
            client = Client(self.incorrect_api_key)
            client.get_status(request_ids=[self.correct_request_id])

    def test_incorrect_filename(self):
        with self.assertRaises(FileError):
            self.client.download(filename=self.incorrect_filename,
                                 request_id=self.correct_request_id)

    def test_incorrect_only_ids(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests_raw(only_ids=20)

    def test_incorrect_page(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests(page='foo')

    def test_incorrect_page_size(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests(per_page=1)

    def test_incorrect_request_id(self):
        with self.assertRaises(ParameterError):
            self.client.get_records(request_id='foo')

    def test_incorrect_request_ids(self):
        with self.assertRaises(ParameterError):
            self.client.get_status(request_ids='foo')

    def test_incorrect_sort(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests(sort='bar')

    def test_output(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests(response_format='yaml')

    def test_output_csv_common(self):
        with self.assertRaises(ParameterError):
            self.client.get_requests(response_format=Client.CSV_FORMAT)

    def test_raw_create(self):
        response = self.client.create_request_raw(
            emails=self.correct_emails,
            output_format=Client.XML_FORMAT
        )

        self.assertTrue(response.startswith('<?xml'))

    def test_raw_csv(self):
        response = self.client.get_records_raw(
            request_id=self.correct_request_id,
            output_format=Client.CSV_FORMAT
        )

        self.assertTrue(response.startswith('"Email Address"'))

    def test_raw_records(self):
        response = self.client.get_records_raw(
            request_id=self.correct_request_id,
            output_format=Client.XML_FORMAT
        )

        self.assertTrue(response.startswith('<?xml'))

    def test_raw_requests(self):
        response = self.client.get_requests_raw(
            output_format=Client.XML_FORMAT
        )

        self.assertTrue(response.startswith('<?xml'))

    def test_raw_status(self):
        response = self.client.get_status_raw(
            request_ids=[self.correct_request_id],
            output_format=Client.XML_FORMAT
        )

        self.assertTrue(response.startswith('<?xml'))

    def test_wrong_request_id(self):
        with self.assertRaises(BadRequestError):
            self.client.get_records(request_id=self.wrong_request_id)


if __name__ == '__main__':
    unittest.main()
