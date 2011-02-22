package es.cells.sardana.client.gui.swing;

import es.cells.sardana.client.igui.ContainerType;
import es.cells.sardana.client.igui.IGUIContainer;
import es.cells.sardana.client.igui.IGUIPlugin;

public class SWINGManager implements IGUIPlugin 
{
	protected TreePanel treePanel = null;
	protected EditorPanel editorPanel = null;
	
	protected static SWINGManager _instance = null;
	
	protected SWINGManager()
	{
		init();
	}
	
	private void init() 
	{
		treePanel = new TreePanel();
		editorPanel = new EditorPanel();
	}

	public static SWINGManager getInstance()
	{
		if(_instance == null)
			_instance = new SWINGManager();
		return _instance;
	}
	
	public IGUIContainer getGUIContainer(String hint)
	{
		if(hint.equals(ContainerType.LEFT_VIEW))
			return treePanel;
		else if(hint.equals(ContainerType.RIGHT_VIEW))
			return editorPanel;
		else
			return null;
	}
}
