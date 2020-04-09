from typing import List

from data.db.db_common import Session
from data.db.model import PlanItemEntity


class PlanItemDao:
    """
    Represents a data access object for plan items. It allows for fetching and storing items in the database. Currently
    the table is cleared every time when a new list is stored because for now the app supports only one schedule that
    is constantly pulled and cached from Firebase.
    """

    def __init__(self, session: Session):
        self.session = session

    async def fetch_all(self) -> List[PlanItemEntity]:
        """
        Fetches all stored plan items.
        :return: list of plan items
        """
        return self.session.query(PlanItemEntity)

    async def store(self, plan_items: List[PlanItemEntity]) -> None:
        """
        Removes all existing plan items and stores new ones. The table is cleared because current design supports only
        one schedule that is frequently pulled.
        :param plan_items: list of plan items that should be stored
        """
        self.session.query(PlanItemEntity).delete()
        self.session.add_all(plan_items)
        self.session.commit()
