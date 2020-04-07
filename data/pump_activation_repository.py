from typing import List

from data.db.pump_activation_dao import PumpActivationDao
from data.mapper import map_pump_activation_entity_to_domain, \
    map_pump_activation_to_entity
from data.model import PumpActivation


class PumpActivationRepository:
    def __init__(self, pump_activation_dao: PumpActivationDao):
        self.pump_activation_dao = pump_activation_dao

    async def fetch(self) -> List[PumpActivation]:
        return [map_pump_activation_entity_to_domain(activation) for activation in
                await self.pump_activation_dao.fetch_all()]

    async def store(self, activation: PumpActivation) -> None:
        await self.pump_activation_dao.store(map_pump_activation_to_entity(activation))

    async def exists(self, timestamp: str) -> bool:
        return await self.pump_activation_dao.exists(timestamp)
