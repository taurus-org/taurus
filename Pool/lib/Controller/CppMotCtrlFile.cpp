//+=============================================================================
//
// file :         CppMotCtrlFile.cpp
//
// description :  C++ source for the Pool and its commands.
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                Pool are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author: tiagocoutinho $
//
// $Revision: 298 $
//
// $Log$
// Revision 1.8  2007/08/23 10:32:43  tcoutinho
// - basic pseudo counter check
// - some fixes regarding pseudo motors
//
// Revision 1.7  2007/08/17 13:07:30  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.6  2007/07/17 11:41:57  tcoutinho
// replaced comunication with communication
//
// Revision 1.5  2007/07/02 14:46:36  tcoutinho
// first stable comunication channel commit
//
// Revision 1.4  2007/06/27 08:56:28  tcoutinho
// first commit for comuncation channels
//
// Revision 1.3  2007/01/26 08:36:47  etaurel
// - We now have a first release of ZeroDController
//
// Revision 1.2  2007/01/04 11:55:03  etaurel
// - Added the CounterTimer controller
//
// Revision 1.1  2006/11/07 14:57:08  etaurel
// - Now, the pool really supports different kind of controllers (cpp and py)
//
//
// copyleft :     Alba synchrotron
//				  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
// 				  08193 Bellaterra, Barcelona
//                Spain
//
//-=============================================================================

#include "CppMotCtrlFile.h"

namespace Pool_ns
{

// ----------------------------------------------------------------------------
// CPPUndefCtrlFile

CppUndefCtrlFile::CppUndefCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name,"Undefined")
{
}

CppUndefCtrlFile::~CppUndefCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppMotCtrlFile

CppMotCtrlFile::CppMotCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name,"Motor")
{}

CppMotCtrlFile::CppMotCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl,"Motor")
{}

CppMotCtrlFile::~CppMotCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppPseudoMotCtrlFile

CppPseudoMotCtrlFile::CppPseudoMotCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name, "PseudoMotor")
{
    include_MaxDevice = false;
}

CppPseudoMotCtrlFile::CppPseudoMotCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl, "PseudoMotor")
{
    include_MaxDevice = false;
}

CppPseudoMotCtrlFile::~CppPseudoMotCtrlFile()
{}

void CppPseudoMotCtrlFile::get_particular_info(const std::string &ctrl_class,
                                               vector<string> &info)
{
//
// motor role count and description of each one
//
    vector<string> motor_roles;
    get_cpp_str_array(ctrl_class,"motor_roles",motor_roles);

    stringstream motor_role_nb;
    motor_role_nb << motor_roles.size();
    info.push_back(motor_role_nb.str());

    for(unsigned long ul = 0; ul < motor_roles.size(); ul++)
        info.push_back(motor_roles[ul]);

//
// pseudo motor role count and description of each one
//
    vector<string> pseudo_motor_roles;
    try
    {
        get_cpp_str_array(ctrl_class,"pseudo_motor_roles",pseudo_motor_roles);
    }
    catch(Tango::DevFailed &e)
    {
//
// Pseudo motor roles not defined: this means the pseudo motor controller will
// have only one pseudo motor role and the name of this role will be the class
// name
//
        pseudo_motor_roles.push_back(ctrl_class);
    }

    stringstream pseudo_motor_role_nb;
    pseudo_motor_role_nb << pseudo_motor_roles.size();
    info.push_back(pseudo_motor_role_nb.str());

    for(unsigned long ul = 0; ul < pseudo_motor_roles.size(); ul++)
        info.push_back(pseudo_motor_roles[ul]);
}

// ----------------------------------------------------------------------------
// CppCoTiCtrlFile

CppCoTiCtrlFile::CppCoTiCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name, "CounterTimer")
{}

CppCoTiCtrlFile::CppCoTiCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl, "CounterTimer")
{}

CppCoTiCtrlFile::~CppCoTiCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppZeroDCtrlFile

CppZeroDCtrlFile::CppZeroDCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name, "ZeroDExpChannel")
{}

CppZeroDCtrlFile::CppZeroDCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl, "ZeroDExpChannel")
{}

CppZeroDCtrlFile::~CppZeroDCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppOneDCtrlFile

CppOneDCtrlFile::CppOneDCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name, "OneDExpChannel")
{}

