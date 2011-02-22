package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.ControllerClass;
import es.cells.sardana.client.framework.pool.DevicePool;

public class ControllerClassListViewer extends GenericListViewer {

	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getNonDeviceElementIcon( (ControllerClass) o );
	}

	@Override
	protected List<?> getPoolElements() 
	{
		return pool.getControllerClassesAsList();
	}

	@Override
	public void setModel(DevicePool p) 
	{
		if(pool != null)
		{
			pool.removeControllerClassListListener(getListListener());
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addControllerClassListListener(getListListener());
			model.update();
		}	
	}
}
