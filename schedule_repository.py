import datetime
from dataclasses import dataclass
from typing import Dict, List

from pyrebase import pyrebase
from pyrebase.pyrebase import Firebase
from requests import HTTPError, Timeout, ConnectionError


@dataclass
class PlanItem:
    time: str
    water: int


@dataclass
class Schedule:
    plan: List[PlanItem]


@dataclass
class FirebaseConfig:
    apiKey: str
    authDomain: str
    databaseURL: str
    storageBucket: str
    email: str
    password: str


class ScheduleRepository:
    @staticmethod
    def _configure_firebase(firebase_config: FirebaseConfig) -> Firebase:
        config = {
            "apiKey": firebase_config.apiKey,
            "authDomain": firebase_config.authDomain,
            "databaseURL": firebase_config.databaseURL,
            "storageBucket": firebase_config.storageBucket
        }

        return pyrebase.initialize_app(config)

    async def _authenticate(self) -> Dict[str, str]:
        auth = self.firebase.auth()
        return auth.sign_in_with_email_and_password(self._email, self._password)

    async def _refresh_authentication(self) -> Dict[str, str]:
        auth = self.firebase.auth()
        return auth.refresh(refresh_token=self._refresh_token)

    async def _authenticate_if_needed(self):
        self._time_to_refresh = (self._refresh_time - datetime.datetime.now()).total_seconds()
        if self._time_to_refresh <= 300:
            if not self._refresh_token:
                response = await self._authenticate()
            else:
                response = await self._refresh_authentication()

            expires_in = int(response.get('expiresIn', 3600))
            self._refresh_token = response['refreshToken']
            self._refresh_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

    async def _fetch_schedule(self) -> Schedule:
        plan = self.db.child('plan').get().val()
        return Schedule([
            PlanItem(time=item['time'], water=int(item['water'])) for item in plan
        ])

    def __init__(self, firebase_config: FirebaseConfig):
        self.firebase = self._configure_firebase(firebase_config)
        self.db = self.firebase.database()

        self._email = firebase_config.email
        self._password = firebase_config.password

        self._refresh_token = None
        self._refresh_time = datetime.datetime.now()
        self._time_to_refresh = 0

        self._cached_schedule = {}

    async def fetch(self) -> Schedule:
        try:
            await self._authenticate_if_needed()
            self._cached_schedule = await self._fetch_schedule()

            return self._cached_schedule
        except (HTTPError, ConnectionError, Timeout):
            return Schedule([])

    async def update_schedule(self, schedule: Schedule) -> None:
        try:
            await self._authenticate_if_needed()
            data = {
                "plan": [
                    {"time": p.time, "water": p.water} for p in schedule.plan
                ]
            }

            self.db.update(data)
        except (HTTPError, ConnectionError, Timeout) as e:
            print('err: ', e)
