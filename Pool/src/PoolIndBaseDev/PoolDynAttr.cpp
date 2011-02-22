//+=============================================================================
//
// file :         PoolDynAttr.cpp
//
// description :  C++ source for the PoolIndBaseDev and its commands. 
//                The class is derived from Device. It represents the
//                CORBA servant object which will be accessed from the
//                network. All commands which can be executed on the
//                PoolIndBaseDev are implemented in this file.
//
// project :      TANGO Device Server
//
// $Author$
//
// $Revision$
//
// $Log$
// Revision 1.1  2007/08/17 13:10:09  tcoutinho
// - pseudo motor restructure
// - pool base dev class restructure
// - initial commit for pseudo counters
//
// Revision 1.5  2007/06/13 15:17:16  etaurel
// - Only a new log message
//
// Revision 1.4  2007/02/22 12:03:52  tcoutinho
// - just fixed some error messages
//
// Revision 1.3  2007/02/08 07:55:54  etaurel
// - Changes after compilation -Wall. Handle case of different ctrl for the
// same class of device but with same extra attribute name
//
// Revision 1.2  2007/01/30 15:57:41  etaurel
// - Add a missing data member init
// - Add code to manage case with different controller of the same Tango class
// with extra attribute of the same name but with different data type
//
// Revision 1.1  2007/01/16 14:22:25  etaurel
// - Initial revision
//
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//=============================================================================

#include "CtrlFiCa.h"
#include "Utils.h"
#include "PoolUtil.h"
#include "PoolBaseUtil.h"
#include "PoolIndBaseDev.h"
#include "PoolDynAttr.h"

