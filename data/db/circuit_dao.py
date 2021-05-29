from data.db.db_common import Session
from data.db.model import CircuitEntity, ScheduledActivationEntity


class CircuitDao:
    """
    Represents a data access object for circuit. It allows for fetching and storing schedule in the database.
    Currently there can be only one circuit.
    """

    def __init__(self, session: Session):
        self.session = session

    async def fetch(self) -> CircuitEntity:
        """
        Fetch stored circuit.
        :return: stored circuit
        """
        return self.session.query(CircuitEntity).first()

    async def store(self, circuit: CircuitEntity) -> None:
        """
        Removes previously stored circuit and stores a new one.
        :param circuit: new circuit
        """
        self.session.query(ScheduledActivationEntity).delete()
        self.session.query(CircuitEntity).delete()
        self.session.add(circuit)
        self.session.commit()
