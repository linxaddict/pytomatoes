import asyncio

from data.db.db_common import Session
from data.db.plan_item_dao import PlanItemDao
from data.db.pump_activation_dao import PumpActivationDao
from data.db.schedule_dao import ScheduleDao
from data.firebase_backend import FirebaseBackend, FirebaseConfig
from data.pump_activation_repository import PumpActivationRepository
from data.schedule_repository import ScheduleRepository
from log.logger import logger
from pump.pump import Pump
from schedule_executor import ScheduleExecutor
from settings import Settings

GPIO_PIN = 21


async def main():
    from dotenv import load_dotenv
    load_dotenv()

    settings = Settings()
    firebase_config = settings.firebase_aggregated_config

    firebase_backend = FirebaseBackend(FirebaseConfig(**firebase_config))
    session = Session()

    plan_item_dao = PlanItemDao(session=session)
    schedule_dao = ScheduleDao(session=session)
    pump_activation_dao = PumpActivationDao(session=session)

    schedule_repository = ScheduleRepository(firebase_backend, plan_item_dao, schedule_dao, logger)
    pump_activation_repository = PumpActivationRepository(pump_activation_dao)

    pump = Pump(gpio_pin=GPIO_PIN)

    schedule_executor = ScheduleExecutor(firebase_backend=firebase_backend, schedule_repository=schedule_repository,
                                         pump_activation_repository=pump_activation_repository, pump=pump,
                                         logger=logger)

    await asyncio.gather(
        schedule_executor.execute(),
        schedule_executor.run_health_check_loop()
    )


if __name__ == "__main__":
    asyncio.run(main())
