from typing import Optional

from aiohttp import ClientResponse


class FirebaseException(Exception):
    def __init__(self, internal_error: Optional[Exception] = None, response: Optional[ClientResponse] = None,
                 *args: object) -> None:
        super().__init__(*args)

        self.internal_error = internal_error
        self.response = response


class FirebaseResponseError(FirebaseException):
    pass


class FirebaseUnauthorizedError(FirebaseResponseError):
    pass


class FirebaseConnectionError(FirebaseException):
    pass


class FirebasePayloadError(FirebaseException):
    pass


class FirebaseInvalidUrl(FirebaseException):
    pass
