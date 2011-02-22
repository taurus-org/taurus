package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.ExperimentChannel;

public class ExperimentChannelListViewer extends GenericListViewer 
{
	public ExperimentChannel getSelectedExperimentChannel()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (ExperimentChannel) list.getSelectedValue();
	}
	
	public List<ExperimentChannel> getSelectedExperimentChannels()
	{
		ArrayList<ExperimentChannel> ret = new ArrayList<ExperimentChannel>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((ExperimentChannel) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getDeviceElementIcon( (ExperimentChannel) o );
	}

	@Override
	public void setModel(DevicePool p) 
	{
		if(pool != null)
		{
			pool.removeExperimentChannelListListener(getListListener());
			for(Object channel : model.elements)
			{
				((ExperimentChannel)channel).removeDevStateScalarListener(stateListener);
			}
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addExperimentChannelListListener(getListListener());
			model.update();
			for(Object channel : model.elements)
			{
				((ExperimentChannel)channel).addDevStateScalarListener(stateListener);
			}
		}
		else
		{
			model.update();
		}
	}

	@Override
	protected List<?> getPoolElements() 
	{
		if(pool == null)
			return null;
		
		List<ExperimentChannel> ret = new ArrayList<ExperimentChannel>(pool.getExperimentChannels());
		ret.addAll(pool.getPseudoCounters());
		return ret;
	}
}
