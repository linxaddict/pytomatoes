import asyncio
from datetime import datetime
from logging import Logger

from data.firebase.firebase_backend import FirebaseBackend
from data.pump_activation_repository import PumpActivationRepository
from device.pump import Pump
from domain.model import PumpActivation


class ActivatePump:
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, pump: Pump, repository: PumpActivationRepository, firebase: FirebaseBackend,
                 logger: Logger) -> None:
        self._pump = pump
        self._repository = repository
        self._firebase = firebase
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
            self._repository.store(PumpActivation(timestamp=timestamp, water=water)),
            self._firebase.send_execution_log(
                activation=PumpActivation(
                    timestamp=datetime.now().strftime(ActivatePump.DATE_TIME_FORMAT),
                    water=water
                )
            )
        )
