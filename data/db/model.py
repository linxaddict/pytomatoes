from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from data.db.db_common import Base


class CircuitEntity(Base):
    """
    Represents circuits in the database. It has a 1 - n relation with ScheduledActivationEntity.
    """

    __tablename__ = 'circuits'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    active = Column(Boolean)
    schedule = relationship('ScheduledActivationEntity', back_populates='circuit')

    def __repr__(self) -> str:
        return "<Circuit(id='{0}')>".format(self.id)


class ScheduledActivationEntity(Base):
    """
    Represents scheduled activation in the database.
    """

    __tablename__ = 'scheduled_activations'

    id = Column(Integer, primary_key=True)
    time = Column(String)
    amount = Column(Integer)
    active = Column(Boolean)

    circuit_id = Column(Integer, ForeignKey('circuits.id'))
    schedule = relationship('CircuitEntity', back_populates="schedule")

    def __repr__(self) -> str:
        return "<PlanItem(id='{0}', time='{1}', water='{2}', active='{3}')>".format(
            self.id, self.time, self.water, self.active
        )


class PumpActivationEntity(Base):
    """
    Represents history of pump activations.
    """

    __tablename__ = 'pump_activations'

    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    amount = Column(Integer)

    def __repr__(self) -> str:
        return "<PumpActivationEntity(id='{0}', timestamp='{1}', amount='{2}')>".format(self.id, self.timestamp,
                                                                                        self.amount)
