from marshmallow import Schema, fields, validate, ValidationError

# def validate_username(username):
#     is_true = isinstance(username, str)
#     if not is_true:
#         raise ValidationError("username must be string") 

# class UserSchema(Schema):
#     id = fields.Int()
#     username = fields.String(validate=validate_username, required=True, allow_none=False)
#     password = fields.String(required=True, allow_none=False, load_only=True, validate=validate.Length(min=8))

class UrlSchema(Schema):
    id = fields.Int()
    identifier = fields.String(required=True, allow_none=False)
    filepath = fields.String(required=False, allow_none=True)
    url = fields.String(required=True, allow_none=False)
    method = fields.String(required=True)
    body = fields.Raw(data_type='json', default={})
    response = fields.Raw(data_type='json', default={})
    headers = fields.Raw(data_type='json', default={})
    status_code = fields.Integer(required=True)
    execute = fields.Boolean(required=True, allow_none=False)
