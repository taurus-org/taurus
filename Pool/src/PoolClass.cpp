static const char *RcsId     = "$Header$";
static const char *TagName   = "$Name$";
static const char *HttpServer= "http://www.esrf.fr/computing/cs/tango/tango_doc/ds_doc/";
//+=============================================================================
//
// file :        PoolClass.cpp
//
// description : C++ source for the PoolClass. A singleton
//               class derived from DeviceClass. It implements the
//               command list and all properties and methods required
//               by the Pool once per process.
//
// project :     TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.59  2007/08/20 06:37:32  tcoutinho
// development commit
//
// Revision 1.58  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.57  2007/08/08 08:47:55  tcoutinho
// Fix bug 18 : CreateController should be a one step operation
//
// Revision 1.56  2007/07/30 11:01:00  tcoutinho
// Fix bug 5 : Additional information for controllers
//
// Revision 1.55  2007/07/26 10:25:15  tcoutinho
// - Fix bug 1 :  Automatic temporary MotorGroup/MeasurementGroup deletion
//
// Revision 1.54  2007/07/17 11:41:57  tcoutinho
// replaced comunication with communication
//
// Revision 1.53  2007/07/04 15:06:38  tcoutinho
// first commit with stable Pool API
//
// Revision 1.52  2007/07/02 14:46:37  tcoutinho
// first stable comunication channel commit
//
// Revision 1.51  2007/06/28 07:15:34  tcoutinho
// safety commit during comunication channels development
//
// Revision 1.50  2007/06/27 10:24:45  tcoutinho
// scond commit for comuncation channels. Added command/attribute skeleton with pogo
//
// Revision 1.49  2007/06/13 15:18:58  etaurel
// - Fix memory leak
//
// Revision 1.48  2007/05/17 13:04:46  etaurel
// - More cleaver management of the CtrlFiCa vector
//
// Revision 1.47  2007/05/17 07:05:45  etaurel
// - Better mgnt of Ctrl files vector
//
// Revision 1.46  2007/05/11 08:07:48  tcoutinho
// - added new propertie to allow different sleep time in CounterTimer
// - added new property to allow sleep time in 0D experiment channel
//
// Revision 1.45  2007/04/24 14:14:58  tcoutinho
// - removed extra python debug output
//
// Revision 1.44  2007/04/23 15:23:06  tcoutinho
// - changes according to Sardana metting 26-03-2007: ActiveMeasurementGroup attribute became obsolete
//
// Revision 1.43  2007/02/26 09:53:00  tcoutinho
// - Introduction of properties for defult abs_change values in measurement group with fix
//
// Revision 1.42  2007/02/26 09:46:04  tcoutinho
// - Introduction of properties for defult abs_change values in measurement group
//
// Revision 1.41  2007/02/08 08:51:15  etaurel
// - Many changes. I don't remember the list
//
// Revision 1.40  2007/02/06 09:41:02  tcoutinho
// - added MeasurementGroup
//
// Revision 1.39  2007/01/26 08:36:48  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.38  2007/01/23 08:27:21  tcoutinho
// - fix some pm bugs found with the test procedure
// - added internal event for MotionEnded
//
// Revision 1.37  2007/01/16 14:32:21  etaurel
// - Coomit after a first release with CT
//
// Revision 1.36  2007/01/05 15:02:38  etaurel
// - First implementation of the Counter Timer class
//
// Revision 1.35  2007/01/04 11:55:04  etaurel
// - Added the CounterTimer controller
//
// Revision 1.34  2006/12/18 11:37:10  etaurel
// - Features are only boolean values invisible from the external world
// - ExtraFeature becomes ExtraAttribute with data type of the old features
//
// Revision 1.33  2006/12/13 10:32:37  tcoutinho
// -comment python module tracer code
//
// Revision 1.32  2006/12/12 11:09:18  tcoutinho
// - support for pseudo motors and motor groups in a motor group
//
// Revision 1.31  2006/11/20 14:32:43  etaurel
// - Add ghost group and event on motor group position attribute
//
// Revision 1.30  2006/11/07 14:57:09  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
// Revision 1.29  2006/10/27 14:43:02  etaurel
// - New management of the MaxDevice stuff
// - SendToCtrl cmd added
// - Some bug fixed in prop management
//
// Revision 1.28  2006/10/06 14:58:55  tcoutinho
// fix strange behaviour from Pogo
//
// Revision 1.27  2006/10/06 13:30:43  tcoutinho
// changed info command names, added properties functionality
//
// Revision 1.26  2006/10/02 09:19:12  etaurel
// - Motor controller now supports extra features (both CPP and Python)
//
// Revision 1.25  2006/09/27 15:15:50  etaurel
// - ExternalFile and CtrlFile has been splitted in several classes:
//   ExternalFile, CppCtrlFile, PyExternalFile and PyCtrlFile
//
// Revision 1.24  2006/09/21 12:44:41  tcoutinho
// - python path changes
//
// Revision 1.23  2006/09/21 10:20:53  etaurel
// - The motor group do not ID any more
//
// Revision 1.22  2006/09/21 07:25:57  etaurel
// - Changes due to the removal of Motor ID in the Tango interface
//
// Revision 1.21  2006/09/20 16:07:51  tcoutinho
// pseudo motor API changed
//
// Revision 1.20  2006/09/20 15:58:43  tcoutinho
// pseudo motor API changed
//
// Revision 1.19  2006/09/20 13:11:12  etaurel
// - For the user point of view, the controller does not have ID any more.
// We are now using the controller instance name (uniq) to give them a name
//
// Revision 1.18  2006/09/19 13:57:35  tcoutinho
// pseudo motor with test procedure clear.
//
// Revision 1.17  2006/09/19 09:57:12  etaurel
// - Commit after the controller, motor and motor_group test sequences works after the merge
//
// Revision 1.16  2006/09/19 07:24:31  tcoutinho
// - changes to make pseudo motor interface homogenous with the rest of the Pool
//
// Revision 1.15  2006/09/18 10:32:22  etaurel
// - Commit after merge with pseudo-motor branch
//
// Revision 1.14  2006/07/07 12:38:42  etaurel
// - Some changes in file header
// - Commit after implementing the group multi motor read
//
// Revision 1.13  2006/06/28 15:56:46  etaurel
// - Commit after first series of tests
//
// Revision 1.12  2006/06/15 15:36:31  etaurel
// - many changes after due to first test suite only on controller related stuff!!!
//
// Revision 1.11  2006/06/12 10:28:57  etaurel
// - Many changes dur to bug fixes found when writing test units...
//
// Revision 1.10  2006/05/26 09:12:52  etaurel
// - Add some exception checking between the thread used to move motor and the
// write_Position method
//
// Revision 1.9  2006/05/25 09:13:47  etaurel
// - Stop Pool startup sequence in case Python LoadModule failed
// - Add logging possibility in the CtrlFiCa and CtrlFile classes
//
// Revision 1.8  2006/05/24 14:12:50  etaurel
// - Again many changes
//
// Revision 1.7  2006/03/29 07:09:00  etaurel
// - Added motor group features
//
// Revision 1.6  2006/03/20 08:25:52  etaurel
// - Commit changes before changing the Motor interface
//
// Revision 1.5  2006/03/16 08:05:45  etaurel
// - Added code for the ControllerCode load and unload commands
// - Test and debug InnitController cmd with motor attached to the controller
//
// Revision 1.4  2006/03/14 14:54:09  etaurel
// - Again new changes in the internal structure
//
// Revision 1.3  2006/03/14 08:44:06  etaurel
// - Change the orders of the CreateController command arguments
//
// Revision 1.2  2006/03/14 08:25:11  etaurel
// - Change the way objects are aorganized within the pool device
//
// Revision 1.1.1.1  2006/03/10 13:40:57  etaurel
// Initial import
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//-=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================

