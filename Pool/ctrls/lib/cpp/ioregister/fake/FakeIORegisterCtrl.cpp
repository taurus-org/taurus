#include <iostream>
#include <FakeIORegisterCtrl.h>

using namespace std;

//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::FakeIORegisterController
// 
// description : 	Ctor of the FakeIORegisterController class
//					It retrieve some properties from Tango DB, build a 
//					connection to the Simulated controller and ping it
//					to check if it is alive
//
//-----------------------------------------------------------------------------

FakeIORegisterController::FakeIORegisterController(const char *inst,vector<Controller::Properties> &prop):
IORegisterController(inst)
{
	read_nb = 0;
	write_nb = 0;
	CppComCh_extra_2 = 0.0;
	
	/*
	cout << "Received " << prop.size() << " properties" << endl;
	for (unsigned long loop = 0;loop < prop.size();loop++)
	{
		cout << "\tProperty name = " << prop[loop].name << endl;
		if (prop[loop].value.bool_prop.size() != 0)
		{
			for (unsigned ll = 0;ll < prop[loop].value.bool_prop.size();ll++)
				cout << "\t\tProp value = " << prop[loop].value.bool_prop[ll] << endl;
		}
		else if (prop[loop].value.long_prop.size() != 0)
		{
			for (unsigned ll = 0;ll < prop[loop].value.long_prop.size();ll++)
				cout << "\t\tProp value = " << prop[loop].value.long_prop[ll] << endl;
		}
		else if (prop[loop].value.double_prop.size() != 0)
		{
			for (unsigned ll = 0;ll < prop[loop].value.double_prop.size();ll++)
				cout << "\t\tProp value = " << prop[loop].value.double_prop[ll] << endl;
		}
		else
		{
			for (unsigned ll = 0;ll < prop[loop].value.string_prop.size();ll++)
				cout << "\t\tProp value = " << prop[loop].value.string_prop[ll] << endl;
		}
	}
	*/
}

//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::~FakeIORegisterController
// 
// description : 	Dtor of the DummyController class
//
//-----------------------------------------------------------------------------

FakeIORegisterController::~FakeIORegisterController()
{
	//cout << "[FakeIORegisterController] class dtor" << endl;
}

//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::AddDevice
// 
// description : 	Register a new device for the controller
//					For the simulated controller, this simply means increment
//					motor count
//
//-----------------------------------------------------------------------------

void FakeIORegisterController::AddDevice(int32_t idx)
{
	//cout << "[FakeIORegisterController] Creating a new IORegister with index " << idx << " on controller FakeIORegisterController/" << inst_name << endl;
}

//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::DeleteDevice
// 
// description : 	Unregister a new device for the controller
//					For the simulated controller, this simply means decrement
//					motor count
//
//-----------------------------------------------------------------------------

void FakeIORegisterController::DeleteDevice(int32_t idx)
{
	//cout << "[FakeIORegisterController] Deleting IORegister with index " << idx << " on controller FakeIORegisterController/" << inst_name << endl;
}

string &FakeIORegisterController::ReadOne(int32_t idx, int32_t max_read_len /* = -1*/)
{
	if(max_read_len == 0)
	{
		read_buff.clear();
		return read_buff;
	}
	
	ostringstream oss;
	oss << "Read Message #" << read_nb++;
	string msg(oss.str());
	
	int32_t read_count = (int32_t)msg.size();
	
	if(max_read_len != -1)
	{
		if(max_read_len < read_count)
		{
			read_count = max_read_len;
		}
	}
	
	//carefull here
	read_buff.assign(msg.c_str(),read_count);
	
	return read_buff;
}



int32_t FakeIORegisterController::WriteOne(int32_t, string &istr, int32_t write_len /*= -1*/)
{	
	write_nb++;
	
	if(write_len == 0)
		return 0;
	
	int32_t write_count;

  	int32_t buf_size = (int32_t) istr.size();
	
	if(write_len == -1)
		write_count = buf_size;
	else
		write_count = write_len > buf_size ? buf_size : write_len;

	cout << "[FakeIORegisterController]::WriteOne Sending stream: [" << std::hex;
	
	for(int32_t i = 0; i < write_count; i++)
	{
		char c = istr[i];
		cout << "'" << c << "' (0x" << (unsigned short)c << ")" ;
		if(i < write_count-1) 
			cout << ", ";
	}
	cout << std::dec << "]" << endl; 	
	
	return write_count;
}



//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::GetState
// 
// description : 	Get one motor status. Motor status means two things :
//					1 - The motor state (Tango sense)
//
// arg(s) : - idx : The motor number (starting at 1)
//			- mot_info_ptr : Pointer to a struct. which willbe filled with
//							 motor status
//
//-----------------------------------------------------------------------------

