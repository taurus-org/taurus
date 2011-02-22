#ifndef _PYZERODCTRL_H
#define _PYZERODCTRL_H

#include "PyCtrl.h"
#include <tango.h>
#include <pool/ZeroDCtrl.h>

extern "C"
{
    Controller *_create_PyZeroDExpChannelController(const char *,const char *,PyObject *,PyObject *);
}

/**
 * The Python 0D experiment channel controller base class
 */
class PyZeroDController:public PyController,public ZeroDController
{
public:
    PyZeroDController(const char *,const char *,PyObject *,PyObject *);
    ~PyZeroDController();

    virtual void AddDevice(int32_t idx);
    virtual void DeleteDevice(int32_t idx);
        
    virtual void PreReadAll();
    virtual void PreReadOne(int32_t);
    virtual void ReadAll();
    virtual double ReadOne(int32_t);
    
    virtual void PreStateAll();
    virtual void PreStateOne(int32_t);
    virtual void StateAll();
    virtual void StateOne(int32_t, Controller::CtrlState *);
    
    virtual std::string SendToCtrl(std::string &);
    
    virtual void SetExtraAttributePar(int32_t,std::string &,Controller::CtrlData &);
    virtual Controller::CtrlData GetExtraAttributePar(int32_t,std::string &);
                
protected:
    void clear_method_flag();
    void check_existing_methods(PyObject *);
    
    bool		pre_read_all;
    bool		pre_read_one;
    bool		read_all;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif /* _PYZERODCTRL_H */
