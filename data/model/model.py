# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional, List
#
#
# @dataclass
# class AuthPayload:
#     email: str
#     password: str
#     return_secure_token: bool = True
#
#
# @dataclass
# class AuthRefreshPayload:
#     refresh_token: str
#     grant_type: str = 'refresh_token'
#
#
# @dataclass
# class AuthData:
#     kind: str
#     local_id: str
#     email: str
#     display_name: str
#     id_token: str
#     expires_in: str
#     registered: bool
#     refresh_token: str
#
#
# @dataclass
# class AuthRefreshData:
#     access_token: str
#     expires_in: str
#     token_type: str
#     refresh_token: str
#     id_token: str
#     user_id: str
#     project_id: str
#
#
# @dataclass
# class HealthCheckPayloadData:
#     health_check: datetime
#
#
# @dataclass
# class ScheduleItemData:
#     time: str
#     water: int
#     active: bool
#
#
# @dataclass
# class OneTimeActivationData:
#     date: str
#     water: int
#
#
# @dataclass
# class ScheduleData:
#     plan: List[ScheduleItemData]
#     active: bool
#     one_time_activation: Optional[OneTimeActivationData]
#
#
# @dataclass
# class PumpActivationData:
#     timestamp: str
#     water: int
#
#
# @dataclass
# class ExecutionLogPayloadData:
#     last_activation: PumpActivationData
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