void FakeIORegisterController::StateOne(int32_t idx,Controller::CtrlState *ch_info_ptr)
{
	ch_info_ptr->state = Tango::ON;
}


//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::GetExtraAttributePar
// 
// description : 	Get a counter timer extra attribute parameter.
//
// arg(s) : - idx : The C/T number (starting at 1)
//			- par_name : The parameter name
//
// This method returns the parameter value
//-----------------------------------------------------------------------------

Controller::CtrlData FakeIORegisterController::GetExtraAttributePar(int32_t idx,string &par_name)
{
	Controller::CtrlData par_value;	
	if (par_name == "CppComCh_extra_1")
	{
		par_value.int32_data = 12345;
		par_value.data_type = Controller::INT32;		
	}
	else if (par_name == "CppComCh_extra_2")
	{
		par_value.db_data = CppComCh_extra_2;
		par_value.data_type = Controller::DOUBLE;		
	} 
	else
	{
		TangoSys_OMemStream o;
		o << "Parameter " << par_name << " is unknown for controller FakeIORegisterController/" << get_name() << ends;
		
		Tango::Except::throw_exception((const char *)"FakeIORegisterController_BadCtrlPtr",o.str(),
					       			   (const char *)"FakeIORegisterController::GetPar()");
	}
	
	return par_value;
}

//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::SetExtraAttributePar
// 
// description : 	Set a counter timer extra attribute parameter.
//
// arg(s) : - idx : The C/T number (starting at 1)
//			- par_name : The parameter name
//			- new_value : The parameter value
//
//-----------------------------------------------------------------------------

void FakeIORegisterController::SetExtraAttributePar(int32_t idx, string &par_name, Controller::CtrlData &new_value)
{
	if (par_name == "CppComCh_extra_2")
	{
		CppComCh_extra_2 = new_value.db_data;
	}
 	else
	{
		TangoSys_OMemStream o;
		o << "Parameter " << par_name << " is unknown for controller FakeIORegisterController/" << get_name() << ends;
		
		Tango::Except::throw_exception((const char *)"FakeIORegisterController_BadCtrlPtr",o.str(),
					       			   (const char *)"FakeIORegisterController::GetPar()");
	}
}


//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::send_to_ctrl
// 
// description : 	Send a string to the controller
//
// arg(s) : - in_str : the string to send to the ctrl
//
//-----------------------------------------------------------------------------

string FakeIORegisterController::SendToCtrl(string &in_str)
{
	cout << "[FakeIORegisterController] I have received the string: " << in_str << endl;
	string returned_str("Hasta luego");
	return returned_str;	
}

//-----------------------------------------------------------------------------
//
// method : 		FakeIORegisterController::bad_data_type
// 
// description : 	Throw a bad data type excepton
//
// arg(s) : - par_name : The parameter name
//
//-----------------------------------------------------------------------------

void FakeIORegisterController::bad_data_type(string &par_name)
{
	TangoSys_OMemStream o;
	o << "A wrong data type has been used to set the parameter " << par_name << ends;

	Tango::Except::throw_exception((const char *)"DummyComCtrl_BadParameter",o.str(),
			       			   	   (const char *)"FakeIORegisterController::SetPar()");
}

//
//===============================================================================================
//

const char *IORegister_Ctrl_class_name[] = {"FakeIORegisterController",NULL};

const char *FakeIORegisterController_doc = "This is the C++ controller for the FakeIORegisterController class";
const char *FakeIORegisterController_gender = "Fake";
const char *FakeIORegisterController_model = "Fake 2000";
const char *FakeIORegisterController_image = "fake_com.png";
const char *FakeIORegisterController_organization = "Fake Inc.";
const char *FakeIORegisterController_logo = "ALBA_logo.png";

Controller::ExtraAttrInfo FakeIORegisterController_ctrl_extra_attributes[] = {{"CppComCh_extra_1","DevLong","Read"},
												 {"CppComCh_extra_2","DevDouble","Read_Write"},
												 NULL};

Controller::PropInfo FakeIORegisterController_class_prop[] = {{"The prop","The first CPP property","DevLong","12"},
							  			 {"Another_Prop","The second CPP property","DevString","Hola"},
							  			 {"Third_Prop","The third CPP property","DevVarLongArray","11,22,33"},
							  			 NULL};
							  			 
int32_t FakeIORegisterController_MaxDevice = 12;

extern "C"
{
	
Controller *_create_FakeIORegisterController(const char *inst,vector<Controller::Properties> &prop)
{
	return new FakeIORegisterController(inst,prop);
}

}
