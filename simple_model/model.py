import inspect
from typing import Any, Iterable, Iterator, Tuple, Union

from .exceptions import ValidationError
from .field import ModelField


class BaseModel(Iterable[Tuple[str, Any]]):
    _field_class = ModelField

    def __init__(self, **kwargs):
        for field_name, field_value in kwargs.items():
            setattr(self, field_name, field_value)

    def __eq__(self, other: Any) -> bool:
        try:
            return dict(self) == dict(other)
        except (TypeError, ValueError):
            return False

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        self.clean()

        for field in self._get_fields():
            yield field.name, field.to_python()

    def __repr__(self) -> str:
        attrs = ', '.join(
            '{field.name}={field.value!r}'.format(field=field) for field in self._get_fields()
        )
        return '{class_name}({attrs})'.format(class_name=type(self).__name__, attrs=attrs)

    def _get_fields(self) -> Iterator[ModelField]:
        for field_name in self.get_fields():
            field_value = getattr(self, field_name)
            yield self._field_class(self, field_name, field_value)

    def get_fields(self):
        raise NotImplementedError()

    def is_empty(self, value: Any) -> bool:
        if value == 0 or value is False:
            return False
        return not bool(value)

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


class DynamicModel(BaseModel):
    def get_fields(self) -> Tuple[str, ...]:
        return tuple(
            name for name, value in inspect.getmembers(self)
            if not(name.startswith('_') or inspect.ismethod(value))
        )


class Model(BaseModel):
    fields = ()
    allow_empty = ()

    def __init__(self, **kwargs):
        for field_name in self.get_fields():
            field_value = kwargs.get(field_name, None)
            setattr(self, field_name, field_value)

    def _get_fields(self) -> Iterator[ModelField]:
        fields = super()._get_fields()
        allow_empty_fields = self.get_allow_empty()
        for field in fields:
            allow_empty = '__all__' in allow_empty_fields or field.name in allow_empty_fields
            field.allow_empty = allow_empty
            yield field

    def get_fields(self) -> Tuple[str]:
        assert self.fields, ('{} should include a fields attribute or override '
                             'the get_fields method'.format(type(self).__name__))

        return self.fields

    def get_allow_empty(self) -> Tuple[str, ...]:
        return self.allow_empty
