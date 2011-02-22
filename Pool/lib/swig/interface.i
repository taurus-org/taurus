%module Pool
%{
#include "Utils.h"
#include "CtrlFiCa.h"
#include "CPoolDefs.h"
#include "CPoolExcept.h"
#include "CPoolData.h"
#include "CPoolElementEvent.h"
#include "CPoolElement.h"
#include "CPoolController.h"
#include "CPoolMoveable.h"
#include "CPoolMotor.h"
#include "CPoolCommunicationChannel.h"
#include "CPoolCTExpChannel.h"
#include "CPoolMeasurementGroup.h"
#include "CPoolPseudoMotor.h"
#include "CPoolMotorGroup.h"
#include "CPoolPseudoCounter.h"
#include "CPoolZeroDExpChannel.h"
#include "CPoolOneDExpChannel.h"
#include "CPoolTwoDExpChannel.h"
#include "CPoolIORegister.h"
#include "CPoolElementContainer.h"
#include "CPool.h"
%}

%include "Utils.h"
%include "CPoolDefs.h"
%include "CPoolExcept.h"
%include "CPoolData.h"
%include "CPoolElementEvent.h"
%include "CPoolElement.h"

%template(DValuablePoolElement) Pool_ns::ValuablePoolElement<double>;
%template(IValuablePoolElement) Pool_ns::ValuablePoolElement<int32_t>;

%include "CPoolController.h"
%include "CPoolMoveable.h"
%include "CPoolMotor.h"
%include "CPoolCommunicationChannel.h"
%include "CPoolCTExpChannel.h"
%include "CPoolMeasurementGroup.h"
%include "CPoolPseudoMotor.h"
%include "CPoolMotorGroup.h"
%include "CPoolPseudoCounter.h"
%include "CPoolZeroDExpChannel.h"
%include "CPoolOneDExpChannel.h"
%include "CPoolTwoDExpChannel.h"
%include "CPoolIORegister.h"
%include "CPoolElementContainer.h"
%include "CPool.h"



