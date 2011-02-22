package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.CommunicationChannel;
import es.cells.sardana.client.framework.pool.DevicePool;

public class CommunicationChannelListViewer extends GenericListViewer 
{
	public CommunicationChannel getSelectedCommunicationChannel()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (CommunicationChannel) list.getSelectedValue();
	}
	
	public List<CommunicationChannel> getSelectedCommunicationChannels()
	{
		ArrayList<CommunicationChannel> ret = new ArrayList<CommunicationChannel>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((CommunicationChannel) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getDeviceElementIcon( (CommunicationChannel) o );
	}

	@Override
	public void setModel(DevicePool p) 
	{
		if(pool != null)
		{
			pool.removeCommunicationChannelListListener(getListListener());
			for(Object channel : model.elements)
			{
				((CommunicationChannel)channel).removeDevStateScalarListener(stateListener);
			}
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addCommunicationChannelListListener(getListListener());
			model.update();
			for(Object channel : model.elements)
			{
				((CommunicationChannel)channel).addDevStateScalarListener(stateListener);
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
		
		return pool.getCommunicationChannels();
	}
}
