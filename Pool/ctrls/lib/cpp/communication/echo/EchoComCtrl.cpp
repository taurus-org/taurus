#include <pool/PoolAPI.h>
#include <EchoComCtrl.h>
#include <iostream>
#include <tango.h>

using namespace std;

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::EchoCommunicationController
// 
// description : 	Ctor of the EchoCommunicationController class
//					It retrieve some properties from Tango DB, build a 
//					connection to the Simulated controller and ping it
//					to check if it is alive
//
//-----------------------------------------------------------------------------

EchoCommunicationController::EchoCommunicationController(const char *inst,vector<Controller::Properties> &prop):
ComController(inst),state(100,ChDisabled),last_write(100,"")
{
	read_nb = 0;
	write_nb = 0;
}

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::~EchoCommunicationController
// 
// description : 	Dtor of the DummyController class
//
//-----------------------------------------------------------------------------

EchoCommunicationController::~EchoCommunicationController()
{
	//cout << "[EchoCommunicationController] class dtor" << endl;
}

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::AddDevice
// 
// description : 	Register a new device for the controller
//					For the simulated controller, this simply means increment
//					motor count
//
//-----------------------------------------------------------------------------

void EchoCommunicationController::AddDevice(int32_t idx)
{
	//cout << "[EchoCommunicationController] Creating a new Communication Channel with index " << idx << " on controller EchoCommunicationController/" << inst_name << endl;
	
	state[idx-1] = ChOpen;
	last_write[idx-1] = "";
}

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::DeleteDevice
// 
// description : 	Unregister a new device for the controller
//					For the simulated controller, this simply means decrement
//					motor count
//
//-----------------------------------------------------------------------------

void EchoCommunicationController::DeleteDevice(int32_t idx)
{
	//cout << "[EchoCommunicationController] Deleting Communication Channel with index " << idx << " on controller EchoCommunicationController/" << inst_name << endl;
	state[idx-1] = ChDisabled;
}

string &EchoCommunicationController::ReadOne(int32_t idx, int32_t max_read_len /* = -1*/)
{
	if(state[idx-1] == ChDisabled)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to read in an invalid channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}
	else if(state[idx-1] == ChClosed)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to read in a closed channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}
	
	string &msg = last_write[idx-1];

	if(max_read_len == 0)
	{
		read_buff.clear();
		return read_buff;
	}

	if(max_read_len < msg.size())
	{
		read_buff.assign(msg,0,max_read_len);
	}
	else 
	{
		read_buff = msg;
	}
	
	return read_buff;
}

string &EchoCommunicationController::ReadLineOne(int32_t idx)
{
	if(state[idx-1] == ChDisabled)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to readline in an invalid channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}
	else if(state[idx-1] == ChClosed)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to readline in a closed channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}

	string &msg = last_write[idx-1];
	string::iterator it = find(msg.begin(),msg.end(),'\n');
	if(it == msg.end())
		read_buff = msg;
	else
		read_buff.assign(msg.begin(),it);

	return read_buff;
}

int32_t EchoCommunicationController::WriteOne(int32_t idx, string &istr, int32_t write_len /*= -1*/)
{	
	if(state[idx-1] == ChDisabled)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to readline in an invalid channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}
	else if(state[idx-1] == ChClosed)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to readline in a closed channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}
	
	string &msg = last_write[idx-1];
	if(write_len == 0)
		msg = "";
	else
		msg.assign(istr,0,write_len);

	return write_len;
}

string &EchoCommunicationController::WriteReadOne(int32_t idx, string &istr, int32_t write_len /*= -1*/, int32_t max_read_len /*= -1*/)
{	
	if(state[idx-1] == ChDisabled)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to readline in an invalid channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}
	else if(state[idx-1] == ChClosed)
	{
		Tango::Except::throw_exception(
			(const char *)"EchoCommunicationController_BadIndex",
			(const char *)"Trying to readline in a closed channel",
			(const char *)"EchoCommunicationController::ReadOne()");
	}

	WriteOne(idx,istr,write_len);
	return ReadOne(idx,max_read_len);

}

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::GetState
// 
// description : 	Get one motor status. Motor status means two things :
//					1 - The motor state (Tango sense)
//
// arg(s) : - idx : The motor number (starting at 1)
//			- mot_info_ptr : Pointer to a struct. which willbe filled with
//							 motor status
//
//-----------------------------------------------------------------------------