namespace Pool_ns
{
	
//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::create_dyn_attr
// 
// description : 	Creates the dynamic attributes (if any) attache dto this
//					device
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::create_dyn_attr()
{
	DEBUG_STREAM << "Adding dynamic attribute for motor " << device_name << endl;
	
//
// Get the list of extra attributes
//

	vector<PoolExtraAttr> &extra = fica_ptr->get_extra_attributes();
	
	DEBUG_STREAM << extra.size() << " extra attributes defined" << endl;
	for (unsigned long ll= 0;ll < extra.size();ll++)
	{
		DEBUG_STREAM << "Extra attribute name = " << extra[ll].ExtraAttr_name << endl;
		DEBUG_STREAM << "Extra attribute type = " << extra[ll].ExtraAttr_data_type << endl;
	}

//
// Create one attribute for each of them
// and some storage to keep its value
//

	for (unsigned long loop = 0;loop < extra.size();loop++)
	{
		create_one_extra_attr(extra[loop]);
	}
	
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::create_one_extra_attr
// 
// description : 	Create one dynamic attribute for the motor 
//
// args : - x_attr : Extra attribute info (name, data type and R/W type)
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::create_one_extra_attr(PoolExtraAttr &x_attr)
{
	
//
// Create the attribute
//

	Tango::Attr *new_attr = NULL;
	
	switch (x_attr.ExtraAttr_data_type)
	{
		
//
// Boolean attribute
//

		case BOOLEAN:
		{
			if (x_attr.ExtraAttr_write_type == READ)
				new_attr = new Boo_R_Attrib(x_attr.ExtraAttr_name);
			else
			{
				new_attr = new Boo_RW_Attrib(x_attr.ExtraAttr_name);
				new_attr->set_memorized();
			}

//
// The default value for the attribute is True.
// Is it OK also for all attributes ?
//

			map<string,bool>::iterator map_ite = bool_extra_data.find(x_attr.ExtraAttr_name);
			if (map_ite == bool_extra_data.end())
			{		
				pair<map<string,bool>::iterator,bool> status;
				status = bool_extra_data.insert(make_pair(x_attr.ExtraAttr_name,true));
				if (status.second == false)
				{
					TangoSys_OMemStream o;
					o << "Can't create storage for motor extra attribute " << x_attr.ExtraAttr_name << ends;
					Tango::Except::throw_exception((const char *)"Pool_CantCreateExtraDataStorage",o.str(),
			   									   (const char *)"PoolIndBaseDev::create_one_extra_attr()");	
				}
			}
		}	
		break;

//
// Long attribute
//
		
		case LONG:
		{
			if (x_attr.ExtraAttr_write_type == READ)
				new_attr = new Lo_R_Attrib(x_attr.ExtraAttr_name);
			else
			{
				new_attr = new Lo_RW_Attrib(x_attr.ExtraAttr_name);
				new_attr->set_memorized();
			}

			map<string,Tango::DevLong>::iterator map_ite = long_extra_data.find(x_attr.ExtraAttr_name);
			if (map_ite == long_extra_data.end())
			{				
				pair<map<string,Tango::DevLong>::iterator,long> status;
				status = long_extra_data.insert(make_pair(x_attr.ExtraAttr_name,0));
				if (status.second == false)
				{
					TangoSys_OMemStream o;
					o << "Can't create storage for motor extra attribute " << x_attr.ExtraAttr_name << ends;
					Tango::Except::throw_exception((const char *)"Pool_CantCreateExtraDataStorage",o.str(),
		   									   (const char *)"PoolIndBaseDev::create_one_extra_attr()");	
				}
			}
		}
		break;

//
// Double attribute
//
		
		case DOUBLE:
		{
			if (x_attr.ExtraAttr_write_type == READ)
				new_attr = new Dou_R_Attrib(x_attr.ExtraAttr_name);
			else
			{
				new_attr = new Dou_RW_Attrib(x_attr.ExtraAttr_name);
				new_attr->set_memorized();
			}

			map<string,double>::iterator map_ite = double_extra_data.find(x_attr.ExtraAttr_name);
			if (map_ite == double_extra_data.end())
			{				
				pair<map<string,double>::iterator,double> status;
				status = double_extra_data.insert(make_pair(x_attr.ExtraAttr_name,0.0));
				if (status.second == false)
				{
					TangoSys_OMemStream o;
					o << "Can't create storage for motor extra attribute " << x_attr.ExtraAttr_name << ends;
					Tango::Except::throw_exception((const char *)"Pool_CantCreateExtraDataStorage",o.str(),
		   										   (const char *)"PoolIndBaseDev::create_one_extra_attr()");	
				}
			}
		}
		break;

//
// String attribute
//
		
		case STRING:
		{
			if (x_attr.ExtraAttr_write_type == READ)
				new_attr = new Str_R_Attrib(x_attr.ExtraAttr_name);
			else
			{
				new_attr = new Str_RW_Attrib(x_attr.ExtraAttr_name);
				new_attr->set_memorized();
			}

			map<string,long>::iterator map_ite = string_extra_index.find(x_attr.ExtraAttr_name);
			if (map_ite == string_extra_index.end())
			{				
				pair<map<string,long>::iterator,long> status;
				status = string_extra_index.insert(make_pair(x_attr.ExtraAttr_name,sf_index));
				if (status.second == false)
				{
					TangoSys_OMemStream o;
					o << "Can't create storage for motor extra attribute " << x_attr.ExtraAttr_name << ends;
					Tango::Except::throw_exception((const char *)"Pool_CantCreateExtraDataStorage",o.str(),
		   									  	 (const char *)"PoolIndBaseDev::create_one_extra_attr()");	
				}
			}
			sf_index++;
			string_extra_data.resize(sf_index);
		}
		break;
	}

	new_attr->set_disp_level(Tango::EXPERT);
	this->add_attribute(new_attr);	
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::remove_unwanted_dyn_attr_from_device
// 
// description : 	Remove the dynamic attributes (if any) attached to this
//					device
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::remove_unwanted_dyn_attr_from_device()
{
	
//
// Get how many attributes this device has
// (static and added)
//

	long nb_static = utils->get_static_attr_nb(get_device_class());
	long nb_att = dev_attr->get_attr_nb(); 
	
	vector<PoolExtraAttr> &extra = fica_ptr->get_extra_attributes();	
	long nb_added_attr = extra.size();
		
//
// Leave method if the device does not have any unwanted attribute
//

	long nb_unwanted = nb_att - (nb_static + nb_added_attr);
	if (nb_unwanted <= 0)
	{
//		return;
	}

//
// Get the number of real "static" attribute (remove the state
// and status one)
//
	
	nb_static = nb_static - 2;
	
//
// Build a list of attributes to be removed. These are the attributes which are
// not member of the extra list
//

	long loop;
	vector<string> att_to_remove;
	vector<bool> att_to_free;
	vector<long> att_to_add;	
	
	for (loop = nb_static;loop < nb_att;loop++)
	{
		bool leave_loop = false;
		string &att_name_lower = dev_attr->get_attr_by_ind(loop).get_name_lower();
		if ((att_name_lower == "state") || (att_name_lower == "status"))
			continue;

		Tango::Attribute &the_att = dev_attr->get_attr_by_ind(loop);			
		string &att_name = the_att.get_name();

		unsigned long ll;			
		for (ll = 0;ll < extra.size();ll++)
		{
			if (extra[ll].ExtraAttr_name == att_name)
			{
				leave_loop = true;
				break;
			}
		}
		
		if (leave_loop == true)
		{
			
//
// Check that the attribute we have has the correct data type and R/W type
// (in case of devices coming from different ctrl with extra attributes having
// the same name but with a different data type or R/W type)
//

			if ((ExtraAttrDataType_2_Tango(extra[ll].ExtraAttr_data_type) == the_att.get_data_type()) &&
				(ExtraAttrWriteType_2_Tango(extra[ll].ExtraAttr_write_type) == the_att.get_writable()))
			{
				continue;
			}
			else
			{
				att_to_add.push_back(ll);
				att_to_remove.push_back(att_name);
				att_to_free.push_back(true);
			}
		}		
		else
		{
			att_to_remove.push_back(att_name);
			att_to_free.push_back(false);
		}
	}

//
// Remove the unwanted attribute to this device
//

	for (unsigned long lp = 0;lp < att_to_remove.size();lp++)
	{
		DEBUG_STREAM << "Removing dynamic attribute " << att_to_remove[lp] << endl;
		dev_attr->remove_attribute(att_to_remove[lp]);
	}
	
//
// Add the attribute removed due to bad data or write type
//

	for (unsigned long lp = 0;lp < att_to_add.size();lp++)
	{
		DEBUG_STREAM << "Adding dynamic attribute (because bad data or write type) " << endl;
		
		Tango::Attr &att = device_class->get_class_attr()->get_attr(extra[att_to_add[lp]].ExtraAttr_name);
		device_class->get_class_attr()->remove_attr(extra[att_to_add[lp]].ExtraAttr_name);
		delete &att;
		
		create_one_extra_attr(extra[att_to_add[lp]]);
	}
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Boo_R_Attr
// 
// description : 	Extract real attribute values for Boo_R_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Boo_R_Attr(Tango::Attribute &attr)
{
    PoolElement &pool_element = get_pool_element();
	string par_name(attr.get_name());
	DEBUG_STREAM << "PoolIndBaseDev::read_Boo_R_Attr(Tango::Attribute &attr) for attribute " << par_name << " entering... " << endl;

	Controller::CtrlData tmp_val;	
	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			tmp_val = pool_element.get_controller()->GetExtraAttributePar(get_axis(), par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Boo_R_Attr");
		
		if ((tmp_val.data_type == Controller::STRING) && (tmp_val.str_data == DEFAULT_DEFINITION_STR))
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not re-defined method to get motor extra attributes",
					  (const char *)"PoolIndBaseDev::read_Boo_R_Attr");
		}
		if (tmp_val.data_type != Controller::BOOLEAN)
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor extra attributes. It returns a bad data type",
					  (const char *)"PoolIndBaseDev::read_Boo_R_Attr");
		}		
	}
		
