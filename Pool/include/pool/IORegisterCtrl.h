#ifndef _IOREGISTERCONTROLLER_H
#define _IOREGISTERCONTROLLER_H

#include <pool/Ctrl.h>

/**
  * class IORegisterController
  */

class IORegisterController : public Controller
{
public:
	std::string read_buff;

	IORegisterController(const char *);
	virtual ~IORegisterController();

	/**
	 * 
	 * @param idx - ioregister id
     *
	 */
	virtual int32_t ReadOne(int32_t); 


	/**
	 * @param idx - ioregister id
	 */
	virtual void WriteOne(int32_t, int32_t); 

//
// Methods to Get/Set ioregister parameters
//

//	virtual Controller::CtrlData GetPar(long,std::string &);
	virtual void SetPar(int32_t, std::string &, Controller::CtrlData &) {}

protected:
	std::string		meth_not_impl;
};

#endif // IOREGISTERCONTROLLER_H
