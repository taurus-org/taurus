
#include <CommunicationPlugin.h>

namespace Communication_ns
{

CommunicationPlugin::CommunicationPlugin(Pool *pool):
PoolPlugin(pool),name("Pool Communication Plugin"),extension("Communication")
{
	
}

CommunicationPlugin::~CommunicationPlugin()
{

}

void post_init()
{
	PoolPlugin::post_init();
}

void create_proxies()
{
	PoolPlugin::create_proxies();
}

virtual PoolElement &create_elem(ElemCreateParams &)
{

}

virtual ControllerPool &create_ctrl(CtrlCreateParams &)
{

}

virtual void delete_ctrl(Tango::DevString name)
{

}

virtual void delete_elem(Tango::DevString name)
{

}

} // namespace
