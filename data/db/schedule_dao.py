from data.db.db_common import Session
from data.db.model import ScheduleEntity, PlanItemEntity


class ScheduleDao:
    def __init__(self, session: Session):
        self.session = session

    async def fetch(self) -> ScheduleEntity:
        return self.session.query(ScheduleEntity).first()

    async def store(self, schedule: ScheduleEntity) -> None:
        self.session.query(PlanItemEntity).delete()
        self.session.query(ScheduleEntity).delete()
        self.session.add(schedule)
        self.session.commit()
