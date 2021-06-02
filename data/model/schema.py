from marshmallow import Schema, fields, EXCLUDE


class OneTimeActivationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    timestamp = fields.Str()
    amount = fields.Int(missing=0)


class ScheduledActivationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    time = fields.Str()
    amount = fields.Int(missing=0)
    active = fields.Bool(missing=False)


class CircuitSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int()
    name = fields.Str()
    active = fields.Bool()
    healthy = fields.Bool()
    one_time_activation = fields.Nested(OneTimeActivationSchema, allow_none=True, missing=None)
    schedule = fields.Nested(ScheduledActivationSchema, many=True, allow_none=True, missing=[])
