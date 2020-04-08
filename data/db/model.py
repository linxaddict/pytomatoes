from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from data.db.db_common import Base


class ScheduleEntity(Base):
    """
    Represents schedules in the database. It has a 1 - n relation with PlanItemEntity.
    """

    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    plan_items = relationship('PlanItemEntity', back_populates='schedule')

    def __repr__(self) -> str:
        return "<Schedule(id='{0}')>".format(self.id)


class PlanItemEntity(Base):
    """
    Represents schedule plan items in the database. Every item can be related to one schedule.
    """

    __tablename__ = 'plan_items'

    id = Column(Integer, primary_key=True)
    time = Column(String)
    water = Column(Integer)

    schedule_id = Column(Integer, ForeignKey('schedules.id'))
    schedule = relationship('ScheduleEntity', back_populates="plan_items")

    def __repr__(self) -> str:
        return "<PlanItem(id='{0}', time='{1}', water='{2}')>".format(self.id, self.time, self.water)


class PumpActivationEntity(Base):
    """
    Represents history of pump activations.
    """

    __tablename__ = 'pump_activations'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    water = Column(Integer)

    def __repr__(self) -> str:
        return "<PumpActivationEntity(id='{0}', timestamp='{1}', water='{2}')>".format(self.id, self.timestamp,
                                                                                       self.water)
