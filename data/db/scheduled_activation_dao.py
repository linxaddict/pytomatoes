from typing import List

from data.db.db_common import Session
from data.db.model import ScheduledActivationEntity


class ScheduledActivationDao:
    """
    Represents a data access object for scheduled activations. It allows for fetching and storing items in the database.
    Currently the table is cleared every time when a new list is stored because for now the app supports only one
    schedule that is constantly pulled and cached from the backend.
    """

    def __init__(self, session: Session):
        self.session = session

    async def fetch_all(self) -> List[ScheduledActivationEntity]:
        """
        Fetches all stored plan items.
        :return: list of plan items
        """
        return self.session.query(ScheduledActivationEntity)

    async def store(self, schedule: List[ScheduledActivationEntity]) -> None:
        """
        Removes all existing activations and stores new ones. The table is cleared because current design supports only
        one schedule that is frequently pulled.
        :param schedule: list of activations that should be stored
        """
        self.session.query(ScheduledActivationEntity).delete()
        self.session.add_all(schedule)
        self.session.commit()
