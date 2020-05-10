import asyncio
from datetime import datetime, date
from logging import Logger

from data.firebase_backend import FirebaseBackend
from data.model import PlanItem, PumpActivation, OneTimeActivation
from data.pump_activation_repository import PumpActivationRepository
from data.schedule_repository import ScheduleRepository
from pump.pump import Pump


class ScheduleExecutor:
    """
    Manages water pump activation by executing the schedule defined by the user.
    """

    """
    Specifies how often the schedule should po fetched from Firebase.
    """
    INTERVAL = 5

    """
    Date and time format for all timestamps.
    """
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    """
    Time format for used for describing time slots in the schedule.
    """
    TIME_FORMAT = '%H:%M'

    def __init__(self, firebase_backend: FirebaseBackend, schedule_repository: ScheduleRepository,
                 pump_activation_repository: PumpActivationRepository, pump: Pump, logger: Logger):
        self._firebase_backend = firebase_backend
        self._schedule_repository = schedule_repository
        self._pump_activation_repository = pump_activation_repository
        self._pump = pump
        self._logger = logger

    @staticmethod
    def extract_slot_ts(item: PlanItem) -> str:
        """
        Extracts the timestamp of given plan item in DATE_TIME_FORMAT.
        :param item: plan item
        :return: properly formatted timestamp
        """
        time = datetime.strptime(item.time, ScheduleExecutor.TIME_FORMAT).time()
        slot = datetime.combine(date.today(), time)

        return slot.strftime(ScheduleExecutor.DATE_TIME_FORMAT)

    @staticmethod
    async def should_start_pump(item: PlanItem, activation_repository: PumpActivationRepository,
                                margin_in_minutes=60) -> bool:
        """
        Checks if the water pump should be activated for given plan item taking into account time margin. The margin
        specifies the limit beyond which plan items are recognized as invalid and are not executed.
        :param item: plan item
        :param activation_repository: pump activation data source
        :param margin_in_minutes: the margin for determining if given plan item is still valid
        :return:true if the plan item should be executed
        """
        time = datetime.strptime(item.time, ScheduleExecutor.TIME_FORMAT).time()
        now = datetime.now().time()

        slot = datetime.combine(date.today(), time)

        slot_str = slot.strftime(ScheduleExecutor.DATE_TIME_FORMAT)
        delta = datetime.combine(date.today(), now) - slot

        return now > time and delta.seconds < margin_in_minutes * 60 and not await activation_repository.exists(
            slot_str)

    @staticmethod
    async def should_start_one_time_activation(item: OneTimeActivation, activation_repository: PumpActivationRepository,
                                               margin_in_minutes=60) -> bool:
        """
        Checks if the water pump should be activated for given activation item taking into account time margin.
        The margin specifies the limit beyond which plan items are recognized as invalid and are not executed.
        :param item: one-time activation item
        :param activation_repository: pump activation data source
        :param margin_in_minutes: the margin for determining if given plan item is still valid
        :return:true if the activate item should be executed
        """
        one_time_date = datetime.strptime(item.date, ScheduleExecutor.DATE_TIME_FORMAT)
        now = datetime.now()

        slot_str = one_time_date.strftime(ScheduleExecutor.DATE_TIME_FORMAT)
        delta = now - one_time_date

        return now > one_time_date and delta.seconds < margin_in_minutes * 60 \
               and not await activation_repository.exists(slot_str)

    async def execute(self, margin_in_minutes=60) -> None:
        """
        Runs an infinite loop in which the schedule is constantly fetched and its items are executed. This method
        contains the logic responsible for managing water pump activation with regard to the timetable created by
        the user.
        :param margin_in_minutes: the margin for determining if given plan item is still valid
        """
        while True:
            schedule = await self._schedule_repository.fetch()

            if schedule and schedule.active:
                try:
                    if schedule.one_time_activation and await self.should_start_one_time_activation(
                            schedule.one_time_activation, self._pump_activation_repository, margin_in_minutes):
                        slot_ts = schedule.one_time_activation.date

                        self._logger.info('activating the pump, ts: {0}, water: {1} ml'.format(
                            slot_ts, schedule.one_time_activation.water))
                        self._pump.on_async(schedule.one_time_activation.water)

                        await asyncio.gather(
                            self._pump_activation_repository.store(
                                PumpActivation(timestamp=slot_ts, water=schedule.one_time_activation.water)),
                            self._firebase_backend.send_execution_log(
                                timestamp=datetime.now().strftime(ScheduleExecutor.DATE_TIME_FORMAT),
                                water=schedule.one_time_activation.water)
                        )

                    for item in schedule.plan:
                        if await self.should_start_pump(item, self._pump_activation_repository, margin_in_minutes):
                            slot_ts = self.extract_slot_ts(item)

                            self._logger.info('activating the pump, ts: {0}, water: {1} ml'.format(slot_ts, item.water))
                            self._pump.on_async(item.water)

                            await asyncio.gather(
                                self._pump_activation_repository.store(
                                    PumpActivation(timestamp=slot_ts, water=item.water)),
                                self._firebase_backend.send_execution_log(
                                    timestamp=datetime.now().strftime(ScheduleExecutor.DATE_TIME_FORMAT),
                                    water=item.water)
                            )
                except Exception as e:
                    self._logger.error('an exception occurred: {0}'.format(e))

            await asyncio.sleep(self.INTERVAL),

    async def run_health_check_loop(self, interval=INTERVAL) -> None:
        """
        Runs an infinite loop in which health checks are sent so the user knows that his device is alive.
        :param interval: interval between health checks
        """
        while True:
            await asyncio.gather(
                asyncio.sleep(interval),
                self._firebase_backend.send_health_check(datetime.now().strftime(ScheduleExecutor.DATE_TIME_FORMAT))
            )