	map<string,bool>::iterator map_ite = bool_extra_data.find(par_name);
	if (map_ite == bool_extra_data.end())
	{
		TangoSys_OMemStream o;
		o << "Can't find data storage for extra attribute " << par_name << ends;
		Tango::Except::throw_exception((const char *)"Pool_CantFindDataStorage",o.str(),
   									   (const char *)"PoolIndBaseDev::read_Boo_R_Attr()");	
	}

	if (!pool_element.get_simulation_mode())	
		map_ite->second = tmp_val.bo_data;
	attr.set_value(&(bool_extra_data[par_name]));
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Boo_RW_Attr
// 
// description : 	Extract real attribute values for Boo_R_NoMemAttr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Boo_RW_Attr(Tango::Attribute &attr)
{
	DEBUG_STREAM << "PoolIndBaseDev::read_Boo_RW_Attr(Tango::Attribute &attr) entering... "<< endl;
	read_Boo_R_Attr(attr);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::write_Boo_RW_Attr
// 
// description : 	Write Boo_RW_Attr attribute values to hardware.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::write_Boo_RW_Attr(Tango::WAttribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::write_Boo_RW_Attr(Tango::WAttribute &attr) entering... "<< endl;
	
	bool received_value;	
	attr.get_write_value(received_value);

	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	DEBUG_STREAM << "PoolIndBaseDev: new extra attribute " << par_name << " set to value = " << received_value << endl;
	tmp_val.bo_data = received_value;
	tmp_val.data_type = Controller::BOOLEAN;

	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{	
		    pool_element.get_controller()->SetExtraAttributePar(get_axis(),par_name,tmp_val);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Boo_RW_Attr");
	}
}


//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Dou_R_Attr
// 
// description : 	Extract real attribute values for Dou_R_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Dou_R_Attr(Tango::Attribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::read_Dou_R_Attr(Tango::Attribute &attr) entering... " << endl;
	
	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			tmp_val = pool_element.get_controller()->GetExtraAttributePar(get_axis(),par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Dou_R_Attr");
		
		if ((tmp_val.data_type == Controller::STRING) && (tmp_val.str_data == DEFAULT_DEFINITION_STR))
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not re-defined method to get motor features",
					  (const char *)"PoolIndBaseDev::read_Dou_R_Attr");
		}
		if (tmp_val.data_type != Controller::DOUBLE)
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor extra attributes. It returns a bad data type",
					  (const char *)"PoolIndBaseDev::read_Dou_R_Attr");
		}		
	}	
		
	map<string,double>::iterator map_ite = double_extra_data.find(par_name);
	if (map_ite == double_extra_data.end())
	{
		TangoSys_OMemStream o;
		o << "Can't find data storage for extr attribute " << par_name << ends;
		Tango::Except::throw_exception((const char *)"Pool_CantFindDataStorage",o.str(),
   									   (const char *)"PoolIndBaseDev::read_Dou_R_Attr()");	
	}

	if (!pool_element.get_simulation_mode())	
		map_ite->second = tmp_val.db_data;
	attr.set_value(&(double_extra_data[par_name]));
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Dou_RW_Attr
// 
// description : 	Extract real attribute values for Dou_RW_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Dou_RW_Attr(Tango::Attribute &attr)
{
	DEBUG_STREAM << "PoolIndBaseDev::read_Dou_RW_Attr(Tango::Attribute &attr) entering... "<< endl;
	read_Dou_R_Attr(attr);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::write_Boo_RW_Attr
// 
// description : 	Write Dou_RW_Attr attribute values to hardware.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::write_Dou_RW_Attr(Tango::WAttribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::write_Dou_RW_Attr(Tango::WAttribute &attr) entering... "<< endl;
	
	double received_value;	
	attr.get_write_value(received_value);

	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	DEBUG_STREAM << "PoolIndBaseDev: new extra attribute " << par_name << " set to value = " << received_value << endl;
	tmp_val.db_data = received_value;
	tmp_val.data_type = Controller::DOUBLE;

	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			pool_element.get_controller()->SetExtraAttributePar(get_axis(),par_name,tmp_val);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Dou_RW_Attr");
	}
}


