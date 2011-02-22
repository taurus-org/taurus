
#include <PoolAPI.h>
#include <Pool.h>

namespace Pool_ns
{


PoolPlugin::PoolPlugin(Pool *p):
Tango::LogAdapter(p), pool(p)
{
	
}

PoolPlugin::~PoolPlugin()
{
	
}

PoolElement &PoolPlugin::get_elem_from_name(string &)
{
	
}

PoolElement &PoolPlugin::get_elem_from_id(int32_t )
{
	
}	

bool PoolPlugin::elem_exist(string &elem_name)
{
	list<PoolElement>::iterator ite;

	string elem_name_lower(elem_name);
	transform(elem_name_lower.begin(),
		elem_name_lower.end(),
		elem_name_lower.begin(),::tolower);
	
	for (ite = elem_list.begin();ite != elem_list.end();++ite)
	{
		string tg_name_lower(ite->obj_tango_name);
		transform(tg_name_lower.begin(),
			tg_name_lower.end(),
			tg_name_lower.begin(),::tolower);
		
		if ((ite->obj_alias_lower == elem_name_lower) ||
			(tg_name_lower == elem_name_lower))
		{
			return true;
		}
	}
	return false;
}

//+------------------------------------------------------------------
/**
 *	method:	PoolPlugin::get_ctrl_from_id
 *
 *	description:	Return a reference to the ControllerPool structure
 * 					for the controller with ID passed as input argument
 *
 * arg(s) : - id: The controller id
 *
 * This method returns a reference to the ControllerPool structure or
 * throws an exception
 */
//+------------------------------------------------------------------

ControllerPool &PoolPlugin::get_ctrl_from_id(long id)
{
	list<ControllerPool>::iterator ctrl_ite;
	for (ctrl_ite = ctrl_list.begin();ctrl_ite != ctrl_list.end();++ctrl_ite)
	{
		if (ctrl_ite->id == id)
			break;
	}

	if (ctrl_ite == ctrl_list.end())
	{
		TangoSys_OMemStream reason, descr, origin;
		reason << get_name() << "_BadArgument" << ends;
		descr << "No controller with ID " << id;
		descr << " found in controller list" << ends;
		origin << get_name() << "::get_ctrl_from_id" << endl;
		Tango::Except::throw_exception(reason.str(), descr.str(), origin.str());
	}	
	return *ctrl_ite;
}

ControllerPool &PoolPlugin::get_ctrl_from_elem_id(long id)
{
	PoolElement &elem = get_elem_from_id(id);
	return get_ctrl_from_elem(elem);
}

ControllerPool &PoolPlugin::get_ctrl_from_name(string &name)
{
	string name_lower(name);
	transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);
	
	list<ControllerPool>::iterator ctrl_ite;
	for (ctrl_ite = ctrl_list.begin();ctrl_ite != ctrl_list.end();++ctrl_ite)
	{
		if (ctrl_ite->name == name_lower)
			break;
	}

	if (ctrl_ite == ctrl_list.end())
	{
		TangoSys_OMemStream reason, descr, origin;
		reason << get_name() << "_ControllerNotFound" << ends;
		descr << "No controller with name " << name;
		descr << " found in controller list" << ends;
		origin << get_name() << "::get_ctrl_from_name" << endl;
		Tango::Except::throw_exception(reason.str(), descr.str(), origin.str());	
	}	
	return *ctrl_ite;
}
//+------------------------------------------------------------------
/**
 *	method:	PoolPlugin::get_ctrl_from_inst_name
 *
 *	description:	Return a reference to the ControllerPool structure
 * 					for the controller with instance name passed as input 
 * 					argument (controller instance name are uniq)
 *
 * arg(s) : - name: The controller instance name
 *
 * This method returns a reference to the ControllerPool structure or
 * throws an exception
 */
//+------------------------------------------------------------------

ControllerPool &PoolPlugin::get_ctrl_from_inst_name(string &name)
{
	string name_lower(name);
	transform(name_lower.begin(),name_lower.end(),name_lower.begin(),::tolower);
	
	list<ControllerPool>::iterator ctrl_ite;
	for (ctrl_ite = ctrl_list.begin();ctrl_ite != ctrl_list.end();++ctrl_ite)
	{
		string tmp_str(ctrl_ite->name);
		tmp_str.erase(0,tmp_str.find('/') + 1);
		if (tmp_str == name_lower)
			break;
	}

	if (ctrl_ite == ctrl_list.end())
	{
		TangoSys_OMemStream reason, descr, origin;
		reason << get_name() << "_ControllerNotFound" << ends;
		descr << "No controller with instance name " << name;
		descr << " found in controller list" << ends;
		origin << get_name() << "::get_ctrl_from_inst_name" << endl;
		Tango::Except::throw_exception(reason.str(), descr.str(), origin.str());
	}	
	return *ctrl_ite;
}

//+------------------------------------------------------------------
/**
 *	method:	PoolPlugin::get_ctrl_from_elem
 *
 *	description:	Retrieve the controller structure from the
 * 					pool element structure
 *
 * arg(s) : - chan: A reference to the controller structure
 */
//+------------------------------------------------------------------

ControllerPool &PoolPlugin::get_ctrl_from_elem(PoolElement &elem)
{
	list<ControllerPool>::iterator ite;
	for (ite = ctrl_list.begin();ite != ctrl_list.end();++ite)
	{
		if (ite->id == elem.ctrl_id)
			return *ite;
	}

	if (ite == ctrl_list.end())
	{	
		TangoSys_OMemStream reason, descr, origin;
		reason << get_name() << "_ControllerNotFound" << ends;
		descr << "Can't find controller for exp channel " << elem.name;
		descr << "(" << elem.obj_tango_name << ")" << ends;
		origin << get_name() << "::get_ctrl_from_inst_name" << endl;
		Tango::Except::throw_exception(reason.str(), descr.str(), origin.str());
	}
	return *ite;
}

void PoolPlugin::delete_ctrl(Tango::DevString )
{
	
}

void PoolPlugin::delete_elem(Tango::DevString )
{
	
}

}
