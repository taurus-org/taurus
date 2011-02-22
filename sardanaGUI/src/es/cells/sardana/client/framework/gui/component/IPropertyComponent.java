package es.cells.sardana.client.framework.gui.component;

import es.cells.sardana.client.framework.pool.PropertyInstance;

public interface IPropertyComponent 
{
	Object getValue();
	void setValue(Object o);
	
	PropertyInstance getPropertyModel();
	
}
