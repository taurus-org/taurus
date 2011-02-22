#include <pool/CoTiCtrl.h>
#include <stdlib.h>

#include <limits.h>

CoTiController::CoTiController(const char *inst):Controller(inst),meth_not_impl("Pool_meth_not_implemented")
{
	//cout << "In the CoTiController class ctor" << endl;
	
	mot_NaN = strtod("NAN",NULL);
}

CoTiController::~CoTiController()
{
	//cout << "In the CoTiController class dtor" << endl;
}

double CoTiController::ReadOne(int32_t )
{
	//cout << "Default ReadOne method returning NaN" << endl;
	return mot_NaN;
}
