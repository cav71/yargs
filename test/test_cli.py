import unittest
import textwrap
import yargs
import yargs.cli as cli

try:
    basestring
    PY2 = True
except NameError:
    basestring = str
    PY2 = False


class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.maxDiff = None
        self.addTypeEqualityFunc(basestring, self.assertMultiLineEqual)


class TestArgumentParserBase(TestCase):
    def test_base(self):
        parser = cli.ArgumentParserBase()       
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h]

optional arguments:
  -h, --help  show this help message and exit
'''))

    def test_doc_arg(self):
        doc = '''A summary for the script

This is a rather large text
explaining what the code does
   and it keept in this format
'''
        parser = cli.ArgumentParserBase(doc=doc)       
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h]

A summary for the script

optional arguments:
  -h, --help  show this help message and exit

This is a rather large text
explaining what the code does
   and it keept in this format
'''))

        parser = cli.ArgumentParserBase(doc=doc, description='Hello world')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h]

Hello world

optional arguments:
  -h, --help  show this help message and exit

This is a rather large text
explaining what the code does
   and it keept in this format
'''))
        parser = cli.ArgumentParserBase(doc=doc, description='Hello world', epilog='blah')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h]

Hello world

optional arguments:
  -h, --help  show this help message and exit

blah
'''))
        


class TestCommandBaseStandAlone(TestCase):
    class MyCommandBase(cli.CommandBase):
        def add_arguments(self, parser):
            parser.add_argument('-c', type=int, help='an integer value')
        
        def process_options(self, options):
            options.c = None if options.c is None else options.c * 2

        
    class MyCommand(MyCommandBase):
        '''a simple stand alone command
        
        This is a simple stand alone command.
        '''
        pass

            
    def test_help(self):
        parser = self.MyCommand('blah').parse_args(_get='parser')

        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h] [-c C]

a simple stand alone command

optional arguments:
  -h, --help  show this help message and exit
  -c C        an integer value (default: None)

This is a simple stand alone command.
'''))

    def test_parse(self):
        command = self.MyCommand('blah')
        options = command.parse_args([])
        self.assertEqual(options.c, None)
        options = command.parse_args([ '-c', '1'])
        self.assertEqual(options.c, 2)


class TestArgumentParserWithCommands1CommandCase(unittest.TestCase):
    def test_argparse_no_commands(self):
        doc = '''a simple stand alone command
            
        This is a simple stand alone command.
        '''
        parser = cli.ArgumentParserWithCommand(doc=doc)
        parser.add_argument('-c', type=int, help='an integer value')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h] [-c C]

a simple stand alone command

optional arguments:
  -h, --help  show this help message and exit
  -c C        an integer value (default: None)

This is a simple stand alone command.
'''))


    class MyCommandBase(cli.CommandBase):
        '''a simple stand alone command
            
        This is a simple stand alone command.
        '''

    def test_single_commandbase_help(self):
        parser = cli.ArgumentParserWithCommand(commands=self.MyCommandBase('one'))
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h]

a simple stand alone command

optional arguments:
  -h, --help  show this help message and exit

This is a simple stand alone command.
'''))


    class MyCommand(MyCommandBase):
        '''a simple stand alone command
            
        This is a simple stand alone command.
        '''
        def add_arguments(self, parser):
            parser.add_argument('-c', type=int, help='an integer value')
        
        def process_options(self, options):
            options.c = None if options.c is None else options.c * 2

        def __call__(self, options):
            return options.c * 2 if options.c else options.c

    def test_single_command_help(self):
        parser = cli.ArgumentParserWithCommand(commands=self.MyCommand('one'))

        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h] [-c C]

a simple stand alone command

optional arguments:
  -h, --help  show this help message and exit
  -c C        an integer value (default: None)

This is a simple stand alone command.
'''))

    def test_single_command_parse(self):
        parser = cli.ArgumentParserWithCommand(commands=[self.MyCommand('one')])
               
        options = parser.parse_args([ ])
        self.assertEqual(options.c, None)

        options = parser.parse_args([ '-c', '0', ])
        self.assertEqual(options.c, 0)

        options = parser.parse_args([ '-c', '12', ])
        self.assertEqual(options.c, 24)


class TestArgumentParserWithCommandsNCommandCase(unittest.TestCase):
    class MyCommand(cli.CommandBase):
        '''a simple stand alone command
            
        This is a simple stand alone command.
        '''
        def __init__(self, factor, *args, **kwargs):
            self.factor = factor
            super(TestArgumentParserWithCommandsNCommandCase.MyCommand, self).__init__(*args, **kwargs)

        def add_arguments(self, parser):
            parser.add_argument('-c', type=int, help='an integer value')
        
        def process_options(self, options):
            options.c = None if options.c is None else options.c * self.factor

        def __call__(self, options):
            return options.c * 2 if options.c else options.c

    def test_multi_commandbase_help(self):
        commands = [ self.MyCommand(2, 'one'), self.MyCommand(3, 'two'), self.MyCommand(4, 'three')]
        parser = cli.ArgumentParserWithCommand(commands=commands)
        parser.add_argument('-c', type=int, help='an integer value')
        self.assertEqual(parser.format_help(), textwrap.dedent('''\
usage: test_cli.py [-h] [-c C] {one,two,three} ...

positional arguments:
  {one,two,three}  commands help
    one            command-0
    two            command-1
    three          command-2

optional arguments:
  -h, --help       show this help message and exit
  -c C             an integer value (default: None)
'''))

    def test_multi_commandbase_parse(self):
        commands = [ self.MyCommand(1, 'one'), self.MyCommand(2, 'two'), self.MyCommand(3, 'three')]
        parser = cli.ArgumentParserWithCommand(commands=commands)
        parser.add_argument('-c', type=int, help='an integer value')

        options = parser.parse_args([])
        self.assertEqual(options.c, None)

        #options = parser.parse_args([ 'one', '-c', '7', ])
        #self.assertEqual(options.c, 7)

        #import pdb; pdb.set_trace()
        print()
        options = parser.parse_args([ 'one', ])
        print()
        options = parser.parse_args([ '-c', '7', 'one', ])
        options = parser.parse_args([ 'one', '-c', '7' ])
        print()
        options = parser.parse_args([ '-c', '7', 'one', '-c', '7' ])
        print()
        #self.assertEqual(options.c, 7)
        
if __name__ == '__main__':
    unittest.main()

