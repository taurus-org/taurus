import PyTango
import taurus
import csv
import sys

def checkPoolElements(pool):
    pool_dev = taurus.Device(pool)

    # GET CONTROLLER CLASSES
    pool_ctrl_classes = {}
    for info in pool_dev['ControllerClassList'].value:
        ctrl_class, library_path, ctrl_type = info.split()
        pool_ctrl_classes[ctrl_class] = (library_path, ctrl_type)

    # GET CONTROLLERS INFO
    pool_controllers_by_type = {'Motor': [],
                                'PseudoMotor': [],
                                'IORegister': [],
                                'CounterTimer': [],
                                'PseudoCounter': [],
                                'ZeroDExpChannel': []}
    pool_controllers = {}
    for info in pool_dev['ControllerList'].value:
        info_splitted = info.split()
        ctrl_name = info_splitted[0]
        ctrl_library = info_splitted[-1].replace('(','').replace(')','')
        ctrl_class = info_splitted[1].rsplit('.')[1].split('/')[0]
        ctrl_type = ''
        try:
            ctrl_type = pool_ctrl_classes[ctrl_class][1]
            pool_controllers_by_type[ctrl_type].append(ctrl_name)
        except:
            pass
        ctrl_properties = {}
        ctrl_elements = []
        ctrl_pool_elements = []
        for prop in pool_dev.get_property_list(ctrl_name+'/*'):
            prop_name = prop.split('/')[1]
            prop_value = pool_dev.get_property(prop)[prop]
            ctrl_properties[prop_name] = ' '.join(prop_value)
        pool_controllers[ctrl_name] = {}
        pool_controllers[ctrl_name]['type'] = ctrl_type
        pool_controllers[ctrl_name]['name'] = ctrl_name
        pool_controllers[ctrl_name]['file'] = ctrl_library
        pool_controllers[ctrl_name]['class'] = ctrl_class
        pool_controllers[ctrl_name]['properties'] = ctrl_properties
        pool_controllers[ctrl_name]['elements'] = ctrl_elements
        pool_controllers[ctrl_name]['ctrl_pool_elements'] = ctrl_pool_elements

    for ctrl_type, controllers in pool_controllers_by_type.iteritems():
        if len(controllers) == 0:
            continue
        
        print '\n'
        print '----------------------------------------------------------------'
        print len(controllers), ctrl_type, 'CONTROLLERS FOR POOL '+pool
        print '----------------------------------------------------------------'

        for ctrl in controllers:
            details = pool_controllers[ctrl]
            ###print 'Controller',ctrl,':'
            ###for k, v in details.iteritems():
            ###    if k == 'ctrl_pool_elements':
            ###        print '\tElements count:\t'+str(len(v))
            ###    print '\t'+k+':\t'+str(v)
            ###
            ###pool_controllers[ctrl_name]['type'] = ctrl_type
            ###pool_controllers[ctrl_name]['name'] = ctrl_name
            ###pool_controllers[ctrl_name]['file'] = ctrl_library
            ###pool_controllers[ctrl_name]['class'] = ctrl_class
            ###pool_controllers[ctrl_name]['properties'] = ctrl_properties
            ###pool_controllers[ctrl_name]['elements'] = ctrl_elements
            ###pool_controllers[ctrl_name]['ctrl_pool_elements'] = ctrl_pool_elements

            pool_elements_summary = '('+str(len(details['ctrl_pool_elements']))+')'
            print '{type}\t{name}\t{file}\t{class}\t{properties}\t{elements}'.format(**details), pool_elements_summary
            

    pool_elements = {}
    pool_elements['ExpChannels'] = pool_dev['ExpChannelList'].value or []
    pool_elements['Motors'] = pool_dev['MotorList'].value or []
    pool_elements['IORegs'] = pool_dev['IORegisterList'].value or []
    pool_instruments = pool_dev['InstrumentList'].value or []

    print '\n'
    print '----------------------------------------------------------------'
    print len(pool_instruments),'INSTRUMENTS FOR POOL '+pool
    print '----------------------------------------------------------------'
    print pool_instruments

    # CHECK ELEMENTS WITHOUT INSTRUMENT
    for element_type in pool_elements.keys():
        elements = pool_elements[element_type]
        elements_with_no_instrument = []
        for info in elements:
            info_splitted = info.split()
            alias = info_splitted[0]
            dev_name = info_splitted[1]
            ctrl_name, ctrl_axis = info_splitted[2].replace('(','').replace(')','').split('/')
            specific_element_type = info_splitted[3]

            pool_controllers[ctrl_name]['ctrl_pool_elements'].append(alias)
            if specific_element_type in ['PseudoMotor', 'PseudoCounter']:
                if len(pool_controllers[ctrl_name]['elements']) == 0:
                    pool_controllers[ctrl_name]['elements'] = ' '.join(info_splitted[4:])

            element_dev = taurus.Device(alias)
            if element_dev['Instrument'].value == '':
                elements_with_no_instrument.append(alias)
        if len(elements_with_no_instrument) > 0:
            print '\n***',element_type,'with no Instrument:',elements_with_no_instrument,'***'

    print '\n'
    print '----------------------------------------------------------------'
    print 'ELEMENTS FOR POOL '+pool
    print '----------------------------------------------------------------'
    for element_type in pool_elements.keys():
        elements = pool_elements[element_type]
        print element_type+':',len(elements)

    print '\n'
    print '----------------------------------------------------------------'
    print 'ELEMENTS MEMORIZED ATTRIBUTES AND ATTRIBUTE CONFIGURATIONS FOR POOL '+pool
    print '----------------------------------------------------------------'
    db = taurus.Database()
    for element_type in pool_elements.keys():
        elements = pool_elements[element_type]
        for info in elements:
            info_splitted = info.split()
            alias = info_splitted[0]
            dev_name = info_splitted[1]
            ctrl_name, ctrl_axis = info_splitted[2].replace('(','').replace(')','').split('/')
            specific_element_type = info_splitted[3]
            element_dev = taurus.Device(alias)
            for attr, attr_dict in db.get_device_attribute_property(element_dev.getNormalName(), element_dev.get_attribute_list()).iteritems():
                if len(attr_dict) > 0:
                    print specific_element_type, alias, attr, attr_dict
                else:
                    if attr.lower() in ['position', 'value']:
                        print '***',specific_element_type, alias, attr,  'NO MEMORIZED ATTRIBUTES OR ATTRIBUTE CONFIGURATIONS ***'




if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] == '?':
        print '----------------------------------------'
        print 'Invalid number of arguments.'
        print ''
        print 'Example of usage:'
        print '    python get_pool_config pool'
        print ''
        print '    where pool is the name of the pool'
        print '----------------------------------------'


    pool = sys.argv[1]
    checkPoolElements(pool)
