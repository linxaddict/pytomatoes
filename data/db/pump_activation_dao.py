from typing import List

from data.db.db_common import Session
from data.db.model import PumpActivationEntity


class PumpActivationDao:
    """
    Represents a data access object for pump activations. It allows for fetching, storing and checking if an activation
    with specified timestamp is present in the database.
    """

    def __init__(self, session: Session):
        self.session = session

    async def fetch_all(self) -> List[PumpActivationEntity]:
        """
        Fetches all stored pump activations.
        :return: list of pump activations
        """
        return self.session.query(PumpActivationEntity)

    async def store(self, pump_activation: PumpActivationEntity) -> None:
        """
        Stores a new pump activation in the database.
        :param pump_activation: pump activation that should be stored
        """
        self.session.add(pump_activation)
        self.session.commit()

    async def exists(self, timestamp: str) -> bool:
        """
        Checks if there is a pump activation with specified timestamp in the database.
        :param timestamp: activation timestamp
        :return: true if such activation exists, false otherwise
        """
        return self.session.query(
            self.session.query(PumpActivationEntity).filter_by(timestamp=timestamp).exists()).scalar()
