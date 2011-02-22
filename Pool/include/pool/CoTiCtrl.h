#ifndef COTICTRL_H_
#define COTICTRL_H_

#include <pool/Ctrl.h>

/**
 * The counter/timer controller base class
 */
class CoTiController:public Controller
{
public:
	CoTiController(const char *);
	virtual ~CoTiController();
	
//
// Methods to read counter(s) value
//

	virtual void PreReadAll() {}
	virtual void PreReadOne(int32_t) {}
	virtual void ReadAll() {}
	virtual double ReadOne(int32_t);
	
//
// Methods to set counter(s) value
//

	virtual void PreLoadAll() {}
	virtual bool PreLoadOne(int32_t,double) {return true;}
	virtual void LoadOne(int32_t,double) {}
	virtual void LoadAll() {}

//
// Methods to start counting
//

	virtual void PreStartAllCT() {}
	virtual bool PreStartOneCT(int32_t) {return true;}
	virtual void StartOneCT(int32_t) {}
	virtual void StartAllCT() {}
	
//
// Method to abort counting
//

	virtual void AbortOne(int32_t) {}
	
protected:
	double			mot_NaN;
	std::string		meth_not_impl;
};

		
#endif /*COTICTRL_H_*/
