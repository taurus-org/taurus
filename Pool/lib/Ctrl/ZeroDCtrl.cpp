#include <pool/ZeroDCtrl.h>

ZeroDController::ZeroDController(const char *inst):Controller(inst)
{
    //cout << "[ZeroDController] class ctor" << endl;
    
    ZeroD_NaN = strtod("NAN",NULL);
}

ZeroDController::~ZeroDController()
{
    //cout << "[ZeroDController] class dtor" << endl;
}

double ZeroDController::ReadOne(int32_t )
{
    //cout << "[ZeroDController] Default ReadOne method returning NaN" << endl;
    return ZeroD_NaN;
}
