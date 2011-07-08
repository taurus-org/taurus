#!/usr/bin/env python

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


class Up01To02(Upgrade):

    def get_pool_controllers(self, db, serv):
        """Gets the list of Pool controllers from pool version 0.1.x"""
        pool_serv_name = "Pool/%s" % serv
        pool_dev_name = get_pool_device_from_server(serv,db=db)
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
        return ("0.1.x", "0.2.0")

    @classmethod
    def supports(cls, old_vers, new_vers):
        return old_vers.startswith('0.1') and new_vers.startswith('0.2')

    @classmethod
    def supports_old(cls, old_vers):
        return old_vers.startswith('0.1')

    @classmethod
    def supports_new(cls, new_vers):
        return new_vers.startswith('0.2')

    
    def upgrade(self, db, serv, old_vers, new_vers):
        
        if not Up01To02.supports(old_vers, new_vers):
            raise Exception("Unsupported upgrade")
        
        yield "Upgrading %s from %s to %s... " % (serv, old_vers, new_vers), 1

        id = 1
        
        pending_put_properties = {}
        
        # map used to store <id, name (alias)>
        elem_map, reverse_elem_map = {}, {}
    
        pool_serv_name = "Pool/%s" % serv
        pool_dev_name = get_pool_device_from_server(serv,db=db)
        
        # 1 - Update the controller property with unique id
        yield "Updating the controller property with unique id...", 5
        controllers = self.get_pool_controllers(db, serv)

        ctrl_prop_value = []
        for c in controllers:
            c.id = str(id)
            ctrl_prop_value.extend(c.get_controller_prop())
            elem_map[c.id] = c.name.lower()
            reverse_elem_map[c.name.lower()] = c.id
            id += 1

        db.put_device_property(pool_dev_name, { "Controller" : ctrl_prop_value })

        # 2 - Update PoolPath: replace ':' by '\n'
        yield "Updating PoolPath: replace ':' by '%sn'..." % '\\', 10
        pool_path = db.get_device_property(pool_dev_name, ["PoolPath"])["PoolPath"]

        pool_path_prop_value = []
        for p in pool_path:
            pool_path_prop_value.extend(p.split(":"))
        db.put_device_property(pool_dev_name, { "PoolPath" : pool_path_prop_value })

        # 3 - Update the properties of all elements
        elems = db.get_device_class_list(pool_serv_name)

        i = 0
        elems_dict = {}
        while i < len(elems):
            dev, kcls = elems[i], elems[i+1]
            if not elems_dict.has_key(kcls): elems_dict[kcls] = []
            elems_dict[kcls].append(dev)
            i += 2

        # 3.1 - For motor remove 'motor_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating motors...", 15
        for m_dev_name in elems_dict.get("Motor", []):
            m, ctrl, axis = m_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }

            db.put_device_property(m_dev_name, props)
            db.delete_device_property(m_dev_name, ["motor_id"])
            
            m_alias = db.get_alias(m_dev_name)
            elem_map[id] = m_alias.lower()
            reverse_elem_map[m_alias.lower()] = id
            
            id += 1
            
        # 3.2 - For Counter remove 'channel_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating counters...", 20
        for expch_dev_name in elems_dict.get("CTExpChannel", []):
            exp, ctrl, axis = expch_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }
            
            db.put_device_property(expch_dev_name, props)
            db.delete_device_property(expch_dev_name, ["channel_id"])

            expch_alias = db.get_alias(expch_dev_name)
            elem_map[id] = expch_alias.lower()
            reverse_elem_map[expch_alias.lower()] = id
            
            id += 1

        # 3.3 - For 0D remove 'channel_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating 0Ds...", 25
        for expch_dev_name in elems_dict.get("ZeroDExpChannel", []):
            exp, ctrl, axis = expch_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }

            db.put_device_property(expch_dev_name, props)
            db.delete_device_property(expch_dev_name, ["channel_id"])
            
            expch_alias = db.get_alias(expch_dev_name)
            elem_map[id] = expch_alias.lower()
            reverse_elem_map[expch_alias.lower()] = id
            
            id += 1

        # 3.4 - For 1D remove 'channel_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating 1Ds...", 30
        for expch_dev_name in elems_dict.get("OneDExpChannel", []):
            exp, ctrl, axis = expch_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }

            db.put_device_property(expch_dev_name, props)
            db.delete_device_property(expch_dev_name, ["channel_id"])

            expch_alias = db.get_alias(expch_dev_name)
            elem_map[id] = expch_alias.lower()
            reverse_elem_map[expch_alias.lower()] = id
            
            id += 1

        # 3.5 - For 2D remove 'channel_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating 2Ds...", 35
        for expch_dev_name in elems_dict.get("TwoDExpChannel", []):
            exp, ctrl, axis = expch_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }

            db.put_device_property(expch_dev_name, props)
            db.delete_device_property(expch_dev_name, ["channel_id"])
            
            expch_alias = db.get_alias(expch_dev_name)
            elem_map[id] = expch_alias.lower()
            reverse_elem_map[expch_alias.lower()] = id
            
            id += 1

        # 3.6 - For CommunicationChannel remove 'channel_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating Communication channels...", 40
        for comch_dev_name in elems_dict.get("CommunicationChannel", []):
            com, ctrl, axis = comch_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }

            db.put_device_property(comch_dev_name, props)
            db.delete_device_property(comch_dev_name, ["channel_id"])

            comch_alias = db.get_alias(comch_dev_name)
            elem_map[id] = comch_alias.lower()
            reverse_elem_map[comch_alias.lower()] = id
            
            id += 1

        # 3.7 - For IORegister remove 'channel_id' and add 'id', 'ctrl_id' and 'axis'
        yield "Updating IORegisters...", 45
        for ior_dev_name in elems_dict.get("IORegister", []):
            ior, ctrl, axis = ior_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)], "ctrl_id" : [str(ctrl)], "axis" : [str(axis)] }

            db.put_device_property(ior_dev_name, props)
            db.delete_device_property(ior_dev_name, ["channel_id"])

            ior_alias = db.get_alias(ior_dev_name)
            elem_map[id] = ior_alias.lower()
            reverse_elem_map[ior_alias.lower()] = id
            
            id += 1

        # 3.8 - For MotorGroup remove 'motor_group_id' and add 'id'
        yield "Updating MotorGroups...", 50
        for mg_dev_name in elems_dict.get("MotorGroup", []):
            mg, inst, name = mg_dev_name.split("/")

            props = { "id" : [str(id)] }

            db.put_device_property(mg_dev_name, props)
            db.delete_device_property(mg_dev_name, ["motor_group_id", "pool_device"])

            mg_alias = db.get_alias(mg_dev_name)
            elem_map[id] = mg_alias.lower()
            reverse_elem_map[mg_alias.lower()] = id
            
            # change the format of some properties from list of names to list of IDs
            props = ('motor_list', 'motor_group_list', 'pseudo_motor_list', 'phys_group_elt', 'user_group_elt')
            props = db.get_device_property(mg_dev_name, props)

            pending_put_properties[mg_dev_name.lower()] = {}

            new_motor_list = []
            skip = True
            for name in props['motor_list']:
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_motor_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'motor_list': new_motor_list})
            
            new_motor_group_list = []
            skip = True
            for name in props['motor_group_list']:
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_motor_group_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'motor_group_list': new_motor_group_list})

            new_pseudo_motor_list = []
            skip = True
            for name in props['pseudo_motor_list']:
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e:
                    skip = False
                    new_pseudo_motor_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'pseudo_motor_list': new_pseudo_motor_list})

            new_phys_group_elt = []
            skip = True
            for name in props['phys_group_elt']:
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_phys_group_elt.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'phys_group_elt': new_phys_group_elt})

            new_user_group_elt = []
            skip = True
            for name in props['user_group_elt']:
                # if all are already IDs, skip the property
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_user_group_elt.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'user_group_elt': new_user_group_elt})
            
            id += 1
            
        # 3.9 - For MeasurementGroup remove 'measurement_group_id' and add 'id'
        yield "Updating MeasurementGroups...", 55
        for mg_dev_name in elems_dict.get("MeasurementGroup", []):
            mg, inst, name = mg_dev_name.split("/")

            props = { "id" : [str(id)] }

            db.put_device_property(mg_dev_name, props)
            db.delete_device_property(mg_dev_name, ["measurement_group_id",  "pool_device"])

            mg_alias = db.get_alias(mg_dev_name)
            elem_map[id] = mg_alias.lower()
            reverse_elem_map[mg_alias.lower()] = id
            
            props = ('ct_list', 'zerodexpchannel_list', 'onedexpchannel_list',
                     'twodexpchannel_list', 'pseudocounter_list', 'motor_list',
                     'phys_group_elt', 'user_group_elt')
            props = db.get_device_property(mg_dev_name, props)
            
            pending_put_properties[mg_dev_name.lower()] = {}
            
            new_ct_list = []
            skip = True
            for name in props['ct_list']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_ct_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'ct_list': new_ct_list})

            new_zerodexpchannel_list = []
            skip = True
            for name in props['zerodexpchannel_list']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_zerodexpchannel_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'zerodexpchannel_list': new_zerodexpchannel_list})

            new_onedexpchannel_list = []
            skip = True
            for name in props['onedexpchannel_list']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_onedexpchannel_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'onedexpchannel_list': new_onedexpchannel_list})

            new_twodexpchannel_list = []
            skip = True
            for name in props['twodexpchannel_list']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_twodexpchannel_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'twodexpchannel_list': new_twodexpchannel_list})

            new_pseudocounter_list = []
            skip = True
            for name in props['pseudocounter_list']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_pseudocounter_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'pseudocounter_list': new_pseudocounter_list})

            new_motor_list = []
            skip = True
            for name in props['motor_list']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_motor_list.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'motor_list': new_motor_list})

            new_phys_group_elt = []
            skip = True
            for name in props['phys_group_elt']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_phys_group_elt.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'phys_group_elt': new_phys_group_elt})

            new_user_group_elt = []
            skip = True
            for name in props['user_group_elt']:
                try: int(name) 
                except Exception, e: 
                    skip = False
                    new_user_group_elt.append(reverse_elem_map.get(name.lower(), name.lower()))
            if not skip:
                pending_put_properties[mg_dev_name.lower()].update({'user_group_elt': new_user_group_elt})
            
            id += 1

        # 3.10 - For PseudoMotor remove 'pseudo_motor_id', 'motor_group', 'role'
        #        and 'role_idx' and add 'id', 'ctrl_id', 'axis', 'motor_group_id'
        #        Replace motor_list from a list of names to a list of IDs
        yield "Updating PseudoMotors...", 60
        for pm_dev_name in elems_dict.get("PseudoMotor", []):
            pm, ctrl, axis = pm_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)],
                      "ctrl_id" : [str(ctrl)],
                      "axis" : [str(axis)] }
            
            prop_values = db.get_device_property(pm_dev_name, ["motor_group", "motor_group_id", "motor_list"])
            motor_group = prop_values["motor_group"]

            if not motor_group:
                motor_group_id = motor_group = prop_values["motor_group_id"]
                if not motor_group_id:
                    print "WARNING: neither motor_group nor motor_group_id property is defined for %s." % pm_dev_name
            else:
                motor_group = motor_group[0]
                motor_group_dev_name = db.get_device_alias(motor_group)
                motor_group_id = db.get_device_property(motor_group_dev_name,["id"])["id"][0]
                props["motor_group_id"] = [str(motor_group_id)]

            db.put_device_property(pm_dev_name, props)
            db.delete_device_property(pm_dev_name, ["pseudo_motor_id", "motor_group", "role", "role_idx"])

            skip = True
            motor_ids = []
            for name in prop_values["motor_list"]:
                try: int(name)
                except Exception,e: 
                    skip = False
                    motor_ids.append(reverse_elem_map[name.lower()])
            if not skip:
                db.put_device_property(pm_dev_name, { "motor_list" : motor_ids })

            pm_alias = db.get_alias(pm_dev_name)
            elem_map[id] = pm_alias.lower()
            reverse_elem_map[pm_alias.lower()] = id
            
            id += 1

        # 3.11 - For PseudoCounter remove 'pseudo_counter_id', 'role' and
        #        'role_idx' and add 'id', 'ctrl_id', 'axis'
        #        Replace channel_list from a list of names to a list of IDs
        yield "Updating PseudoCounters...", 65
        for pc_dev_name in elems_dict.get("PseudoCounter", []):
            pc, ctrl, axis = pc_dev_name.split("/")

            for c in controllers:
                if c.name.lower() == ctrl.lower():
                    ctrl = c.id

            props = { "id" : [str(id)],
                      "ctrl_id" : [str(ctrl)],
                      "axis" : [str(axis)] }

            db.put_device_property(pc_dev_name, props)
            db.delete_device_property(pc_dev_name, ["pseudo_counter_id", "role", "role_idx"])

            channel_list = db.get_device_property(pc_dev_name, "channel_list")["channel_list"]
            
            skip = True
            channel_ids = []
            for name in channel_list:
                try: int(name)
                except Exception,e: 
                    skip = False
                    channel_ids.append(reverse_elem_map[name.lower()])
            if not skip:
                db.put_device_property(pm_dev_name, { "channel_list" : channel_ids })
                
            pc_alias = db.get_alias(pc_dev_name)
            elem_map[id] = pc_alias.lower()
            reverse_elem_map[pc_alias.lower()] = id
            
            id += 1

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

