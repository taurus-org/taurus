package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;

public class MotorListViewer extends GenericListViewer 
{
	public Motor getSelectedMotor()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (Motor) list.getSelectedValue();
	}
	
	public List<Motor> getSelectedMotors()
	{
		ArrayList<Motor> ret = new ArrayList<Motor>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((Motor) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getDeviceElementIcon( (Motor) o );
	}

	@Override
	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeMotorListListener(getListListener());
			pool.removePseudoMotorListListener(getListListener());
			for(Object m : model.elements)
				((Motor)m).removeDevStateScalarListener(stateListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addMotorListListener(getListListener());
			pool.addPseudoMotorListListener(getListListener());
			model.update();
			
			for(Object m : model.elements)
				((Motor)m).addDevStateScalarListener(stateListener);
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
		
		ArrayList<Motor> elems = new ArrayList<Motor>(pool.getMotors());
		elems.addAll(pool.getPseudoMotors());
		return elems;
	}	
}
