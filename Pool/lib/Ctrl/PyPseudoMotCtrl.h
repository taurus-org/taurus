#ifndef PYPSEUDOMOTCTRL_H_
#define PYPSEUDOMOTCTRL_H_

#include "PyCtrl.h"
#include <tango.h>
#include <pool/PseudoMotCtrl.h>

extern "C"
{
    Controller *_create_PyPseudoMotorController(const char *,const char *,PyObject *,PyObject *);
}


#define CALC_PHYSICAL_METHOD			"calc_physical"
#define CALC_PSEUDO_METHOD				"calc_pseudo"
#define CALC_ALL_PHYSICAL_METHOD		"calc_all_physical"
#define CALC_ALL_PSEUDO_METHOD			"calc_all_pseudo"
#define GET_PSEUDO_CLASS_INFO			"get_pseudo_class_info"

#define MOTOR_ROLES_ATTR				"motor_roles"
#define GET_PSEUDO_MOTOR_ROLES			"get_pseudo_motor_roles"
#define GET_PSEUDO_MOTOR_NB				"get_pseudo_motor_nb"

/**
 * The Python motor controller base class
 */
class PyPseudoMotorController : public PyController, public PseudoMotorController
{
public:
    PyPseudoMotorController(const char *,const char *,PyObject *,PyObject *);
    ~PyPseudoMotorController();

    virtual double CalcPhysical(int32_t,std::vector<double> &);
    virtual double CalcPseudo(int32_t,std::vector<double> &);
    
    virtual void CalcAllPhysical(std::vector<double> &,std::vector<double> &);
    virtual void CalcAllPseudo(std::vector<double> &,std::vector<double> &);

    virtual std::string SendToCtrl(std::string &);
    
    virtual void SetExtraAttributePar(int32_t,std::string &,Controller::CtrlData &);
    virtual Controller::CtrlData GetExtraAttributePar(int32_t,std::string &);
                
protected:
    void clear_method_flag();
    void check_existing_methods(PyObject *);

    int32_t get_motor_nb_from_py();
    int32_t get_pseudo_motor_nb_from_py();
    
    bool		calc_pseudo;
    bool		calc_physical;
    bool		calc_all_pseudo;
    bool		calc_all_physical;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif /*PYPSEUDOMOTCTRL_H_*/
