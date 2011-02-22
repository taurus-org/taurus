package es.cells.sardana.client.igui;

import java.awt.Component;
import java.awt.Container;

public interface IGUIContainer 
{
	void addGUIComponent(Component component);
	Container getContainer();
}
