package es.cells.sardana.client.framework.pool;

import java.util.HashMap;

public class PropertyContainer
{
	/**
	 * A map of properties. 
	 * Key = property name, Value = property instance information 
	 */
	protected HashMap<String,PropertyInstance> propertyData;
	
	public PropertyContainer()
	{
	}
	
	public HashMap<String,PropertyInstance> getPropertyData()
	{
		if(propertyData == null) propertyData = new HashMap<String,PropertyInstance>();
		return propertyData; 
	}
	
	public PropertyInstance getPropertyInstance(String propName)
	{
		return propertyData.get(propName); 
	}
	
	public void addPropertyInstance(PropertyInstance info)
	{
		if(propertyData == null) propertyData = new HashMap<String,PropertyInstance>();
		propertyData.put(info.getPropertyInfo().getName(), info);
	}
}
