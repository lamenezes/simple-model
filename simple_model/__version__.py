import re
from pathlib import Path

here = Path(__file__).absolute().parent

with open(here.parent / 'CHANGES.rst') as f:
    changes = '\n' + f.read()
    version_match = re.search(r'\n(\d+.\d+.\d+) /', changes)
    version = version_match.groups()[0]

__author__ = 'Luiz Menezes'
__title__ = 'simple-model'
__version__ = version
