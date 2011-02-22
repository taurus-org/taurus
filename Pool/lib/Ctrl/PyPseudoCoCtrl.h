#ifndef PYPSEUDOCOCTRL_H_
#define PYPSEUDOCOCTRL_H_

#include "PyCtrl.h"
#include <tango.h>
#include <pool/PseudoCoCtrl.h>

extern "C"
{
    Controller *_create_PyPseudoCounterController(const char *,const char *,PyObject *,PyObject *);
}


#define CALC_METHOD					"calc"
#define GET_PSEUDO_CLASS_INFO		"get_pseudo_class_info"
#define COUNTER_ROLES_ATTR			"counter_roles"
#define PSEUDO_COUNTER_ROLES_ATTR	"pseudo_counter_roles"

#define GET_PSEUDO_COUNTER_ROLES	"get_pseudo_counter_roles"
#define GET_PSEUDO_COUNTER_NB		"get_pseudo_counter_nb"

/**
 * The Python pseudo counter controller base class
 */
class PyPseudoCounterController : public PyController, public PseudoCounterController
{
public:
    PyPseudoCounterController(const char *,const char *,PyObject *,PyObject *);
    ~PyPseudoCounterController();

    virtual double Calc(int32_t, std::vector<double> &);

    virtual std::string SendToCtrl(std::string &);

    virtual void SetExtraAttributePar(int32_t,std::string &,Controller::CtrlData &);
    virtual Controller::CtrlData GetExtraAttributePar(int32_t,std::string &);

protected:
    void clear_method_flag();
    void check_existing_methods(PyObject *);

    int32_t get_counter_nb_from_py();
    int32_t get_pseudo_counter_nb_from_py();

    bool		calc;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif /*PYPSEUDOCOCTRL_H_*/