#include "CtrlFiCa.h"
#include <tango.h>

#include "Pool.h"
#include "PoolClass.h"

#include "PyMotCtrlFile.h"
#include "CppMotCtrlFile.h"

extern "C"
{

// typedef Tango::DeviceClass *(*Cpp_creator_ptr)(const char *);

Tango::DeviceClass* _create_libPool_class(const char *n)
{
    std::string class_name(n);
    Tango::DeviceClass* ret = NULL;

    if (class_name == "Pool")
    {
        std::cout << "Dynamic load of Pool" << std::endl;
        ret = static_cast<Tango::DeviceClass*>(Pool_ns::PoolClass::init("Pool"));
    }
    std::cout << "Done " << ret->get_name() << std::endl;
    return ret;
}

}

namespace Pool_ns
{
//+----------------------------------------------------------------------------
//
// method : 		DeleteIORegisterCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteIORegisterCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteIORegisterCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);
    
    ((static_cast<Pool *>(device))->delete_ioregister(argin));

    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateIORegisterCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateIORegisterCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateIORegisterCmd::execute(): arrived" << endl;

    const Tango::DevVarLongStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_ioregister(argin));

    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		PutFileCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *PutFileCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "PutFileCmd::execute(): arrived" << endl;

    const Tango::DevVarCharArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->put_file(argin));
    
    return new CORBA::Any();
}


//+----------------------------------------------------------------------------
//
// method : 		GetFileClass::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *GetFileClass::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "GetFileClass::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    return insert((static_cast<Pool *>(device))->get_file(argin));    
}

//+----------------------------------------------------------------------------
//
// method : 		DeletePseudoCounterCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeletePseudoCounterCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeletePseudoCounterCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_pseudo_counter(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		GetControllerInfoExCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *GetControllerInfoExCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "GetControllerInfoExCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    return insert((static_cast<Pool *>(device))->get_controller_info_ex(argin));
}

//+----------------------------------------------------------------------------
//
// method : 		DeleteComChannelCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteComChannelCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteComChannelCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_com_channel(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateComChannelCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateComChannelCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateComChannelCmd::execute(): arrived" << endl;

    const Tango::DevVarLongStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_com_channel(argin));

    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		DeleteMeasurementGroupCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteMeasurementGroupCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteMeasurementGroupCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_measurement_group(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateMeasurementGroupCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateMeasurementGroupCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateMeasurementGroupCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_measurement_group(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		DeleteExpChannelCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteExpChannelCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteExpChannelCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_exp_channel(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateExpChannelCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateExpChannelCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateExpChannelCmd::execute(): arrived" << endl;

    const Tango::DevVarLongStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_exp_channel(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		SendToControllerCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *SendToControllerCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "SendToControllerCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    return insert((static_cast<Pool *>(device))->send_to_controller(argin));
}

//+----------------------------------------------------------------------------
//
// method : 		GetControllerInfoCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *GetControllerInfoCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "GetControllerInfoCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    return insert((static_cast<Pool *>(device))->get_controller_info(argin));
}


//+----------------------------------------------------------------------------
//
// method : 		DeleteMotorGroupCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteMotorGroupCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteMotorGroupCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_motor_group(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateMotorGroupCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateMotorGroupCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateMotorGroupCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_motor_group(argin));

    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		DeleteMotorCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteMotorCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteMotorCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_motor(argin));

    return new CORBA::Any();
}



