#!/usr/bin/env python

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

"""This module is part of the Python Pool library. It defines the base classes
for"""

__all__ = [ "PoolMeasurementGroup" ]

__docformat__ = 'restructuredtext'

from taurus.core.taurusvalidator import AttributeNameValidator
from taurus.core.tango.sardana import PlotType, Normalization

from sardana import State,ElementType, \
    TYPE_EXP_CHANNEL_ELEMENTS, TYPE_TIMERABLE_ELEMENTS
from sardana.sardanaevent import EventType

from .pooldefs import AcqMode, AcqTriggerType
from .poolgroupelement import PoolGroupElement
from .poolacquisition import PoolAcquisition
from .poolexternal import PoolExternalObject

#----------------------------------------------
# Measurement Group Configuration information
#----------------------------------------------
# dict <str, obj> with (at least) keys:
#    - 'timer' : the timer channel name / timer channel id
#    - 'monitor' : the monitor channel name / monitor channel id
#    - 'controllers' : dict<Controller, dict> where:
#        - key: ctrl
#        - value: dict<str, dict> with (at least) keys:
#            - 'units': dict<str, dict> with (at least) keys:
#                - 'id' : the unit ID inside the controller
#                - 'timer' : the timer channel name / timer channel id
#                - 'monitor' : the monitor channel name / monitor channel id
#                - 'trigger_type' : 'Gate'/'Software'
#                - 'channels' where value is a dict<str, obj> with (at least) keys:
#                    - 'id' : the channel name ( channel id )
#                    optional keys:
#                    - 'enabled' : True/False (default is True)
#                    any hints:
#                    - 'output' : True/False (default is True)
#                    - 'plot_type' : 'No'/'1D'/'2D' (default is 'No')
#                    - 'plot_axes' : list<str> 'where str is channel name/'step#/'index#' (default is [])
#                    - 'label' : prefered label (default is channel name)
#                    - 'scale' : <float, float> with min/max (defaults to channel
#                                range if it is defined
#                    - 'plot_color' : int representing RGB
#    optional keys:
#    - 'label' : measurement group label (defaults to measurement group name)
#    - 'description' : measurement group description

# <MeasurementGroupConfiguration>
#  <timer>UxTimer</timer>
#  <monitor>CT1</monitor>
# </MeasurementGroupConfiguration>

# Example: 2 NI cards, where channel 1 of card 1 is wired to channel 1 of card 2
# at configuration time we should set:
# ctrl.setPar( <unit>, <parameter name>, <parameter value> )
# ni0ctrl.setCtrlPar(0, 'trigger_type', AcqTriggerType.Software)
# ni0ctrl.setCtrlPar(0, 'timer', 1) # channel 1 is the timer
# ni0ctrl.setCtrlPar(0, 'monitor', 4) # channel 4 is the monitor
# ni1ctrl.setCtrlPar(0, 'trigger_type', AcqTriggerType.ExternalTrigger)
# ni1ctrl.setCtrlPar(0, 'master', 0)

# when we count for 1.5 seconds:
# ni1ctrl.Load(1.5)
# ni0ctrl.Load(1.5)
# ni1ctrl.Start()
# ni0ctrl.Start()

"""

"""

