#ifndef _PYIOREGISTERCONTROLLER_H
#define _PYIOREGISTERCONTROLLER_H

#include "PyCtrl.h"
#include <pool/IORegisterCtrl.h>
#include <tango.h>

extern "C"
{
    Controller *_create_PyIORegisterController(const char *,const char *,PyObject *,PyObject *);
}


/**
 * The Python ioregister controller base class
 */
class PyIORegisterController : public PyController, public IORegisterController
{
public:
    PyIORegisterController(const char *,const char *,PyObject *,PyObject *);
    ~PyIORegisterController();

    virtual void AddDevice(int32_t idx);
    virtual void DeleteDevice(int32_t idx);

    /**
     *
     * @param idx - ioregister id
     */
    virtual int32_t ReadOne(int32_t); 

    /**
     *
     * @param idx - ioregister id
     */
    virtual void WriteOne(int32_t, int32_t write_len ); 
    

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

    bool		read_one;
    bool		write_one;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif // _PYIOREGISTERCONTROLLER_H
