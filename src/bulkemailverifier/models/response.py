import copy
import datetime
import sys

from .base import BaseModel

if sys.version_info < (3, 9):
    import typing


def _bool_value(values: dict, key: str) -> bool or None:
    if key in values:
        if type(values[key]) is str:
            str_value = str(values[key]).lower()
            if str_value == 'true':
                return True
            if str_value == '1':
                return True
            if str_value == 'null':
                return None
            return False
        return bool(values[key])
    return None


def _int_value(values: dict, key: str) -> int:
    if key in values and values[key]:
        return int(values[key])
    return 0


def _list_of_objects(values: dict, key: str, classname: str) -> list:
    r = []
    if key in values and type(values[key]) is list:
        r = [globals()[classname](x) for x in values[key]]
    return r


def _list_value(values: dict, key: str) -> list:
    if key in values and type(values[key]) is list:
        return copy.deepcopy(values[key])
    return []


def _string_value(values: dict, key: str) -> str:
    if key in values and values[key]:
        return str(values[key])
    return ''


def _timestamp2datetime(timestamp) -> datetime.datetime or None:
    if timestamp is not None:
        return datetime.datetime.utcfromtimestamp(timestamp)
    return None


class BulkRequest(BaseModel):
    id: int
    date_start: datetime.datetime or None
    total_emails: int
    invalid_emails: int
    processed_emails: int
    failed_emails: int
    ready: bool

    def __init__(self, values):
        super().__init__()
        self.id = 0
        self.date_start = None
        self.total_emails = 0
        self.invalid_emails = 0
        self.processed_emails = 0
        self.failed_emails = 0
        self.ready = False

        if values is not None:
            self.id = _int_value(values, 'id')

            if 'date_start' in values:
                self.date_start = _timestamp2datetime(
                    _int_value(values, 'date_start')
                )

            self.total_emails = _int_value(values, 'total_emails')
            self.invalid_emails = _int_value(values, 'invalid_emails')
            self.processed_emails = _int_value(values, 'processed_emails')
            self.failed_emails = _int_value(values, 'failed_emails')
            self.ready = _bool_value(values, 'ready')


class ErrorMessage(BaseModel):
    code: int

    if sys.version_info < (3, 9):
        message: typing.List[str]
    else:
        message: [str]

    def __init__(self, values, code):
        super().__init__()

        self.code = code
        self.message = []

        if values is not None and 'response' in values:
            response = values['response']
            if 'error' in response:
                self.message.append(_string_value(response, 'error'))
            if 'errors' in response:
                self.message = _list_value(response, 'errors')


class Record(BaseModel):
    email_address: str
    format_check: bool or None
    smtp_check: bool or None
    dns_check: bool or None
    free_check: bool or None
    disposable_check: bool or None
    catch_all_check: bool or None
    result: str
    error: str

    if sys.version_info < (3, 9):
        mx_records: typing.List[str]
    else:
        mx_records: [str]

    def __init__(self, values):
        super().__init__()

        self.email_address = ''
        self.format_check = False
        self.smtp_check = None
        self.dns_check = None
        self.free_check = None
        self.disposable_check = None
        self.catch_all_check = None
        self.mx_records = []
        self.result = ''
        self.error = ''

        if values is not None:
            self.email_address = _string_value(values, 'emailAddress')
            self.format_check = _bool_value(values, 'formatCheck')
            self.smtp_check = _bool_value(values, 'smtpCheck')
            self.dns_check = _bool_value(values, 'dnsCheck')
            self.free_check = _bool_value(values, 'freeCheck')
            self.disposable_check = _bool_value(values, 'disposableCheck')
            self.catch_all_check = _bool_value(values, 'catchAllCheck')
            self.mx_records = _list_value(values, 'mxRecords')
            self.result = _string_value(values, 'result')
            self.error = _string_value(values, 'error')


class ResponseRecords(BaseModel):
    if sys.version_info < (3, 9):
        data: typing.List[Record]
    else:
        data: [Record]

    def __init__(self, values):
        super().__init__()

        self.data = []

        if values is not None:
            self.data = _list_of_objects(values, 'response', 'Record')


class ResponseStatus(BaseModel):
    if sys.version_info < (3, 9):
        data: typing.List[BulkRequest]
    else:
        data: [BulkRequest]

    def __init__(self, values):
        super().__init__()

        if values is not None and 'response' in values:
            self.data = _list_of_objects(values, 'response', 'BulkRequest')


class ResponseRequests(ResponseStatus):
    current_page: int
    from_requests: int
    last_page: int
    per_page: int
    to_requests: int
    total: int

    def __init__(self, values):
        super().__init__(values)

        self.current_page = 0
        self.from_requests = 0
        self.last_page = 0
        self.per_page = 0
        self.to_requests = 0
        self.to_requests = 0

        if values is not None and 'response' in values:
            response = values['response']
            self.current_page = _int_value(response, 'current_page')
            self.from_requests = _int_value(response, 'from')
            self.last_page = _int_value(response, 'last_page')
            self.per_page = _int_value(response, 'per_page')
            self.to_requests = _int_value(response, 'to')
            self.total = _int_value(response, 'total')
            self.data = _list_of_objects(response, 'data', 'BulkRequest')