class PoolMeasurementGroup(PoolGroupElement):

    DFT_DESC = 'General purpose measurement group'

    def __init__(self, **kwargs):
        self._integration_time = None
        self._monitor_count = None
        self._acquisition_mode = AcqMode.Timer
        self._config = None
        self._config_dirty = True
        kwargs['elem_type'] = ElementType.MeasurementGroup
        PoolGroupElement.__init__(self, **kwargs)
        self.set_configuration(kwargs.get('configuration'))

    def _create_action_cache(self):
        acq_name = "%s.Acquisition" % self._name
        return PoolAcquisition(self, acq_name)

    def _calculate_element_state(self, elem, elem_state_info):
        if elem.get_type() == ElementType.ZeroDExpChannel:
            if elem_state_info[0] == State.Moving:
                elem_state_info = State.On, elem_state_info[1]
        return PoolGroupElement._calculate_element_state(self, elem,
                                                         elem_state_info)

    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name
        if name == 'state':
            if evt_src.get_type() == ElementType.ZeroDExpChannel:
                # 0D channels are "passive", which means they cannot contribute
                # to set the measurement group into a moving state
                if evt_value in (State.On, State.Moving):
                    return
            state, status = self._calculate_states()
            self.set_state(state, propagate=2)
            self.set_status("\n".join(status))

    def get_pool_controllers(self):
        return self.get_acquisition().get_pool_controllers()

    def get_pool_controller_by_name(self, name):
        name = name.lower()
        for ctrl in self.get_pool_controllers():
            if ctrl.name.lower() == name or ctrl.full_name.lower() == name:
                return ctrl

    # --------------------------------------------------------------------------
    # configuration
    # --------------------------------------------------------------------------

    def _is_managed_element(self, element):
        return element.get_type() in TYPE_EXP_CHANNEL_ELEMENTS

    def _build_channel_defaults(self, channel_data, channel):
        """Fills the channel default values for the given channel dictionary"""

        external_from_name = isinstance(channel, (str, unicode))
        ndim = None
        instrument = None
        if external_from_name:
            name = full_name = source = channel
        else:
            name = channel.name
            full_name = channel.full_name
            source = channel.get_source()
            ndim = None
            instrument = None
            ctype = channel.get_type()
            if ctype != ElementType.External:
                instrument = channel.instrument
            if ctype == ElementType.CTExpChannel:
                ndim = 0
            elif ctype == ElementType.PseudoCounter:
                ndim = 0
            elif ctype == ElementType.ZeroDExpChannel:
                ndim = 0
            elif ctype == ElementType.OneDExpChannel:
                ndim = 1
            elif ctype == ElementType.TwoDExpChannel:
                ndim = 2
            elif ctype == ElementType.External:
                config = channel.get_config()
                if config is not None:
                    ndim = int(config.data_format)
            elif ctype == ElementType.IORegister:
                ndim = 0

        # Definitively should be initialized by measurement group
        # index MUST be here already (asserting this in the following line)
        channel_data['index'] = channel_data['index']
        channel_data['name'] = channel_data.get('name', name)
        channel_data['full_name'] = channel_data.get('full_name', full_name)
        channel_data['source'] = channel_data.get('source', source)
        channel_data['enabled'] = channel_data.get('enabled', True)
        channel_data['label'] = channel_data.get('label', channel_data['name'])
        channel_data['instrument'] = channel_data.get('instrument', getattr(instrument,'name',None))
        channel_data['ndim'] = ndim
        # Probably should be initialized by measurement group
        channel_data['output'] = channel_data.get('output', True)

        # Perhaps should NOT be initialized by measurement group
        channel_data['plot_type'] = channel_data.get('plot_type', PlotType.No)
        channel_data['plot_axes'] = channel_data.get('plot_axes', [])
        channel_data['conditioning'] = channel_data.get('conditioning', '')
        channel_data['normalization'] = channel_data.get('normalization', Normalization.No)

        return channel_data

    def _build_configuration(self):
        """Builds a configuration object from the list of elements"""
        config = {}
        user_elements = self.get_user_elements()
        ctrls = self.get_pool_controllers()

        # find the first CT
        first_timerable = None
        for elem in user_elements:
            if elem.get_type() in TYPE_TIMERABLE_ELEMENTS:
                first_timerable = elem
                break
        if first_timerable is None:
            raise Exception("It is not possible to construct a measurement "
                            "group without at least one timer able channel "
                            "(Counter/timer, 1D or 2D)")
        g_timer = g_monitor = first_timerable
        config['timer'] = g_timer
        config['monitor'] = g_monitor
        config['controllers'] = controllers = {}

        external_user_elements = []
        for index, element in enumerate(user_elements):
            elem_type = element.get_type()
            if elem_type == ElementType.External:
                external_user_elements.append((index, element))
                continue
            
            ctrl = element.controller
            ctrl_data = controllers.get(ctrl)

            # attention: following lines are only prepared for 1 unit per
            # controller
            if ctrl_data is None:
                controllers[ctrl] = ctrl_data = {}
                ctrl_data['units'] = units = {}
                units['0'] = unit_data = {}
                unit_data['id'] = 0
                unit_data['channels'] = channels = {}
                if elem_type in TYPE_TIMERABLE_ELEMENTS:
                    elements = ctrls[ctrl]
                    if g_timer in elements:
                        unit_data['timer'] = g_timer
                    else:
                        unit_data['timer'] = elements[0]
                    if g_monitor in elements:
                        unit_data['monitor'] = g_monitor
                    else:
                        unit_data['monitor'] = elements[0]
                    unit_data['trigger_type'] = AcqTriggerType.Software
            else:
                channels = ctrl_data['units']['0']['channels']
            channels[element] = channel_data = {}
            channel_data['index'] = user_elements.index(element)
            channel_data = self._build_channel_defaults(channel_data, element)
        config['label'] = self.name
        config['description'] = self.DFT_DESC

        if len(external_user_elements) > 0:
            controllers['__tango__'] = ctrl_data = {}
            ctrl_data['units'] = units = {}
            units['0'] = unit_data = {}
            unit_data['id'] = 0
            unit_data['channels'] = channels = {}
            for index, element in external_user_elements:
                channels[element] = channel_data = {}
                channel_data['index'] = index
                channel_data = self._build_channel_defaults(channel_data, element)
        return config

    def set_configuration(self, config=None, propagate=1):
        if config is None:
            config = self._build_configuration()
        else:
            # create a configuration based on a new configuration
            user_elem_ids = {}
            pool = self.pool
            for c, c_data in config['controllers'].items():
                external = isinstance(c, (str, unicode))
                # attention: following line only prepared for 1 unit per controller
                for channel_data in c_data['units']['0']['channels'].values():
                    if external:
                        element = id = channel_data['full_name']
                        channel_data['source'] = id
                    else:
                        element = pool.get_element_by_full_name(channel_data['full_name'])
                        id = element.id
                    user_elem_ids[channel_data['index']] = id
                    channel_data = self._build_channel_defaults(channel_data, element)
            indexes = sorted(user_elem_ids.keys())
            assert indexes == range(len(indexes))
            self.set_user_element_ids([ user_elem_ids[idx] for idx in indexes ])

        # checks
        g_timer, g_monitor = config['timer'], config['monitor']

        # attention: following line only prepared for 1 unit per controller
        timer_ctrl_data = config['controllers'][g_timer.controller]['units']['0']
        if timer_ctrl_data['timer'] != g_timer:
            self.warning('unit timer and global timer mismatch. '
                         'Using global timer')
            self.debug('For controller %s, timer is defined as channel %s. '
                       'The global timer is set to channel %s which belongs '
                       'to the same controller', g_timer.controller.name,
                       timer_ctrl_data['timer'].name, g_timer.name)
            timer_ctrl_data['timer'] = g_timer

        # attention: following line only prepared for 1 unit per controller
        monitor_ctrl_data = config['controllers'][g_monitor.controller]['units']['0']
        if monitor_ctrl_data['monitor'] != g_monitor:
            self.warning('unit monitor and global monitor mismatch. '
                         'Using global monitor')
            self.debug('For controller %s, monitor is defined as channel %s. '
                       'The global timer is set to channel %s which belongs '
                       'to the same controller', g_monitor.controller.name,
                       monitor_ctrl_data['monitor'].name, g_monitor.name)
            monitor_ctrl_data['monitor'] != g_monitor

        self._config = config
        self._config_dirty = True
        if not propagate:
            return
        self.fire_event(EventType("configuration", priority=propagate), config)

    def set_configuration_from_user(self, cfg, propagate=1):
        config = {}
        user_elements = self.get_user_elements()
        pool = self.pool

        timer_name = cfg.get('timer', user_elements[0].full_name)
        monitor_name = cfg.get('monitor', user_elements[0].full_name)
        config['timer'] = pool.get_element_by_full_name(timer_name)
        config['monitor'] = pool.get_element_by_full_name(monitor_name)
        config['controllers'] = controllers = {}

        for c_name, c_data in cfg['controllers'].items():
            # discard controllers which don't have items (garbage)
            ch_count = 0
            for u_data in c_data['units'].values():
                ch_count += len(u_data['channels'])
            if ch_count == 0:
                continue
                
            external = c_name.startswith('__')
            if external:
                ctrl = c_name
            else:
                ctrl = pool.get_element_by_full_name(c_name)
                assert ctrl.get_type() == ElementType.Controller
            controllers[ctrl] = ctrl_data = {}
            ctrl_data['units'] = units = {}
            for u_id, u_data in c_data['units'].items():
                # discard units which don't have items (garbage)
                if len(u_data['channels']) == 0:
                    continue
                units[u_id] = unit_data = dict(u_data)
                unit_data['id'] = u_data.get('id', u_id)
                if not external and ctrl.is_timerable():
                    unit_data['timer'] = pool.get_element_by_full_name(u_data['timer'])
                    unit_data['monitor'] = pool.get_element_by_full_name(u_data['monitor'])
                    unit_data['trigger_type'] = u_data['trigger_type']
                unit_data['channels'] = channels = {}
                for ch_name, ch_data in u_data['channels'].items():
                    if external:
                        validator = AttributeNameValidator()
                        params = validator.getParams(ch_data['full_name'])
                        params['pool'] = self.pool
                        channel = PoolExternalObject(**params)
                    else:
                        channel = pool.get_element_by_full_name(ch_name)
                    channels[channel] = dict(ch_data)

        config['label'] = cfg.get('label', self.name)
        config['description'] = cfg.get('description', self.DFT_DESC)
        self.set_configuration(config, propagate=propagate)

    def get_configuration(self):
        return self._config

    def get_user_configuration(self):
        cfg = self.get_configuration()
        config = {}

        config['timer'] = cfg['timer'].full_name
        config['monitor'] = cfg['monitor'].full_name
        config['controllers'] = controllers = {}

        for c, c_data in cfg['controllers'].items():
            ctrl_name = c
            if not isinstance(c, (str, unicode)):
                ctrl_name = c.full_name
            external = ctrl_name.startswith('__')
            controllers[ctrl_name] = ctrl_data = {}
            ctrl_data['units'] = units = {}
            for u_id, u_data in c_data['units'].items():
                units[u_id] = unit_data = {}
                unit_data['id'] = u_data['id']
                if not external and c.is_timerable():
                    if u_data.has_key('timer'):
                        unit_data['timer'] = u_data['timer'].full_name
                    if u_data.has_key('monitor'):
                        unit_data['monitor'] = u_data['monitor'].full_name
                    if u_data.has_key('trigger_type'):
                        unit_data['trigger_type'] = u_data['trigger_type']
                unit_data['channels'] = channels = {}
                for ch, ch_data in u_data['channels'].items():
                    channels[ch.full_name] = dict(ch_data)

        config['label'] = cfg['label']
        config['description'] = cfg['description']
        return config

    def load_configuration(self, force=False):
        """Loads the current configuration to all involved controllers"""
        cfg = self.get_configuration()
        g_timer, g_monitor = cfg['timer'], cfg['monitor']

        for ctrl, ctrl_data in cfg['controllers'].items():
            # skip external channels
            if type(ctrl) is str:
                continue
            if ctrl.operator == self and not force and not self._config_dirty:
                continue
            ctrl.operator = self
            if ctrl.is_timerable():
                for unit, unit_data in ctrl_data['units'].items():
                    #if ctrl == g_timer.controller:
                    #    ctrl.set_ctrl_par('timer', g_timer.axis)
                    #if ctrl == g_monitor.controller:
                    #    ctrl.set_ctrl_par('monitor', g_monitor.axis)
                    ctrl.set_ctrl_par('timer', unit_data['timer'].axis)
                    ctrl.set_ctrl_par('monitor', unit_data['monitor'].axis)
                    ctrl.set_ctrl_par('trigger_type', unit_data['trigger_type'])

        self._config_dirty = False

    def get_timer(self):
        return self.get_configuration()['timer']

    timer = property(get_timer)

    # --------------------------------------------------------------------------
    # integration time
    # --------------------------------------------------------------------------

    def get_integration_time(self):
        return self._integration_time

    def set_integration_time(self, integration_time, propagate=1):
        self._integration_time = integration_time
        if not propagate:
            return
        self.fire_event(EventType("integration_time", priority=propagate),
                        integration_time)

    integration_time = property(get_integration_time, set_integration_time,
                                doc="the current integration time")

    # --------------------------------------------------------------------------
    # integration time
    # --------------------------------------------------------------------------

    def get_monitor_count(self):
        return self._monitor_count

    def set_monitor_count(self, monitor_count, propagate=1):
        self._monitor_count = monitor_count
        if not propagate:
            return
        self.fire_event(EventType("monitor_count", priority=propagate),
                        monitor_count)

    monitor_count = property(get_monitor_count, set_monitor_count,
                             doc="the current monitor count")

    # --------------------------------------------------------------------------
    # acquisition mode
    # --------------------------------------------------------------------------

    def get_acquisition_mode(self):
        return self._acquisition_mode

    def set_acquisition_mode(self, acquisition_mode, propagate=1):
        self._acquisition_mode = acquisition_mode
        if not propagate:
            return
        self.fire_event(EventType("acquisition_mode", priority=propagate),
                        acquisition_mode)

    acquisition_mode = property(get_acquisition_mode, set_acquisition_mode,
                                doc="the current acquisition mode")

    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------

    def start_acquisition(self, value=None, multiple=1):
        self._aborted = False
        if not self._simulation_mode:
            # load configuration into controller(s) if necessary
            self.load_configuration()
            # start acquisition
            kwargs = dict(head=self, config=self._config, multiple=multiple)
            if self.acquisition_mode == AcqMode.Timer:
                kwargs["integ_time"] = self._integration_time
            elif self.acquisition_mode == AcqMode.Monitor:
                kwargs["monitor_count"] = self._monitor_count
            self.acquisition.run(**kwargs)

    def set_acquisition(self, acq_cache):
        self.set_action_cache(acq_cache)

    def get_acquisition(self):
        return self.get_action_cache()

    acquisition = property(get_acquisition, doc="acquisition object")

