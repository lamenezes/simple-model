# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:


class ValidationError(Exception):
    pass


class EmptyField(ValidationError):
    def __init__(self, field_name):
        self.field_name = field_name

    def __str__(self):
        return '{} field cannot be empty'.format(self.field_name)
