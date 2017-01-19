import unittest
import textwrap
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


class SimpleTest(TestCase):
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

        

if __name__ == '__main__':
    unittest.main()

