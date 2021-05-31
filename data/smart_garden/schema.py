from marshmallow import Schema, fields


class SmartGardenAuthPayloadSchema(Schema):
    email = fields.Email()
    password = fields.Str()


class SmartGardenAuthRefreshPayloadSchema(Schema):
    refresh = fields.Str()


class SmartGardenAuthSchema(Schema):
    access = fields.Str()
    refresh = fields.Str()


class SmartGardenAuthRefreshSchema(Schema):
    access = fields.Str()
    refresh = fields.Str()


class PumpActivationSchema(Schema):
    timestamp = fields.Str()
    amount = fields.Int(missing=0)
