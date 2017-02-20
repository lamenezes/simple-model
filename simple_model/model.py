from .exceptions import ValidationError
from .field import ModelField


class Model:
    fields = ()
    allow_empty = ()
    _field_class = ModelField

    def __init__(self, **kwargs):
        for field_name in self.fields:
            field_value = kwargs.get(field_name, None)
            setattr(self, field_name, field_value)

    def __iter__(self):
        return ((field.name, field.value) for field in self._get_fields())

    def __repr__(self):
        return '{}(fields={!r})'.format(type(self).__name__, list(self._get_fields()))

    def _get_fields(self):
        for field_name in self.fields:
            allow_empty = '__all__' in self.allow_empty or field_name in self.allow_empty
            field_value = getattr(self, field_name)
            yield self._field_class(self, field_name, field_value, allow_empty)

    def is_empty(self, value):
        return bool(value)

    def clean(self):
        for field in self._get_fields():
            field.clean()
            setattr(self, field.name, field.value)

    def validate(self, raise_exception=True):
        for field in self._get_fields():
            try:
                field.validate()
            except ValidationError:
                if raise_exception:
                    raise
                return False

        return None if raise_exception else True

    def serialize(self, exclude_fields=None):
        self.validate()
        self.clean()

        data = {}
        for field in self._get_fields():
            if exclude_fields and field.name in exclude_fields:
                continue

            data[field.name] = field.serialize()

        return data
