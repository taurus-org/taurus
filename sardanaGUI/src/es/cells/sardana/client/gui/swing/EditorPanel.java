package es.cells.sardana.client.gui.swing;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Container;

import javax.swing.JPanel;

import es.cells.sardana.client.igui.IGUIContainer;


@SuppressWarnings("serial")
public class EditorPanel extends JPanel implements IGUIContainer {
	
	public EditorPanel()
	{
		super();
		setLayout( new BorderLayout(0, 0) );
	}
	
	// IGUIContainer implementation
	
	/**
	 * 
	 */
	public void addGUIComponent(Component component) 
	{
		this.add(component, BorderLayout.CENTER);
	}

	public Container getContainer()
	{
		return this;
	}
}
