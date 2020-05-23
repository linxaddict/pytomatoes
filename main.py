import asyncio

from aiohttp import ClientSession

from data.db.db_common import Session
from data.db.plan_item_dao import PlanItemDao
from data.db.pump_activation_dao import PumpActivationDao
from data.db.schedule_dao import ScheduleDao
from data.firebase.firebase_backend import FirebaseBackend
from data.pump_activation_repository import PumpActivationRepository
from data.schedule_repository import ScheduleRepository
from device.pump import Pump
from interactors.activate_pump import ActivatePump
from interactors.fetch_schedule import FetchSchedule
from interactors.run_healthcheck_loop import RunHealthcheckLoop
from interactors.run_schedule_execution_loop import RunScheduleExecutionLoop
from log.logger import logger
from settings import Settings


async def main() -> None:
    """
    Main function that is responsible for:
        - creating and configuring all the components,
        - starting infinite schedule execution,
        - starting infinite health check loop.
    """

    settings = Settings()

    async with ClientSession() as session:
        firebase_backend = FirebaseBackend(
            email=settings.firebase_email,
            password=settings.firebase_password,
            api_key=settings.api_key,
            db_url=settings.database_url,
            node=settings.node,
            client_session=session
        )
        session = Session()

        plan_item_dao = PlanItemDao(session=session)
        schedule_dao = ScheduleDao(session=session)
        pump_activation_dao = PumpActivationDao(session=session)

        schedule_repository = ScheduleRepository(firebase_backend, plan_item_dao, schedule_dao, logger)
        pump_activation_repository = PumpActivationRepository(pump_activation_dao)

        pump = Pump(
            gpio_pin=settings.pin_number,
            ml_per_second=settings.ml_per_seconds
        )

        activate_pump = ActivatePump(
            pump=pump,
            repository=pump_activation_repository,
            firebase=firebase_backend,
            logger=logger
        )
        fetch_schedule = FetchSchedule(schedule_repository=schedule_repository)
        run_healthcheck_loop = RunHealthcheckLoop(firebase=firebase_backend)
        run_schedule_execution_loop = RunScheduleExecutionLoop(
            fetch_schedule=fetch_schedule,
            activate_pump=activate_pump,
            repository=pump_activation_repository, logger=logger
        )

        while True:
            # noinspection PyBroadException
            try:
                await asyncio.gather(
                    run_healthcheck_loop.execute(),
                    run_schedule_execution_loop.execute()
                )
            except Exception:
                logger.error('unexpected error occurred', exc_info=True)
                logger.info('pausing for 60 seconds')

                await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
