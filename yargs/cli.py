import sys
import os
import os.path
import re
import ast
import imp
import types
import collections
import inspect
import textwrap
import argparse
import itertools
import logging
import abc

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


# from https://gist.githubusercontent.com/sampsyo/471779/raw/0637678058034d5e7e6f5a3baf6c3ca58537e67a/aliases.py
class AliasedSubParsersAction(argparse._SubParsersAction):
    class _AliasedPseudoAction(argparse.Action):
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += ' (%s)' % ','.join(aliases)
            sup = super(AliasedSubParsersAction._AliasedPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help) 

    def add_parser(self, name, **kwargs):
        if 'aliases' in kwargs:
            aliases = kwargs['aliases']
            del kwargs['aliases']
        else:
            aliases = []

        parser = super(AliasedSubParsersAction, self).add_parser(name, **kwargs)

        # Make the aliases work.
        for alias in aliases:
            self._name_parser_map[alias] = parser
        # Make the help text reflect them, first removing old help entry.
        if 'help' in kwargs:
            help = kwargs.pop('help')
            self._choices_actions.pop()
            pseudo_action = self._AliasedPseudoAction(name, aliases, help)
            self._choices_actions.append(pseudo_action)

        return parser


class ArgumentParserBase(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        doc = __doc__
        if 'doc' in kwargs:
            doc = kwargs['doc']
            kwargs.pop('doc')
        description, epilog = splitdoc(doc)
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

        # support for subcommand aliases
        self.register('action', 'parsers', AliasedSubParsersAction)

    def parse_args(self, args=None, namespace=None):
        options = super(ArgumentParserBase, self).parse_args(args, namespace)
        options.error = self.error
        return options

class _CommandBase(object):
    def parse_args(self, args=None, _get=None):
        parser = ArgumentParserBase(doc=self.__doc__)
        self.add_arguments(parser)
        if _get == 'parser':
            return parser
        options = parser.parse_args(args)
        self.process_options(options)
        return options
        
    def main(self, args=None):
        options = self.parse_args(args)
        return self(options)

    def __init__(self, name=None, aliases=None, helpmsg=None):
        if name is not None:
            self.name = name
        if aliases is not None:
            self.aliases = aliases
        if helpmsg is not None:
            self.helpmsg = helpmsg


class CommandBase(_CommandBase):
    name = 'abc'        # a command name
    aliases = []        # aliases for the command
    helpmsg = None      # short help to display

    def add_arguments(self, parser):
        'adds argument to the parser'
        pass
    
    def process_options(self, option):
        'process options oject before running the command'
        pass


class ArgumentParserWithCommand(ArgumentParserBase):
    def __init__(self, **kwargs):
        commands = []
        if 'commands' in kwargs:
            commands = kwargs['commands']
            kwargs.pop('commands')
            commands = commands if isinstance(commands, (list, tuple)) else [ commands, ]
            commands = [ c if isinstance(c, CommandBase) else c() for c in commands ]
        self._my_commands = commands

        if len(commands) == 0:
            super(ArgumentParserWithCommand, self).__init__(**kwargs)
        elif len(commands) == 1:
            command = commands[0]
            kwargs['doc'] = kwargs.get('doc', command.__doc__)
            super(ArgumentParserWithCommand, self).__init__(**kwargs)
            command.add_arguments(self)
            self.set_defaults(kommand=command)
        else:
            super(ArgumentParserWithCommand, self).__init__(**kwargs)
            subparsers = self.add_subparsers(help='commands help')
            for index, command in enumerate(commands):
                name = command.name
                helpmsg = getattr(command, 'helpmsg', '') or 'command-{0}'.format(index)
                aliases = getattr(command, 'aliases', []) or []
                p = subparsers.add_parser(name, help=helpmsg, doc=command.__doc__, aliases=aliases)
                command.add_arguments(p)
                p.set_defaults(kommand=command)

    def parse_args(self, args=None):

        n = len(self._my_commands)
        if n in [ 0, 1 ]:
            options = super(ArgumentParserWithCommand, self).parse_args(args)
            for command in self._my_commands:
                command.process_options(options)
            return options

        print('BEGIN')
        class MyNamespace(argparse.Namespace):
            def __setattr__(self, name, value):
                self._innercounter = getattr(self, '_innercounter', collections.defaultdict(list))
                
                print('Setting', name, value)
                return super(MyNamespace, self).__setattr__(name, value)

        known = super(ArgumentParserWithCommand, self).parse_known_args(args, MyNamespace())
        return known
        #if len(self._my_commands) > 1:
        #    known = super(ArgumentParserWithCommand, self).parse_known_args(args, MyNamespace())

        options = super(ArgumentParserWithCommand, self).parse_args(args, namespace=MyNamespace())
        #if known:
        #    for a in dir(known):
        #        if a.startswith('_') or a == 'kommand':
        #            continue
        #        setattr(options, a, getattr(known, a))
        

        if hasattr(options, 'kommand') and callable(options.kommand):
            options.kommand.process_options(options)
        print('END')
                
        return options
