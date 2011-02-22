#include <pool/MotCtrl.h>
#include <stdlib.h>

MotorController::MotorController(const char *inst):Controller(inst),meth_not_impl("Pool_meth_not_implemented")
{
	//cout << "[MotorController] class ctor" << endl;
	
	mot_NaN = strtod("NAN",NULL);
}

MotorController::~MotorController()
{
	//cout << "[MotorController] class dtor" << endl;
}

double MotorController::ReadOne(int32_t )
{
	//cout << "[MotorController] Default ReadOne method returning NaN" << endl;
	return mot_NaN;
}

Controller::CtrlData MotorController::GetPar(int32_t, string &)
{
	//cout << "[MotorController] Default GetPar method returning NaN" << endl;
	Controller::CtrlData cd;
	cd.db_data = mot_NaN;
	cd.data_type = Controller::DOUBLE;
	return cd;
}
