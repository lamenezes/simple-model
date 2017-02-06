# Copyright (c) 2017 Luiz Menezes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

from setuptools import setup, find_packages

setup(
    name='pysimplemodel',
    version='0.1.0',
    description='Simple Models for Python',
    url='https://github.com/lamenezes/simple-model',
    author='Luiz Menezes',
    author_email='luiz.menezesf@gmail.com',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
