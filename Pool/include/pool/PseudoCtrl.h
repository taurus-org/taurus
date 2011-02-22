#ifndef PSEUDOCTRL_H_
#define PSEUDOCTRL_H_

#include <vector>
#include <map>
#include <tango.h>
#include <pool/Ctrl.h>

class PseudoController:public Controller
{
public:
	PseudoController(const char *inst):
	Controller(inst),meth_not_impl("Pool_meth_not_implemented")
	{ val_NaN = strtod("NAN",NULL);	}

	virtual ~PseudoController() {}

	virtual void AddDevice(int32_t idx) {}
	virtual void DeleteDevice(int32_t idx) {}

	//
	// Methods to Get/Set pseudo motor parameters
	//
	virtual Controller::CtrlData GetPar(int32_t, std::string &)
	{
		Controller::CtrlData cd;
		cd.db_data = val_NaN;
		cd.data_type = Controller::DOUBLE;
		return cd;
	}
	virtual void SetPar(int32_t, std::string &, Controller::CtrlData &) {}

protected:
	double			val_NaN;
	std::string		meth_not_impl;
};

#endif /*PSEUDOCTRL_H_*/
