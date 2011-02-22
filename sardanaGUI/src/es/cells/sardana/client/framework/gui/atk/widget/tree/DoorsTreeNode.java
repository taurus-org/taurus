package es.cells.sardana.client.framework.gui.atk.widget.tree;



import java.util.List;

import es.cells.sardana.client.framework.macroserver.Door;
import es.cells.sardana.client.framework.macroserver.MacroServer;

public class DoorsTreeNode extends ElementListTreeNode
{	
	
	public DoorsTreeNode(String name, MacroServer macroServer)
	{
		super(name, macroServer);
		//updateChilds();
	}
	
	public DoorsTreeNode(MacroServer macroServer)
	{
		this("Doors",macroServer);
	}
	
	
	
	public List<Door> getDoors()
	{
		return ((MacroServer)getModel()).getDoors();		
	}
	
	public void updateChilds()
	{
		List<Door> doors = getDoors();
		updateChilds(doors);
	}
	
	public GenericSardanaTreeNode getChildByDeviceName(String deviceName)
	{
		for(Object node : children)
		{
			GenericSardanaTreeNode snode = (GenericSardanaTreeNode) node;
			Door elem = (Door) snode.getUserObject();
		
			if(elem.getName().equalsIgnoreCase(deviceName))
				return snode;
		}
		return null;
	}

}
