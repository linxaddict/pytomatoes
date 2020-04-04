from requests import HTTPError, Timeout, ConnectionError

from data.firebase_backend import FirebaseBackend
from data.model import Schedule


class ScheduleRepository:
    def __init__(self, firebase_backend: FirebaseBackend):
        self._firebase_backend = firebase_backend
        self._cached_schedule = {}

    async def fetch(self) -> Schedule:
        try:
            return await self._firebase_backend.fetch_schedule()
        except (HTTPError, ConnectionError, Timeout):
            return Schedule([])

    async def update_schedule(self, schedule: Schedule) -> None:
        await self._firebase_backend.update_schedule(schedule)
