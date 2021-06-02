from dataclasses import dataclass
from typing import List


@dataclass
class OneTimeActivationData:
    timestamp: str
    amount: int


@dataclass
class ScheduledActivationData:
    time: str
    amount: int
    active: bool


@dataclass
class CircuitData:
    id: int
    name: str
    active: bool
    one_time_activation: OneTimeActivationData
    schedule: List[ScheduledActivationData]
