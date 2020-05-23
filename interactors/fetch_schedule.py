from typing import Optional

from data.schedule_repository import ScheduleRepository
from domain.model import Schedule


class FetchSchedule:
    def __init__(self, schedule_repository: ScheduleRepository):
        self._repository = schedule_repository

    async def execute(self) -> Optional[Schedule]:
        return await self._repository.fetch()
