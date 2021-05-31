import asyncio
import datetime
from logging import Logger

from data.pump_activation_repository import PumpActivationRepository
from data.smart_garden.smart_garden_backend import SmartGardenBackend
from device.pump_mock import Pump
from domain.model import PumpActivation


class ActivatePump:
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, pump: Pump, repository: PumpActivationRepository, backend: SmartGardenBackend,
                 logger: Logger) -> None:
        self._pump = pump
        self._repository = repository
        self._backend = backend
        self._logger = logger

    async def execute(self, timestamp: str, water: int) -> None:
        """
        Activates the pump and logs it in the Firebase backend.
        :param timestamp: timestamp of pump activation
        :param water: amount of water
        """
        self._logger.info('activating the pump, ts: {0}, water: {1} ml'.format(timestamp, water))
        self._pump.on_async(water)

        await asyncio.gather(
            self._repository.store(PumpActivation(timestamp=timestamp, amount=water)),
            self._backend.send_execution_log(
                activation=PumpActivation(
                    timestamp=datetime.datetime.now().strftime(ActivatePump.DATE_TIME_FORMAT),
                    amount=water
                )
            )
        )
