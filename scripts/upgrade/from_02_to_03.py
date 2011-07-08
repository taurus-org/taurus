#!/usr/bin/env python

import sys
import PyTango
from upgrade_utils import *

class Controller:
    def __init__(self, type, file, kcls, name, id):
        self.type = type
        self.file = file
        self.kcls = kcls
        self.name = name
        self.id = id

    def __str__(self):
        return "%s %s %s %s %s" % (self.type, self.file, self.kcls, self.name, self.id)

    def get_controller_prop(self):
        return [self.type, self.file, self.kcls, self.name, self.id]


class Up02To03(Upgrade):

    def get_pool_controllers(self, serv, db=None):
        """Gets the list of Pool controllers from pool version 0.1.x"""
        pool_serv_name = "Pool/%s" % serv
        pool_dev_name = get_pool_device_from_server(serv)
        db = db or get_db()
        ctrls = db.get_device_property(pool_dev_name, ["Controller"])["Controller"]
        i = 0
        ret = []
        while i < len(ctrls):
            type = ctrls[i]
            file = ctrls[i+1]
            kcls = ctrls[i+2]
            name = ctrls[i+3]
            id = ctrls[i+4]
            i += 5
            ret.append(Controller(type, file, kcls, name, id))
        return ret

    @classmethod
    def fromTo(cls):
        return ("0.2.x", "0.3.0")

    @classmethod
    def supports(cls, old_vers, new_vers):
        return old_vers.startswith('0.2') and new_vers.startswith('0.3')

    @classmethod
    def supports_old(cls, old_vers):
        return old_vers.startswith('0.2')

    @classmethod
    def supports_new(cls, new_vers):
        return new_vers.startswith('0.3')

    def upgrade(self, db, serv, old_vers, new_vers):
        
        if not Up02To03.supports(old_vers, new_vers):
            raise Exception("Unsupported upgrade")

        yield "Upgrading %s from %s to %s... " % (serv, old_vers, new_vers), 1

        id = 1
        
        pending_put_properties = {}
        
        # map used to store <id, name (alias)>
        elem_map, reverse_elem_map = {}, {}

        pool_serv_name = "Pool/%s" % serv
        pool_dev_name = get_pool_device_from_server(serv,db=db)

        # 1 - get controllers

        # 2 - get elements
        elems = db.get_device_class_list(pool_serv_name)

        i = 0
        elems_dict = {}
        while i < len(elems):
            dev, kcls = elems[i], elems[i+1]
            if not elems_dict.has_key(kcls): elems_dict[kcls] = []
            elems_dict[kcls].append(dev)
            i += 2

        # 3.1 - store motors
        yield "Storing motor information...", 5
        for m_dev_name in elems_dict.get("Motor", []):
            props = db.get_device_property(m_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            m_alias = db.get_alias(m_dev_name).lower()
            elem_map[id] = m_alias
            reverse_elem_map[m_alias] = id
            
        # 3.2 - store counter timers
        yield "Storing counter information...", 10
        for expch_dev_name in elems_dict.get("CTExpChannel", []):
            props = db.get_device_property(expch_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            expch_alias = db.get_alias(expch_dev_name).lower()
            elem_map[id] = expch_alias
            reverse_elem_map[expch_alias] = id

        # 3.3 - store 0D
        yield "Storing 0D information...", 15
        for expch_dev_name in elems_dict.get("ZeroDExpChannel", []):
            props = db.get_device_property(expch_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            expch_alias = db.get_alias(expch_dev_name).lower()
            elem_map[id] = expch_alias
            reverse_elem_map[expch_alias] = id

        # 3.4 - store 1D
        yield "Storing 1D information...", 20
        for expch_dev_name in elems_dict.get("OneDExpChannel", []):
            props = db.get_device_property(expch_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            expch_alias = db.get_alias(expch_dev_name).lower()
            elem_map[id] = expch_alias
            reverse_elem_map[expch_alias] = id

        # 3.5 - store 2D
        yield "Storing 2D information...", 25
        for expch_dev_name in elems_dict.get("TwoDExpChannel", []):
            props = db.get_device_property(expch_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            expch_alias = db.get_alias(expch_dev_name).lower()
            elem_map[id] = expch_alias
            reverse_elem_map[expch_alias] = id

        # 3.6 - store communication channels
        yield "Storing communication channel information...", 30
        for comch_dev_name in elems_dict.get("CommunicationChannel", []):
            props = db.get_device_property(comch_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            comch_alias = db.get_alias(comch_dev_name).lower()
            elem_map[id] = comch_alias
            reverse_elem_map[comch_alias] = id

        # 3.7 - store IO register
        yield "Storing ioregister information...", 35
        for ior_dev_name in elems_dict.get("IORegister", []):
            props = db.get_device_property(ior_dev_name, ("id", "ctrl_id", "axis"))
            id = int(props["id"][0])
            ior_alias = db.get_alias(ior_dev_name).lower()
            elem_map[id] = ior_alias
            reverse_elem_map[ior_alias] = id

        # 3.8 - For MotorGroup remove 'motor_group_id' and add 'id'
        yield "Storing MotorGroup information...", 40
        for mg_dev_name in elems_dict.get("MotorGroup", []):
            mg_dev_name = mg_dev_name.lower()
            props = ('id', 'motor_list', 'motor_group_list', 'pseudo_motor_list', 'phys_group_elt', 'user_group_elt')
            props = db.get_device_property(mg_dev_name, props)
            id = int(props["id"][0])
            mg_alias = db.get_alias(mg_dev_name).lower()
            elem_map[id] = mg_alias
            reverse_elem_map[mg_alias] = id

            pending_put_properties[mg_dev_name] = {}

            new_motor_list = []
            skip = True
            for name in props['motor_list']:
                name = name.lower()
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_motor_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'motor_list': new_motor_list})
            
            new_motor_group_list = []
            skip = True
            for name in props['motor_group_list']:
                name = name.lower()
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_motor_group_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'motor_group_list': new_motor_group_list})

            new_pseudo_motor_list = []
            skip = True
            for name in props['pseudo_motor_list']:
                name = name.lower()
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e:
                    skip = False
                    new_pseudo_motor_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'pseudo_motor_list': new_pseudo_motor_list})

            new_phys_group_elt = []
            skip = True
            for name in props['phys_group_elt']:
                name = name.lower()
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_phys_group_elt.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'phys_group_elt': new_phys_group_elt})

            new_user_group_elt = []
            skip = True
            for name in props['user_group_elt']:
                name = name.lower()
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_user_group_elt.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'user_group_elt': new_user_group_elt})
            
        # 3.9 - For MeasurementGroup remove 'measurement_group_id' and add 'id'
        yield "Storing MeasurementGroup information...", 45
        for mg_dev_name in elems_dict.get("MeasurementGroup", []):
            mg_dev_name = mg_dev_name.lower()
            props = ('id', 'ct_list', 'zerodexpchannel_list', 'onedexpchannel_list',
                     'twodexpchannel_list', 'pseudocounter_list', 'motor_list',
                     'phys_group_elt', 'user_group_elt')
            props = db.get_device_property(mg_dev_name, props)
            id = int(props["id"][0])
            mg_alias = db.get_alias(mg_dev_name).lower()
            elem_map[id] = mg_alias
            reverse_elem_map[mg_alias] = id
            
            pending_put_properties[mg_dev_name] = {}
            
            new_ct_list = []
            skip = True
            for name in props['ct_list']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_ct_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'ct_list': new_ct_list})

            new_zerodexpchannel_list = []
            skip = True
            for name in props['zerodexpchannel_list']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_zerodexpchannel_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'zerodexpchannel_list': new_zerodexpchannel_list})

            new_onedexpchannel_list = []
            skip = True
            for name in props['onedexpchannel_list']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_onedexpchannel_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'onedexpchannel_list': new_onedexpchannel_list})

            new_twodexpchannel_list = []
            skip = True
            for name in props['twodexpchannel_list']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_twodexpchannel_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'twodexpchannel_list': new_twodexpchannel_list})

            new_pseudocounter_list = []
            skip = True
            for name in props['pseudocounter_list']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_pseudocounter_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'pseudocounter_list': new_pseudocounter_list})

            new_motor_list = []
            skip = True
            for name in props['motor_list']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_motor_list.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'motor_list': new_motor_list})

            new_phys_group_elt = []
            skip = True
            for name in props['phys_group_elt']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_phys_group_elt.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'phys_group_elt': new_phys_group_elt})

            new_user_group_elt = []
            skip = True
            for name in props['user_group_elt']:
                name = name.lower()
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_user_group_elt.append(reverse_elem_map.get(name, name))
            if not skip:
                pending_put_properties[mg_dev_name].update({'user_group_elt': new_user_group_elt})

        # 3.10 - For PseudoMotor replace motor_list from a list of names to a list of IDs
        yield "Storing PseudoMotor information...", 50
        for pm_dev_name in elems_dict.get("PseudoMotor", []):
            pm_dev_name = pm_dev_name.lower()
            props = db.get_device_property(pm_dev_name, ("id", "ctrl_id", "axis", 
                "motor_group", "motor_group_id", "motor_list"))
            id = int(props["id"][0])
            pm_alias = db.get_alias(pm_dev_name).lower()
            elem_map[id] = pm_alias
            reverse_elem_map[pm_alias] = id
            
            motor_group = props["motor_group"]
            if not motor_group:
                motor_group_id = motor_group = props["motor_group_id"]
                if not motor_group_id:
                    print "WARNING: neither motor_group nor motor_group_id property is defined for %s." % pm_dev_name
            else:
                motor_group = motor_group[0].lower()
                motor_group_id = reverse_elem_map[motor_group]
                props["motor_group_id"] = [str(motor_group_id)]
                db.put_device_property(pm_dev_name, props)
            
            db.delete_device_property(pm_dev_name, ["pseudo_motor_id", "motor_group", "role", "role_idx"])

            skip = True
            motor_ids = []
            for name in props["motor_list"]:
                name = name.lower()
                try: int(name)
                except Exception,e: 
                    skip = False
                    motor_ids.append(reverse_elem_map[name])
            if not skip:
                db.put_device_property(pm_dev_name, { "motor_list" : motor_ids })

        # 3.11 - For PseudoCounter replace channel_list from a list of names to a list of IDs
        yield "Storing PseudoCounter information...", 60
        for pc_dev_name in elems_dict.get("PseudoCounter", []):
            pc_dev_name = pc_dev_name.lower()
            props = db.get_device_property(pc_dev_name, ("id", "ctrl_id", "axis", 
                "channel_list"))
            id = int(props["id"][0])
            pc_alias = db.get_alias(pc_dev_name).lower()
            elem_map[id] = pc_alias
            reverse_elem_map[pc_alias] = id
            
            db.delete_device_property(pc_dev_name, ["pseudo_counter_id", "role", "role_idx"])

            skip = True
            channel_ids = []
            for name in props["channel_list"]:
                name = name.lower()
                try: int(name)
                except Exception,e: 
                    skip = False
                    channel_ids.append(reverse_elem_map[name])
            if not skip:
                db.put_device_property(pc_dev_name, { "channel_list" : channel_ids })
                
        # 4. - Apply pending properties
        yield "Applying pending properties...", 75
        for dev, props in pending_put_properties.iteritems():
            for name, val in props.iteritems():
                for i, elem in enumerate(val):
                    if isinstance(elem, str):
                        val[i] = reverse_elem_map[elem]
            db.put_device_property(dev, props)

        # 5. - Finally update the version property in the database
        yield "Updating the version property in the database...", 85
        db.put_device_property(pool_dev_name, { "Version" : [new_vers] })

        # 6. - Check if the service is already registered
        yield "Checking if the service is already registered...", 95
        services = db.get_services("Sardana", serv)
        if len(services) == 0:
            db.register_service("Sardana", serv, pool_dev_name)

        yield "Finished", 100

class Up01To03(Upgrade):

    @classmethod
    def fromTo(cls):
        return ("0.1.x", "0.3.0")

    @classmethod
    def supports(cls, old_vers, new_vers):
        return old_vers.startswith('0.1') and new_vers.startswith('0.3')
    
    @classmethod
    def supports_old(cls, old_vers):
        return old_vers.startswith('0.1')

    @classmethod
    def supports_new(cls, new_vers):
        return new_vers.startswith('0.3')

    def upgrade(self, db, serv, old_vers, new_vers):

        if not Up01To03.supports(old_vers, new_vers):
            raise Exception("Unsupported upgrade")
        
        from from_01_to_02 import Up01To02
        up = Up01To02()
        for msg, perc in up.upgrade(db, serv, old_vers, '0.2.0'):
            yield msg, perc / 2
        up = Up02To03()
        
        for msg, perc in up.upgrade(db, serv, '0.2.0', new_vers):
            yield msg, (perc/2) + 50
