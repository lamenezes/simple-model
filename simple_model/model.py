# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

from .exceptions import EmptyField, ValidationError
from .field import ModelField


class Model:
    fields = ()
    allow_empty = ()

    def __init__(self, **kwargs):
        for field_name in self.fields:
            field_value = kwargs.get(field_name, None)
            setattr(self, field_name, field_value)

    def _get_fields(self):
        for field_name in self.fields:
            allow_empty = '__all__' in self.allow_empty or field_name in self.allow_empty
            field_value = getattr(self, field_name)
            yield ModelField(self, field_name, field_value, allow_empty)

    def is_empty(self, value):
        return bool(value)

    def validate(self, raise_exception=True):
        for field in self._get_fields():
            allow_empty = '__all__' in self.allow_empty or field.name in self.allow_empty
            if not allow_empty and not self.is_empty(field.value):
                if raise_exception:
                    raise EmptyField(field.name)
                return False

            try:
                validate_field = getattr(self, 'validate_{}'.format(field.name))
            except AttributeError:
                continue

            try:
                validate_field(field.value)
            except ValidationError:
                if raise_exception:
                    raise
                return False

        return True

    def serialize(self, exclude_fields=None):
        self.validate()

        data = {}
        for field in self._get_fields():
            if exclude_fields and field.name in exclude_fields:
                continue

            data[field.name] = field.serialize()

        return data
