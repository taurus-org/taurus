package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.List;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.ExperimentChannel;

public class ExpChannelsTreeNode extends ElementListTreeNode 
{

	public ExpChannelsTreeNode(DevicePool pool) 
	{
		this("Experiment Channels", pool);
	}
	
	public ExpChannelsTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds(getExperimentChannels());
	}

	public List<ExperimentChannel> getExperimentChannels()
	{
		return ((DevicePool)getModel()).getExperimentChannels();
	}

	@Override
	public void updateChilds() 
	{
		updateChilds(getExperimentChannels());
	}
}
