#include <pool/OneDCtrl.h>
#include <stdlib.h>

#include <limits.h>

OneDController::OneDController(const char *inst):Controller(inst)
{
	//cout << "[OneDController] class ctor" << endl;
	
	OneD_NaN = strtod("NAN",NULL);	
}

OneDController::~OneDController()
{
	//cout << "[OneDController] class dtor" << endl;
}

double *OneDController::ReadOne(int32_t )
{
	//cout << "[OneDController] Default ReadOne method returning NaN" << endl;
	return NULL;
}

Controller::CtrlData OneDController::GetPar(int32_t, string &)
{
        //cout << "[OneDController] Default GetPar method returning NaN" << endl;
        Controller::CtrlData cd;
        cd.db_data = OneD_NaN;
        cd.data_type = Controller::DOUBLE;
        return cd;
}
