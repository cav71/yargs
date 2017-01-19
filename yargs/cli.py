import sys
import os
import os.path
import re
import ast
import imp
import types
import inspect
import textwrap
import argparse
import itertools
import logging

try:
    basestring
    PY2 = True
except NameError:
    basestring = str
    PY2 = False


logger = logging.getLogger(__name__)


def npath(*args):
    x = os.path.join(*args)
    x = os.path.expanduser(x)
    x = os.path.abspath(x)
    x = os.path.normpath(x)
    return x


def splitdoc(txt):
    if not (txt or '').strip():
        return ('', '')
    descr, _, epi = txt.partition('\n')
    epi = textwrap.dedent(epi)
    return descr, epi.strip()


class ArgumentParserBase(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        if 'doc' in kwargs:
            description, epilog = splitdoc(kwargs['doc'])
            kwargs.pop('doc')
            kwargs['description'] = kwargs.get('description', description)
            kwargs['epilog'] = kwargs.get('epilog', epilog)

        class MyFormatter(argparse.ArgumentDefaultsHelpFormatter,
                            argparse.RawDescriptionHelpFormatter):
            pass
        kwargs['formatter_class'] = kwargs.get('formatter_class', MyFormatter)
        version = None
        if 'version' in kwargs:
            version = kwargs['version']
            kwargs.pop('version')
        super(ArgumentParserBase, self).__init__(**kwargs)

        if version:
            self.add_argument('--version', action='version', version=version)

    def parse_args(self, args=None):
        options = super(ArgumentParserBase, self).parse_args(args)
        options.error = self.error
        return options
