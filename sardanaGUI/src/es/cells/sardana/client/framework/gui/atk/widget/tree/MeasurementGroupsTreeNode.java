package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.List;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.MeasurementGroup;

public class MeasurementGroupsTreeNode extends ElementListTreeNode 
{
	public MeasurementGroupsTreeNode(DevicePool pool)
	{
		this("Measurement Groups", pool);
	}
	
	public MeasurementGroupsTreeNode(String name, DevicePool pool) 
	{
		super(name, pool);
		updateChilds(getMeasurementGroups());
	}

	public List<MeasurementGroup> getMeasurementGroups()
	{
		return ((DevicePool)getModel()).getMeasurementGroups();
	}
	
	@Override
	public void updateChilds() 
	{
		updateChilds(getMeasurementGroups());
	}

}
