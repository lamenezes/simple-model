from typing import Any, Callable, Iterable, Iterator, Tuple, Union

from .base import ModelMetaClass
from .exceptions import ValidationError
from .fields import ModelField
from .utils import getkey


class BaseModel:
    def __init__(self, **kwargs):
        for field_name in self._meta.fields:
            descriptor = self._meta.descriptors[field_name]

            field_value = kwargs.get(field_name)
            default = descriptor.default_value
            factory = default if isinstance(default, Callable) else None
            field_value = factory() if factory and not field_value else kwargs.get(field_name, default)

            if descriptor and descriptor.is_property:
                self.__setattr__(field_name, field_value)
            else:
                object.__setattr__(self, field_name, field_value)

        self.__post_init__(**kwargs)

    def __post_init__(self, **kwargs):
        pass

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Model):
            other_fields = list(other._get_fields())
            get_func = getattr
        else:
            try:
                other = dict(other)
            except (ValueError, TypeError):
                return NotImplemented
            other_fields = other
            get_func = getkey  # type: ignore

        self_fields = list(self._get_fields())
        if len(self_fields) != len(other_fields):
            return False

        for name, _ in self_fields:
            value = getattr(self, name)
            try:
                if value != get_func(other, name):
                    return False
            except AttributeError:
                return False

        return True

    def __repr__(self) -> str:
        attrs = ', '.join(
            '{name}={value!r}'.format(name=name, value=getattr(self, name))
            for name, _ in self._get_fields()
        )
        return '{class_name}({attrs})'.format(class_name=type(self).__name__, attrs=attrs)

    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except AttributeError:
            descriptor = self._meta.descriptors.get(name, False)
            if descriptor and not descriptor.is_property:
                raise  # TODO: find/implement a test case for this statement

    def _get_fields(self) -> Iterator[Tuple[str, ModelField]]:
        return (
            (field_name, self._meta.descriptors[field_name])  # type: ignore
            for field_name in self._meta.fields  # type: ignore
        )

    @classmethod
    def build_many(cls, source: Iterable) -> list:
        if cls.is_empty(source):
            return []

        keys_sets = [d.keys() for d in source]
        for key_set in keys_sets:
            if key_set ^ keys_sets[0]:
                raise ValueError('All elements in source should have the same keys')

        return [cls(**item) for item in source]

    @staticmethod
    def is_empty(value: Any) -> bool:
        if value == 0 or value is False:
            return False
        return not bool(value)

    def convert_fields(self):
        for name, descriptor in self._get_fields():
            if descriptor.is_property:
                continue

            value = object.__getattribute__(self, name)
            new_value = descriptor.convert_to_type(self, value)

            object.__setattr__(self, name, new_value)

    def validate(self, raise_exception: bool = True) -> Union[None, bool]:
        self.convert_fields()

        for name, descriptor in self._get_fields():
            if descriptor.is_property and descriptor._validate is None:
                continue

            value = object.__getattribute__(self, name)
            try:
                value = descriptor.validate(self, value)
            except ValidationError:
                self._is_valid = False
                if raise_exception:
                    raise
                return False
            except Exception:
                self._is_valid = False
                raise

            try:
                object.__setattr__(self, name, value)
            except AttributeError:
                self.__setattr__(name, value)

        self._is_valid = True
        return None if raise_exception else True

    def as_dict(self):
        """
        Returns the model as a dict
        """
        from .converters import to_dict
        return to_dict(self)


class Model(BaseModel, metaclass=ModelMetaClass):
    pass


class LazyModel(BaseModel, metaclass=ModelMetaClass):
    """ LazyModel is a short name for LazyValidationModel. Example:

    class FooModel(LazyModel):
        foo: 'str'


    >>> model = FooModel()
    >>> model.foo
    Traceback (most recent call last):
      ...
    simple_model.exceptions.EmptyField: 'foo' field cannot be empty
    """

    def __getattribute__(self, name):
        meta = object.__getattribute__(self, '_meta')
        if name in meta.fields and not self._is_valid:
            validate = object.__getattribute__(self, 'validate')
            validate()

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        meta = object.__getattribute__(self, '_meta')
        if name in meta.fields and self._is_valid:
            self._is_valid = False

        return super().__setattr__(name, value)

    def as_dict(self):
        """
        Returns the model as a dict
        """
        if not self._is_valid:
            self.validate()

        from .converters import to_dict
        return to_dict(self)
