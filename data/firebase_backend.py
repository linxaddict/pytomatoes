import datetime
import functools
from dataclasses import dataclass
from typing import Dict, Any, List

from pyrebase import pyrebase
from pyrebase.pyrebase import Firebase

from data.model import Schedule, PlanItem, OneTimeActivation


@dataclass
class FirebaseConfig:
    """
    Represents the set of all data needed to properly initialize Firebase client.
    """

    apiKey: str
    authDomain: str
    databaseURL: str
    storageBucket: str
    node: str
    email: str
    password: str


def authenticate(func: Any):
    """
    Simple decorator that authenticates Firebase user.
    """

    @functools.wraps(func)
    async def wrapped(*args: List[Any], **kwargs):
        # noinspection PyUnresolvedReferences
        await args[0].authenticate_if_needed()
        return await func(*args, **kwargs)

    return wrapped


class FirebaseBackend:
    """
    Represents Firebase backend that provides access to the schedule and some config and diagnostic data. It allows
    for fetching and updating the schedule, sending short execution log and sending health checks.
    """

    """
    Specifies time to live of the authentication token. It's not always provided by Firebase and in such situations
    default value of 1 hour is used.
    """
    TOKEN_TTL = 3600

    """
    Specifies when the authentication token should be refreshed before exceeding it's time to live. It's just a small
    time margin for avoiding 401 errors.
    """
    TOKEN_REFRESH_TIME_MARGIN = 300

    def __init__(self, config: FirebaseConfig):
        self.firebase = self._configure_firebase(config)
        self.db = self.firebase.database()

        self._email = config.email
        self._password = config.password
        self._node = config.node

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
        """
        Authenticates Firebase user if the token is invalid.
        """
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
        """
        Fetches the schedule and returns its domain model.
        """

        plan = self.db.child('nodes').child(self._node).child('plan').get().val()
        one_time_activation = None
        if self.db.child('nodes').child(self._node).child('one_time').child('water').get().val():
            one_time_activation = OneTimeActivation(
                date=self.db.child('nodes').child(self._node).child('one_time').child('date').get().val(),
                water=int(self.db.child('nodes').child(self._node).child('one_time').child('water').get().val()),
            )

        return Schedule(
            [
                PlanItem(time=item['time'], water=int(item['water'])) for item in plan
            ],
            active=bool(self.db.child('nodes').child(self._node).child('active').get().val()),
            one_time_activation=one_time_activation
        )

    @authenticate
    async def update_schedule(self, schedule: Schedule) -> None:
        """
        Updates the schedule.
        :param schedule: updated schedule
        """
        data = {
            'plan': [
                {'time': p.time, 'water': p.water} for p in schedule.plan
            ]
        }

        self.db.child('nodes').child(self._node).update(data)

    @authenticate
    async def send_execution_log(self, timestamp: str, water: int) -> None:
        """
        Updates data about last pump activation. This may be helpful for checking if the pump was actually activated
        when it should be according to the schedule.
        :param timestamp: timestamp of pump activation
        :param water: amount of water that was pumped
        """
        data = {
            'last_activation': {
                'timestamp': timestamp,
                'water': water
            }
        }

        self.db.child('nodes').child(self._node).update(data)

    @authenticate
    async def send_health_check(self, timestamp: str) -> None:
        """
        Sends current timestamp so the user can check if his device is alive.
        :param timestamp: current timestamp
        """
        data = {
            'health_check': timestamp
        }

        self.db.child('nodes').child(self._node).update(data)
