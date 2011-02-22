package es.cells.sardana.client.framework.gui.atk.widget.tree;

import es.cells.sardana.client.framework.pool.DevicePool;

public class PseudoMotorsTreeNode extends ElementListTreeNode
{

	public PseudoMotorsTreeNode(DevicePool pool)
	{
		this("Pseudo Motors", pool);
	}
	
	public PseudoMotorsTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds(pool.getPseudoMotors());
	}

	@Override
	public void updateChilds() 
	{
		updateChilds(((DevicePool)getModel()).getPseudoMotors());
	}

	/*
	public void stringSpectrumChange(StringSpectrumEvent e)
	{
		updateChilds(getModel().getPseudoMotors());
	}
	*/

}
