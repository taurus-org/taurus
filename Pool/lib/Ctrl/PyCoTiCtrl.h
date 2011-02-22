#ifndef _PYCOTICTRL_H
#define _PYCOTICTRL_H

#include "PyCtrl.h"
#include <tango.h>
#include <pool/CoTiCtrl.h>

extern "C"
{
    Controller *_create_PyCoTiController(const char *,const char *,PyObject *,PyObject *);
}

/**
 * The Python counter/timer controller base class
 */
class PyCoTiController:public PyController, public CoTiController
{
public:
    PyCoTiController(const char *,const char *,PyObject *,PyObject *);
    ~PyCoTiController();

    virtual void AddDevice(int32_t idx);
    virtual void DeleteDevice(int32_t idx);
        
    virtual void PreReadAll();
    virtual void PreReadOne(int32_t);
    virtual void ReadAll();
    virtual double ReadOne(int32_t);
    
    virtual void PreLoadAll();
    virtual bool PreLoadOne(int32_t,double);
    virtual void LoadOne(int32_t,double);
    virtual void LoadAll();

    virtual void PreStateAll();
    virtual void PreStateOne(int32_t);
    virtual void StateAll();
    virtual void StateOne(int32_t, Controller::CtrlState *);

    virtual void PreStartAllCT();
    virtual bool PreStartOneCT(int32_t);
    virtual void StartOneCT(int32_t);
    virtual void StartAllCT();
    
    virtual void AbortOne(int32_t);
    virtual string SendToCtrl(string &);
    
    virtual void SetExtraAttributePar(int32_t,string &,Controller::CtrlData &);
    virtual Controller::CtrlData GetExtraAttributePar(int32_t,string &);
                
protected:
    void clear_method_flag();
    void check_existing_methods(PyObject *);

    bool		pre_start_all_ct;
    bool		pre_start_one_ct;
    bool		start_one_ct;
    bool		start_all_ct;
    
    bool		pre_load_all;
    bool		pre_load_one;
    bool		load_one;
    bool		load_all;
    
    bool		pre_read_all;
    bool		pre_read_one;
    bool		read_all;
            
    bool		abort_one;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif /* _PYCOTICTRL_H */
