class ValidationError(Exception):
    pass


class EmptyField(ValidationError):
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self) -> str:
        return '{!r} field cannot be empty'.format(self.field_name)
