#ifndef _CPOOL_DEFS_H_
#define _CPOOL_DEFS_H_

#include <sstream>
#include <vector>
#include <map>
#include <set>
#include <stdint.h>
#include "Utils.h"
#include "CPoolExcept.h"

namespace Pool_ns
{

const int32_t CTRL_MAXDEVICE_NOTDEF =   -1;

/**
 * This type identifies an element (motor, controller, counter, etc) in the 
 * Pool
 */
typedef int32_t ElementId;

const ElementId InvalidId = 0;
const int32_t InvalidAxis = 0;

typedef std::vector<ElementId> ElemIdVector;
typedef ElemIdVector::iterator ElemIdVectorIt;

typedef std::set<ElementId, std::less<int32_t> > ElemIdSet;
typedef ElemIdSet::iterator ElemIdSetIt;

typedef std::vector<double> DoubleVector;
typedef DoubleVector::iterator DoubleVectorIt;

typedef DoubleVector ValueVector;
typedef DoubleVectorIt ValueVectorIt;

typedef DoubleVector PositionVector;
typedef DoubleVectorIt PositionVectorIt;

/**
 * a map definition intended to contain: 
 * - key is a pool element ID,
 * - value is its value
 */
typedef std::map<ElementId, double> ValueMap;
typedef ValueMap::iterator ValueMapIt;

/**
 * a map definition intended to contain: 
 * - key is controller ID,
 * - value is a map where:
 *   - key is a pool element ID,
 *   - value is its value
 */
typedef std::map<ElementId, ValueMap> CtrlValueMap;
typedef CtrlValueMap::iterator CtrlValueMapIt;

/**
 * Returns a string representing an invalid Id
 *
 * @return a string representing an invalid Id
 */
inline std::string get_InvalidId_str()
{
    std::ostringstream ostr;
    ostr << InvalidId;
    return ostr.str();
}

enum Language
{
    UNDEF_LANG = 0,
    PYTHON,
    CPP,
};

const char * const LanguageStr[] =
{
    "Python",
    "C++"
};

/**
 * The type of element in the Device Pool
 */
enum ElementType
{
    UNDEF_ELEM = 0,
    CTRL_ELEM,
    MOTOR_ELEM,
    COTI_ELEM,
    ZEROD_ELEM,
    ONED_ELEM,
    TWOD_ELEM,
    COM_ELEM,
    IOREGISTER_ELEM,
    PSEUDO_MOTOR_ELEM,
    PSEUDO_COUNTER_ELEM,
    CONSTRAINT_ELEM,
    MOTOR_GROUP_ELEM,
    MEASUREMENT_GROUP_ELEM,
    INSTRUMENT_ELEM,
    numElementType
};

typedef std::vector<ElementType> ElemTypeVector;
typedef ElemTypeVector::iterator ElemTypeVectorIt;

typedef std::set<ElementType>    ElemTypeSet;
typedef ElemTypeSet::iterator    ElemTypeSetIt;

const char * const ElementTypeStr[] = 
{
    "UndefElem",
    "Controller",
    "Motor",
    "CounterTimer",
    "ZeroDExpChannel",
    "OneDExpChannel",
    "TwoDExpChannel",
    "ComChannel",
    "IORegister",
    "PseudoMotor",
    "PseudoCounter",
    "Constraint",
    "MotorGroup",
    "MeasurementGroup",
    "Instrument",
    "OutOfBounds"
};

const char * const FullElementTypeStr[] = 
{
    "Undefined Element",
    "Controller",
    "Physical Motor",
    "Counter/Timer",
    "0D Experiment Channel",
    "1D Experiment Channel",
    "2D Experiment Channel",
    "Communication Channel",
    "IO Register",
    "Pseudo Motor",
    "Pseudo Counter",
    "Constraint",
    "Motor Group",
    "Measurement Group",
    "Instrument",
    "Out of bounds element"
};

#define IS_PHYSICAL(type) \
    (((type) == MOTOR_ELEM) || ((type) == COTI_ELEM) || \
     ((type) == ZEROD_ELEM) || ((type) == ONED_ELEM) || \
     ((type) == TWOD_ELEM)  || ((type) == COM_ELEM)  || \
     ((type) == IOREGISTER_ELEM))

#define IS_PSEUDO(type) \
    (((type) == PSEUDO_MOTOR_ELEM) || ((type) == PSEUDO_COUNTER_ELEM))
    
#define IS_EXPERIMENT_CHANNEL(type) \
    (((type) == COTI_ELEM) || ((type) == ZEROD_ELEM) || \
     ((type) == ONED_ELEM) || ((type) == TWOD_ELEM)  || \
     ((type) == PSEUDO_COUNTER_ELEM))

#define IS_GROUP(type) \
    (((type) == MOTOR_GROUP_ELEM) || ((type) == MEASUREMENT_GROUP_ELEM))

#define IS_MOTOR(type) \
    (((type) == MOTOR_ELEM) || ((type) == PSEUDO_MOTOR_ELEM))

#define IS_MOVEABLE(type) \
    (IS_MOTOR(type) || ((type) == MOTOR_GROUP_ELEM))
    
/**
 * The type of controller in the DevicePool
 */
enum CtrlType
{
    UNDEF_CTRL = 0,
    PSEUDO_MOTOR_CTRL,
    MOTOR_CTRL,
    COTI_CTRL,
    ZEROD_CTRL,
    ONED_CTRL,
    TWOD_CTRL,
    PSEUDO_COUNTER_CTRL,
    COM_CTRL,
    IOREGISTER_CTRL,
    CONSTRAINT_CTRL,
// the members below don't have a controller directly associated but they
// might be affected when a controller changes so they must be considered    
    MOTOR_GROUP_CTRL,
    MEASUREMENT_GROUP_CTRL,
    numCtrlType
};

const char *const CtrlTypeStr[] = 
{
    "Undefined",
    "PseudoMotor",
    "Motor",
    "CounterTimer",
    "ZeroDExpChannel",
    "OneDExpChannel",
    "TwoDExpChannel",
    "PseudoCounter",
    "Communication",
    "IORegister",
    "Constraint",
    "MotorGroup",
    "MeasurementGroup",
    "OutOfBounds"
};

const char *const FullCtrlTypeStr[] = 
{
    "Undefined Controller",
    "Pseudo Motor Controller",
    "Motor Controller",
    "Counter/Timer Controller",
    "0D Experiment Channel Controller",
    "1D Experiment Channel Controller",
    "2D Experiment Channel Controller",
    "Pseudo Counter Controller",
    "Communication Channel Controller",
    "IO Register Controller",
    "Constraint Controller",
    "Motor Group 'Controller'",
    "Measurement Group 'Controller'",
    "Out of bounds controller"
};

/**
 * The type of algorithm used by the 0D experiment channel
 */
enum ZeroDExpChannelCumType
{
    AVERAGE = 0,
    SUM,
    INTEGRAL,
    NO_COMPUTATION,
    ONE_SHOT,
    numCumType
};

enum AquisitionMode 
{
    aqNone = 0,
    aqTimer,
    aqMonitor,
    numAqMode
};

enum GrpEltType
{
    MOTOR = 0,
    GROUP,
    PSEUDO_MOTOR
};

enum MntGrpEltType
{
    ANY_CHANNEL = 0,
    CT_EXP_CHANNEL,
    ZEROD_EXP_CHANNEL,
    ONED_EXP_CHANNEL,
    TWOD_EXP_CHANNEL,
    PSEUDO_EXP_CHANNEL,
    MOTOR_CHANNEL
};


enum PoolState 
{ 
    ON, 
    OFF, 
    CLOSE, 
    OPEN, 
    INSERT, 
    EXTRACT, 
    MOVING, 
    STANDBY, 
    FAULT, 
    INIT, 
    RUNNING, 
    ALARM, 
    DISABLE, 
    UNKNOWN
};

//
// The state name
//

const char * const PoolStateName[] = {
    "ON",
    "OFF",
    "CLOSE",
    "OPEN",
    "INSERT",
    "EXTRACT",
    "MOVING",
    "STANDBY",
    "FAULT",
    "INIT",
    "RUNNING",
    "ALARM",
    "DISABLE",
    "UNKNOWN"
};

//==============================================================================
//
//  Pool extra attribute 
//  ---------------------
//
//
// A pool device extra attribute is defined by three informations which are:
//  1 - The extra attribute name
//  2 - The extra attribute data type
//  3 - The extra attribute write type
//
// Four data types are supported. They are:
//  - BOOLEAN
//  - LONG
//  - DOUBLE
//  - STRING
//
// Two write types are supported for each of the data type. They are:
//  - READ
//  - READ_WRITE
//
//==============================================================================


enum ExtraAttrDataType
{
    BOOLEAN = 0,
    LONG,
    DOUBLE,
    STRING,
};

enum ExtraAttrDataWrite
{
    READ = 0,
    READ_WRITE
};

struct PoolExtraAttr
{
    std::string         ExtraAttr_name;
    ExtraAttrDataType   ExtraAttr_data_type;
    ExtraAttrDataWrite  ExtraAttr_write_type;
};

}


#endif // _CPOOL_DEFS_H_
