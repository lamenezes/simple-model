# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

from typing import List

from .exceptions import EmptyField, ValidationError


class ModelField:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def serialize(self):
        serialized = None
        if isinstance(self.value, Model):
            serialized = self.value.serialize()
        elif isinstance(self.value, (List, tuple)):
            serialized = [field.serialize() for field in self.value]
        return serialized or self.value


class Model:
    fields = ()
    allow_empty = ()

    def __init__(self, **kwargs):
        for field_name in self.fields:
            field_value = kwargs.get(field_name, None)
            setattr(self, field_name, field_value)

    def _get_fields(self):
        return (ModelField(field_name, getattr(self, field_name))
                for field_name in self.fields)

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
