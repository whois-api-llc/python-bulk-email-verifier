from requests import request, Response

import logging

from ..exceptions.error import ApiAuthError, BadRequestError, HttpApiError
from ..version import LIBRARY_NAME, VERSION


class ApiRequester:
    __connect_timeout = 10
    __logger = logging.getLogger('api-requester')
    __user_agent = '{name}/{ver}'.format(name=LIBRARY_NAME, ver=VERSION)

    _base_url: str
    _timeout: float

    def __init__(self, **kwargs):
        """
        :param kwargs: Supported parameters:
        - base_url: (optional) API endpoint URL; str
        - timeout: (optional) API call timeout in seconds; float
        """
        self._base_url = ''
        self.timeout = 30

        if 'base_url' in kwargs:
            self.base_url = kwargs['base_url']
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, url: str):
        if url is None or len(url) <= 8 or not url.startswith('http'):
            raise ValueError('Invalid URL specified.')
        self._base_url = url

    @property
    def timeout(self) -> float:
        """API call timeout in seconds"""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        """API call timeout in seconds"""
        if value is not None and 1 <= value <= 60:
            self._timeout = value
        else:
            raise ValueError('Timeout value should be in [1, 60]')

    def post(self, path: str, data: dict) -> str:
        headers = {
            'User-Agent': ApiRequester.__user_agent,
            'Connection': 'close'
        }

        response = request(
            'POST',
            self.base_url + path,
            json=data,
            headers=headers,
            timeout=(ApiRequester.__connect_timeout, self.timeout)
        )

        return ApiRequester._handle_response(response)

    @staticmethod
    def _handle_response(response: Response) -> str:
        status_code = response.status_code

        if 200 <= status_code < 300:
            return response.content.decode('UTF-8')

        if status_code in [401, 402, 403]:
            raise ApiAuthError(response.text, status_code)

        if status_code in [400, 422]:
            raise BadRequestError(response.text, status_code)

        if status_code >= 300:
            raise HttpApiError(response.text, status_code)
