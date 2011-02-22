#ifndef _CONSTRAINT_H
#define _CONSTRAINT_H

#include <pool/Ctrl.h>

class Constraint : public Controller
{
public:
	
	Constraint(const char *);
	virtual ~Constraint();
	
	/**
	 * Determines if the given values are allowed according to the constraint 
	 * algorithm giving also a corresponding description.
	 * 
	 * @param pos	[in]	array of positions.
	 * @param descr	[out]	a description of the current state
	 * @return <code>true</code> if allowed or <code>false</code> otherwise.
	 */
	virtual bool isAllowed(std::vector<double> &, std::string &) = 0;
	
	/**
	 * Determines if the constraint is dynamic (should be checked while moving)
	 * or not.
	 * 
	 * @return <code>true</code> if dynamic or <code>false</code> otherwise.
	 */
	virtual bool isDynamic() { return false; }
	
	/* 
	 * no devices exist on a constraint so the following two methods are always 
	 * empty and in fact they should not be called at all for a contraint.
	 */
	virtual void AddDevice(int32_t idx) {}
	virtual void DeleteDevice(int32_t idx) {}
	
	virtual std::string SendToCtrl(std::string &) { return ""; }

	
};

#endif
