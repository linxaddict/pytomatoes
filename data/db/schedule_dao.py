from data.db.db_common import Session
from data.db.model import ScheduleEntity, PlanItemEntity


class ScheduleDao:
    """
    Represents a data access object for schedules. It allows for fetching and storing schedule in the database.
    Currently there can be only one schedule.
    """

    def __init__(self, session: Session):
        self.session = session

    async def fetch(self) -> ScheduleEntity:
        """
        Fetch stored schedule.
        :return: stored schedule
        """
        return self.session.query(ScheduleEntity).first()

    async def store(self, schedule: ScheduleEntity) -> None:
        """
        Removes previously stored schedule and stores a new one.
        :param schedule: new schedule
        """
        self.session.query(PlanItemEntity).delete()
        self.session.query(ScheduleEntity).delete()
        self.session.add(schedule)
        self.session.commit()
