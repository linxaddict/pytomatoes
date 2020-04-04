from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.db_common import Base


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<Schedule(id='{0}')>".format(self.id)


class PlanItem(Base):
    __tablename__ = 'plan_items'

    id = Column(Integer, primary_key=True)
    time = Column(String)
    water = Column(Integer)

    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    schedule = relationship('Schedule', back_populates="plan_items")

    def __repr__(self):
        return "<PlanItem(id='{0}', time='{1}', water='{2}')>".format(self.id, self.time, self.water)