CppOneDCtrlFile::CppOneDCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl, "OneDExpChannel")
{}

CppOneDCtrlFile::~CppOneDCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppTwoDCtrlFile

CppTwoDCtrlFile::CppTwoDCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name, "TwoDExpChannel")
{}

CppTwoDCtrlFile::CppTwoDCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl, "TwoDExpChannel")
{}

CppTwoDCtrlFile::~CppTwoDCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppPseudoCoCtrlFile

CppPseudoCoCtrlFile::CppPseudoCoCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name,"PseudoCounter")
{
    include_MaxDevice = false;
}

CppPseudoCoCtrlFile::CppPseudoCoCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl,"PseudoCounter")
{
    include_MaxDevice = false;
}

CppPseudoCoCtrlFile::~CppPseudoCoCtrlFile()
{}

void CppPseudoCoCtrlFile::get_particular_info(const std::string &ctrl_class,
                                              vector<string> &info)
{
//
// counter role count and description of each one
//
    vector<string> counter_roles;
    get_cpp_str_array(ctrl_class,"counter_roles",counter_roles);

    stringstream counter_role_nb;
    counter_role_nb << counter_roles.size();
    info.push_back(counter_role_nb.str());

    for(unsigned long ul = 0; ul < counter_roles.size(); ul++)
        info.push_back(counter_roles[ul]);

//
// pseudo counter role count and description of each one
//
    vector<string> pseudo_counter_roles;
    try
    {
        get_cpp_str_array(ctrl_class,"pseudo_counter_roles",pseudo_counter_roles);
    }
    catch(Tango::DevFailed &e)
    {
//
// Pseudo counter roles not defined: this means the pseudo counter controller will
// have only one pseudo counter role and the name of this role will be the class
// name
//
        pseudo_counter_roles.push_back(ctrl_class);
    }

    stringstream pseudo_counter_role_nb;
    pseudo_counter_role_nb << pseudo_counter_roles.size();
    info.push_back(pseudo_counter_role_nb.str());

    for(unsigned long ul = 0; ul < pseudo_counter_roles.size(); ul++)
        info.push_back(pseudo_counter_roles[ul]);
}

// ----------------------------------------------------------------------------
// CppComCtrlFile

CppComCtrlFile::CppComCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name,"Communication")
{}

CppComCtrlFile::CppComCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl,"Communication")
{}

CppComCtrlFile::~CppComCtrlFile()
{}

// ----------------------------------------------------------------------------
// CppIORegisterCtrlFile

CppIORegisterCtrlFile::CppIORegisterCtrlFile(const std::string &f_name)
:CppCtrlFile(f_name,"IORegister")
{}

CppIORegisterCtrlFile::CppIORegisterCtrlFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl,"IORegister")
{}

CppIORegisterCtrlFile::~CppIORegisterCtrlFile()
{}

void CppIORegisterCtrlFile::get_particular_info(const std::string &ctrl_class,
                                               vector<string> &info)
{

//
//  predefined values, description of each one and total number
//
    vector<string> predefined_values;
    vector<string> predefined_values_description;
    vector<string> values;

    stringstream predefined_values_nb;

    try
    {
        get_cpp_str_array(ctrl_class,"predefined_values",predefined_values);
                
        predefined_values_nb << predefined_values.size()/2;
        info.push_back(predefined_values_nb.str());
        
        for(unsigned long ul = 0; ul < predefined_values.size(); ul++)
            info.push_back(predefined_values[ul]);
        
        for(unsigned long ul = 0; ul < predefined_values.size(); ul+=2)
            values.push_back(predefined_values[ul]);
        
        for(unsigned long ul = 1; ul < predefined_values.size(); ul+=2)
            predefined_values_description.push_back(predefined_values[ul]);

        
    }
    catch(Tango::DevFailed &e)
    {
        predefined_values_nb << 0;
        info.push_back(predefined_values_nb.str());
    }


    
}

// ----------------------------------------------------------------------------
// CppConstraintFile

CppConstraintFile::CppConstraintFile(const std::string &f_name)
:CppCtrlFile(f_name,"Constraint")
{}

CppConstraintFile::CppConstraintFile(CppUndefCtrlFile &undef_ctrl)
:CppCtrlFile(undef_ctrl,"Constraint")
{}

CppConstraintFile::~CppConstraintFile()
{}

} // End of Pool_ns namespacce
