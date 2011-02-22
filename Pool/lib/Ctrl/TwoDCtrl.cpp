#include <pool/TwoDCtrl.h>

TwoDController::TwoDController(const char *inst):Controller(inst)
{
    //cout << "[TwoDController] class ctor" << endl;
    
    TwoD_NaN = strtod("NAN",NULL);
}

TwoDController::~TwoDController()
{
    //cout << "[TwoDController] class dtor" << endl;
}

double *TwoDController::ReadOne(int32_t )
{
    //cout << "[TwoDController] Default ReadOne method returning NaN" << endl;
    return NULL;
}

Controller::CtrlData TwoDController::GetPar(int32_t, string &)
{
        //cout << "[TwoDController] Default GetPar method returning NaN" << endl;
        Controller::CtrlData cd;
        cd.db_data = TwoD_NaN;
        cd.data_type = Controller::DOUBLE;
        return cd;
}
