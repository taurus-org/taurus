package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class Controller 
{
	protected String name;
	protected ControllerClass ctrlClass;
	protected List<SardanaDevice> elements;
	protected CtrlState state;
	protected DevicePool pool;
	
	protected PropertyContainer propertyData;
	
	protected List<ControllerStateListener> stateListeners;
	
	public Controller()
	{
		this("");
	}
	
	public Controller(String name)
	{
		this.name = name;
		this.ctrlClass = null;
		state = CtrlState.InvalidCtrlState;
		elements = new ArrayList<SardanaDevice>();
		stateListeners = new ArrayList<ControllerStateListener>();
		propertyData = new PropertyContainer();
	}
	
	public CtrlState getState()
	{
		return state;
	}

	public void setState(CtrlState state)
	{
		this.state = state;
	}
	
	public String getName() 
	{
		return name;
	}
	
	public void setName(String name)
	{
		this.name = name;
	}
	
	public DevicePool getPool() 
	{
		return pool;
	}

	public void setPool(DevicePool pool) 
	{
		this.pool = pool;
	}
	
	@Override
	public String toString() {
		return name;
	}

	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof Controller ) )
			return false;
		
		return name.equals(((Controller)obj).getName());
	}

	public void addElement(SardanaDevice element) 
	{
		if(elements.indexOf(element) < 0)
			elements.add(element);
	}
	
	public List<SardanaDevice> getElements() 
	{
		return elements;
	}

	public void setElements(List<SardanaDevice> elements) 
	{
		this.elements = elements;
	}

	public ControllerClass getCtrlClass()
	{
		return ctrlClass;
	}

	public void setCtrlClass(ControllerClass ctrlClass)
	{
		this.ctrlClass = ctrlClass;
	}

	public ControllerType getType()
	{
		if(ctrlClass == null) return ControllerType.InvalidControllerType;
		
		return ctrlClass.getType();
	}

	public String getFullPathName()
	{
		if(ctrlClass == null) return null;
		
		return ctrlClass.getFullPathName();
	}
	
	public String getFullClassName()
	{
		if(ctrlClass == null) return null;
		
		return ctrlClass.getFullClassName();
	}
	
	public String getFileName()
	{
		if(ctrlClass == null) return null;
		
		return ctrlClass.getFileName();
	}
	
	public String getClassName()
	{
		if(ctrlClass == null) return null;
		
		return ctrlClass.getClassName();
	}
	
	public ControllerLanguage getLanguage()
	{
		if(ctrlClass == null) return ControllerLanguage.InvalidCtrlLanguage;
		
		return ctrlClass.getLanguage();	
	}
	
	public HashMap<String,PropertyInstance> getPropertyInstances()
	{
		return propertyData.getPropertyData(); 
	}
	
	public PropertyInstance getPropertyInstance(String propName)
	{
		return propertyData.getPropertyInstance(propName); 
	}
	
	public void addPropertyInstance(PropertyInstance info)
	{
		propertyData.addPropertyInstance(info);
	}
	
	public void addControllerStateListener(ControllerStateListener listener)
	{
		stateListeners.add(listener);
	}
	
	public void removeControllerStateListener(ControllerStateListener listener)
	{
		stateListeners.remove(listener);
	}	
}
