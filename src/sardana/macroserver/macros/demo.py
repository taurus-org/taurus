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

"""This is the standard macro module"""

from __future__ import print_function

__all__ = ["sar_demo"]

import PyTango

from sardana.macroserver.macro import macro

def get_free_names(db, prefix, nb, start_at=1):
    ret = []
    i = start_at
    failed = 96
    while len(ret) < nb and failed > 0:
        name = "%s%02d" % (prefix, i)
        try:
            db.get_device_alias(name)
            failed -= 1
        except:
            ret.append(name)
        i += 1
    if len(ret) < nb or failed == 0:
        raise Exception("Too many sardana demos registered on this system.\n"
                        "Please try using a different tango system")
    return ret

@macro()
def clear_sar_demo():
    try:
        SAR_DEMO = self.getEnv("SAR_DEMO")
    except:
        self.error("No demo has been prepared yet on this sardana!")
        return
    
    print("Removing measurement groups...")
    for mg in SAR_DEMO.get("measurement_groups", ()):
        udefmeas(mg)
    
    print("Removing measurement elements...")
    for elem in SAR_DEMO.get("elements", ()):
        udefelem(elem)
    
    print("Removing measurement controllers...")
    for ctrl in SAR_DEMO.get("controllers", ()):
        udefctrl(ctrl)
    
    self.unsetEnv("SAR_DEMO")

@macro()
def sar_demo():
    
    try:
        SAR_DEMO = self.getEnv("SAR_DEMO")
        self.error("A demo has already been prepared on this sardana")
        return
    except:
        pass
    
    db = PyTango.Database()
    
    mot_ctrl_name = get_free_names(db, "motctrl", 1)[0]
    ct_ctrl_name = get_free_names(db, "ctctrl", 1)[0]
    zerod_ctrl_name = get_free_names(db, "0dctrl", 1)[0]
    pm_ctrl_name = get_free_names(db, "slitctrl", 1)[0]
    
    motor_names = get_free_names(db, "mot", 4)
    ct_names = get_free_names(db, "ct", 4)
    zerod_names = get_free_names(db, "0d", 4)
    gap, offset = get_free_names(db, "gap", 1) + get_free_names(db, "offset", 1)
    
    mg_name = get_free_names(db, "mntgrp", 1)[0]
    
    pools = self.getPools()
    if not len(pools):
        self.error('This is not a valid sardana demonstration system.\n'
                   'Sardana demostration systems must be connect to at least '
                   'one Pool')
        return
    pool = pools[0]
    
    print("Creating motor controller", mot_ctrl_name, "...")
    defctrl("DummyMotorController", mot_ctrl_name)
    for axis, motor_name in enumerate(motor_names, 1):
        print("Creating motor", motor_name, "...")
        defelem(motor_name , mot_ctrl_name, axis)
        
    print("Creating counter controller", ct_ctrl_name, "...")
    defctrl("DummyCounterTimerController", ct_ctrl_name)
    for axis, ct_name in enumerate(ct_names, 1):
        print("Creating counter channel", ct_name, "...")
        defelem(ct_name , ct_ctrl_name, axis)
    
    print("Creating counter controller", zerod_ctrl_name, "...")
    defctrl("DummyZeroDController", zerod_ctrl_name)
    for axis, zerod_name in enumerate(zerod_names, 1):
        print("Creating 0D channel", zerod_name, "...")
        defelem(zerod_name , zerod_ctrl_name, axis)
    
    print("Creating Slit", pm_ctrl_name, "with", gap, ",", offset, "...")
    sl2t, sl2b = motor_names[:2]
    defctrl("Slit", pm_ctrl_name,
            "sl2t="+sl2t, "sl2b="+sl2b,
            "Gap="+gap, "Offset="+offset)
   
    print("Creating measurement group", mg_name, "...")
    defmeas(mg_name, *ct_names)
    
    d = dict(controllers=(pm_ctrl_name, mot_ctrl_name, ct_ctrl_name, zerod_ctrl_name),
             elements=[gap, offset] + motor_names+ct_names+zerod_names,
             measurement_groups=[mg_name])
    
    self.setEnv("SAR_DEMO", d)
    
    print("DONE!")
    
