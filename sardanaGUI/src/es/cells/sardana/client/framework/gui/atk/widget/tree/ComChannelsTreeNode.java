package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.List;

import es.cells.sardana.client.framework.pool.CommunicationChannel;
import es.cells.sardana.client.framework.pool.DevicePool;

public class ComChannelsTreeNode extends ElementListTreeNode 
{

	public ComChannelsTreeNode(DevicePool pool) 
	{
		this("Communication Channels", pool);
	}
	
	public ComChannelsTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds(getCommunicationChannels());
	}

	public List<CommunicationChannel> getCommunicationChannels()
	{
		return ((DevicePool)getModel()).getCommunicationChannels();
	}

	@Override
	public void updateChilds() 
	{
		updateChilds(getCommunicationChannels());
	}
}
