##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Environment related macros"""

__all__ = ["dumpenv", "load_env", "lsenv", "senv", "usenv"]

__docformat__ = 'restructuredtext'

from taurus.console.list import List
from sardana.macroserver.macro import *

################################################################################
#
# Environment related macros
#
################################################################################

from lxml import etree

def reprValue(v, max=74):
    # cut long strings
    v = str(v)
    if len(v) > max:
        v = v[:max] + ' [...]'
    return v


class dumpenv(Macro):
    """Dumps the complete environment"""
    
    def run(self):
        env = self.getGlobalEnv()
        out = List(['Name','Value','Type'])
        for k,v in env.iteritems():
            str_v = reprValue(v)
            type_v = type(v).__name__
            out.appendRow([str(k), str_v, type_v])

        for line in out.genOutput():
            self.output(line)


class lsvo(Macro):
    """Lists the view options"""
    def run(self):
        vo = self.getViewOptions()
        out = List(['View option', 'Value'])
        for key, value in vo.items():
            out.appendRow([key, str(value)])

        for line in out.genOutput():
            self.output(line)


class setvo(Macro):
    """Sets the given view option to the given value"""

    param_def = [['name', Type.String, None, 'View option name'],
                 ['value', Type.String, None, 'View option value']]

    def run(self, name, value):
        try:
            value = eval(value)
        except:
            pass
        self.setViewOption(name, value)


class usetvo(Macro):
    """Resets the value of the given view option"""
    
    param_def = [['name', Type.String, None, 'View option name']]

    def run(self, name):
        self.resetViewOption(name)

            
class lsenv(Macro):
    """Lists the environment"""
    
    param_def = [
        ['macro_list',
         ParamRepeat(['macro', Type.MacroClass, None, 'macro name'], min=0),
         None, 'List of macros to show environment'],
    ]
    
    def prepare(self, *macro_list, **opts):
        self.table_opts = opts
        
    def run(self, *macro_list):
        # list the environment for the current door
        if len(macro_list) == 0:
            # list All the environment for the current door
            out = List(['Name', 'Value', 'Type'])
            env = self.getAllDoorEnv()
            for k,v in env.iteritems():
                str_val = reprValue(v)
                type_name = type(v).__name__
                out.appendRow([str(k), str_val, type_name])
        else:
            # list the environment for the current door for the given macros
            out = List(['Macro', 'Name', 'Value', 'Type'])
            for macro in macro_list:
                env = self.getEnv(key=None, macro_name=macro.name)
                for k, v in env.iteritems():
                    type_name = type(v).__name__
                    out.appendRow([ macro.name, k, self.reprValue(v), type_name ])

        for line in out.genOutput():
            self.output(line)

    def reprValue(self, v, max=54):
        # cut long strings
        v = str(v)
        if len(v) > max: v = '%s [...]' % v[:max]
        return v

class senv(Macro):
    """Sets the given environment variable to the given value"""

    param_def = [['name', Type.Env, None,
                  'Environment variable name. Can be one of the following:\n' \
                  ' - <name> - global variable\n' \
                  ' - <full door name>.<name> - variable value for a specific door\n' \
                  ' - <macro name>.<name> - variable value for a specific macro\n' \
                  ' - <full door name>.<macro name>.<name> - variable value for a specific macro running on a specific door'],
                 ['value_list',
                  ParamRepeat(['value', Type.String, None, 'environment value item'], min=1),
                  None, 'value(s). one item will eval to a single element. More than one item will eval to a tuple of elements'],
                ]

    def run(self, env, *value):
        if len(value) == 1: 
            value = value[0]
        else:
            value = '(%s)' % ', '.join(value)
        k,v = self.setEnv(env, value)
        line = '%s = %s' % (k, str(v))
        self.output(line)

class usenv(Macro):
    """Unsets the given environment variable"""
    param_def = [
        ['environment_list',
         ParamRepeat(['env', Type.Env, None, 'Environment variable name'], min=1),
         None, 'List of environment items to be removed'],
    ]    
    
    def run(self, *env):
        self.unsetEnv(env)
        self.output("Success!")
        
