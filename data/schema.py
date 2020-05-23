from marshmallow import Schema, fields, EXCLUDE

from domain.schema import LastActivationSchema


class AuthPayloadSchema(Schema):
    email = fields.Email()
    password = fields.Str()
    return_secure_token = fields.Bool(data_key='returnSecureToken')


class AuthRefreshPayloadSchema(Schema):
    refresh_token = fields.Str()
    grant_type = fields.Str()


class AuthSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    kind = fields.Str()
    local_id = fields.Str(data_key='localId', )
    email = fields.Str()
    display_name = fields.Str(data_key='displayName')
    id_token = fields.Str(data_key='idToken')
    expires_in = fields.Str(data_key='expiresIn')
    registered = fields.Bool()
    refresh_token = fields.Str(data_key='refreshToken')


class AuthRefreshSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    access_token = fields.Str()
    expires_in = fields.Str()
    token_type = fields.Str()
    refresh_token = fields.Str()
    id_token = fields.Str()
    user_id = fields.Str()
    project_id = fields.Str()


class ExecutionLogPayloadSchema(Schema):
    last_activation = fields.Nested(LastActivationSchema)


class HealthCheckPayloadSchema(Schema):
    health_check = fields.DateTime('%Y-%m-%dT%H:%M:%S')
