#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

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
   
You can easily extend the taurus options with your application specific options.
Supose you want to add an option like ``--model=<model name>``::
    
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

__all__ = ["get_taurus_parser", "init_taurus_args", "parse_taurus_args"]

__docformat__ = "restructuredtext"

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
                         "error, warning/warn, info, debug, trace"
        help_tangohost = "Tango host name"
        help_tauruspolling = "taurus global polling period in milliseconds"
        help_taurusserial= "taurus serialization mode. Allowed values are (case insensitive): "\
                           "serial, concurrent (default)"
        group.add_option("--taurus-log-level", dest="taurus_log_level", metavar="LEVEL",
                         help=help_tauruslog, type="str", default="info")
        group.add_option("--taurus-polling-period", dest="taurus_polling_period", metavar="MILLISEC",
                         help=help_tauruspolling, type="int", default=None)
        group.add_option("--taurus-serialization-mode", dest="taurus_serialization_mode", metavar="SERIAL",
                         help=help_taurusserial, type="str", default="Concurrent")
        group.add_option("--tango-host", dest="tango_host", metavar="TANGO_HOST",
                         help=help_tangohost, type="str", default=None)
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
    parser, options, args = parse_taurus_args(parser=parser, args=args, values=values)
    
    # initialize taurus log level
    log_level_str = options.taurus_log_level.capitalize()
    if hasattr(taurus, log_level_str):
        log_level = getattr(taurus, log_level_str)
        taurus.setLogLevel(log_level)
        
    # initialize tango host
    if options.tango_host is not None:
        tango_factory = taurus.Factory("tango")
        tango_factory.set_default_tango_host(options.tango_host)

    # initialize taurus polling period
    if options.taurus_polling_period is not None:
        taurus.Manager().changeDefaultPollingPeriod(options.taurus_polling_period)

    # initialize taurus serialization mode
    if options.taurus_serialization_mode is not None:
        import taurus.core
        m = options.taurus_serialization_mode.capitalize()
        if hasattr(taurus.core.TaurusSerializationMode, m):
            m = getattr(taurus.core.TaurusSerializationMode, m)
            taurus.Manager().setSerializationMode(m)
        
    return parser, options, args
    