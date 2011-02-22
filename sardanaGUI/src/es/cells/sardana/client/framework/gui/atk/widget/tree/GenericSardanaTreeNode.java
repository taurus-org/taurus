package es.cells.sardana.client.framework.gui.atk.widget.tree;

import java.util.Vector;

import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.MutableTreeNode;

public class GenericSardanaTreeNode extends DefaultMutableTreeNode 
{
	public GenericSardanaTreeNode(Object userObject) 
	{
		super(userObject);
	}
	
    synchronized public void insert(MutableTreeNode newChild, int childIndex) 
    {
    	if (!allowsChildren) {
    		throw new IllegalStateException("node does not allow children");
    	} else if (newChild == null) {
    		throw new IllegalArgumentException("new child is null");
    	} else if (isNodeAncestor(newChild)) {
    		throw new IllegalArgumentException("new child is an ancestor");
    	}

    	MutableTreeNode oldParent = (MutableTreeNode)newChild.getParent();

    	if (oldParent != null) {
    		oldParent.remove(newChild);
    	}
    	newChild.setParent(this);
    	if (children == null) {
    		children = new Vector(10,4);
    	}
    	children.insertElementAt(newChild, childIndex);
    }
}
