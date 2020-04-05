import datetime
from dataclasses import dataclass
from typing import Dict

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


class FirebaseBackend:
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

    async def fetch_schedule(self) -> Schedule:
        await self._authenticate_if_needed()

        plan = self.db.child('plan').get().val()
        return Schedule([
            PlanItem(time=item['time'], water=int(item['water'])) for item in plan
        ])

    async def update_schedule(self, schedule: Schedule) -> None:
        await self._authenticate_if_needed()
        data = {
            "plan": [
                {"time": p.time, "water": p.water} for p in schedule.plan
            ]
        }

        self.db.update(data)

    async def send_health_check(self, timestamp: str) -> None:
        await self._authenticate_if_needed()
        data = {
            "health_check": timestamp
        }

        self.db.update(data)
