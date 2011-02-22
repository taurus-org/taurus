package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.ArrayList;
import java.util.List;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;

public class MotorsTreeNode extends ElementListTreeNode
{
	public MotorsTreeNode(DevicePool pool)
	{
		this("Motors", pool);
	}
	
	public MotorsTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds(getMotors());
	}

	public List<Motor> getMotors()
	{
		ArrayList<Motor> elems = new ArrayList<Motor>(((DevicePool)getModel()).getMotors());
		elems.addAll(((DevicePool)getModel()).getPseudoMotors());
		return elems;
	}

	@Override
	public void updateChilds() 
	{
		updateChilds(getMotors());
	}
	
	/*
	public void stringSpectrumChange(StringSpectrumEvent evt)
	{
		updateChilds(getModel().getMotors());
	}
	*/
}
