package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.List;

import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.DevicePool;

public class ControllersTreeNode extends ElementListTreeNode
{
	public ControllersTreeNode(DevicePool pool)
	{
		this("Controllers", pool);
	}
	
	public ControllersTreeNode(String name, DevicePool pool)
	{
		super(name, pool);
		updateChilds();
	}

	public List<Controller> getControllers()
	{
		return ((DevicePool)getModel()).getControllers();
	}

	@Override
	public void updateChilds() 
	{
		List<Controller> ctrls = getControllers();
		updateChilds(ctrls);
	}
	
	/*
	public void stringSpectrumChange(StringSpectrumEvent evt)
	{
		updateChilds(getModel().getControllers());
	}
	*/
	
	public GenericSardanaTreeNode getChildByDeviceName(String deviceName)
	{
		for(Object node : children)
		{
			GenericSardanaTreeNode snode = (GenericSardanaTreeNode) node;
			Controller elem = (Controller) snode.getUserObject();
			
			if(elem.getName().equalsIgnoreCase(deviceName))
				return snode;
		}
		return null;
	}
}
