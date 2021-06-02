from typing import Optional

from data.circuit_repository import CircuitRepository
from domain.model import Circuit


class FetchCircuit:
    def __init__(self, circuit_repository: CircuitRepository):
        self._repository = circuit_repository

    async def execute(self) -> Optional[Circuit]:
        return await self._repository.fetch()
