package es.cells.sardana.client.framework.gui.atk.widget.tree;

import es.cells.sardana.client.framework.pool.DevicePool;

public class MotorGroupsTreeNode extends ElementListTreeNode
{
	public MotorGroupsTreeNode(DevicePool pool)
	{
		this("Motor Groups", pool);
	}
	
	public MotorGroupsTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds(pool.getMotorGroups());
	}

	@Override
	public void updateChilds() 
	{
		updateChilds(((DevicePool)getModel()).getMotorGroups());
	}
	
	/*
	public void stringSpectrumChange(StringSpectrumEvent evt)
	{
		updateChilds(getModel().getMotorGroups());
	}
	*/
}
