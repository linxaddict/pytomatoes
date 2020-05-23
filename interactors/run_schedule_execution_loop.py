import asyncio
from datetime import datetime, date
from logging import Logger

from data.pump_activation_repository import PumpActivationRepository
from domain.model import PlanItem, OneTimeActivation
from interactors.activate_pump import ActivatePump
from interactors.fetch_schedule import FetchSchedule


class RunScheduleExecutionLoop:
    """
    Date and time format for all timestamps.
    """
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    """
    Time format for used for describing time slots in the schedule.
    """
    TIME_FORMAT = '%H:%M'

    """
    Execution margin specified in minutes for determining if given plan item is still valid. 
    """
    EXECUTION_MARGIN = 60

    """
    Specifies how often the schedule should po fetched from Firebase.
    """
    FETCH_INTERVAL = 5

    def __init__(self, fetch_schedule: FetchSchedule, activate_pump: ActivatePump, repository: PumpActivationRepository,
                 logger: Logger) -> None:
        self._fetch_schedule = fetch_schedule
        self._activate_pump = activate_pump
        self._repository = repository
        self._logger = logger

    @staticmethod
    def _extract_slot_ts(item: PlanItem) -> str:
        """
        Extracts the timestamp of given plan item in DATE_TIME_FORMAT.
        :param item: plan item
        :return: properly formatted timestamp
        """
        time = datetime.strptime(item.time, RunScheduleExecutionLoop.TIME_FORMAT).time()
        slot = datetime.combine(date.today(), time)

        return slot.strftime(RunScheduleExecutionLoop.DATE_TIME_FORMAT)

    async def _should_start_pump(self, item: PlanItem, margin_in_minutes=60) -> bool:
        """
        Checks if the water pump should be activated for given plan item taking into account time margin. The margin
        specifies the limit beyond which plan items are recognized as invalid and are not executed.
        :param item: plan item
        :param margin_in_minutes: the margin for determining if given plan item is still valid
        :return:true if the plan item should be executed
        """
        time = datetime.strptime(item.time, RunScheduleExecutionLoop.TIME_FORMAT).time()
        now = datetime.now().time()

        slot = datetime.combine(date.today(), time)

        slot_str = slot.strftime(RunScheduleExecutionLoop.DATE_TIME_FORMAT)
        delta = datetime.combine(date.today(), now) - slot

        return now > time and delta.seconds < margin_in_minutes * 60 and not await self._repository.exists(slot_str)

    async def _should_start_one_time_activation(self, item: OneTimeActivation, margin_in_minutes=60) -> bool:
        """
        Checks if the water pump should be activated for given activation item taking into account time margin.
        The margin specifies the limit beyond which plan items are recognized as invalid and are not executed.
        :param item: one-time activation item
        :param margin_in_minutes: the margin for determining if given plan item is still valid
        :return:true if the activate item should be executed
        """
        one_time_date = datetime.strptime(item.date, RunScheduleExecutionLoop.DATE_TIME_FORMAT)
        now = datetime.now()

        slot_str = one_time_date.strftime(RunScheduleExecutionLoop.DATE_TIME_FORMAT)
        delta = now - one_time_date

        return now > one_time_date and delta.seconds < margin_in_minutes * 60 and not \
            await self._repository.exists(slot_str)

    async def execute(self) -> None:
        """
        Runs an infinite loop in which the schedule is constantly fetched and its items are executed. This method
        contains the logic responsible for managing water pump activation with regard to the timetable created by
        the user.
        """
        while True:
            schedule = await self._fetch_schedule.execute()

            if schedule and schedule.active:
                try:
                    if schedule.one_time_activation and await self._should_start_one_time_activation(
                            schedule.one_time_activation, RunScheduleExecutionLoop.EXECUTION_MARGIN):
                        await self._activate_pump.execute(timestamp=schedule.one_time_activation.date,
                                                          water=schedule.one_time_activation.water)

                    for item in [pi for pi in schedule.plan if pi.active]:
                        if await self._should_start_pump(item, RunScheduleExecutionLoop.EXECUTION_MARGIN):
                            await self._activate_pump.execute(timestamp=self._extract_slot_ts(item), water=item.water)
                except Exception as e:
                    self._logger.error('an exception occurred: {0}'.format(e))

            await asyncio.sleep(RunScheduleExecutionLoop.FETCH_INTERVAL)
