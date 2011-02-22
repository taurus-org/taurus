package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.DevicePool;

public class ControllerListViewer extends GenericListViewer 
{
	public Controller getSelectedController()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (Controller) list.getSelectedValue();
	}
	
	public List<Controller> getSelectedControllers()
	{
		ArrayList<Controller> ret = new ArrayList<Controller>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((Controller) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return ((Controller)o).getClassName();
	}

	@Override
	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeControllerListListener(getListListener());
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addControllerListListener(getListListener());
		}
		model.update();
	}

	@Override
	protected List<?> getPoolElements() 
	{
		return pool != null ? pool.getControllers() : null;
	}
}
