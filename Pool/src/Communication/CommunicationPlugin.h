
#ifndef _COMMUNICATIONPLUGIN_H_
#define _COMMUNICATIONPLUGIN_H_

#include <PoolPlugin.h>

namespace Communication_ns
{

typedef struct CommunicationChannelPool: public PoolElement
{
	CommunicationChannel_ns::CommunicationChannel *com_channel;
	
	virtual Tango::Device_3Impl *get_device();
	virtual void pool_elem_changed(PoolElemEventList &evt);
};

class CommunicationPlugin: public PoolPlugin
{
protected:

	protected CommunicationChannelPool &create_com_channel();

	virtual void solve_dependencies();
public:

	CommunicationPlugin(Pool *);
	~CommunicationPlugin();

	virtual void post_init();
	virtual void create_proxies();
	
	virtual PoolElement &create_elem(ElemCreateParams &);
	
	virtual ControllerPool &create_ctrl(CtrlCreateParams &);

	virtual void delete_ctrl(Tango::DevString );
	virtual void delete_elem(Tango::DevString );
};

} // namespace

#endif
