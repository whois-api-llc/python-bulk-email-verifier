from json import loads, JSONDecodeError

import re

from .exceptions.error import EmptyApiKeyError, FileError, ParameterError, \
    UnparsableApiResponseError
from .models.response import ResponseRecords, ResponseRequests, ResponseStatus
from .net.http import ApiRequester


class Client:
    __default_url = 'https://emailverification.whoisxmlapi.com/api/bevService'
    _api_requester: ApiRequester or None
    _api_key: str

    _re_api_key = re.compile(r'^at_[a-z0-9]{29}$', re.IGNORECASE)

    _DOWNLOAD_FORMAT = 'csv'
    _PARSABLE_FORMAT = 'json'

    _PATH_CREATE = '/request'
    _PATH_COMPLETED = _PATH_CREATE + '/completed'
    _PATH_FAILED = _PATH_CREATE + '/failed'
    _PATH_REQUESTS = _PATH_CREATE + '/list'
    _PATH_STATUS = _PATH_CREATE + '/status'

    MIN_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50

    SORT_ASC = 'asc'
    SORT_DESC = 'desc'

    CSV_FORMAT = 'csv'
    JSON_FORMAT = 'json'
    XML_FORMAT = 'xml'

    def __init__(self, api_key: str, **kwargs):
        """
        :param api_key: str: Your API key
        :key base_url: str: (optional) API endpoint URL
        :key timeout: float: (optional) API call timeout in seconds
        """

        self._api_key = ''

        self.api_key = api_key

        if 'base_url' not in kwargs:
            kwargs['base_url'] = Client.__default_url

        self.api_requester = ApiRequester(**kwargs)

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = Client._validate_api_key(value)

    @property
    def api_requester(self) -> ApiRequester or None:
        return self._api_requester

    @api_requester.setter
    def api_requester(self, value: ApiRequester):
        self._api_requester = value

    @property
    def base_url(self) -> str:
        return self._api_requester.base_url

    @base_url.setter
    def base_url(self, value: str or None):
        if value is None:
            self._api_requester.base_url = Client.__default_url
        else:
            self._api_requester.base_url = value

    @property
    def timeout(self) -> float:
        return self._api_requester.timeout

    @timeout.setter
    def timeout(self, value: float):
        self._api_requester.timeout = value

    def create_request(self, **kwargs) -> int:
        """
        Create bulk emails processing request
        :key emails: Required. list[str]
        :return: int. Created request ID
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        response = self.create_request_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'response' in parsed:
                return int(parsed['response']['id'])
            raise UnparsableApiResponseError(
                'Could not find the correct root element.', None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    'Could not parse API response',
                    error)

    def download(self, **kwargs):
        """
        Download processing results CSV and save to file
        :key request_id: Required. int. Request ID
        :key return_failed: Optional.
                Returns only completed emails if False, failed - otherwise.
                False by default
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        filename = None

        kwargs['output_format'] = Client._DOWNLOAD_FORMAT

        if 'filename' in kwargs:
            filename = kwargs['filename']

        if type(filename) is not str or not filename:
            raise ParameterError('Output file name required')

        try:
            result_file = open(filename, 'w')
        except Exception:
            raise FileError('Cannot open output file')

        result_file.close()

        response = self.get_records_raw(**kwargs)

        try:
            result_file = open(filename, 'w')
            result_file.write(response)
        except Exception:
            raise FileError('Cannot write result to file')
        finally:
            result_file.close()

    def get_records(self, **kwargs) -> ResponseRecords:
        """
        Get processed email results
        :key request_id: Required. int. Request ID
        :key return_failed: Optional.
                Returns only completed emails if False, failed - otherwise.
                False by default
        :return: `ResponseRecords` instance
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        response = self.get_records_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'response' in parsed:
                return ResponseRecords(parsed)
            raise UnparsableApiResponseError(
                'Cannot find the correct root element', None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    'Could not parse API response',
                    error)

    def get_requests(self, **kwargs) -> ResponseRequests:
        """
        Get a list of your requests
        :key page: Optional. Used to paginate results.
                Min: 1.
                1 by default
        :key per_page: Optional. Limit pages of the result set to this number
                of requests.
                Min: `Client.MIN_PAGE_SIZE`, Max: `Client.MAX_PAGE_SIZE`.
                `Client.MIN_PAGE_SIZE` by default
        :key sort: Optional. Specify the order of requests in the response.
                Supported options: SORT_ASC, SORT_DESC.
                SORT_DESC by default
        :return: `ResponseRequests` instance
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT
        kwargs['only_ids'] = False

        response = self.get_requests_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'response' in parsed:
                return ResponseRequests(parsed)
            raise UnparsableApiResponseError(
                'Cannot find the correct root element', None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    'Could not parse API response',
                    error)

    def get_status(self, **kwargs) -> ResponseStatus:
        """
        Get statuses of the specified requests
        :key request_ids: Required. list[str]. Request IDs
        :return: `ResponseStatus` instance
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        kwargs['output_format'] = Client._PARSABLE_FORMAT

        response = self.get_status_raw(**kwargs)

        try:
            parsed = loads(str(response))
            if 'response' in parsed:
                return ResponseStatus(parsed)
            raise UnparsableApiResponseError(
                'Cannot find the correct root element', None)
        except JSONDecodeError as error:
            raise UnparsableApiResponseError(
                    'Could not parse API response',
                    error)

    def create_request_raw(self, **kwargs) -> str:
        """
        Get raw create response
        :key emails: Required. list[str]
        :key output_format: Optional. Response output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: int. Created request ID
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        emails = None

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'emails' in kwargs:
            emails = Client._validate_emails(kwargs['emails'])

        if not emails:
            raise ParameterError('Emails required')

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        return self._api_requester.post(
                self._PATH_CREATE,
                self._build_payload(self.api_key, output_format, emails)
        )

    def get_records_raw(self, **kwargs) -> str:
        """
        Get processed email results
        :key request_id: Required. int. Request ID
        :key return_failed: Optional.
                Returns only completed emails if False, failed - otherwise.
                False by default
        :key output_format: Optional. Response output format.
                Supported options: CSV_FORMAT, JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: str
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        request_id = None
        return_failed = False

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'request_id' in kwargs:
            request_id = Client._validate_request_id(kwargs['request_id'])

        if not request_id:
            raise ParameterError('Request ID required')

        if 'return_failed' in kwargs:
            return_failed = \
                Client._validate_return_failed(kwargs['return_failed'])

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format_records(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        path = self._PATH_FAILED if return_failed else self._PATH_COMPLETED

        return self._api_requester.post(
            path,
            self._build_payload(
                self.api_key, output_format, request_id=request_id)
        )

    def get_requests_raw(self, **kwargs) -> str:
        """
        Get a list of your requests
        :key page: Optional. Used to paginate results.
                Min: 1.
                1 by default
        :key only_ids: Optional. When True only the list of IDs is returned.
                True by default
        :key per_page: Optional. Limit pages of the result set to this number
                of requests.
                Min: `Client.MIN_PAGE_SIZE`, Max: `Client.MAX_PAGE_SIZE`.
                `Client.MIN_PAGE_SIZE` by default
        :key sort: Optional. Specify the order of requests in the response.
                Supported options: SORT_ASC, SORT_DESC.
                SORT_DESC by default
        :key output_format: Optional. Response output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: str
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        page, only_ids, per_page, sort = [None] * 4

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        if 'page' in kwargs:
            page = Client._validate_page(kwargs['page'])

        if 'only_ids' in kwargs:
            only_ids = Client._validate_only_ids(kwargs['only_ids'])

        if 'per_page' in kwargs:
            per_page = Client._validate_page_size(kwargs['per_page'])

        if 'sort' in kwargs:
            sort = Client._validate_sort(kwargs['sort'])

        return self._api_requester.post(
            self._PATH_REQUESTS,
            self._build_payload(
                self.api_key,
                output_format,
                page=page,
                only_ids=only_ids,
                per_page=per_page,
                sort=sort
            )
        )

    def get_status_raw(self, **kwargs) -> str:
        """
        Get statuses of the specified requests
        :key request_ids: Required. list[str]. Request IDs
        :key output_format: Optional. Response output format.
                Supported options: JSON_FORMAT, XML_FORMAT.
                JSON_FORMAT by default
        :return: str
        :raises ConnectionError:
        :raises BulkEmailVerificationApiError: Base class for all errors below
        :raises ResponseError: response contains an error message
        :raises ApiAuthError: Server returned 401, 402 or 403 HTTP code
        :raises BadRequestError: Server returned 400 or 422 HTTP code
        :raises HttpApiError: HTTP code >= 300 and not equal to above codes
        :raises ParameterError: invalid parameter value
        """

        request_ids = None

        if self.api_key == '':
            raise EmptyApiKeyError('')

        if 'request_ids' in kwargs:
            request_ids = Client._validate_request_ids(kwargs['request_ids'])

        if not request_ids:
            raise ParameterError('Request ID list required')

        if 'response_format' in kwargs:
            kwargs['output_format'] = kwargs['response_format']
        if 'output_format' in kwargs:
            output_format = Client._validate_output_format(
                kwargs['output_format'])
        else:
            output_format = Client._PARSABLE_FORMAT

        return self._api_requester.post(
            self._PATH_STATUS,
            self._build_payload(
                self.api_key, output_format, request_ids=request_ids)
        )

    @staticmethod
    def _build_payload(
            api_key,
            output_format=None,
            emails=None,
            page=None,
            only_ids=None,
            per_page=None,
            sort=None,
            request_ids=None,
            request_id=None
    ) -> dict:
        tmp = {
            'apiKey': api_key,
            'format': output_format,
            'emails': emails,
            'page': page,
            'onlyIds': only_ids,
            'perPage': per_page,
            'sort': sort,
            'ids': request_ids,
            'id': request_id
        }

        payload = {}
        for k, v in tmp.items():
            if v is not None:
                payload[k] = v
        return payload

    @staticmethod
    def _validate_api_key(api_key) -> str:
        if Client._re_api_key.search(str(api_key)) is not None:
            return str(api_key)
        else:
            raise ParameterError('Invalid API key format')

    @staticmethod
    def _validate_emails(value) -> list:
        if value is None:
            raise ParameterError('Email list cannot be None')
        elif type(value) is list:
            if len(value) < 1:
                raise ParameterError('Email list cannot be empty')
            for item in value:
                if type(item) is not str:
                    raise ParameterError('Incorrect email value')
            return value

        raise ParameterError('Expected a list of emails')

    @staticmethod
    def _validate_only_ids(value: int) -> int:
        if type(value) is bool:
            return value

        raise ParameterError('Only IDs parameter must be boolean')

    @staticmethod
    def _validate_output_format(value: str):
        if type(value) is str \
                and value.lower() in [Client.JSON_FORMAT, Client.XML_FORMAT]:
            return value.lower()

        raise ParameterError(
            f'Response format must be {Client.JSON_FORMAT} '
            f'or {Client.XML_FORMAT}')

    @staticmethod
    def _validate_output_format_records(value: str):
        if type(value) is str \
                and value.lower() in \
                [Client.CSV_FORMAT, Client.JSON_FORMAT, Client.XML_FORMAT]:
            return value.lower()

        raise ParameterError(
            f'Response format must be {Client.CSV_FORMAT},'
            f'{Client.JSON_FORMAT} or {Client.XML_FORMAT}')

    @staticmethod
    def _validate_page(value: int) -> int:
        if type(value) is int and value > 0:
            return value

        raise ParameterError('Page must be greater than or equal to 1')

    @staticmethod
    def _validate_page_size(value: int) -> int:
        if type(value) is int \
                and Client.MIN_PAGE_SIZE <= value <= Client.MAX_PAGE_SIZE:
            return value

        raise ParameterError(
            f'Page size must be between {Client.MIN_PAGE_SIZE} '
            f'and {Client.MAX_PAGE_SIZE}')

    @staticmethod
    def _validate_request_id(value: int) -> int:
        if type(value) is int and value > 0:
            return value

        raise ParameterError('Incorrect request ID')

    @staticmethod
    def _validate_request_ids(value) -> list:
        if value is None:
            raise ParameterError('Request ID list cannot be None')
        elif type(value) is list:
            if len(value) < 1:
                raise ParameterError('Request ID list cannot be empty')
            for item in value:
                if type(item) is not int:
                    raise ParameterError('Incorrect request ID')
            return value

        raise ParameterError('Expected a list of request IDs')

    @staticmethod
    def _validate_return_failed(value: bool) -> bool:
        if type(value) is bool:
            return value or None

        raise ParameterError('Return failed parameter must be True or False')

    @staticmethod
    def _validate_sort(value: str):
        if type(value) is str \
                and value.lower() in [Client.SORT_ASC, Client.SORT_DESC]:
            return value.lower()

        raise ParameterError(
            f'Sort must be {Client.SORT_ASC} or {Client.SORT_DESC}')
