"""
    create_python_project.scripts.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Base class for script manipulation

    :copyright: Copyright 2017 by Nicolas Maurice, see AUTHORS.rst for more details.
    :license: BSD, see :ref:`license` for more details.
"""

from .content import ScriptContent
from .io import IOMeta, InputDescriptor, OutputDescriptor


class BaseParser:
    """Base parser for scripts"""

    content_class = ScriptContent

    def setup_parse(self, input_string):
        self.input_string = input_string

    def parse(self, input_string, content):
        self.setup_parse(input_string)
        content.set_lines(self.input_string.split('\n'))


class BaseReader:
    """Base reader for scripts"""

    content_class = ScriptContent

    def __init__(self, parser=None):
        self.parser = parser

        self.input = None
        self.content = None

    def read(self, source, parser):
        self.init_content()
        self.source = source
        self.parser = parser or self.parser
        self.input = self.source.read()
        self.parse()
        return self.content

    def parse(self):
        self.parser.parse(self.input, self.content)

    def init_content(self):
        self.content = self.content_class()


class BaseWriter:
    """Base writer for scripts"""

    def write(self, content, destination):
        self.content = content
        self.destination = destination
        self.translate(content)
        output = self.destination.write(self.output)
        return output

    def translate(self, content):
        self.output = content.output()


class BaseScript(metaclass=IOMeta):
    """Base class for manipulating scripts"""

    supported_format = ('*',)

    source = InputDescriptor()
    destination = OutputDescriptor()

    reader_class = BaseReader
    writer_class = BaseWriter
    parser_class = BaseParser

    def __init__(self, source=None, destination=None,
                 reader=None, parser=None, writer=None):
        self.source = source
        self.destination = destination

        self.reader = reader or self.reader_class()
        self.parser = parser or self.parser_class()
        self.writer = writer or self.writer_class()

        self.content = None

    def read(self):
        if self.content is None:
            self.content = self.reader.read(self.source, self.parser)

    def apply_transform(self, *args, **kwargs):
        self.content.transform(*args, **kwargs)

    def write(self):
        return self.writer.write(self.content, self.destination)

    def publish(self, *args, **kwargs):
        self.read()
        self.apply_transform(*args, **kwargs)
        output = self.write()
        return output

    def set_source(self, source=None, source_path=None):
        self.source = source or source_path
        self.reset()

    def reset(self, reader=None, parser=None, writer=None):
        self.content = None

        self.reader = reader or self.reader_class()
        self.parser = parser or self.parser_class()
        self.writer = writer or self.writer_class()

    def set_destination(self, destination=None, destination_path=None):
        self.destination = destination or destination_path
