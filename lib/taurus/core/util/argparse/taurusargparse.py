#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

# TODO: This module should be updated to use argparse instead of optparse

"""Helper command line parser for taurus based on :mod:`optparse`.
Suppose you have an application file::

    import sys
    from PyQt4 import Qt


    class GUI(Qt.QMainWindow):
        pass


    def main():
        import taurus.core.util.argparse as argparse

        parser, options, args = argparse.init_taurus_args()

        app = Qt.QApplication(sys.argv)
        w = GUI()
        w.show()
        sys.exit(app.exec_())

    if __name__ == "__main__":
        main()

The call to :func:`taurus.core.util.argparse.init_taurus_args` will initialize
taurus environment based on the command line options given by the user.
Currently, the known options are:

    #. ``--help`` prints the total number of available options
    #. ``--taurus-log-level`` sets the taurus log level
    #. ``--tango-host`` sets the default tango host
    #. ``--taurus-polling-period`` sets the default taurus global polling period (milliseconds)
    #. ``--taurus-serialization-mode`` sets the default taurus serialization mode
    #. ``--remote-console-port`` enables remote debugging using the given port

You can easily extend the taurus options with your application specific options.
Suppose you want to add an option like ``--model=<model name>``::

    def main():
        import taurus.core.util.argparse as argparse
        parser = argparse.get_taurus_parser(parser=parser)
        parser.set_usage("%prog [options] <special item>")
        parser.set_description("my own GUI application")
        parser.add_option("--model")

        parser, options, args = argparse.init_taurus_args(parser=parser)

        app = Qt.QApplication(sys.argv)
        w = GUI()
        w.show()
        sys.exit(app.exec_())
"""

__all__ = ["get_taurus_parser", "init_taurus_args", "parse_taurus_args",
           "split_taurus_args"]

__docformat__ = "restructuredtext"


from taurus.core.util import log as __log

__log.deprecated(dep='taurus.core.util.argparse', rel='4.5.4',
                 alt='argparse or (better) click')


def get_taurus_parser(parser=None):
    """ Returns a :class:`optparse.OptionParser` initialized with a
    :class:`optparse.OptionGroup` containning some taurus options.
    If a parser is given as parameter then it uses this parser instead of
    creating a new one.

    :param parser: an option parser or None (default) to create a new parser
    :type parser: :class:`optparse.OptionParser`
    :return: an option parser or the given parser if it is not None
    :rtype: :class:`optparse.OptionParser`"""
    import optparse
    if parser is None:
        parser = optparse.OptionParser()

    g = parser.get_option_group('--taurus-log-level')
    if g is None:
        group = optparse.OptionGroup(parser, "Taurus Options",
                                     "Basic options present in any taurus application")

        help_tauruslog = "taurus log level. Allowed values are (case insensitive): critical, "\
                         "error, warning, info, debug, trace"
        help_tangohost = "Tango host name (either HOST:PORT or a Taurus URI, e.g. tango://foo:1234)"
        help_tauruspolling = "taurus global polling period in milliseconds"
        help_taurusserial = "taurus serialization mode. Allowed values are (case insensitive): "\
            "serial, concurrent (default)"
        help_rcport = "enables remote debugging using the given port"
        help_formatter = "Override the default formatter"
        group.add_option("--taurus-log-level", dest="taurus_log_level", metavar="LEVEL",
                         help=help_tauruslog, type="str", default="info")
        group.add_option("--taurus-polling-period", dest="taurus_polling_period", metavar="MILLISEC",
                         help=help_tauruspolling, type="int", default=None)
        group.add_option("--taurus-serialization-mode", dest="taurus_serialization_mode", metavar="SERIAL",
                         help=help_taurusserial, type="str", default="Concurrent")
        group.add_option("--tango-host", dest="tango_host", metavar="TANGO_HOST",
                         help=help_tangohost, type="str", default=None)
        group.add_option("--remote-console-port", dest="remote_console_port", metavar="PORT",
                         help=help_rcport, type="int", default=None)
        group.add_option("--default-formatter", dest="default_formatter",
                         metavar="FORMATTER", help=help_formatter, type="str",
                         default=None)
        parser.add_option_group(group)
    return parser


