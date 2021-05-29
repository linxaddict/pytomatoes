# from datetime import datetime
# from functools import wraps
#
# from aiohttp import ClientSession, ClientResponse
# from aiohttp.client_exceptions import ClientResponseError, ClientConnectionError, ClientPayloadError, \
#     InvalidURL
#
# from data.firebase.exceptions import FirebaseResponseError, FirebaseConnectionError, FirebasePayloadError, \
#     FirebaseInvalidUrl, FirebaseUnauthorizedError
# from data.model.mapper import map_domain_to_pump_activation
# from data.model.model import AuthData, AuthPayload, AuthRefreshData, AuthRefreshPayload, ExecutionLogPayloadData, \
#     HealthCheckPayloadData, ScheduleData, OneTimeActivationData, ScheduleItemData
# from data.model.schema import AuthPayloadSchema, AuthSchema, AuthRefreshPayloadSchema, AuthRefreshSchema, \
#     ExecutionLogPayloadSchema, HealthCheckPayloadSchema, ScheduleSchema
# from domain.model import PumpActivation
#
#
# def map_errors(f):
#     @wraps(f)
#     async def decorated(*args, **kwargs):
#         try:
#             return await f(*args, **kwargs)
#         except ClientResponseError as e:
#             raise FirebaseResponseError(internal_error=e)
#         except ClientConnectionError as e:
#             raise FirebaseConnectionError(internal_error=e)
#         except ClientPayloadError as e:
#             raise FirebasePayloadError(internal_error=e)
#         except InvalidURL as e:
#             raise FirebaseInvalidUrl(internal_error=e)
#
#     return decorated
#
#
# def authenticate(f):
#     @wraps(f)
#     async def decorated(*args, **kwargs):
#         try:
#             return await f(*args, **kwargs)
#         except FirebaseUnauthorizedError:
#             client = args[0]
#             # noinspection PyProtectedMember
#             await client._authenticate()
#
#             return await f(*args, **kwargs)
#
#     return decorated
#
#
# class FirebaseBackend:
#     """
#     Represents Firebase backend that provides access to the schedule and some config and diagnostic data. It allows
#     for fetching the schedule, sending short execution log and sending health checks.
#     """
#
#     def __init__(self, email: str, password: str, api_key: str, db_url: str, node: str, client_session: ClientSession):
#         self._auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
#         self._auth_refresh_url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
#         self._node_url = f"https://pytomatoes.firebaseio.com/nodes/{node}.json"
#
#         self._email = email
#         self._password = password
#
#         self._db_url = db_url
#         self._client_session = client_session
#
#         self._id_token = None
#         self._refresh_token = None
#         self._expires_in = None
#
#     @staticmethod
#     def _returned_http_200(response: ClientResponse) -> bool:
#         return response.status == 200
#
#     @staticmethod
#     def _returned_http_401(response: ClientResponse) -> bool:
#         return response.status == 401
#
#     def _append_auth_token(self, url: str) -> str:
#         if not self._valid_token_present():
#             return url
#
#         return f"{url}?auth={self._id_token}"
#
#     def _valid_token_present(self) -> bool:
#         return self._id_token is not None
#
#     @map_errors
#     async def _get(self, url: str) -> ClientResponse:
#         return await self._client_session.get(url=url)
#
#     @map_errors
#     async def _patch(self, url: str, data: str) -> ClientResponse:
#         return await self._client_session.patch(url=url, data=data)
#
#     @map_errors
#     async def _post(self, url: str, data: str) -> ClientResponse:
#         return await self._client_session.post(url=url, data=data)
#
#     async def _get_id_token(self) -> AuthData:
#         payload = AuthPayload(email=self._email, password=self._password)
#         json = AuthPayloadSchema().dumps(payload)
#         raw_response = await self._post(self._auth_url, data=json)
#
#         if not self._returned_http_200(response=raw_response):
#             raise FirebaseResponseError(response=raw_response)
#
#         schema = AuthSchema()
#         json = await raw_response.json()
#         response = AuthData(**schema.load(data=json))
#
#         self._id_token = response.id_token
#         self._refresh_token = response.refresh_token
#         self._expires_in = int(response.expires_in)
#
#         return response
#
#     async def _refresh_id_token(self, refresh_token: str) -> AuthRefreshData:
#         payload = AuthRefreshPayload(refresh_token=refresh_token)
#         json = AuthRefreshPayloadSchema().dumps(payload)
#
#         raw_response = await self._post(self._auth_refresh_url, data=json)
#         if not self._returned_http_200(response=raw_response):
#             raise FirebaseResponseError(response=raw_response)
#
#         schema = AuthRefreshSchema()
#         json = await raw_response.json()
#         response = AuthRefreshData(**schema.load(data=json))
#
#         self._id_token = response.id_token
#         self._refresh_token = response.refresh_token
#         self._expires_in = int(response.expires_in)
#
#         return response
#
#     async def _authenticate(self) -> None:
#         if self._refresh_token is not None:
#             await self._refresh_id_token(refresh_token=self._refresh_token)
#         else:
#             await self._get_id_token()
#
#     @authenticate
#     async def fetch_schedule(self) -> ScheduleData:
#         """
#         Fetches the node data and returns its domain model.
#         """
#         raw_response = await self._get(url=self._append_auth_token(url=self._node_url))
#         if not self._returned_http_200(response=raw_response):
#             if self._returned_http_401(response=raw_response):
#                 raise FirebaseUnauthorizedError(response=raw_response)
#             else:
#                 raise FirebaseResponseError(response=raw_response)
#
#         schema = ScheduleSchema()
#         json = await raw_response.json()
#         loaded_data = schema.load(data=json)
#
#         one_time_activation = None
#         if 'one_time' in loaded_data:
#             one_time_activation = OneTimeActivationData(
#                 date=loaded_data['one_time']['date'],
#                 water=loaded_data['one_time']['water']
#             )
#
#         plan = []
#         if 'plan' in loaded_data:
#             plan = [ScheduleItemData(time=p['time'], water=p['water'], active=p['active']) for p in loaded_data['plan']]
#
#         return ScheduleData(
#             plan=plan,
#             active=loaded_data.get('active', False),
#             one_time_activation=one_time_activation
#         )
#
#     @authenticate
#     async def send_execution_log(self, activation: PumpActivation) -> bool:
#         """
#         Updates data about last pump activation. This may be helpful for checking if the pump was actually activated
#         when it should be according to the schedule.
#         :param activation: activation details with timestamp and water amount
#         """
#         execution_log = ExecutionLogPayloadData(last_activation=map_domain_to_pump_activation(activation))
#         schema = ExecutionLogPayloadSchema()
#
#         raw_response = await self._patch(url=self._append_auth_token(url=self._node_url),
#                                          data=schema.dumps(execution_log))
#
#         if not self._returned_http_200(response=raw_response):
#             if self._returned_http_401(response=raw_response):
#                 raise FirebaseUnauthorizedError(response=raw_response)
#             else:
#                 raise FirebaseResponseError(response=raw_response)
#
#         return True
#
#     @authenticate
#     async def send_health_check(self) -> bool:
#         """
#         Sends current timestamp so the user can check if his device is alive.
#         """
#         health_check = HealthCheckPayloadData(health_check=datetime.now())
#         schema = HealthCheckPayloadSchema()
#
#         raw_response = await self._patch(url=self._append_auth_token(url=self._node_url),
#                                          data=schema.dumps(health_check))
#
#         if not self._returned_http_200(response=raw_response):
#             if self._returned_http_401(response=raw_response):
#                 raise FirebaseUnauthorizedError(response=raw_response)
#             else:
#                 raise FirebaseResponseError(response=raw_response)
#
#         return True
