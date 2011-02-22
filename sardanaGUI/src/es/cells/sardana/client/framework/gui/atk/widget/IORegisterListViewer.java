package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.IORegister;
import es.cells.sardana.client.framework.pool.DevicePool;

public class IORegisterListViewer extends GenericListViewer 
{
	public IORegister getSelectedIORegister()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (IORegister) list.getSelectedValue();
	}
	
	public List<IORegister> getSelectedIORegisters()
	{
		ArrayList<IORegister> ret = new ArrayList<IORegister>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((IORegister) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getDeviceElementIcon( (IORegister) o );
	}

	@Override
	public void setModel(DevicePool p) 
	{
		if(pool != null)
		{
			pool.removeIORegisterListListener(getListListener());
			for(Object ioregister : model.elements)
			{
				((IORegister)ioregister).removeDevStateScalarListener(stateListener);
			}
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addIORegisterListListener(getListListener());
			model.update();
			for(Object ioregister : model.elements)
			{
				((IORegister)ioregister).addDevStateScalarListener(stateListener);
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
		
		return pool.getIORegisters();
	}
}
