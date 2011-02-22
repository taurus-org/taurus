#include "PyUtils.h"
#include <iostream>
#include <tango.h>

#include "PoolClass.h"

int64_t PythonGIL::py_GIL_counter = 0;

PythonGIL::PythonGIL(): gstate(PyGILState_UNLOCKED), lock_id(++py_GIL_counter)
{}

void PythonGIL::get()
{
    gstate = PythonUtils::instance()->ensure();
}

void PythonGIL::release()
{
    PythonUtils::instance()->release(gstate);
}

AutoPythonGIL::AutoPythonGIL()
{ 
    py_lock.get();
}

AutoPythonGIL::~AutoPythonGIL()
{
    py_lock.release();
}

PythonUtils* PythonUtils::_instance = NULL;

PythonUtils::PythonUtils(): py_thread_state(NULL), 
    python_initialized(false), init_python_th_id(-1)
{ }

PythonUtils* PythonUtils::instance()
{
    if(_instance == NULL)
        _instance = new PythonUtils;
    return _instance;
}

void PythonUtils::initialize()
{
    if (python_initialized)
        return;

    Py_Initialize();
    
    init_python_th_id = get_thread_id();
    
    if (!PyEval_ThreadsInitialized())
    {
        PyEval_InitThreads();
    }
    else
    {
        std::cerr << "Python threads already improperly initialized by "
                     "someone else !!!" << std::endl;
        PyEval_AcquireLock();
    }
    
    py_thread_state = PyEval_SaveThread();
    
    python_initialized = true;
}

void PythonUtils::finalize()
{
    if (!python_initialized)
        return;
    
    clear(get_thread_id());
    
    PyEval_RestoreThread(get_py_thread_state());
    
    Py_Finalize();
    
    python_initialized = false;
}

PyThreadState* PythonUtils::get_py_thread_state()
{
    return py_thread_state;
}

PyInterpreterState* PythonUtils::get_py_interpreter_state()
{
    PyThreadState* tstate = get_py_thread_state();
    if (!python_initialized || !tstate)
        return NULL;
    return tstate->interp;
}

PyGILState_STATE PythonUtils::ensure()
{
    return PyGILState_Ensure();
}

void PythonUtils::release(PyGILState_STATE gstate)
{
    PyGILState_Release(gstate);
}

int PythonUtils::get_thread_id()
{
    return omni_thread::self()->id();
}

void PythonUtils::clear(int except_thread_id)
{

}

void PythonUtils::clear_current_thread()
{

}

void PythonUtils::translate_exception(std::string &reason, std::string &desc, std::string &origin)
{
    PyObjectPtr exec_ptr, value_ptr, tb_ptr;
    PyErr_Fetch(&exec_ptr, &value_ptr, &tb_ptr);
    
    AutoPyDecRef ref(exec_ptr);
    ref.append(value_ptr);
    ref.append(tb_ptr);
    
//
// Send a default exception in case Python does not send us information
//
    if (!value_ptr)
    {
        origin = "PyExternalFile::translate_py_error";
        desc   = "A badly formed exception has been received";
        reason = "Pool_BadPythonException";
        return;
    }
    
//
// Populate a one level DevFailed exception
//
    PyObject *traceback = ref.append(PyImport_ImportModule("traceback"));
    if (traceback)
    {
        PyObjectPtr format_tb, format_exception_only, join, tbList, 
                    emptyString, strRetval;

//
// Format the traceback part of the Python exception
// and store it in the origin part of the Tango exception
//
        format_tb = ref.append( PyString_FromString("format_tb") );
        tbList = ref.append( 
            PyObject_CallMethodObjArgs(traceback, format_tb,
                                       tb_ptr == NULL ? Py_None : tb_ptr, NULL));
                                       
        emptyString = ref.append( PyString_FromString("") );
        join = ref.append( PyString_FromString("join") );
        strRetval = ref.append( 
            PyObject_CallMethodObjArgs(emptyString, join, tbList, NULL) );

        origin = PyString_AsString(strRetval);

//
// Format the exec and value part of the Python exception
// and store it in the desc part of the Tango exception
//
        format_exception_only = ref.append( PyString_FromString("format_exception_only") );
        tbList = ref.append( 
            PyObject_CallMethodObjArgs(traceback, format_exception_only, exec_ptr,
                                       value_ptr == NULL ? Py_None : value_ptr, NULL));
        emptyString = ref.append( PyString_FromString("") );
        strRetval = ref.append( 
            PyObject_CallMethodObjArgs(emptyString, join, tbList, NULL) );

        desc = PyString_AsString(strRetval);

        reason = "Pool_PythonControllerError";
    }
    else
    {
//
// Send a default exception because we can't format the
// different parts of the Python's one !
//
        origin = "PyExternalFile::translate_py_error";
        desc   = "Can't import Python traceback module. Can't extract info from Python exception";
        reason = "Pool_PythonControllerError";
    }
}