void EchoCommunicationController::StateOne(int32_t idx,Controller::CtrlState *ch_info_ptr)
{
	ch_info_ptr->state = Tango::ON;
}


//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::GetExtraAttributePar
// 
// description : 	Get a counter timer extra attribute parameter.
//
// arg(s) : - idx : The C/T number (starting at 1)
//			- par_name : The parameter name
//
// This method returns the parameter value
//-----------------------------------------------------------------------------

Controller::CtrlData EchoCommunicationController::GetExtraAttributePar(int32_t idx, string &par_name)
{

	TangoSys_OMemStream o;
	o << "Parameter " << par_name << " is unknown for controller EchoCommunicationController/" << get_name() << ends;
	
	Tango::Except::throw_exception(
		(const char *)"EchoCommunicationController_BadCtrlPtr",o.str(),
		(const char *)"EchoCommunicationController::GetPar()");
}

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::SetExtraAttributePar
// 
// description : 	Set a counter timer extra attribute parameter.
//
// arg(s) : - idx : The C/T number (starting at 1)
//			- par_name : The parameter name
//			- new_value : The parameter value
//
//-----------------------------------------------------------------------------

void EchoCommunicationController::SetExtraAttributePar(int32_t idx, string &par_name, Controller::CtrlData &new_value)
{
	TangoSys_OMemStream o;
	o << "Parameter " << par_name << " is unknown for controller EchoCommunicationController/" << get_name() << ends;
	
	Tango::Except::throw_exception((const char *)"EchoCommunicationController_BadCtrlPtr",o.str(),
									(const char *)"EchoCommunicationController::GetPar()");
}


//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::send_to_ctrl
// 
// description : 	Send a string to the controller
//
// arg(s) : - in_str : the string to send to the ctrl
//
//-----------------------------------------------------------------------------

string EchoCommunicationController::SendToCtrl(string &in_str)
{
	cout << "[EchoCommunicationController] I have received the string: " << in_str << endl;
	string returned_str("Hasta luego");
	return returned_str;	
}

//-----------------------------------------------------------------------------
//
// method : 		EchoCommunicationController::bad_data_type
// 
// description : 	Throw a bad data type excepton
//
// arg(s) : - par_name : The parameter name
//
//-----------------------------------------------------------------------------

void EchoCommunicationController::bad_data_type(string &par_name)
{
	TangoSys_OMemStream o;
	o << "A wrong data type has been used to set the parameter " << par_name << ends;

	Tango::Except::throw_exception((const char *)"EchoCommunicationController_BadParameter",o.str(),
			       			   	   (const char *)"EchoCommunicationController::SetPar()");
}

//
//===============================================================================================
//

const char *Communication_Ctrl_class_name[] = {"EchoCommunicationController",NULL};

const char *EchoCommunicationController_doc = "This class is the Tango Sardana Echo like communication controller in C++";
const char *EchoCommunicationController_gender = "Echo";
const char *EchoCommunicationController_model = "Simplest Echo";
const char *EchoCommunicationController_image = "echo_com.png";
const char *EchoCommunicationController_organization = "CELLS - ALBA";
const char *EchoCommunicationController_logo = "ALBA_logo.png";

Controller::ExtraAttrInfo EchoCommunicationController_ctrl_extra_attributes[] = {NULL};

Controller::PropInfo EchoCommunicationController_class_prop[] = {NULL};

int32_t EchoCommunicationController_MaxDevice = 100;

extern "C"
{
	
Controller *_create_EchoCommunicationController(const char *inst,vector<Controller::Properties> &prop)
{
	return new EchoCommunicationController(inst,prop);
}

}
