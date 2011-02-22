package es.cells.sardana.client.framework.gui.atk.widget;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.MeasurementGroup;

public class MeasurementGroupListViewer extends GenericListViewer 
{
	public static final String CMD_ADD_CHANNEL = "Add channel";
	public static final String CMD_REMOVE_CHANNEL = "Remove channel";
	public static final String CMD_ADD_MG = "Add new measurement group";
	public static final String CMD_DELETE_MG = "Delete measurement group(s)";
	public static final String CMD_CLONE_MG = "Clone measurement group";
	
	@Override
	protected void initComponents() 
	{
		super.initComponents();
		
	}

	public MeasurementGroup getSelectedMeasurementGroup()
	{
		int row =  list.getSelectedIndex();
		
		if(row < 0)
			return null;
		
		return (MeasurementGroup) list.getSelectedValue();
	}
	
	public List<MeasurementGroup> getSelectedMeasurementGroups()
	{
		ArrayList<MeasurementGroup> ret = new ArrayList<MeasurementGroup>();
		int[] rows = list.getSelectedIndices();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((MeasurementGroup) model.getElementAt(row));
		}
		
		return ret;
	}
	
	@Override
	protected String getElementIconName(Object o) 
	{
		return IImageResource.getDeviceElementIcon( (MeasurementGroup) o );
	}

	@Override
	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeMeasurementGroupListListener(getListListener());

			for(Object mg : model.elements)
				((MeasurementGroup)mg).removeDevStateScalarListener(stateListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addMeasurementGroupListListener(getListListener());
			model.update();
			
			for(Object mg : model.elements)
				((MeasurementGroup)mg).addDevStateScalarListener(stateListener);
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
		
		return pool.getMeasurementGroups();
	}
}
