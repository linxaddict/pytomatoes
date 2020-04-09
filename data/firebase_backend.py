import datetime
import functools
from dataclasses import dataclass
from typing import Dict, Any, List

from pyrebase import pyrebase
from pyrebase.pyrebase import Firebase

from data.model import Schedule, PlanItem


@dataclass
class FirebaseConfig:
    apiKey: str
    authDomain: str
    databaseURL: str
    storageBucket: str
    email: str
    password: str


def authenticate(func: Any):
    @functools.wraps(func)
    async def wrapped(*args: List[Any], **kwargs):
        # noinspection PyUnresolvedReferences
        await args[0].authenticate_if_needed()
        return await func(*args, **kwargs)

    return wrapped


class FirebaseBackend:
    TOKEN_TTL = 3600
    TOKEN_REFRESH_TIME_MARGIN = 300

    def __init__(self, config: FirebaseConfig):
        self.firebase = self._configure_firebase(config)
        self.db = self.firebase.database()

        self._email = config.email
        self._password = config.password

        self._refresh_token = None
        self._refresh_time = datetime.datetime.now()
        self._time_to_refresh = 0

    @staticmethod
    def _configure_firebase(firebase_config: FirebaseConfig) -> Firebase:
        config = {
            'apiKey': firebase_config.apiKey,
            'authDomain': firebase_config.authDomain,
            'databaseURL': firebase_config.databaseURL,
            'storageBucket': firebase_config.storageBucket
        }

        return pyrebase.initialize_app(config)

    async def _authenticate(self) -> Dict[str, str]:
        auth = self.firebase.auth()
        return auth.sign_in_with_email_and_password(self._email, self._password)

    async def _refresh_authentication(self) -> Dict[str, str]:
        auth = self.firebase.auth()
        return auth.refresh(refresh_token=self._refresh_token)

    async def authenticate_if_needed(self) -> None:
        self._time_to_refresh = (self._refresh_time - datetime.datetime.now()).total_seconds()
        if self._time_to_refresh <= self.TOKEN_REFRESH_TIME_MARGIN:
            if not self._refresh_token:
                response = await self._authenticate()
            else:
                response = await self._refresh_authentication()

            expires_in = int(response.get('expiresIn', self.TOKEN_TTL))
            self._refresh_token = response['refreshToken']
            self._refresh_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

    @authenticate
    async def fetch_schedule(self) -> Schedule:
        plan = self.db.child('plan').get().val()
        return Schedule([
            PlanItem(time=item['time'], water=int(item['water'])) for item in plan
        ], active=bool(self.db.child('active').get().val()))

    @authenticate
    async def update_schedule(self, schedule: Schedule) -> None:
        data = {
            'plan': [
                {'time': p.time, 'water': p.water} for p in schedule.plan
            ]
        }

        self.db.update(data)

    @authenticate
    async def send_execution_log(self, timestamp: str, water: int) -> None:
        data = {
            'last_activation': {
                'timestamp': timestamp,
                'water': water
            }
        }

        self.db.update(data)

    @authenticate
    async def send_health_check(self, timestamp: str) -> None:
        data = {
            'health_check': timestamp
        }

        self.db.update(data)
