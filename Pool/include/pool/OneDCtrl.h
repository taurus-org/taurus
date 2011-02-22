#ifndef ONEDCTRL_H_
#define ONEDCTRL_H_

#include <pool/Ctrl.h>

/**
 * The 1D experiment channel controller base class
 */
class OneDController:public Controller
{
public:
	OneDController(const char *);
	virtual ~OneDController();
	
//
// Methods to read ExpChannel value
//

	virtual void PreReadAll() {}
	virtual void PreReadOne(int32_t ) {}
	virtual void ReadAll() {}
	virtual double *ReadOne(int32_t );
	
	virtual void StartOne(int32_t ) {}
	virtual void AbortOne(int32_t ) {}

    virtual Controller::CtrlData GetPar(int32_t, std::string &);
    virtual void SetPar(int32_t, std::string &, Controller::CtrlData &) {}
    	
protected:

    double                  OneD_NaN;
};

		
#endif /*ONEDCTRL_H_*/
