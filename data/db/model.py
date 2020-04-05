from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from data.db.db_common import Base


class ScheduleEntity(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    plan_items = relationship('PlanItemEntity', back_populates='schedule')

    def __repr__(self):
        return "<Schedule(id='{0}')>".format(self.id)


class PlanItemEntity(Base):
    __tablename__ = 'plan_items'

    id = Column(Integer, primary_key=True)
    time = Column(String)
    water = Column(Integer)

    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    schedule = relationship('ScheduleEntity', back_populates="plan_items")

    def __repr__(self):
        return "<PlanItem(id='{0}', time='{1}', water='{2}')>".format(self.id, self.time, self.water)


class PumpActivationEntity(Base):
    __tablename__ = 'pump_activations'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    water = Column(Integer)
