import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, date
from logging import Logger

from data.firebase_backend import FirebaseBackend
from data.model import PlanItem, PumpActivation
from data.pump_activation_repository import PumpActivationRepository
from data.schedule_repository import ScheduleRepository
from pump.pump import Pump


class ScheduleExecutor:
    INTERVAL = 5
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    TIME_FORMAT = '%H:%M'

    def __init__(self, firebase_backend: FirebaseBackend, schedule_repository: ScheduleRepository,
                 pump_activation_repository: PumpActivationRepository, pump: Pump, logger: Logger):
        self._firebase_backend = firebase_backend
        self._schedule_repository = schedule_repository
        self._pump_activation_repository = pump_activation_repository
        self._pump = pump
        self._logger = logger

        self._background_executor = ThreadPoolExecutor(max_workers=1)

    @staticmethod
    def extract_slot_ts(item: PlanItem) -> str:
        time = datetime.strptime(item.time, ScheduleExecutor.TIME_FORMAT).time()
        slot = datetime.combine(date.today(), time)

        return slot.strftime(ScheduleExecutor.DATE_TIME_FORMAT)

    @staticmethod
    async def should_start_pump(item: PlanItem, activation_repository: PumpActivationRepository,
                                margin_in_minutes=60) -> bool:
        time = datetime.strptime(item.time, ScheduleExecutor.TIME_FORMAT).time()
        now = datetime.now().time()

        slot = datetime.combine(date.today(), time)

        slot_str = slot.strftime(ScheduleExecutor.DATE_TIME_FORMAT)
        delta = datetime.combine(date.today(), now) - slot

        return now > time and delta.seconds < margin_in_minutes * 60 and not await activation_repository.exists(
            slot_str)

    async def execute(self, margin_in_minutes=60) -> None:
        loop = asyncio.get_event_loop()

        while True:
            schedule = await self._schedule_repository.fetch()

            if schedule and schedule.active:
                try:
                    for item in schedule.plan:
                        if await self.should_start_pump(item, self._pump_activation_repository, margin_in_minutes):
                            slot_ts = self.extract_slot_ts(item)

                            self._logger.info('activating the pump, ts: {0}, water: {1} ml'.format(slot_ts, item.water))

                            await asyncio.gather(
                                self._pump_activation_repository.store(
                                    PumpActivation(timestamp=slot_ts, water=item.water)),
                                self._firebase_backend.send_execution_log(
                                    timestamp=datetime.now().strftime(ScheduleExecutor.DATE_TIME_FORMAT),
                                    water=item.water),
                                loop.run_in_executor(executor=self._background_executor,
                                                     func=lambda: self._pump.on(item.water))
                            )
                except Exception as e:
                    self._logger.error('an exception occurred: {0}'.format(e))

            await asyncio.sleep(self.INTERVAL),

    async def run_health_check_loop(self, interval=INTERVAL) -> None:
        while True:
            await asyncio.gather(
                asyncio.sleep(interval),
                self._firebase_backend.send_health_check(datetime.now().strftime(ScheduleExecutor.DATE_TIME_FORMAT))
            )
