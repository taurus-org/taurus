#ifndef _CTRLFILE_
#define _CTRLFILE_

#include "PropertyData.h"
#include "ExternalFile.h"
#include "CPoolDefs.h"
#include <tango.h>

namespace Pool_ns
{
    
class PoolClass;
class Pool;

#define DEFAULT_GENDER			"Generic"
#define DEFAULT_MODEL			"Generic"
#define DEFAULT_ORGANIZATION	"Tango community"
/**
 * The CtrlFile class declaration
 */
class CtrlFile:public ExternalFile
{
public:
    CtrlFile(const std::string &);
    virtual ~CtrlFile();
    
    virtual int32_t get_classes(vector<string>&,vector<string> &) = 0;
    
    virtual void get_info(const std::string &, vector<string> &) = 0;
    virtual void get_info(const std::string &, const std::string &, vector<string> &) = 0;

    virtual void get_info_ex(const std::string &, Tango::DevVarCharArray *) = 0;
    virtual void get_info_ex(const std::string &, const std::string &, Tango::DevVarCharArray *) = 0;

    virtual void get_prop_info(const std::string &, vector<string> &);
    virtual void get_prop_info(const std::string &, vector<PropertyData*> &) = 0;
        
    virtual void get_sequence_value(const std::string &,const char *,vector<string> &) = 0;
    virtual void get_extra_attr_dec(const std::string &,const char *,vector<PoolExtraAttr> &) {}
    
    virtual int32_t get_MaxDevice(const std::string &cl) {return -1;}

    virtual void reload() = 0;

    CtrlType get_ctrl_type() {return ctrl_obj_type;}
            
protected:
    CtrlType        ctrl_obj_type;

    virtual void vecinfo_to_chararray(vector<string> &,Tango::DevVarCharArray *);
};

typedef vector<CtrlFile *>::iterator     vcf_ite;

typedef std::map<ElementId, CtrlFile*>   CtrlFileIdMap;
typedef CtrlFileIdMap::iterator          CtrlFileIdMapIt;

typedef std::map<std::string, ElementId> CtrlFileNameMap;
typedef CtrlFileNameMap::iterator        CtrlFileNameMapIt;

typedef std::multimap<std::string, ElementId> CtrlFileNameMultiMap;
typedef CtrlFileNameMultiMap::iterator        CtrlFileNameMultiMapIt;

} // End of Pool_ns namespace

#endif /*_CTRLFILE_*/
