from json import loads

from ..models.response import ErrorMessage


class BulkEmailVerificationApiError(Exception):
    def __init__(self, message):
        self.message = message

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def __str__(self):
        return str(self.__dict__)


class ResponseError(BulkEmailVerificationApiError):
    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = code

    def __init__(self, message, code):
        self.code = code
        self.message = message
        self.parsed_message = None
        try:
            parsed = loads(message)
            self.parsed_message = ErrorMessage(parsed, code)
        except Exception:
            pass

    @property
    def parsed_message(self):
        return self._parsed_message

    @parsed_message.setter
    def parsed_message(self, pm):
        self._parsed_message = pm


class ApiAuthError(ResponseError):
    pass


class BadRequestError(ResponseError):
    pass


class EmptyApiKeyError(BulkEmailVerificationApiError):
    pass


class FileError(BulkEmailVerificationApiError):
    pass


class HttpApiError(BulkEmailVerificationApiError):
    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = code

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class ParameterError(BulkEmailVerificationApiError):
    pass


class UnparsableApiResponseError(BulkEmailVerificationApiError):
    def __init__(self, message, origin_error):
        self.message = message
        self.original_error = origin_error

    @property
    def original_error(self):
        return self._original_error

    @original_error.setter
    def original_error(self, oe):
        self._original_error = oe