def parse_taurus_args(parser=None, args=None, values=None):
    """Parses the command line. If parser is not given, then a new parser
    is created. In any case, the parser is initialized using the
    :func:`taurus.core.util.argparse.get_taurus_parser`.
    args and values are the optional parameters that will be given when
    executing :meth:`optparse.OptionParser.parse_args`.

    :param parser: an option parser or None (default) to create a new parser
    :type parser: :class:`optparse.OptionParser`
    :param args: the list of arguments to process (default is None meaning: sys.argv[1:])
    :type args: seq<str>
    :param values: a :class:`optparse.Values` object to store option arguments in
                  (default is None meaning: a new instance of Values) - if you give an
                  existing object, the option defaults will not be initialized on it
    :return: a tuple of three elements: parser, options, args
    :rtype: :class:`optparse.OptionParser`, :class:`optparse.Values`, seq<str> """
    parser = get_taurus_parser(parser=parser)
    options, args = parser.parse_args(args=args, values=values)
    return parser, options, args


def init_taurus_args(parser=None, args=None, values=None):
    """Parses the command line using :func:`taurus.core.util.argparse.parse_taurus_args`.

    After the command line is parsed, actions are taken on each recognized parameter.
    For example, the taurus log level and the default tango host are set accordingly.

    :param parser: an option parser or None (default) to create a new parser
    :type parser: :class:`optparse.OptionParser`
    :param args: the list of arguments to process (default is None meaning: sys.argv[1:])
    :type args: seq<str>
    :param values: a :class:`optparse.Values` object to store option arguments in
                  (default is None meaning: a new instance of Values) - if you give an
                  existing object, the option defaults will not be initialized on it
    :return: a tuple of three elements: parser, options, args
    :rtype: :class:`optparse.OptionParser`, :class:`optparse.Values`, seq<str> """
    import taurus
    parser, options, args = parse_taurus_args(
        parser=parser, args=args, values=values)

    # initialize taurus log level
    log_level_str = options.taurus_log_level.capitalize()
    if hasattr(taurus, log_level_str):
        log_level = getattr(taurus, log_level_str)
        taurus.setLogLevel(log_level)

    # initialize tango host
    if options.tango_host is not None:
        tango_factory = taurus.Factory("tango")
        tango_host = options.tango_host
        tango_factory.set_default_tango_host(tango_host)

    # initialize taurus polling period
    if options.taurus_polling_period is not None:
        taurus.Manager().changeDefaultPollingPeriod(options.taurus_polling_period)

    # initialize taurus serialization mode
    if options.taurus_serialization_mode is not None:
        import taurus.core.taurusbasetypes
        SerMode = taurus.core.taurusbasetypes.TaurusSerializationMode
        m = options.taurus_serialization_mode.capitalize()
        if hasattr(SerMode, m):
            m = getattr(SerMode, m)
            taurus.Manager().setSerializationMode(m)

    # initialize remote console port
    if options.remote_console_port is not None:
        try:
            import rfoo.utils.rconsole
            rfoo.utils.rconsole.spawn_server(port=options.remote_console_port)
            taurus.info("rconsole started. You can connect to it by typing: rconsole -p %d",
                        options.remote_console_port)
        except Exception as e:
            taurus.warning("Cannot spawn debugger. Reason: %s", e)

    # initialize default formatter
    if options.default_formatter is not None:
        from taurus import tauruscustomsettings
        setattr(tauruscustomsettings, 'DEFAULT_FORMATTER',
                options.default_formatter)

    return parser, options, args


def split_taurus_args(parser, args=None):
    """Splits arguments into valid parser arguments and non valid parser
    arguments.

    :param parser: an option parser
    :type parser: :class:`optparse.OptionParser`
    :param args: the list of arguments to process
                 (default is None meaning: sys.argv)
    :type args: seq<str>
    :return: a tuple of two elements: parser args, non parser args
    :rtype: seq<seq<str>, seq<str>>"""

    if args is None:
        import sys
        args = sys.argv

    taurus_args, non_taurus_args = [args[0]], [args[0]]
    for arg in args[1:]:
        arg_name = arg.split("=", 1)[0]
        if parser.has_option(arg_name):
            taurus_args.append(arg)
        else:
            non_taurus_args.append(arg)

    return taurus_args, non_taurus_args
