from functools import wraps

from aiohttp import ClientSession, ClientResponse
from aiohttp.client_exceptions import ClientResponseError, ClientConnectionError, ClientPayloadError, \
    InvalidURL

from data.model.model import CircuitData, OneTimeActivationData, ScheduledActivationData
from data.model.schema import CircuitSchema
from data.smart_garden.exceptions import SmartGardenResponseError, SmartGardenConnectionError, SmartGardenPayloadError, \
    SmartGardenInvalidUrl, SmartGardenUnauthorizedError
from data.smart_garden.model import SmartGardenAuthData, SmartGardenAuthPayload, SmartGardenAuthRefreshData, \
    SmartGardenAuthRefreshPayload
from data.smart_garden.schema import SmartGardenAuthPayloadSchema, SmartGardenAuthSchema, \
    SmartGardenAuthRefreshPayloadSchema, SmartGardenAuthRefreshSchema


def map_errors(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except ClientResponseError as e:
            raise SmartGardenResponseError(internal_error=e)
        except ClientConnectionError as e:
            raise SmartGardenConnectionError(internal_error=e)
        except ClientPayloadError as e:
            raise SmartGardenPayloadError(internal_error=e)
        except InvalidURL as e:
            raise SmartGardenInvalidUrl(internal_error=e)

    return decorated


def authenticate(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except SmartGardenUnauthorizedError:
            client = args[0]
            # noinspection PyProtectedMember
            await client._authenticate()

            return await f(*args, **kwargs)

    return decorated


class SmartGardenBackend:
    """
    Represents Smart Garden backend that provides access to the circuit and some config and diagnostic data. It allows
    for fetching the circuit, sending short execution log and sending health checks.
    """

    def __init__(self, email: str, password: str, client_session: ClientSession):
        self._auth_url = "https://smart-garden-1.herokuapp.com/api/auth/token"
        self._auth_refresh_url = "https://smart-garden-1.herokuapp.com/api/auth/token/refresh"
        self._circuit_url = "https://smart-garden-1.herokuapp.com/api/circuits/mine"
        self._health_check_url = "https://smart-garden-1.herokuapp.com/api/circuits/mine/health-check"

        self._email = email
        self._password = password

        self._client_session = client_session

        self._access_token = None
        self._refresh_token = None

    @staticmethod
    def _returned_http_200(response: ClientResponse) -> bool:
        return response.status == 200

    @staticmethod
    def _returned_http_401(response: ClientResponse) -> bool:
        return response.status == 401

    # def _append_auth_token(self, url: str) -> str:
    #     if not self._valid_token_present():
    #         return url
    #
    #     return f"{url}?auth={self._id_token}"

    def _valid_token_present(self) -> bool:
        return self._access_token is not None

    @map_errors
    async def _get(self, url: str, **kwargs) -> ClientResponse:
        return await self._client_session.get(url=url, **kwargs)

    @map_errors
    async def _patch(self, url: str, data: str, **kwargs) -> ClientResponse:
        return await self._client_session.patch(url=url, data=data, **kwargs)

    @map_errors
    async def _post(self, url: str, data: str, **kwargs) -> ClientResponse:
        return await self._client_session.post(url=url, data=data, **kwargs)

    async def _get_auth_data(self) -> SmartGardenAuthData:
        payload = SmartGardenAuthPayload(email=self._email, password=self._password)
        json = SmartGardenAuthPayloadSchema().dumps(payload)
        raw_response = await self._post(self._auth_url, data=json, headers={'Content-Type': 'application/json'})

        if not self._returned_http_200(response=raw_response):
            raise SmartGardenResponseError(response=raw_response)

        schema = SmartGardenAuthSchema()
        json = await raw_response.json()
        response = SmartGardenAuthData(**schema.load(data=json))

        self._access_token = response.access
        self._refresh_token = response.refresh

        return response

    async def _refresh_auth_data(self, refresh_token: str) -> SmartGardenAuthRefreshData:
        payload = SmartGardenAuthRefreshPayload(refresh=refresh_token)
        json = SmartGardenAuthRefreshPayloadSchema().dumps(payload)

        raw_response = await self._post(self._auth_refresh_url, data=json, headers={'Content-Type': 'application/json'})
        if not self._returned_http_200(response=raw_response):
            raise SmartGardenResponseError(response=raw_response)

        schema = SmartGardenAuthRefreshSchema()
        json = await raw_response.json()
        response = SmartGardenAuthRefreshData(**schema.load(data=json))

        self._access_token = response.access
        # self._refresh_token = response.refresh

        return response

    async def _authenticate(self) -> None:
        if self._refresh_token is not None:
            await self._refresh_auth_data(refresh_token=self._refresh_token)
        else:
            await self._get_auth_data()

    @authenticate
    async def fetch_circuit(self) -> CircuitData:
        """
        Fetches the node data and returns its domain model.
        """
        if not self._access_token:
            await self._authenticate()

        headers = {
            'Authorization': f"Bearer {self._access_token}"
        }
        raw_response = await self._get(url=self._circuit_url, headers=headers)

        if not self._returned_http_200(response=raw_response):
            if self._returned_http_401(response=raw_response):
                raise SmartGardenUnauthorizedError(response=raw_response)
            else:
                raise SmartGardenResponseError(response=raw_response)

        schema = CircuitSchema()
        json = await raw_response.json()
        loaded_data = schema.load(data=json)

        one_time_activation = loaded_data.get('today_one_time_activations', None)
        if one_time_activation and len(one_time_activation) > 0:
            activation_data = one_time_activation[0]
            one_time_activation = OneTimeActivationData(
                timestamp=activation_data['timestamp'],
                amount=activation_data['amount']
            )

        schedule = []
        if 'schedule' in loaded_data:
            schedule = [ScheduledActivationData(time=p['time'], amount=p['amount'], active=p['active']) for p in
                        loaded_data['schedule']]

        return CircuitData(
            id=loaded_data.get('id', 0),
            name=loaded_data.get('name'),
            active=loaded_data.get('active', False),
            one_time_activation=one_time_activation,
            schedule=schedule,
        )

    @authenticate
    async def send_health_check(self) -> bool:
        """
        Sends current timestamp so the user can check if his device is alive.
        """
        if not self._access_token:
            await self._authenticate()

        headers = {
            'Authorization': f"Bearer {self._access_token}"
        }

        raw_response = await self._patch(url=self._health_check_url, data={}, headers=headers)

        if not self._returned_http_200(response=raw_response):
            if self._returned_http_401(response=raw_response):
                raise SmartGardenUnauthorizedError(response=raw_response)
            else:
                raise SmartGardenResponseError(response=raw_response)

        return True