//+----------------------------------------------------------------------------
//
// method : 		ReloadControllerCodeCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *ReloadControllerCodeCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "ReloadControllerCodeCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->reload_controller_code(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateMotorCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateMotorCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateMotorCmd::execute(): arrived" << endl;

    const Tango::DevVarLongStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_motor(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		InitControllerCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *InitControllerCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "InitControllerCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->init_controller(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		DeleteControllerCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteControllerCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteControllerCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_controller(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateControllerCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateControllerCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateControllerCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_controller(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		DeletePseudoMotorClass::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeletePseudoMotorClass::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeletePseudoMotorClass::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_pseudo_motor(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		DeleteElementCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *DeleteElementCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "DeleteElementCmd::execute(): arrived" << endl;

    Tango::DevString	argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->delete_element(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		CreateElementCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *CreateElementCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "CreateElementCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->create_element(argin));
    
    return new CORBA::Any();
}

//+----------------------------------------------------------------------------
//
// method : 		RenameElementCmd::execute()
// 
// description : 	method to trigger the execution of the command.
//                PLEASE DO NOT MODIFY this method core without pogo   
//
// in : - device : The device on which the command must be excuted
//		- in_any : The command input data
//
// returns : The command output data (packed in the Any object)
//
//-----------------------------------------------------------------------------
CORBA::Any *RenameElementCmd::execute(Tango::DeviceImpl *device,const CORBA::Any &in_any)
{

    cout2 << "RenameElementCmd::execute(): arrived" << endl;

    const Tango::DevVarStringArray	*argin;
    extract(in_any, argin);

    ((static_cast<Pool *>(device))->rename_element(argin));
    
    return new CORBA::Any();
}

//
//----------------------------------------------------------------
//	Initialize pointer for singleton pattern
//----------------------------------------------------------------
//
PoolClass *PoolClass::_instance = NULL;

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::PoolClass(string &s)
// 
// description : 	constructor for the PoolClass
//
// in : - s : The class name
//
//-----------------------------------------------------------------------------
PoolClass::PoolClass(string &s):DeviceClass(s)
{

    cout2 << "Entering PoolClass constructor" << endl;
    set_default_property();
    get_class_property();
    write_class_property();
    
/*	get_class_property();
    set_default_property();
    write_class_property();*/

//
// Reserve place in the vector in advance in order to be able
// to keep pointer on this svector valid whatever the element 
// number is
//

    ctrl_ficas.reserve(MAX_FICA);
    ctrl_files.reserve(MAX_FILE);

    cout2 << "Leaving PoolClass constructor" << endl;

}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::~PoolClass()
// 
// description : 	destructor for the PoolClass
//
//-----------------------------------------------------------------------------
PoolClass::~PoolClass()
{
    this->clear_ctrl_ficas();
    this->clear_ctrl_files();

    PythonUtils::instance()->finalize();
    
    _instance = NULL;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::instance
// 
// description : 	Create the object if not already done. Otherwise, just
//			return a pointer to the object
//
// in : - name : The class name
//
//-----------------------------------------------------------------------------
PoolClass *PoolClass::init(const char *name)
{
    if (_instance == NULL)
    {
        try
        {
            string s(name);
            _instance = new PoolClass(s);
        }
        catch (bad_alloc)
        {
            throw;
        }		
    }		
    return _instance;
}

PoolClass *PoolClass::instance()
{
    if (_instance == NULL)
    {
        cerr << "Class is not initialised !!" << endl;
        exit(-1);
    }
    return _instance;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::command_factory
// 
// description : 	Create the command object(s) and store them in the 
//			command list
//
//-----------------------------------------------------------------------------
void PoolClass::command_factory()
{
    command_list.push_back(new CreateControllerCmd("CreateController",
        Tango::DEVVAR_STRINGARRAY, Tango::DEV_VOID,
        "in[0] = Controller dev type, in[1] = Controller lib, in[2] = Controller name, in[3] = Instance name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new CreateExpChannelCmd("CreateExpChannel",
        Tango::DEVVAR_LONGSTRINGARRAY, Tango::DEV_VOID,
        "long[0] = Exp Channel number in Ctrl, string[0] = Exp Channel name, string[1] = Controller instance name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new CreateMotorCmd("CreateMotor",
        Tango::DEVVAR_LONGSTRINGARRAY, Tango::DEV_VOID,
        "long[0] = Motor number in Ctrl, string[0] = Motor name, string[1] = Controller instance name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new CreateMotorGroupCmd("CreateMotorGroup",
        Tango::DEVVAR_STRINGARRAY, Tango::DEV_VOID,
        "Group name followed by motor's name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteControllerCmd("DeleteController",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "The controller name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteExpChannelCmd("DeleteExpChannel",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Exp Channel name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteMotorCmd("DeleteMotor",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Motor name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteMotorGroupCmd("DeleteMotorGroup",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "The motor group name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeletePseudoMotorClass("DeletePseudoMotor",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Pseudo Motor name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new GetControllerInfoCmd("GetControllerInfo",
        Tango::DEVVAR_STRINGARRAY, Tango::DEVVAR_STRINGARRAY,
        "in[0] - Controller type, in[1] - Controller file name, in[2] - Controller class name, in[3] - Controller instance name (optional)",
        "Controller class data",
        Tango::OPERATOR));
    command_list.push_back(new InitControllerCmd("InitController",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Controller name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new ReloadControllerCodeCmd("ReloadControllerCode",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Controller file name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new SendToControllerCmd("SendToController",
        Tango::DEVVAR_STRINGARRAY, Tango::DEV_STRING,
        "In[0] = Controller name, In[1] = String to send",
        "The controller answer",
        Tango::OPERATOR));
    command_list.push_back(new CreateMeasurementGroupCmd("CreateMeasurementGroup",
        Tango::DEVVAR_STRINGARRAY, Tango::DEV_VOID,
        "Measurement Group name followed by names of the elements",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteMeasurementGroupCmd("DeleteMeasurementGroup",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "The motor group name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new CreateComChannelCmd("CreateComChannel",
        Tango::DEVVAR_LONGSTRINGARRAY, Tango::DEV_VOID,
        "long[0] = Communication Channel number in Ctrl, string[0] = communication Channel name, string[1] = Controller instance name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteComChannelCmd("DeleteComChannel",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Communication Channel name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new GetControllerInfoExCmd("GetControllerInfoEx",
        Tango::DEVVAR_STRINGARRAY, Tango::DEVVAR_CHARARRAY,
        "in[0] - Controller type, in[1] - Controller file name, in[2] - Controller class name",
        "Controller class data",
        Tango::OPERATOR));
    command_list.push_back(new DeletePseudoCounterCmd("DeletePseudoCounter",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Pseudo Motor name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new GetFileClass("GetFile",
        Tango::DEV_STRING, Tango::DEVVAR_CHARARRAY,
        "complete(with absolute path) file name",
        "File data",
        Tango::OPERATOR));
    command_list.push_back(new PutFileCmd("PutFile",
        Tango::DEVVAR_CHARARRAY, Tango::DEV_VOID,
        "complete filename (inc. absolute path)+'\0'+\nusername+'\0'+\ndescription of the change+'\0'+\nfile data",
        "",
        Tango::OPERATOR));
    command_list.push_back(new CreateIORegisterCmd("CreateIORegister",
        Tango::DEVVAR_LONGSTRINGARRAY, Tango::DEV_VOID,
        "long[0] = IORegister number in Ctrl, string[0] = IORegister name, string[1] = Controller instance name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteIORegisterCmd("DeleteIORegister",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "IORegister name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new CreateElementCmd("CreateElement",
        Tango::DEVVAR_STRINGARRAY, Tango::DEV_VOID,
        "1 - Type of element (Motor, CounterTimer, ZeroDExpChannel, CommunicationChannel, etc)\n"
        "2 - The element instance name.\n"
        "3 - The controller instance name.\n"
        "4 - The index (aka axis) in the controller.\n"
        "n,n+1 - Pairs of optional parameters. The valid first string in the pair values are:\n"
        "  Description - second string is the element description.\n"
        "  TangoDevName - override the default tango name that the pool gives to the element",
        "",
        Tango::OPERATOR));
    command_list.push_back(new DeleteElementCmd("DeleteElement",
        Tango::DEV_STRING, Tango::DEV_VOID,
        "Element instance name",
        "",
        Tango::OPERATOR));
    command_list.push_back(new RenameElementCmd("RenameElement",
        Tango::DEVVAR_STRINGARRAY, Tango::DEV_VOID,
        "1 - old instance name\n"
        "2 - new instance name.",
        "",
        Tango::OPERATOR));
        
    //	add polling if any
    for (unsigned int i=0 ; i<command_list.size(); i++)
    {
    }
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_class_property
// 
// description : 	Get the class property for specified name.
//
// in :		string	name : The property name
//
//+----------------------------------------------------------------------------
Tango::DbDatum PoolClass::get_class_property(string &prop_name)
{
    for (unsigned int i=0 ; i<cl_prop.size() ; i++)
        if (cl_prop[i].name == prop_name)
            return cl_prop[i];
    //	if not found, return  an empty DbDatum
    return Tango::DbDatum(prop_name);
}
//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_default_device_property()
// 
// description : 	Return the default value for device property.
//
//-----------------------------------------------------------------------------
Tango::DbDatum PoolClass::get_default_device_property(string &prop_name)
{
    for (unsigned int i=0 ; i<dev_def_prop.size() ; i++)
        if (dev_def_prop[i].name == prop_name)
            return dev_def_prop[i];
    //	if not found, return  an empty DbDatum
    return Tango::DbDatum(prop_name);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_default_class_property()
// 
// description : 	Return the default value for class property.
//
//-----------------------------------------------------------------------------
Tango::DbDatum PoolClass::get_default_class_property(string &prop_name)
{
    for (unsigned int i=0 ; i<cl_def_prop.size() ; i++)
        if (cl_def_prop[i].name == prop_name)
            return cl_def_prop[i];
    //	if not found, return  an empty DbDatum
    return Tango::DbDatum(prop_name);
}
//+----------------------------------------------------------------------------
//
// method : 		PoolClass::device_factory
// 
// description : 	Create the device object(s) and store them in the 
//			device list
//
// in :		Tango::DevVarStringArray *devlist_ptr : The device name list
//
//-----------------------------------------------------------------------------
void PoolClass::device_factory(const Tango::DevVarStringArray *devlist_ptr)
{

    if (devlist_ptr->length() > 1)
    {
        TangoSys_OMemStream o;
        o << "It is not allowed to have more than one device of the Pool class. ";
        o << "You actually have " << devlist_ptr->length() << " devices defined." << ends;
        
        Tango::Except::throw_exception((const char *)"Pool_TooManyDevies",
                    o.str(),
                        (const char *)"PoolClass::device_factory");
    }
    
    //	Create all devices.(Automatic code generation)
    //-------------------------------------------------------------
    for (unsigned long i=0 ; i < devlist_ptr->length() ; i++)
    {
        cout4 << "Device name : " << (*devlist_ptr)[i].in() << endl;
                        
        // Create devices and add it into the device list
        //----------------------------------------------------
        device_list.push_back(new Pool(this, (*devlist_ptr)[i]));

        // Export device to the outside world
        // Check before if database used.
        //---------------------------------------------
        if ((Tango::Util::_UseDb == true) && (Tango::Util::_FileDb == false))
            export_device(device_list.back());
        else
            export_device(device_list.back(), (*devlist_ptr)[i]);
    }
    //	End of Automatic code generation
    //-------------------------------------------------------------

}
//+----------------------------------------------------------------------------
//	Method: PoolClass::attribute_factory(vector<Tango::Attr *> &att_list)
//-----------------------------------------------------------------------------
void PoolClass::attribute_factory(vector<Tango::Attr *> &att_list)
{
    //	Attribute : SimulationMode
    SimulationModeAttrib	*simulation_mode = new SimulationModeAttrib();
    Tango::UserDefaultAttrProp	simulation_mode_prop;
    simulation_mode_prop.set_label("Simulation mode");
    simulation_mode_prop.set_description("Set pool in simulation mode. When the pool is switched \nto simulation mode, all the actions on motor are still\npossible but not forwarded to the associated controller.");
    simulation_mode->set_default_properties(simulation_mode_prop);
    att_list.push_back(simulation_mode);

    //	Attribute : ControllerClassList
    ControllerClassListAttrib	*controller_class_list = new ControllerClassListAttrib();
    Tango::UserDefaultAttrProp	controller_class_list_prop;
    controller_class_list_prop.set_label("Controller Class List");
    controller_class_list_prop.set_description("Contains the list of existing controller classes found in the PoolPath property");
    controller_class_list->set_default_properties(controller_class_list_prop);
    att_list.push_back(controller_class_list);

    //	Attribute : ControllerList
    ControllerListAttrib	*controller_list = new ControllerListAttrib();
    Tango::UserDefaultAttrProp	controller_list_prop;
    controller_list_prop.set_label("Controller list");
    controller_list_prop.set_description("Get the list of controller defines in the device pool. For each controller, its name and it full name are\nreturned in the following format :\n<name> (<file_name>.<controller name>/<instance name>) - Ctrl type (file_name)");
    controller_list->set_default_properties(controller_list_prop);
    att_list.push_back(controller_list);

    //	Attribute : ExpChannelList
    ExpChannelListAttrib	*exp_channel_list = new ExpChannelListAttrib();
    Tango::UserDefaultAttrProp	exp_channel_list_prop;
    exp_channel_list_prop.set_label("Motor name list");
    exp_channel_list_prop.set_description("Return the list of devices defined in the pool device. For each motor it is returned the motor \nidentificator, the motor alias and the motor tango name in the following format\n<Identificator> - <Alias> (<Tango device name>)");
    exp_channel_list->set_default_properties(exp_channel_list_prop);
    att_list.push_back(exp_channel_list);

    //	Attribute : MeasurementGroupList
    MeasurementGroupListAttrib	*measurement_group_list = new MeasurementGroupListAttrib();
    Tango::UserDefaultAttrProp	measurement_group_list_prop;
    measurement_group_list_prop.set_label("Measurement Group List");
    measurement_group_list_prop.set_description("Return the list of measurement groups defined in the pool device. For each measurement group it is returned the measurement group name,\nthe tango device name and the list of data aquisition elements belonging to this measurement group.\n \n");
    measurement_group_list->set_default_properties(measurement_group_list_prop);
    att_list.push_back(measurement_group_list);

    //	Attribute : MotorGroupList
    MotorGroupListAttrib	*motor_group_list = new MotorGroupListAttrib();
    Tango::UserDefaultAttrProp	motor_group_list_prop;
    motor_group_list_prop.set_description("Return the list of devices defined in the pool device. For each motor group it is returned the motor group\nname and the motor group tango name in the following format\n<Identificator> - <Alias> (<Tango device name>)");
    motor_group_list->set_default_properties(motor_group_list_prop);
    att_list.push_back(motor_group_list);

    //	Attribute : MotorList
    MotorListAttrib	*motor_list = new MotorListAttrib();
    Tango::UserDefaultAttrProp	motor_list_prop;
    motor_list_prop.set_label("Motor name list");
    motor_list_prop.set_description("Return the list of devices defined in the pool device. For each motor it is returned the motor \nidentificator, the motor alias and the motor tango name in the following format\n<Identificator> - <Alias> (<Tango device name>)");
    motor_list->set_default_properties(motor_list_prop);
    att_list.push_back(motor_list);

    //	Attribute : PseudoMotorList
    PseudoMotorListAttrib	*pseudo_motor_list = new PseudoMotorListAttrib();
    Tango::UserDefaultAttrProp	pseudo_motor_list_prop;
    pseudo_motor_list_prop.set_description("Return the list of devices defined in the pool device. For each pseudo motor it is returned the pseudo\nmotor name, the tango name in the following format\n<Identificator> - <Alias> (<Tango device name>)");
    pseudo_motor_list->set_default_properties(pseudo_motor_list_prop);
    att_list.push_back(pseudo_motor_list);

    //	Attribute : ComChannelList
    ComChannelListAttrib	*com_channel_list = new ComChannelListAttrib();
    Tango::UserDefaultAttrProp	com_channel_list_prop;
    com_channel_list_prop.set_label("Communication channel list");
    com_channel_list_prop.set_description("Return the list of communication channel devices defined in the pool device. For each communication channel it is returned the communication channel\nalias and the channel tango name in the following format\n<Alias> (<Tango device name>)");
    com_channel_list->set_default_properties(com_channel_list_prop);
    att_list.push_back(com_channel_list);

    //	Attribute : PseudoCounterList
    PseudoCounterListAttrib	*pseudo_counter_list = new PseudoCounterListAttrib();
    Tango::UserDefaultAttrProp	pseudo_counter_list_prop;
    pseudo_counter_list_prop.set_label("Pseudo Counter List");
    pseudo_counter_list_prop.set_description("Return the list of devices defined in the pool device. For each pseudo counter it is returned the pseudo\ncounter name, the tango name in the following format\n<Identificator> - <Alias> (<Tango device name>)");
    pseudo_counter_list->set_default_properties(pseudo_counter_list_prop);
    att_list.push_back(pseudo_counter_list);

    //	Attribute : IORegisterList
    IORegisterListAttrib	*ioregister_list = new IORegisterListAttrib();
    Tango::UserDefaultAttrProp	ioregister_list_prop;
    ioregister_list_prop.set_label("IORegister list");
    ioregister_list_prop.set_description("Return the list of ioregister devices defined in the pool device. For each ioregister it is returned the ioregister\nalias and the channel tango name in the following format\n<Alias> (<Tango device name>)");
    ioregister_list->set_default_properties(ioregister_list_prop);
    att_list.push_back(ioregister_list);

    //	Attribute : InstrumentList
    InstrumentListAttrib	*instrument_list = new InstrumentListAttrib();
    Tango::UserDefaultAttrProp	instrument_list_prop;
    instrument_list_prop.set_label("Instrument list");
    instrument_list_prop.set_description("Return the list of instruments defined in the pool device. For each Instrument it is returned the instrument\nname in the following format\n<full instrument name> (<instrument type>)");
    instrument_list->set_default_properties(instrument_list_prop);
    att_list.push_back(instrument_list);

    //	End of Automatic code generation
    //-------------------------------------------------------------
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_class_property()
// 
// description : 	Read the class properties from database.
//
//-----------------------------------------------------------------------------
void PoolClass::get_class_property()
{
    //	Initialize your default values here (if not done with  POGO).
    //------------------------------------------------------------------

    //	Read class properties from database.(Automatic code generation)
    //------------------------------------------------------------------

    //	Call database and extract values
    //--------------------------------------------
    if (Tango::Util::instance()->_UseDb==true)
        get_db_class()->get_property(cl_prop);
    Tango::DbDatum	def_prop;


    //	End of Automatic code generation
    //------------------------------------------------------------------

}

//+----------------------------------------------------------------------------
//
// method : 	PoolClass::set_default_property
// 
// description: Set default property (class and device) for wizard.
//              For each property, add to wizard property name and description
//              If default value has been set, add it to wizard property and
//              store it in a DbDatum.
//
//-----------------------------------------------------------------------------
void PoolClass::set_default_property()
{
    string	prop_name;
    string	prop_desc;
    string	prop_def;

    vector<string>	vect_data;
    //	Set Default Class Properties
    //	Set Default Device Properties
    prop_name = "PoolPath";
    prop_desc = "Path for pool external stuff (C++ shared libraries or Python modules)";
    prop_def  = "";
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultMotPos_AbsChange";
    prop_desc = "Default value for motor position attribute abs_change property";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultMotGrpPos_AbsChange";
    prop_desc = "Default value for motor group position attribute abs_change property";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "GhostGroup_PollingPeriod";
    prop_desc = "Polling period for the ghost motor group";
    prop_def  = "5000";
    vect_data.clear();
    vect_data.push_back("5000");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "MotThreadLoop_SleepTime";
    prop_desc = "Sleep time in the motion thread loop in mS";
    prop_def  = "10";
    vect_data.clear();
    vect_data.push_back("10");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "NbStatePerRead";
    prop_desc = "Number of State to be done before doing a read in the motion thread";
    prop_def  = "10";
    vect_data.clear();
    vect_data.push_back("10");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultCtVal_AbsChange";
    prop_desc = "Default value for counter value attribute abs_change property";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "ZeroDNbReadPerEvent";
    prop_desc = "Number of read between firing event during the Zero D Exp Channel\nacquisition loop";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultZeroDVal_AbsChange";
    prop_desc = "Default value for Zero D Cumulated value attribute abs_change property";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultCtGrpVal_AbsChange";
    prop_desc = "The default abs_change value for Counter/Timer value attributes in a Measurement Group";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultZeroDGrpVal_AbsChange";
    prop_desc = "The default abs_change value for 0D Channel value attributes in a Measurement Group";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "CTThreadLoop_SleepTime";
    prop_desc = "Sleep time in the motion thread loop in mS";
    prop_def  = "10";
    vect_data.clear();
    vect_data.push_back("10");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "ZeroDThreadLoop_SleepTime";
    prop_desc = "Sleep time in the motion thread loop in mS";
    prop_def  = "20";
    vect_data.clear();
    vect_data.push_back("20");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "TmpElement_MaxInactTime";
    prop_desc = "Maximum inactivity time for temporary objects.\nUnits are multiples of GhostGroup_PollingPeriod.\nIf a temporary object (motor/measurement group created with a '__'\nprefix in its name) does not receive a command/attribute request for\nthis amount of time, it is marked for deletion.\n";
    prop_def  = "60";
    vect_data.clear();
    vect_data.push_back("60");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "OneDNbReadPerEvent";
    prop_desc = "Number of read between firing event during the One D Exp Channel\nacquisition loop";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "OneDThreadLoop_SleepTime";
    prop_desc = "Sleep time in the motion thread loop in mS";
    prop_def  = "20";
    vect_data.clear();
    vect_data.push_back("20");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultOneDVal_AbsChange";
    prop_desc = "Default value for One D Cumulated value attribute abs_change property";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "DefaultOneDGrpVal_AbsChange";
    prop_desc = "bs_change value for 1D Channel value attributes in a Measurement Group";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "TwoDNbReadPerEvent";
    prop_desc = "Number of read between firing event during the Two D Exp Channel\nacquisition loop";
    prop_def  = "5";
    vect_data.clear();
    vect_data.push_back("5");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "TwoDThreadLoop_SleepTime";
    prop_desc = "Sleep time in the motion thread loop in mS";
    prop_def  = "20";
    vect_data.clear();
    vect_data.push_back("20");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);

    prop_name = "Version";
    prop_desc = "Pool version in the database";
    prop_def  = "0.1.0";
    vect_data.clear();
    vect_data.push_back("0.1.0");
    if (prop_def.length()>0)
    {
        Tango::DbDatum	data(prop_name);
        data << vect_data ;
        dev_def_prop.push_back(data);
        add_wiz_dev_prop(prop_name, prop_desc,  prop_def);
    }
    else
        add_wiz_dev_prop(prop_name, prop_desc);
}
//+----------------------------------------------------------------------------
//
// method : 		PoolClass::write_class_property
// 
// description : 	Set class description as property in database
//
//-----------------------------------------------------------------------------
void PoolClass::write_class_property()
{
    //	First time, check if database used
    //--------------------------------------------
    if (Tango::Util::_UseDb == false)
        return;

    Tango::DbData	data;
    string	classname = get_name();
    string	header;
    string::size_type	start, end;

    //	Put title
    Tango::DbDatum	title("ProjectTitle");
    string	str_title("Device pool");
    title << str_title;
    data.push_back(title);

    //	Put Description
    Tango::DbDatum	description("Description");
    vector<string>	str_desc;
    str_desc.push_back("  ");
    description << str_desc;
    data.push_back(description);
        
    //	put cvs location
    string	rcsId(RcsId);
    string	filename(classname);
    start = rcsId.find("/");
    if (start!=string::npos)
    {
        filename += "Class.cpp";
        end   = rcsId.find(filename);
        if (end>start)
        {
            string	strloc = rcsId.substr(start, end-start);
            //	Check if specific repository
            start = strloc.find("/cvsroot/");
            if (start!=string::npos && start>0)
            {
                string	repository = strloc.substr(0, start);
                if (repository.find("/segfs/")!=string::npos)
                    strloc = "ESRF:" + strloc.substr(start, strloc.length()-start);
            }
            Tango::DbDatum	cvs_loc("cvs_location");
            cvs_loc << strloc;
            data.push_back(cvs_loc);
        }
    }

    //	Get CVS tag revision
    string	tagname(TagName);
    header = "$Name: ";
    start = header.length();
    string	endstr(" $");
    end   = tagname.find(endstr);
    if (end!=string::npos && end>start)
    {
        string	strtag = tagname.substr(start, end-start);
        Tango::DbDatum	cvs_tag("cvs_tag");
        cvs_tag << strtag;
        data.push_back(cvs_tag);
    }

    //	Get URL location
    string	httpServ(HttpServer);
    if (httpServ.length()>0)
    {
        Tango::DbDatum	db_doc_url("doc_url");
        db_doc_url << httpServ;
        data.push_back(db_doc_url);
    }

    //  Put inheritance
    Tango::DbDatum	inher_datum("InheritedFrom");
    vector<string> inheritance;
    inheritance.push_back("DevicePool");
    inheritance.push_back("Device_4Impl");
    inher_datum << inheritance;
    data.push_back(inher_datum);

    //	Call database and and values
    //--------------------------------------------
    get_db_class()->put_property(data);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::str_2_CtrlType()
// 
// description : 	Return the controller device type as a CtrlType enumeration
//					value from a string
//
// arg(s) : - type : The controller device type as a string
//
//-----------------------------------------------------------------------------
/*
CtrlType PoolClass::str_2_CtrlType(string &type)
{
//
// controller object type string in lower case
//

    string obj_type_lower(type);
    transform(obj_type_lower.begin(),obj_type_lower.end(),obj_type_lower.begin(),::tolower);

//
// Convert string to one value of the CtrlType enumeration
//
    
    CtrlType o_type = UNDEF_CTRL;

    if (obj_type_lower == "motor")
        o_type = MOTOR_CTRL;
    else if (obj_type_lower == "pseudomotor")
        o_type = PSEUDO_MOTOR_CTRL;
    else if (obj_type_lower == "countertimer")
        o_type = COTI_CTRL;
    else if (obj_type_lower == "zerodexpchannel")
        o_type = ZEROD_CTRL;
    else if (obj_type_lower == "onedexpchannel")
        o_type = ONED_CTRL;
    else if (obj_type_lower == "twodexpchannel")
        o_type = TWOD_CTRL;
    else if (obj_type_lower == "pseudocounter")
        o_type = PSEUDO_COUNTER_CTRL;
    else if (obj_type_lower == "communication")
        o_type = COM_CTRL;
    else if (obj_type_lower == "ioregister")
        o_type = IOREGISTER_CTRL;
    else if (obj_type_lower == "undefined")
        o_type = UNDEF_CTRL;
    else
    {
        TangoSys_OMemStream o;
        o << "Controller of type " << type << " unsupported" << ends;

        Tango::Except::throw_exception((const char *)"Pool_UnknownControllerType",o.str(),
                        (const char *)"PoolClass::str_2_CtrlType");
    }
    
    return o_type;
}
*/
//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_ctrl_fica_by_name()
// 
// description : 	Get a controller entry by its name (file_name/ctrl_class_name)
//
//	arg(s) : - name : The controller fica name
//			 - ob_type : The controller device type
//
//-----------------------------------------------------------------------------

vector<CtrlFiCa *>::iterator PoolClass::get_ctrl_fica_by_name(string &name, CtrlType o_type)
{
    vector<CtrlFiCa *>::iterator ite;
    for (ite = ctrl_ficas.begin();ite != ctrl_ficas.end();++ite)
    {
        if ((*ite) != NULL)
        {
            if ((*ite)->get_name() == name)
            {
                if ((*ite)->get_obj_type() == o_type)
                    break;
                else
                {
                    TangoSys_OMemStream o;
                    o << name << " is defined in this pool device server but with device type ";
                    o << CtrlTypeStr[(*ite)->get_obj_type()] << ends;
            
                    Tango::Except::throw_exception((const char *)"Pool_NotDefinedCtrlFiCa",o.str(),
                                    (const char *)"PoolClass::get_ctrl_fica_by_name");
                }
            }
        }
    }
    
    if (ite == ctrl_ficas.end())
    {
        TangoSys_OMemStream o;
        o << name << " is not defined in this pool device server" << ends;

        Tango::Except::throw_exception((const char *)"Pool_NotDefinedCtrlFiCa",o.str(),
                        (const char *)"PoolClass::get_ctrl_fica_by_name");
    }
    
    return ite;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::add_ctrl_fica()
// 
// description : 	Add a new controller entry in the controller fica list
//					and returns an iterator on this new entry
//
// arg(s) : - name : The controller type (filename_lowercase_without_extension/ctrl_class_name_lowercase)
//			- f_name : The controller class file name (case dependant)
//			- ctrl_class_name : The controller class name (case dependant)
//			- obj_type : The controller device type
//			- dev : The device (for logging purpose only)
//
//-----------------------------------------------------------------------------

vector<CtrlFiCa *>::iterator PoolClass::add_ctrl_fica(string &name,
                                                      string &f_name,
                                                      string &ctrl_class_name,
                                                      CtrlType ctrl_type,
                                                      Pool *dev)
{
    vector<CtrlFiCa *>::size_type fica_nb = ctrl_ficas.size();
    vector<CtrlFiCa *>::iterator pos;
    bool free_place = false;
    
    if (fica_nb == MAX_FICA)
    {
        TangoSys_OMemStream o;
        o << "Already at max controller file/class capacity (" << MAX_FICA 
          << ")" << ends;

        Tango::Except::throw_exception(
                        (const char *)"Pool_TooManyCtrlFileClass",o.str(),
                        (const char *)"PoolClass::add_ctrl_fica");
    }
    else
    {
        pos = find(ctrl_ficas.begin(),ctrl_ficas.end(),(CtrlFiCa *)NULL);
        if (pos != ctrl_ficas.end())
            free_place = true;
            
        CtrlFiCa *ptr_fica = NULL;
        switch (ctrl_type)
        {
            case MOTOR_CTRL:
            {
                ptr_fica = new MotCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }
            
            case PSEUDO_MOTOR_CTRL:
            {
                ptr_fica = new PseudoMotCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }
            
            case COTI_CTRL:
            {
                ptr_fica = new CoTiCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }
            
            case ZEROD_CTRL:
            {
                ptr_fica = new ZeroDCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }

            case ONED_CTRL:
            {
                ptr_fica = new OneDCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }

            case TWOD_CTRL:
            {
                ptr_fica = new TwoDCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }
            
            case PSEUDO_COUNTER_CTRL:
            {
                ptr_fica = new PseudoCoCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }
            
            case COM_CTRL:
            {
                ptr_fica = new ComCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }

            case IOREGISTER_CTRL:
            {
                   ptr_fica = new IORegisterCtrlFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }

            case CONSTRAINT_CTRL:
            {
                ptr_fica = new ConstraintFiCa(name,f_name,ctrl_class_name,dev);
                break;
            }
            
            case MOTOR_GROUP_CTRL:
            case MEASUREMENT_GROUP_CTRL:
            {
                Tango::Except::throw_exception(
                        (const char *)"Pool_BadCtrlType",
                        (const char *)"Groups don't have controller type !!!",
                        (const char *)"PoolClass::add_ctrl_fica");
                break;		
            }
            
            default:
            {
                Tango::Except::throw_exception(
                        (const char *)"Pool_BadCtrlType",
                        (const char *)"Undefined controller type !!!",
                        (const char *)"PoolClass::add_ctrl_fica");
                break;
            }
        }
        if (free_place == true)
            *pos = ptr_fica;
        else
        {
            ctrl_ficas.push_back(ptr_fica);
            pos = ctrl_ficas.end() - 1;
        }

    }
        
    return pos;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::clear_ctrl_ficas()
// 
// description : 	Clear the controller fica vector
//
//-----------------------------------------------------------------------------

void PoolClass::clear_ctrl_ficas()
{
    if (ctrl_ficas.empty() == false)
    {
        vector<CtrlFiCa *>::iterator ite;
        for (ite = ctrl_ficas.begin();ite != ctrl_ficas.end();++ite)
        {
            if (*ite != NULL)
                delete *ite;
        }
        ctrl_ficas.clear();
    }

}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::print_all_fica_name()
// 
// description : 	Print name of all FiCa (file/class) registered
//
//-----------------------------------------------------------------------------

void PoolClass::print_all_fica_name()
{
    vector<CtrlFiCa *>::iterator ite;
    int ctr = 0;
    for (ite = ctrl_ficas.begin();ite < ctrl_ficas.end();++ite)
    {
        if ((*ite) != NULL)
            cout << "File/Class name at entry " << ctr << ": " << (*ite)->get_name() << endl;
        else
            cout << "NULL entry at index " << ctr << endl;
        
        ctr++;
    }
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_fica_nb_by_f_name()
// 
// description : 	Get how many FiCa are still registered with this file name
//
//-----------------------------------------------------------------------------

int32_t PoolClass::get_fica_nb_by_f_name(string &wanted_f_name)
{
    vector<CtrlFiCa *>::iterator ite;
    int32_t ctr = 0;
    for (ite = ctrl_ficas.begin();ite < ctrl_ficas.end();++ite)
    {
        if ((*ite) != NULL)
        {
            string &na = (*ite)->get_name();
            string f_name = na.substr(0,na.find('/'));
            if (f_name == wanted_f_name)
                ctr++;
        }
    }
    return ctr;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_fica_nb_by_name()
// 
// description : 	Get how many FiCa are still registered with this 
//					file_name/class_name
//
//-----------------------------------------------------------------------------

int32_t PoolClass::get_fica_nb_by_name(string &wanted_fica_name)
{
    vector<CtrlFiCa *>::iterator ite;
    int32_t ctr = 0;
    for (ite = ctrl_ficas.begin();ite < ctrl_ficas.end();++ite)
    {
        if ((*ite) != NULL)
        {
            if ((*ite)->get_name() == wanted_fica_name)
                ctr++;
        }
    }
    return ctr;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::remove_fica_by_name()
// 
// description : 	Remove a FiCa entry by its name. It does not
//					throw exceptionif the file does not exist
//
//-----------------------------------------------------------------------------


void PoolClass::remove_fica_by_name(string &fica_name)
{
    vector<CtrlFiCa *>::iterator ite;
    
    for (ite = ctrl_ficas.begin();ite < ctrl_ficas.end();++ite)
    {
        if ((*ite) != NULL)
        {
            if ((*ite)->get_name() == fica_name)
            {
                delete (*ite);
                *ite = NULL;
            }
        }
    }
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_ctrl_file_by_name()
// 
// description : 	Get a controller file entry by its name
//
//-----------------------------------------------------------------------------

vector<CtrlFile *>::iterator PoolClass::get_ctrl_file_by_name(const std::string &f_name)
{
    vector<CtrlFile *>::iterator ite;
    for (ite = ctrl_files.begin();ite != ctrl_files.end();++ite)
    {
        if ((*ite) != NULL)
        {
            if ((*ite)->get_name() == f_name)
                break;
        }
    }
    
    if (ite == ctrl_files.end())
    {
        TangoSys_OMemStream o;
        o << f_name << " file name is not defined in this pool device server" << ends;

        Tango::Except::throw_exception((const char *)"Pool_NotDefinedCtrlFile",o.str(),
                        (const char *)"PoolClass::get_ctrl_by_file");
    }
    
    return ite;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::add_ctrl_file()
// 
// description : 	Add a new controller file entry in the controller file list
//					and returns an iterator on this new entry
//
// arg(s) : - f_name : The controller file name
//			- ctrl_dev_type : The controller device type
//			- dev : The device (for logging purpose only)
//
//-----------------------------------------------------------------------------

vector<CtrlFile *>::iterator PoolClass::add_ctrl_file(string &f_name,CtrlType ctrl_dev_type,Pool *dev)
{
    vector<CtrlFile *>::size_type file_nb = ctrl_files.size();
    vector<CtrlFile *>::iterator pos;
    bool free_place = false;
        
    if (file_nb == MAX_FILE)
    {
        TangoSys_OMemStream o;
        o << "Already at max controller files capacity (" << MAX_FILE << ")" << ends;
        
        Tango::Except::throw_exception((const char *)"Pool_TooManyCtrlFiles",o.str(),
                        (const char *)"PoolClass::add_ctrl_file");
    }
    else
    {
        CtrlFile *ptr_ext_file = NULL;
        pos = find(ctrl_files.begin(),ctrl_files.end(),(CtrlFile *)NULL);
        if (pos != ctrl_files.end())
            free_place = true;
        
        Language lang = CtrlFile::get_language(f_name);
        if (lang == CPP)
        {
            switch (ctrl_dev_type)
            {
                case MOTOR_CTRL:
                    ptr_ext_file = new CppMotCtrlFile(f_name);
                    break;

                case PSEUDO_MOTOR_CTRL:
                    ptr_ext_file = new CppPseudoMotCtrlFile(f_name);
                    break;
                
                case COTI_CTRL:
                    ptr_ext_file = new CppCoTiCtrlFile(f_name);
                    break;
                
                case ZEROD_CTRL:
                    ptr_ext_file = new CppZeroDCtrlFile(f_name);
                    break;

                case ONED_CTRL:
                    ptr_ext_file = new CppOneDCtrlFile(f_name);
                    break;
                    
                case TWOD_CTRL:
                    ptr_ext_file = new CppTwoDCtrlFile(f_name);
                    break;

                case PSEUDO_COUNTER_CTRL:
                    ptr_ext_file = new CppPseudoCoCtrlFile(f_name);
                    break;
                    
                case COM_CTRL:
                    ptr_ext_file = new CppComCtrlFile(f_name);
                    break;
                
                case IOREGISTER_CTRL:
                    ptr_ext_file = new CppIORegisterCtrlFile(f_name);
                    break;

                case MOTOR_GROUP_CTRL:
                case MEASUREMENT_GROUP_CTRL:
                    Tango::Except::throw_exception(
                            (const char *)"Pool_BadCtrlType",
                            (const char *)"Groups don't have controller type !!!",
                            (const char *)"PoolClass::add_ctrl_file");
                    break;		
                
                default:
                    Tango::Except::throw_exception(
                            (const char *)"Pool_BadCtrlType",
                            (const char *)"Undefined controller type !!!",
                            (const char *)"PoolClass::add_ctrl_file");
                    break;
            }
        }
        else
        {
            switch (ctrl_dev_type)
            {
                case MOTOR_CTRL:
                    ptr_ext_file = new PyMotCtrlFile(f_name);
                    break;
    
                case PSEUDO_MOTOR_CTRL:
                    ptr_ext_file = new PyPseudoMotCtrlFile(f_name);
                    break;
                
                case COTI_CTRL:
                    ptr_ext_file = new PyCoTiCtrlFile(f_name);
                    break;
                
                case ZEROD_CTRL:
                    ptr_ext_file = new PyZeroDCtrlFile(f_name);
                    break;
                
                case ONED_CTRL:
                    ptr_ext_file = new PyOneDCtrlFile(f_name);
                    break;
                    
                case TWOD_CTRL:
                    ptr_ext_file = new PyTwoDCtrlFile(f_name);
                    break;

                case PSEUDO_COUNTER_CTRL:
                    ptr_ext_file = new PyPseudoCoCtrlFile(f_name);
                    break;
                    
                case COM_CTRL:
                    ptr_ext_file = new PyComCtrlFile(f_name);
                    break;

                case IOREGISTER_CTRL:
                    ptr_ext_file = new PyIORegisterCtrlFile(f_name);
                    break;

                case MOTOR_GROUP_CTRL:
                case MEASUREMENT_GROUP_CTRL:
                    Tango::Except::throw_exception(
                            (const char *)"Pool_BadCtrlType",
                            (const char *)"Groups don't have controller type !!!",
                            (const char *)"PoolClass::add_ctrl_file");
                    break;		
                
                default:
                    Tango::Except::throw_exception(
                            (const char *)"Pool_BadCtrlType",
                            (const char *)"Undefined controller type !!!",
                            (const char *)"PoolClass::add_ctrl_file");
                    break;
            }
        }
        
        if (free_place == true)
        {
            *pos = ptr_ext_file;
        }
        else
        {
            ctrl_files.push_back(ptr_ext_file);
            pos = ctrl_files.end() - 1;
        }
    }
        
    return pos;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::remove_ctrl_file_by_name()
// 
// description : 	Remove a controller file entry by its name. It does not
//					throw exceptionif the file does not exist
//
//-----------------------------------------------------------------------------

void PoolClass::remove_ctrl_file_by_name(string &f_name)
{
    vector<CtrlFile *>::iterator ite;
    string f_name_lower(f_name);
    transform(f_name_lower.begin(),f_name_lower.end(),f_name_lower.begin(),::tolower);
    string::size_type pos = f_name_lower.find('.');
    if (pos != string::npos)
        f_name_lower.erase(pos);
    
    for (ite = ctrl_files.begin();ite < ctrl_files.end();++ite)
    {
        if ((*ite) != NULL)
        {
            if ((*ite)->get_name_lower() == f_name_lower)
            {
                delete (*ite);
                *ite = NULL;
            }
        }
    }
}


//+----------------------------------------------------------------------------
//
// method : 		PoolClass::clear_ctrl_files()
// 
// description : 	Clear the controller files vector
//
//-----------------------------------------------------------------------------

void PoolClass::clear_ctrl_files()
{
    if (ctrl_files.empty() == false)
    {
        vector<CtrlFile *>::iterator ite;
        for (ite = ctrl_files.begin();ite != ctrl_files.end();++ite)
        {
            if (*ite != NULL)
                delete *ite;
        }
        ctrl_files.clear();
    }
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::print_all_file_name()
// 
// description : 	Print name of all controller file registered
//
//-----------------------------------------------------------------------------

void PoolClass::print_all_file_name()
{
    vector<CtrlFile *>::iterator ite;
    int ctr = 0;
    for (ite = ctrl_files.begin();ite < ctrl_files.end();++ite)
    {
        if ((*ite) != NULL)
            cout << "File name at entry " << ctr << ": " << (*ite)->get_name() << endl;
        else
            cout << "NULL entry at index " << ctr << endl;
        
        ctr++;
    }
}

Pool* PoolClass::get_pool()
{
    vector<Tango::DeviceImpl *> &dev_list = this->get_device_list();
    assert(dev_list.size() == 1);
    return static_cast<Pool *>(dev_list[0]);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolClass::get_pool_path()
// 
// description : 	Obtains the current value for the pool path property of the Pool
//                  device.
//
//-----------------------------------------------------------------------------

vector<string> &PoolClass::get_pool_path()
{
    return get_pool()->get_pool_path();
}

}	// namespace
