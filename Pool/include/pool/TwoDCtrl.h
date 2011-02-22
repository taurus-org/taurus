#ifndef TWODCTRL_H_
#define TWODCTRL_H_

#include <pool/Ctrl.h>

/**
 * The 2D experiment channel controller base class
 */
class TwoDController:public Controller
{
public:
	TwoDController(const char *);
	virtual ~TwoDController();
	
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

    double                  TwoD_NaN;
};

		
#endif /*TWODCTRL_H_*/
