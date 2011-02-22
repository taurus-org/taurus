//=============================================================================
//
// file :         PoolClass.h
//
// description :  Include for the PoolClass root class.
//                This class is represents the singleton class for
//                the Pool device class.
//                It contains all properties and methods which the 
//                Pool requires only once e.g. the commands.
//			
// project :      TANGO Device Server
//
// copyleft :     European Synchrotron Radiation Facility
//                BP 220, Grenoble 38043
//                FRANCE
//
//=============================================================================

#ifndef _EXTERNALFICA_H_
#define _EXTERNALFICA_H_

#include "PyUtils.h"
#include <tango.h>

#include "CPoolDefs.h"

namespace Pool_ns
{

class ExternalFile;
class Pool;
class PoolClass;

class ExternalFiCa;

/**
 *  The PoolLock class declaration
 */
class PoolLock
{
protected:

    Tango::TangoMonitor     mon;                   ///< tango monitor
    AutoPythonGIL           *pygil;                ///< python global interpreter lock
    ExternalFiCa            *my_external_fica;     ///< pointer to the external Fica 
    bool                    lock_wanted;           ///< lock wanted
    int32_t                 lock_count;
public:
  
    /**
     * Constructor
     * 
     * @param str name
     * @param external_fica pointer to the external Fica
     */ 
    PoolLock(const char *str,ExternalFiCa *external_fica):
    mon(str), pygil(NULL), my_external_fica(external_fica), lock_wanted(true),
    lock_count(0) {}
    
    /// Destructor
    ~PoolLock() {}
    
    /**
     * Acquire the monitor
     */
    void get_monitor();
    
    /**
     * Release the monitor
     */
    void rel_monitor();
  
    /**
     * Enable/Disable lock
     * 
     * @param val enable/disavle
     */
    void lock_enable(bool val) {lock_wanted = val;}
    
    /** 
     * Determines if the lock is enabled
     * 
     * @return <code>true</code> if enabled or <code>false</code> otherwise
     */
    bool is_lock_enabled() {return lock_wanted;}

};

/**
 * The AutoPoolLock class declaration
 */
class AutoPoolLock
{
public:
    
    /**
     * Constructor
     * 
     * @param po_lock reference to the PoolLock
     */
    AutoPoolLock(PoolLock &po_lock): pool_lock(po_lock) 
    { pool_lock.get_monitor(); }
    
    /// Destructor
    ~AutoPoolLock() 
    { pool_lock.rel_monitor(); }
    
protected:
    PoolLock &pool_lock;	///< reference to the PoolLock
};

/**
 * The ExternalFiCa class declaration
 */
class ExternalFiCa:public Tango::LogAdapter
{
protected:

    std::string			name;            ///< FiCa name
    PoolLock			monitor;         ///< the monitor
    ExternalFile		*my_file;        ///< pointer to the ExternalFile to which this FiCa belongs

    Pool_ns::ElementId  id;              ///< element id
    
public:
    
    /**
     * Constructor
     * 
     * @param type       the FiCa type
     */
    ExternalFiCa(const std::string &, Pool *);

    /**
     * Constructor
     * 
     * @param type       the FiCa type
     * @param f_name     file name
     * @param class_name class name
     */
    ExternalFiCa(const std::string &, const std::string &, const std::string &, Pool *);
    
    /// Destructor
    virtual ~ExternalFiCa();

    /**
     *
     */
    inline Pool_ns::ElementId get_id()
    { return id; }
    
    inline void set_id(Pool_ns::ElementId elem_id)
    { this->id = elem_id; }

    /**
     * Gets the FiCa name
     * @return reference to the string with the FiCa name
     */
    std::string &get_name()
    { return name; }
    
    /**
     * Gets a reference to the monitor of the FiCa
     * @return a reference to the monitor
     */
    PoolLock &get_mon()
    { return monitor; }
        
    /**
     * Gets the ExternalFile
     * @return a pointer to the ExternalFile
     */
    ExternalFile *get_file()
    { return my_file; }

    /**
     * Gets the language
     * @return the language
     */
    Language get_language();
    
    /**
     * check if a file name is defined within all the directories defined in 
     * the PYTHONPATH env. variable. It throws an exception if the file does
     * not exist
     * 
     * @param class_name python class name to be checked
     */
    void check_python(const std::string &);
 
};

typedef vector<ExternalFiCa *>::iterator vex_ite;


}

#endif // EXTERNALFICA_H_
