#ifndef _POOLPLUGIN_H_
#define _POOLPLUGIN_H_

#include <Ctrl.h>

namespace Pool_ns
{



///////////////////////////////////////////////////////////////////////////////
struct PoolPluginExtension
{
	string provider_name;
	string extension_name;
	uint32_t extension_version;
};

struct ElemCreateParams
{
	uint32_t idx;
	string name;
	string ctrl_name;
};

struct CtrlCreateParams
{
	string type;
	string lib_name;
	string class_name;
	string inst_name;
};

class PoolPlugin: public Tango::LogAdapter
{
private:

	Pool					*pool;
	
	string					name;
	string					service;		///< service provided by this plugin
	
	vector<string>			dependencies;	///< list of services the plugin depends on

	list<PoolElement> 		elem_list;
	list<ControllerPool>	ctrl_list;

	virtual void solve_dependencies() = 0;

public:

	PoolPlugin(Pool *);
	virtual ~PoolPlugin();

	string &get_name()		{ return name; }
	string &get_service()	{ return service; }
	
	vector<string> &get_deps()	{ return dependencies; }
	
	list<PoolElement> &get_elem_list()		{ return elem_list; }
	list<ControllerPool> &get_ctrl_list()	{ return ctrl_list; }

	virtual void init()			{ }	
	virtual void post_init()				{ solve_dependencies(); }
	virtual void create_proxies() 			{ }
	
	virtual PoolElement &create_elem(ElemCreateParams &) = 0;
	PoolElement &get_elem_from_name(string &);
	PoolElement &get_elem_from_id(int32_t );
	bool elem_exist(string &);
	
	virtual ControllerPool &create_ctrl(CtrlCreateParams &) = 0;
	ControllerPool &get_ctrl_from_id(int32_t );
	ControllerPool &get_ctrl_from_name(string &);
	ControllerPool &get_ctrl_from_inst_name(string &);
	
	ControllerPool &get_ctrl_from_elem(PoolElement &);
	ControllerPool &get_ctrl_from_elem_id(int32_t );
	
	virtual void delete_ctrl(Tango::DevString ) = 0;
	virtual void delete_elem(Tango::DevString ) = 0;
	
	//void Pool::restore_ctrl(vector<Pool::CtrlBkp> *,vector<Pool::ObjBkp> *);
	
};

typedef PoolPlugin *(*PoolPlugin_creator_ptr)(Pool *);

}  // namespace

#endif
