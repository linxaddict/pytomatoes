from logging import Logger
from typing import Optional

from requests import HTTPError, Timeout, ConnectionError

from data.db.plan_item_dao import PlanItemDao
from data.db.schedule_dao import ScheduleDao
from data.firebase_backend import FirebaseBackend
from data.mapper import map_schedule_to_entity, map_plan_item_entity_to_domain
from data.model import Schedule


class ScheduleRepository:
    def __init__(self, firebase_backend: FirebaseBackend, plan_item_dao: PlanItemDao, schedule_dao: ScheduleDao,
                 logger: Logger):
        self._firebase_backend = firebase_backend
        self._plan_item_dao = plan_item_dao
        self._schedule_dao = schedule_dao
        self._logger = logger

    async def fetch(self) -> Optional[Schedule]:
        try:
            schedule = await self._firebase_backend.fetch_schedule()
            await self._schedule_dao.store(map_schedule_to_entity(schedule))
            return schedule
        except (HTTPError, ConnectionError, Timeout) as e:
            self._logger.error('could not fetch the schedule: {0)'.format(e))
            self._logger.info('fetching the schedule from local database')

            schedule_entity = await self._schedule_dao.fetch()
            if not schedule_entity:
                self._logger.error('could not fetch the schedule from local database')
                return None

            plan_items = [map_plan_item_entity_to_domain(item) for item in schedule_entity.plan_items]

            return Schedule(plan=plan_items)

    async def update_schedule(self, schedule: Schedule) -> None:
        await self._schedule_dao.store(map_schedule_to_entity(schedule))
        await self._firebase_backend.update_schedule(schedule)
