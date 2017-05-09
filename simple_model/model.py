from typing import Any, Iterator, Tuple, Union

from .exceptions import ValidationError
from .field import ModelField


class Model:
    fields = ()
    allow_empty = ()
    _field_class = ModelField

    def __init__(self, **kwargs):
        for field_name in self.get_fields():
            field_value = kwargs.get(field_name, None)
            setattr(self, field_name, field_value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        self.clean()

        for field in self._get_fields():
            yield field.name, field.to_python()

    def __repr__(self) -> str:
        return '{}(fields={!r})'.format(type(self).__name__, list(self._get_fields()))

    def _get_fields(self) -> Iterator[ModelField]:
        allow_empty_fields = self.get_allow_empty()
        for field_name in self.get_fields():
            allow_empty = '__all__' in allow_empty_fields or field_name in allow_empty_fields
            field_value = getattr(self, field_name)
            yield self._field_class(self, field_name, field_value, allow_empty)

    def get_fields(self) -> Tuple[str]:
        assert self.fields, ('{} should include a fields attribute or override '
                             'the get_fields method'.format(type(self).__name__))

        return self.fields

    def get_allow_empty(self) -> Tuple:
        return self.allow_empty

    def is_empty(self, value: Any) -> bool:
        return bool(value)

    def clean(self) -> None:
        for field in self._get_fields():
            field.clean()
            setattr(self, field.name, field.value)

    def validate(self, raise_exception: bool=True) -> Union[None, bool]:
        for field in self._get_fields():
            try:
                field.validate()
            except ValidationError:
                if raise_exception:
                    raise
                return False

        return None if raise_exception else True
