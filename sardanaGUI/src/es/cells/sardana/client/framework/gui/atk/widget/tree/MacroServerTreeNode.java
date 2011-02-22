package es.cells.sardana.client.framework.gui.atk.widget.tree;

import es.cells.sardana.client.framework.macroserver.MacroServer;
import fr.esrf.tangoatk.core.Device;

public class MacroServerTreeNode extends GenericSardanaTreeNode {
	
	protected DoorsTreeNode doorsNode;

	public MacroServerTreeNode(MacroServer ms) 
	{
		super(ms);
	}

	public MacroServer getMacroServer()
	{
		return (MacroServer) getUserObject();
	}
	
	public Object getUserObject()
	{
		return super.getUserObject();
	}
	
	public Device getModel()
	{
		return getMacroServer().getDevice();
	}	
	
	public String getState()
	{
		return getMacroServer().getState();
	}	
	
	public DoorsTreeNode getDoorsNode()
	{
		return doorsNode;
	}
	
	synchronized public void setDoorsNode(DoorsTreeNode treeNode)
	{
		if(doorsNode != null && isNodeChild(doorsNode))
			remove(doorsNode);
		
		doorsNode = treeNode;
		
		add(doorsNode);
	}
	
	synchronized public void removeAllChildren()
	{
		doorsNode = null;
		
		super.removeAllChildren();
		
	}
}
