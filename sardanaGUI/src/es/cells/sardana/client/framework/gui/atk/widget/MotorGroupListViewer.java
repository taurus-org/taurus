package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.gui.swing.SwingResource;

public class MotorGroupListViewer extends GenericListViewer 
{
	public MotorGroup getSelectedMotorGroup()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (MotorGroup) list.getSelectedValue();
	}
	
	public List<MotorGroup> getSelectedMotorGroups()
	{
		ArrayList<MotorGroup> ret = new ArrayList<MotorGroup>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((MotorGroup) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getDeviceElementIcon( (MotorGroup) o );
	}

	@Override
	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeMotorGroupListListener(getListListener());

			for(Object mg : model.elements)
				((MotorGroup)mg).removeDevStateScalarListener(stateListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addMotorGroupListListener(getListListener());
			model.update();
			
			for(Object mg : model.elements)
				((MotorGroup)mg).addDevStateScalarListener(stateListener);
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

		return pool.getMotorGroups();
	}
}