//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Lo_R_Attr
// 
// description : 	Extract real attribute values for Lo_RW_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Lo_R_Attr(Tango::Attribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::read_Lo_R_Attr(Tango::Attribute &attr) entering... "<< endl;
	
	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			tmp_val = pool_element.get_controller()->GetExtraAttributePar(get_axis(),par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Lo_R_Attr");
		
		if ((tmp_val.data_type == Controller::STRING) && (tmp_val.str_data == DEFAULT_DEFINITION_STR))
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not re-defined method to get motor features",
					  (const char *)"PoolIndBaseDev::read_Lo_R_Attr");
		}
		if (tmp_val.data_type != Controller::INT32)
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor extra attributes. It returns a bad data type",
					  (const char *)"PoolIndBaseDev::read_Lo_R_Attr");
		}	
	}	
		
	map<string,Tango::DevLong>::iterator map_ite = long_extra_data.find(par_name);
	if (map_ite == long_extra_data.end())
	{
		TangoSys_OMemStream o;
		o << "Can't find data storage for extra attribute " << par_name << ends;
		Tango::Except::throw_exception((const char *)"Pool_CantFindDataStorage",o.str(),
   									   (const char *)"PoolIndBaseDev::read_Lo_R_Attr()");	
	}

	if (!pool_element.get_simulation_mode())	
		map_ite->second = tmp_val.int32_data;
	attr.set_value(&(long_extra_data[par_name]));
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Lo_RW_Attr
// 
// description : 	Extract real attribute values for Lo_RW_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Lo_RW_Attr(Tango::Attribute &attr)
{
    DEBUG_STREAM << "PoolIndBaseDev::read_Lo_RW_Attr(Tango::Attribute &attr) entering... "<< endl;
	read_Lo_R_Attr(attr);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::write_Lo_RW_Attr
// 
// description : 	Write Lo_RW_Attr attribute values to hardware.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::write_Lo_RW_Attr(Tango::WAttribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::write_Lo_RW_Attr(Tango::WAttribute &attr) entering... "<< endl;
	
	Tango::DevLong received_value;
	attr.get_write_value(received_value);

	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	DEBUG_STREAM << "PoolIndBaseDev: new extra attribute " << par_name << " set to value = " << received_value << endl;
	tmp_val.data_type = Controller::INT32;
	tmp_val.int32_data = received_value;

	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
		    pool_element.get_controller()->SetExtraAttributePar(get_axis(),par_name,tmp_val);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Lo_RW_Attr");
	}
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Str_R_Attr
// 
// description : 	Extract real attribute values for Str_R_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Str_R_Attr(Tango::Attribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::read_Str_R_Attr(Tango::Attribute &attr) entering... "<< endl;
	
	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
			tmp_val = pool_element.get_controller()->GetExtraAttributePar(get_axis(),par_name);
		}
		SAFE_CATCH(fica_ptr->get_name(),"read_Str_R_Attr");
		
		if ((tmp_val.data_type == Controller::STRING) && (tmp_val.str_data == DEFAULT_DEFINITION_STR))
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not re-defined method to get motor features",
					  (const char *)"PoolIndBaseDev::read_Str_R_Attr");
		}
		if (tmp_val.data_type != Controller::STRING)
		{
			Tango::Except::throw_exception((const char *)"PoolIndBaseDev_BadController",
					  (const char *)"The motor controller class has not correctly re-defined method to get motor extra attributes. It returns a bad data type",
					  (const char *)"PoolIndBaseDev::read_Str_R_Attr");
		}			
	}	
		
	map<string,long>::iterator map_ite = string_extra_index.find(par_name);
	if (map_ite == string_extra_index.end())
	{
		TangoSys_OMemStream o;
		o << "Can't find data storage for extra attribute " << par_name << ends;
		Tango::Except::throw_exception((const char *)"Pool_CantFindDataStorage",o.str(),
   									   (const char *)"PoolIndBaseDev::read_Str_R_Attr()");	
	}

	long idx = map_ite->second;
	string_extra_data[idx] = tmp_val.str_data;
	string_extra_attr[idx] = const_cast<char *>(string_extra_data[idx].c_str());

	attr.set_value(&(string_extra_attr[idx]));
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::read_Str_RW_Attr
// 
// description : 	Extract real attribute values for Str_RW_Attr acquisition result.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::read_Str_RW_Attr(Tango::Attribute &attr)
{
	DEBUG_STREAM << "PoolIndBaseDev::read_Str_RW_Attr(Tango::Attribute &attr) entering... "<< endl;
	read_Str_R_Attr(attr);
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::write_Str_RW_Attr
// 
// description : 	Write Str_RW_Attr attribute values to hardware.
//
//-----------------------------------------------------------------------------
void PoolIndBaseDev::write_Str_RW_Attr(Tango::WAttribute &attr)
{
    PoolElement &pool_element = get_pool_element();
    
	DEBUG_STREAM << "PoolIndBaseDev::write_Str_RW_Attr(Tango::WAttribute &attr) entering... "<< endl;
	
	Tango::DevString received_value;	
	attr.get_write_value(received_value);

	string par_name(attr.get_name());
	Controller::CtrlData tmp_val;
	
	DEBUG_STREAM << "PoolIndBaseDev: new extra attribute " << par_name << " set to value = " << received_value << endl;
	tmp_val.data_type = Controller::STRING;
	tmp_val.str_data = received_value;

	if (!pool_element.get_simulation_mode())
	{
		Pool_ns::AutoPoolLock lo(fica_ptr->get_mon());
		try
		{
		    pool_element.get_controller()->SetExtraAttributePar(get_axis(),par_name,tmp_val);
		}
		SAFE_CATCH(fica_ptr->get_name(),"write_Str_RW_Attr");
	}
}


//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::is_ExtraAttr_allowed
// 
// description : 	Default metod for the extra attribute is_allowed method
//
//-----------------------------------------------------------------------------
bool PoolIndBaseDev::is_ExtraAttr_allowed(Tango::AttReqType type)
{
	if (get_state() == Tango::FAULT	||
		get_state() == Tango::UNKNOWN)
		return false;
	else
	{
		if ((type == Tango::WRITE_REQ) && (pool_sd == true))
			return false;
	}
	return true;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::ExtraAttrWriteType_2_Tango()
// 
// description : 	Convert the extra attribute data write type to the Tango
//					data write type definition
//
// args : in : - extra : The extra attribute data type
//-----------------------------------------------------------------------------

Tango::AttrWriteType PoolIndBaseDev::ExtraAttrWriteType_2_Tango(ExtraAttrDataWrite &extra)
{
	Tango::AttrWriteType tg_type = Tango::READ;
	switch(extra)
	{
		case READ:
		tg_type = Tango::READ;
		break;
		
		case READ_WRITE:
		tg_type = Tango::READ_WRITE;
		break;
	}
	return tg_type;
}

//+----------------------------------------------------------------------------
//
// method : 		PoolIndBaseDev::ExtraAttrDataType_2_Tango()
// 
// description : 	Convert the extra attribute data type to the Tango
//					data type definition
//
// args : in : - extra : The extra attribute data type
//-----------------------------------------------------------------------------

long PoolIndBaseDev::ExtraAttrDataType_2_Tango(ExtraAttrDataType &extra)
{
	long data_type = -1;
	switch(extra)
	{
		case BOOLEAN:
		data_type = Tango::DEV_BOOLEAN;
		break;
		
		case LONG:
		data_type = Tango::DEV_LONG;
		break;
		
		case DOUBLE:
		data_type = Tango::DEV_DOUBLE;
		break;
		
		case STRING:
		data_type = Tango::DEV_STRING;
		break;
	}
	return data_type;
}

}	//	namespace
