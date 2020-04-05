from typing import List

from data.db.db_common import Session
from data.db.model import PlanItemEntity


class PlanItemDao:
    def __init__(self, session: Session):
        self.session = session

    async def fetch_all(self) -> List[PlanItemEntity]:
        return self.session.query(PlanItemEntity)

    async def store(self, plan_items: List[PlanItemEntity]) -> None:
        self.session.query(PlanItemEntity).delete()
        self.session.add_all(plan_items)
        self.session.commit()
