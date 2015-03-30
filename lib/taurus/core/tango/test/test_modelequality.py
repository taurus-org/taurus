import unittest
from taurus.core.test.modelequality import TaurusModelEqualityTestCase, \
                                           testDeviceModelEquality, \
                                           testAttributeModelEquality, \
                                           testConfigurationModelEquality 

# the same device models, just different cases 
dev_models1 = ['tango:sys/tg_test/1',
               'tango:SYS/TG_TEST/1']
# different device models
dev_models2 = ['tango:sys/tg_test/1',
               'tango:sys/tg_test/2']
# the same attribute models, just different cases
attr_models1 = ['tango:sys/tg_test/1/float_scalar',
                'tango:SYS/TG_TEST/1/FLOAT_SCALAR']
# different attribute models
attr_models2 = ['tango:sys/tg_test/1/float_scalar',
                'tango:sys/tg_test/2/float_scalar']
# the same configuration models, just different cases
conf_models1 = [
        'tango:sys/tg_test/1/float_scalar?configuration=label',
        'tango:SYS/TG_TEST/1/FLOAT_SCALAR?configuration=LABEL'
        ]
# different configuration models
conf_models2 = [
        'tango:sys/tg_test/1/float_scalar?configuration=label',
        'tango:sys/tg_test/2/float_scalar?configuration=label'
        ]
# the same configuration models, just different cases
conf_models3 = [
        'tango:sys/tg_test/1/float_scalar?configuration=label',
        'tango:SYS/TG_TEST/1/FLOAT_SCALAR?configuration=unit'
        ]

# test cases for the model case insensitiveness
@testAttributeModelEquality(models = attr_models1, equal = True)
@testDeviceModelEquality(models = dev_models1, equal = True)
@testConfigurationModelEquality(models = conf_models1, equal = True)

# test cases for the different models inequality
@testAttributeModelEquality(models = attr_models2, equal = False)
@testDeviceModelEquality(models = dev_models2, equal = False)
@testConfigurationModelEquality(models = conf_models2, equal = False)

# test cases for the different models equality
#TODO: add device/alias equality tests
@testConfigurationModelEquality(models = conf_models3, equal = True)
class TangoModelEqualityTestCase(TaurusModelEqualityTestCase, 
                                 unittest.TestCase):
    """TestCase class for tango model equality testing."""
    pass