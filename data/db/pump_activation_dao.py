from typing import List

from data.db.db_common import Session
from data.db.model import PumpActivationEntity
from sqlalchemy.sql import exists


class PumpActivationDao:
    def __init__(self, session: Session):
        self.session = session

    async def fetch_all(self) -> List[PumpActivationEntity]:
        return self.session.query(PumpActivationEntity)

    async def store(self, pump_activation: PumpActivationEntity) -> None:
        self.session.add(pump_activation)
        self.session.commit()

    async def exists(self, timestamp: str) -> bool:
        return self.session.query(
            self.session.query(PumpActivationEntity).filter_by(timestamp=timestamp).exists()).scalar()
