package es.cells.sardana.client.framework.gui.atk.widget.tree;

import es.cells.sardana.client.framework.macroserver.Door;
import fr.esrf.tangoatk.core.Device;

public class DoorTreeNode extends GenericSardanaTreeNode {

	public DoorTreeNode(Door door) 
	{
		super(door);
	}

	public Door getDoor()
	{
		return (Door) getUserObject();
	}	
	
	public Device getModel()
	{
		return getDoor().getDevice();
	}	
	
	public String getState()
	{
		return getDoor().getState();
	}	
}
