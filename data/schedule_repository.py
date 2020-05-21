from logging import Logger
from typing import Optional

from data.db.plan_item_dao import PlanItemDao
from data.db.schedule_dao import ScheduleDao
from data.firebase.exceptions import FirebaseException
from data.firebase.firebase_backend import FirebaseBackend
from data.mapper import map_schedule_to_entity, map_plan_item_entity_to_domain
from data.model import Schedule


class ScheduleRepository:
    """
    Repository of schedules that allows for fetching the schedule in the online-first fashion. If it's not possible
    to fetch the schedule from Firebase, local database is used.
    """

    def __init__(self, firebase_backend: FirebaseBackend, plan_item_dao: PlanItemDao, schedule_dao: ScheduleDao,
                 logger: Logger):
        self._firebase_backend = firebase_backend
        self._plan_item_dao = plan_item_dao
        self._schedule_dao = schedule_dao
        self._logger = logger

    async def fetch(self) -> Optional[Schedule]:
        """
        Fetches the schedule using Firebase backend as primary data source and local database as the secondary.
        :return: schedule or None if it cannot be fetched
        """
        try:
            schedule = await self._firebase_backend.fetch_schedule()
            await self._schedule_dao.store(map_schedule_to_entity(schedule))
            return schedule
        except FirebaseException as e:
            self._logger.error('could not fetch the schedule: {0)'.format(e))
            self._logger.info('fetching the schedule from local database')

            schedule_entity = await self._schedule_dao.fetch()
            if not schedule_entity:
                self._logger.error('could not fetch the schedule from local database')
                return None

            plan_items = [map_plan_item_entity_to_domain(item) for item in schedule_entity.plan_items]

            return Schedule(plan=plan_items, active=schedule_entity.active)

    async def update_schedule(self, schedule: Schedule) -> None:
        """
        Updates the schedule and stores updated data in the local database.
        :param schedule: updated schedule
        """
        await self._schedule_dao.store(map_schedule_to_entity(schedule))
