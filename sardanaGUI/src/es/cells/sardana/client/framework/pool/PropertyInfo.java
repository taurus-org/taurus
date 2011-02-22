package es.cells.sardana.client.framework.pool;


public class PropertyInfo 
{
	protected String name;
	protected PropertyType type;
	protected String description;
	protected Object defaultValue;
	
	public PropertyInfo()
	{
	}
	
	public PropertyInfo(String name)
	{
		this.name = name;
	}
	
	public Object getDefaultValue() 
	{
		return defaultValue;
	}
	
	public void setDefaultValue(String defaultValue) 
	{
		this.defaultValue = DevicePoolUtils.toPropertyValue(type,defaultValue);
	}	
	
	public void setDefaultValue(Object defaultValue) 
	{
		this.defaultValue = defaultValue;
	}
	public String getDescription() 
	{
		return description;
	}
	
	public void setDescription(String description) 
	{
		this.description = description;
	}
	
	public String getName() 
	{
		return name;
	}
	
	public void setName(String name) 
	{
		this.name = name;
	}
	
	public PropertyType getType() 
	{
		return type;
	}
	
	public void setType(PropertyType type)
	{	
		this.type = type;
	}
	
	public void setType(String type) 
	{
		int dotpos = type.indexOf('.');

		try
		{
			if(dotpos > 0)
				this.type = PropertyType.valueOf(type.substring(dotpos+1));
			else
				this.type = PropertyType.valueOf(type);
		}
		catch(IllegalArgumentException e)
		{
			this.type = PropertyType.InvalidPropertyType;
		}
	}
	public boolean hasDefaultValue()
	{
		return defaultValue != null;
	}

	@Override
	public String toString() 
	{
		return name;
	}
	
	
}
