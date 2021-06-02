from logging import Logger
from typing import Optional

from data.db.circuit_dao import CircuitDao
from data.db.mapper import map_plan_item_entity_to_domain, map_circuit_to_entity
from data.db.scheduled_activation_dao import ScheduledActivationDao
from data.model.mapper import map_circuit_to_domain
from data.smart_garden.exceptions import SmartGardenException
from data.smart_garden.smart_garden_backend import SmartGardenBackend
from domain.model import Circuit


class CircuitRepository:
    """
    Repository of circuits that allows for fetching the circuit in the online-first fashion. If it's not possible
    to fetch the circuit from the smart garden backend, local database is used.
    """

    def __init__(self, backend: SmartGardenBackend, plan_item_dao: ScheduledActivationDao, circuit_dao: CircuitDao,
                 logger: Logger):
        self._backend = backend
        self._plan_item_dao = plan_item_dao
        self._circuit_dao = circuit_dao
        self._logger = logger

    async def fetch(self) -> Optional[Circuit]:
        """
        Fetches the circuit using smart garden backend as primary data source and local database as the secondary.
        :return: circuit or None if it cannot be fetched
        """
        try:
            circuit = map_circuit_to_domain(await self._backend.fetch_circuit())
            await self._circuit_dao.store(map_circuit_to_entity(circuit))
            return circuit
        except SmartGardenException as e:
            self._logger.error('could not fetch the circuit: {0)'.format(e))
            self._logger.info('fetching the circuit from local database')

            circuit_entity = await self._circuit_dao.fetch()
            if not circuit_entity:
                self._logger.error('could not fetch the circuit from local database')
                return None

            schedule = [map_plan_item_entity_to_domain(item) for item in circuit_entity.schedule]

            return Circuit(id=circuit_entity.id, schedule=schedule, active=circuit_entity.active,
                           one_time_activation=None, name=circuit_entity.name)

    async def update_circuit(self, circuit: Circuit) -> None:
        """
        Updates the circuit and stores updated data in the local database.
        :param circuit: updated circuit
        """
        await self._circuit_dao.store(map_circuit_to_entity(circuit))