class load_env(Macro):
    """ Read environment variables from config_env.xml file"""
    
    def run(self):
        doc = etree.parse("config_env.xml")       
        root = doc.getroot()
        for element in root:
            if element.find("./name").text == "auto_filter":
                self.output("Loading auto_filter variables:")
                filter_max_elem = element.find(".//FilterMax")
                if filter_max_elem is not None:
                    filter_max = filter_max_elem.text
                    self.setEnv("FilterMax", filter_max)
                    self.output("FilterMax loaded")
                else:
                    self.output("FilterMax not found")
                filter_min_elem = element.find(".//FilterMin")
                if filter_min_elem is not None:
                    filter_min = filter_max_elem.text
                    self.setEnv("FilterMin", filter_min)
                    self.output("FilterMin loaded")
                else:
                    self.output("FilterMin not found")
                filter_delta_elem = element.find(".//FilterDelta")
                if filter_delta_elem is not None:
                    filter_delta = filter_delta_elem.text
                    self.setEnv("FilterDelta", filter_delta)
                    self.output("FilterDelta loaded")
                else:
                    self.output("FilterDelta not found")
                filter_signal_elem = element.find(".//FilterSignal")
                if filter_signal_elem is not None:
                    filter_signal = filter_signal_elem.text
                    self.setEnv("FilterSignal", filter_signal)
                    self.output("FilterSignal loaded")
                else:
                    self.output("FilterSignal not found")
                filter_absorber_elem = element.find(".//FilterAbsorber")
                if filter_absorber_elem is not None:
                    filter_absorber = filter_absorber_elem.text
                    self.setEnv("FilterAbsorber", filter_absorber)
                    self.output("FilterAbsorber loaded")
                else:
                    self.output("FilterAbsorber not found")
                auto_filter_elem = element.find(".//AutoFilter")
                if auto_filter_elem is not None:
                    auto_filter = auto_filter_elem.text
                    self.setEnv("AutoFilter", auto_filter)
                    self.output("AutoFilter loaded")
                else:
                    self.output("AutoFilter not found")
            if element.find("./name").text == "auto_beamshutter":
                self.output("Loading auto_beamshutter variables:")
                auto_beamshutter_elem = element.find(".//AutoBeamshutter")
                if auto_beamshutter_elem is not None:
                    auto_beamshutter = auto_beamshutter_elem.text
                    self.setEnv("AutoBeamshutter", auto_beamshutter)
                    self.output("AutoBeamshutter loaded")
                else:
                    self.output("AutoBeamshutter not found")
                beamshutter_limit_elem = element.find(".//BeamshutterLimit")
                if beamshutter_limit_elem is not None:
                    beamshutter_limit = beamshutter_limit_elem.text
                    self.setEnv("BeamshutterLimit", beamshutter_limit)
                    self.output("BeamshutterLimit loaded")
                else:
                    self.output("BeamshutterLimit not found")
                beamshutter_signal_elem = element.find(".//BeamshutterSignal")
                if beamshutter_signal_elem is not None:
                    beamshutter_signal = beamshutter_signal_elem.text
                    self.setEnv("BeamshutterSignal", beamshutter_signal)
                    self.output("BeamshutterSignal loaded")
                else:
                    self.output("BeamshutterSignal not found")
                beamshutter_time_elem = element.find(".//BeamshutterTime")
                if beamshutter_time_elem is not None:
                    beamshutter_time = beamshutter_time_elem.text
                    self.setEnv("BeamshutterTime", beamshutter_time)
                    self.output("BeamshutterTime loaded")
                else:
                    self.output("BeamshutterTime not found")
            if element.find("./name").text == "exafs":
                self.output("Loading exafs variables:")
                exafs_int_times_elem = element.find(".//ExafsIntTimes")
                if exafs_int_times_elem is not None:
                    exafs_int_times = exafs_int_times_elem.text
                    self.setEnv("ExafsIntTimes", exafs_int_times)
                    self.output("ExafsIntTimes loaded")
                else:
                    self.output("ExafsIntTimes not found")
                exafs_nb_intervals_elem = element.find(".//ExafsNbIntervals")
                if exafs_nb_intervals_elem is not None:
                    exafs_nb_intervals = exafs_nb_intervals_elem.text
                    self.setEnv("ExafsNbIntervals", exafs_nb_intervals)
                    self.output("ExafsNbIntervals loaded")
                else:
                    self.output("ExafsNbIntervals not found")
                exafs_regions_elem = element.find(".//ExafsRegions")
                if exafs_regions_elem is not None:
                    exafs_regions = exafs_regions_elem.text
                    self.setEnv("ExafsRegions", exafs_regions)
                    self.output("ExafsRegions loaded")
                else:
                    self.output("ExafsRegions not found")  
        misc_tree = root.find("./miscellaneous")
        if misc_tree is not None:
            for parameter in misc_tree:
                if parameter.tag != "name":
                    self.setEnv(parameter.tag, parameter.text) 
            
