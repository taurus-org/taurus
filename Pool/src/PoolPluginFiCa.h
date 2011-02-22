#ifndef _POOLPLUGINFICA_H_
#define _POOLPLUGINFICA_H_

#include <ExternalFiCa.h>

namespace Pool_ns
{

class PoolPluginFiCa: public ExternalFiCa
{
public:
	PoolPluginFiCa(string &,string &,string &,PoolClass *,Pool *);
	virtual ~PoolPluginFiCa();

};

} // namespace

#endif