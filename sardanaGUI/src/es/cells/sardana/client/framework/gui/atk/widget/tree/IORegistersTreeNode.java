package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.List;

import es.cells.sardana.client.framework.pool.IORegister;
import es.cells.sardana.client.framework.pool.DevicePool;

public class IORegistersTreeNode extends ElementListTreeNode 
{

	public IORegistersTreeNode(DevicePool pool) 
	{
		this("IORegisters", pool);
	}
	
	public IORegistersTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds(getIORegisters());
	}

	public List<IORegister> getIORegisters()
	{
		return ((DevicePool)getModel()).getIORegisters();
	}

	@Override
	public void updateChilds() 
	{
		updateChilds(getIORegisters());
	}
}
