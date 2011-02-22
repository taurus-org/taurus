#ifndef _CPOOL_PYUTILS_H_
#define _CPOOL_PYUTILS_H_

#include <Python.h>
#include <string>
#include <vector>

#if PY_VERSION_HEX < 0x02050000
typedef int Py_ssize_t;
#endif

typedef PyObject* PyObjectPtr;

inline PyObjectPtr PyObject_GetAttrString_(PyObjectPtr o, const std::string &attr_name)
{
#if PY_VERSION_HEX < 0x02050000
    char *attr = const_cast<char *>(attr_name.c_str());
#else
    const char *attr = attr_name.c_str();
#endif
    return PyObject_GetAttrString(o, attr);
}

inline PyObjectPtr PyImport_ImportModule_(const std::string &name)
{
#if PY_VERSION_HEX < 0x02050000
    char *attr = const_cast<char *>(name.c_str());
#else
    const char *attr = name.c_str();
#endif
    return PyImport_ImportModule(attr);
}

class AutoPyDecRef : public std::vector<PyObjectPtr>
{
public:
    
    AutoPyDecRef(PyObjectPtr o = NULL):
    std::vector<PyObjectPtr>()
    { 
        append(o);
    }
    
    virtual ~AutoPyDecRef()
    {
        AutoPyDecRef::iterator it = begin(), e = end();
        for(; it != e; ++it)
            Py_XDECREF(*it);
    }
    
    inline PyObjectPtr append(PyObjectPtr obj)
    {
        if(obj) push_back(obj);
        return obj;
    }
};

/**
 * Python lock class. Handles the python GIL state
 */
class PythonGIL
{
protected:
    /** The GIL state storage */
    PyGILState_STATE gstate;

    /** keep a track on the count of GIL locks */
    static int64_t py_GIL_counter;
    
public:
    
    /**
     * Constructor
     */
    PythonGIL();
    
    /**
     * Acquire the python GIL
     */
    void get();
    
    /**
     * Release the python GIL
     */
    void release();

    /** the ID for this lock object. Helps debugging */
    int64_t lock_id;

};

/**
 * The AutoPythonGIL class declaration
 */
class AutoPythonGIL
{
public:
    PythonGIL py_lock;

    AutoPythonGIL();
    ~AutoPythonGIL();
};

#include <map>
#include <tango.h>

class PythonUtils
{
    /** map of python GIL locks by thread */
    //std::map<int, PythonGIL*>   py_locks;
    
    /** mutex for the py lock map */
    omni_mutex                  py_locks_mutex;
    
    /** python thread state at initialization time */
    PyThreadState*              py_thread_state;
    
    /** flag for python initialization */
    bool                        python_initialized;
    
    /** thread in which python was initialized */
    int                         init_python_th_id;

protected:
    
    /** singleton pointer */
    static PythonUtils          *_instance;

    /**
     * Constructor
     */
    PythonUtils();
    
public:
    
    /**
     * Get the Python helper instance
     * 
     * @return the singleton pointer to the python helper
     */
    static PythonUtils* instance();
    
    /**
     * Gets the python thread state for the original thread which initialized
     * python
     *
     * @return the python thread state pointer or NULL if python is not initialized
     */
    PyThreadState* get_py_thread_state();
    
    /**
     * Gets the python interpreter state.
     *
     * @return the python interpreter state pointer or NULL if python is not initialized
     */
    PyInterpreterState* get_py_interpreter_state();
    
    /**
     * Gets the current thread ID (omni thread ID)
     *
     * @return an integer representing the current thread ID
     */
    int get_thread_id();
    
    /**
     * Determines if python has been initialized or not
     *
     * @return true if python has benn initialized or false otherwise
     */
    inline bool is_python_initialized()
    { return python_initialized; }
    
    /**
     * Ensures python is safe to execute for the current thread
     */
    PyGILState_STATE ensure();
    
    /**
     * Releases the python environment for the current thread
     */
    void release(PyGILState_STATE);
    
    /**
     * Clears all python locks except the one for the given thread ID
     * 
     * @param[in] exception_thread_id the thread ID to be excluded from the clean up
     */
    void clear(int );

    /**
     * Clears the current thread python lock
     */
    void clear_current_thread();
    
    /**
     * Initializes python
     */
    void initialize();
    
    /**
     * Finalizes python
     */
    void finalize();
    
    /**
     * Translate a python exception into a tuple of three strings
     *
     * @param[out] origin string to be filled with the exception origin
     * @param[out] desc string to be filled with the exception description
     * @param[out] reason string to be filled with the exception reason
     */
    void translate_exception(std::string &, std::string &, std::string &);
};

/**
 * The AutoCleanPythonGIL class declaration
 */
class AutoCleanPythonGIL
{
public:
    /// Constructor
    AutoCleanPythonGIL() {}
    
    /// Destructor
    ~AutoCleanPythonGIL()
    {
        PythonUtils::instance()->clear_current_thread();
    }
};

#endif
