from dataclasses import dataclass
from datetime import datetime

from domain.model import PumpActivation


@dataclass
class AuthPayload:
    email: str
    password: str
    return_secure_token: bool = True


@dataclass
class AuthRefreshPayload:
    refresh_token: str
    grant_type: str = 'refresh_token'


@dataclass
class AuthData:
    kind: str
    local_id: str
    email: str
    display_name: str
    id_token: str
    expires_in: str
    registered: bool
    refresh_token: str


@dataclass
class AuthRefreshData:
    access_token: str
    expires_in: str
    token_type: str
    refresh_token: str
    id_token: str
    user_id: str
    project_id: str


@dataclass
class ExecutionLogPayload:
    last_activation: PumpActivation


@dataclass
class HealthCheckPayload:
    health_check: datetime
