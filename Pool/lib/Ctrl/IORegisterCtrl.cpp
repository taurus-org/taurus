#include <pool/IORegisterCtrl.h>
#include <sstream>

IORegisterController::IORegisterController(const char *inst):Controller(inst),meth_not_impl("Pool_meth_not_implemented") 
{
	//cout << "In the IORegisterController class ctor" << endl;

}

IORegisterController::~IORegisterController ( ) 
{ 
	//cout << "In the IORegisterController class dtor" << endl;
}

int32_t IORegisterController::ReadOne(int32_t)
{
	//cout << "Default ReadOne method returning 0" << endl;
  
	return 0;
}

void IORegisterController::WriteOne(int32_t, int32_t) 
{
	//cout << "Default WriteOne method" << endl;

}
