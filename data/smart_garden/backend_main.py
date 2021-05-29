import asyncio

from aiohttp import ClientSession

from data.circuit_repository import CircuitRepository
from data.db.circuit_dao import CircuitDao
from data.db.db_common import Session
from data.db.pump_activation_dao import PumpActivationDao
from data.db.scheduled_activation_dao import ScheduledActivationDao
from data.pump_activation_repository import PumpActivationRepository
from data.smart_garden.smart_garden_backend import SmartGardenBackend
from device.pump_mock import Pump
from interactors.activate_pump import ActivatePump
from interactors.fetch_circuit import FetchCircuit
from interactors.run_healthcheck_loop import RunHealthCheckLoop
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
        smart_garden_backend = SmartGardenBackend(
            email=settings.firebase_email,
            password=settings.firebase_password,
            db_url=settings.database_url,
            client_session=session
        )
        session = Session()

        plan_item_dao = ScheduledActivationDao(session=session)
        schedule_dao = CircuitDao(session=session)
        pump_activation_dao = PumpActivationDao(session=session)

        schedule_repository = CircuitRepository(smart_garden_backend, plan_item_dao, schedule_dao, logger)
        pump_activation_repository = PumpActivationRepository(pump_activation_dao)

        pump = Pump(
            ml_per_second=settings.ml_per_seconds
        )

        activate_pump = ActivatePump(
            pump=pump,
            repository=pump_activation_repository,
            backend=smart_garden_backend,
            logger=logger
        )
        fetch_circuit = FetchCircuit(circuit_repository=schedule_repository)
        run_healthcheck_loop = RunHealthCheckLoop(backend=smart_garden_backend)
        run_schedule_execution_loop = RunScheduleExecutionLoop(
            fetch_circuit=fetch_circuit,
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
                await run_schedule_execution_loop.execute()
            except Exception:
                logger.error('unexpected error occurred', exc_info=True)
                logger.info('pausing for 60 seconds')

                await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
