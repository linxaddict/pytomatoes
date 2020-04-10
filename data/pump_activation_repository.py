from typing import List

from data.db.pump_activation_dao import PumpActivationDao
from data.mapper import map_pump_activation_entity_to_domain, \
    map_pump_activation_to_entity
from data.model import PumpActivation


class PumpActivationRepository:
    """
    Repository of pump activations that uses only local database. This data represents local activation history and
    currently is not synchronized with Firebase.
    """

    def __init__(self, pump_activation_dao: PumpActivationDao):
        self.pump_activation_dao = pump_activation_dao

    async def fetch(self) -> List[PumpActivation]:
        """
        Returns all stored pump activations.
        :return: list of pump activations
        """
        return [map_pump_activation_entity_to_domain(activation) for activation in
                await self.pump_activation_dao.fetch_all()]

    async def store(self, activation: PumpActivation) -> None:
        """
        Stores new pump activation in the database.
        :param activation: pump activation
        """
        await self.pump_activation_dao.store(map_pump_activation_to_entity(activation))

    async def exists(self, timestamp: str) -> bool:
        """
        Checks if pump was activated in the past for given timestamp.
        :param timestamp: activation timestamp
        :return: true if pump was activated for the timestamp, false otherwise
        """
        return await self.pump_activation_dao.exists(timestamp)
