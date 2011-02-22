#ifndef _PYCOMCHCONTROLLER_H
#define _PYCOMCHCONTROLLER_H

#include "PyCtrl.h"
#include <pool/ComCtrl.h>
#include <tango.h>

extern "C"
{
    Controller *_create_PyCommunicationController(const char *,const char *,PyObject *,PyObject *);
}


/**
 * The Python communication controller base class
 */
class PyComController : public PyController, public ComController
{
public:
    PyComController(const char *,const char *,PyObject *,PyObject *);
    ~PyComController();

    virtual void AddDevice(int32_t idx);
    virtual void DeleteDevice(int32_t idx);

    /**
     * @param idx - communication channel id
     */
    virtual void OpenOne(int32_t);
    
    /**
     * @param idx - communication channel id
     */
    virtual void CloseOne(int32_t);

    /**
     * Atempts to read data into the given buffer. 
     * The length of the data can be checked by inspecting the buffer.
     * 
     * @param idx - communication channel id
     * @param max_read_len - max length of buff to read.
     *                        0 empties the read_buff and returns 0.
     *                       -1 to read all available data from the channel.
     */
    virtual std::string &ReadOne(int32_t, int32_t max_read_len = -1); 
    
    /**
     * Atempts to read data into the given buffer up to a new line character. 
     * The length of the data can be checked by inspecting the buffer.
     * 
     * @param idx - communication channel id
     */
    virtual std::string &ReadLineOne(int32_t); 
        
    /**
     * @param idx - communication channel id
     * @param write_buff - buffer which contains data to be written
     * @param write_len - length of buffer to write.
     *                    0 will not write anything
     *                    -1 (default value) will atempt to write the entire contents of the write_buff
     * @return the length of the data actually written
     */
    virtual int32_t WriteOne(int32_t, std::string &, int32_t write_len = -1); 
    
    /**
     * @param idx - communication channel id
     * @param write_buff - buffer which contains data to be written
     * @param write_len - length of buffer to write.
     *                    0 will not write anything
     *                    -1 will atempt to write the entire contents of the write_buff
     * @param max_read_len - max length of buff to read.
     *                        0 empties the read_buff and returns 0.
     *                       -1 to read all available data from the channel.
     * @return the length of the data actually written
     */
    virtual std::string &WriteReadOne(int32_t, std::string &, int32_t write_len = -1, int32_t max_read_len = -1); 

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
    bool		read_line_one;
    bool		write_one;
    bool		write_read_one;
    bool		open_one;
    bool		close_one;
};

typedef Controller *(*PyCtrl_creator_ptr)(const char *,const char *,PyObject *,PyObject *);

#endif // _PYCOMCHCONTROLLER_H
