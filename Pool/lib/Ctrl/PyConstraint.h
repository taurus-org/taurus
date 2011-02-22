#ifndef _PYCONSTRAINT_H
#define _PYCONSTRAINT_H

#include "PyCtrl.h"
#include <tango.h>
#include <pool/Constraint.h>

#define IS_ALLOWED		"isAllowed"
#define IS_DYNAMIC		"isDynamic"
#define ROLES_ATTR		"roles"
#define GET_ROLES		"get_roles"
#define GET_ROLE_NB		"get_role_nb"

extern "C"
{
	Controller *_create_PyConstraint(const char *,const char *,PyObject *,PyObject *);
}


/**
 * The Python constraint controller base class
 */
class PyConstraint : public PyController, public Constraint
{
public:
	PyConstraint(const char *,const char *,PyObject *,PyObject *);
	~PyConstraint();

	/**
	 * Determines if the given values are allowed according to the constraint 
	 * algorithm giving also a corresponding description.
	 * 
	 * @param pos	[in]	array of positions.
	 * @param descr	[out]	a description of the current state
	 * @return <code>true</code> if allowed or <code>false</code> otherwise.
	 */
	virtual bool isAllowed(std::vector<double> &, std::string &);

	/**
	 * Determines if the constraint is dynamic (should be checked while moving)
	 * or not.
	 * 
	 * @return <code>true</code> if dynamic or <code>false</code> otherwise.
	 */
	virtual bool isDynamic();
	
protected:
	void clear_method_flag();
	void check_existing_methods(PyObject *);

	long get_role_nb_from_py();
	
	PyObject 	*mod;
	string		py_class_name;

	bool        is_dynamic;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif // _PYCONSTRAINT_H
