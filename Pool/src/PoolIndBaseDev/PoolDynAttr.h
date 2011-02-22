//=============================================================================
//
// file :        PoolDynAttr.h
//
// description : Include for the Pool device extra attributes classes.
//
// project :	Sardana device pool
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
// Revision 1.1  2007/01/16 14:22:25  etaurel
// - Initial revision
//
//
// copyleft :     CELLS/ALBA
//				  Edifici Ciències Nord. Mòdul C-3 central.
//  			  Campus Universitari de Bellaterra. Universitat Autònoma de Barcelona
//  			  08193 Bellaterra, Barcelona
//  			  Spain
//
//==============================================================================

#ifndef _POOLDYNATTR_H
#define _POOLDYNATTR_H

#include <tango.h>

namespace Pool_ns
{

class Boo_R_Attrib: public Tango::Attr
{
public:
	Boo_R_Attrib(string &name):Attr(name.c_str(), Tango::DEV_BOOLEAN, Tango::READ) {};
	~Boo_R_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Boo_R_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Boo_RW_Attrib: public Tango::Attr
{
public:
	Boo_RW_Attrib(string &name):Attr(name.c_str(), Tango::DEV_BOOLEAN, Tango::READ_WRITE) {};
	~Boo_RW_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Boo_RW_Attr(att);}
	virtual void write(Tango::DeviceImpl *dev,Tango::WAttribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->write_Boo_RW_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Dou_R_Attrib: public Tango::Attr
{
public:
	Dou_R_Attrib(string &name):Attr(name.c_str(), Tango::DEV_DOUBLE, Tango::READ) {};
	~Dou_R_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Dou_R_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Dou_RW_Attrib: public Tango::Attr
{
public:
	Dou_RW_Attrib(string &name):Attr(name.c_str(), Tango::DEV_DOUBLE, Tango::READ_WRITE) {};
	~Dou_RW_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Dou_RW_Attr(att);}
	virtual void write(Tango::DeviceImpl *dev,Tango::WAttribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->write_Dou_RW_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Lo_R_Attrib: public Tango::Attr
{
public:
	Lo_R_Attrib(string &name):Attr(name.c_str(), Tango::DEV_LONG, Tango::READ) {};
	~Lo_R_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Lo_R_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Lo_RW_Attrib: public Tango::Attr
{
public:
	Lo_RW_Attrib(string &name):Attr(name.c_str(), Tango::DEV_LONG, Tango::READ_WRITE) {};
	~Lo_RW_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Lo_RW_Attr(att);}
	virtual void write(Tango::DeviceImpl *dev,Tango::WAttribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->write_Lo_RW_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Str_R_Attrib: public Tango::Attr
{
public:
	Str_R_Attrib(string &name):Attr(name.c_str(), Tango::DEV_STRING, Tango::READ) {};
	~Str_R_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Str_R_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

class Str_RW_Attrib: public Tango::Attr
{
public:
	Str_RW_Attrib(string &name):Attr(name.c_str(), Tango::DEV_STRING, Tango::READ_WRITE) {};
	~Str_RW_Attrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->read_Str_RW_Attr(att);}
	virtual void write(Tango::DeviceImpl *dev,Tango::WAttribute &att)
	{(static_cast<PoolIndBaseDev *>(dev))->write_Str_RW_Attr(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<PoolIndBaseDev *>(dev))->is_ExtraAttr_allowed(ty);}
};

}

#endif /* _POOLDYNATTR_H */
