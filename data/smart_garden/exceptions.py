from typing import Optional

from aiohttp import ClientResponse


class SmartGardenException(Exception):
    def __init__(self, internal_error: Optional[Exception] = None, response: Optional[ClientResponse] = None,
                 *args: object) -> None:
        super().__init__(*args)

        self.internal_error = internal_error
        self.response = response

    def __str__(self) -> str:
        return str(self.response)


class SmartGardenResponseError(SmartGardenException):
    pass


class SmartGardenUnauthorizedError(SmartGardenException):
    pass


class SmartGardenConnectionError(SmartGardenException):
    pass


class SmartGardenPayloadError(SmartGardenException):
    pass


class SmartGardenInvalidUrl(SmartGardenException):
    pass
