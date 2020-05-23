from marshmallow import Schema, EXCLUDE, fields


class PlanItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    time = fields.Str()
    water = fields.Int(missing=0)


class OneTimeActivationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    date = fields.Str()
    water = fields.Int(missing=0)


class LastActivationSchema(Schema):
    timestamp = fields.Str()
    water = fields.Int(missing=0)


class ScheduleSchema(Schema):
    active = fields.Bool(missing=False)
    health_check = fields.Str(allow_none=True, missing=None)
    last_activation = fields.Nested(LastActivationSchema, allow_none=True, missing=None)
    one_time = fields.Nested(OneTimeActivationSchema, allow_none=True, missing=None)
    plan = fields.Nested(PlanItemSchema, many=True, allow_none=True, missing=[])
