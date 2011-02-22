package es.cells.sardana.client.framework.pool;

public class PropertyInstance
{
	protected PropertyInfo propertyInfo;
    protected Object dbValue;
	protected Object value;
	
	protected boolean overrideDefault = false; 
	
	public PropertyInstance(PropertyInfo info) 
	{
		this(info,null,null);
	}

	public PropertyInstance(PropertyInfo info, Object dbValue, Object value) 
	{
		if(info==null)
			throw new IllegalArgumentException("The argument 'info' cannot be null");
		
		this.propertyInfo = info;
		setValue(value);
		setDbValue(value);
	}
	
	public PropertyInfo getPropertyInfo()
	{
		return propertyInfo;
	}

	public Object getValue()
	{
		return value;
	}

	public long getLongValue() throws Exception
	{
		if(getType() != PropertyType.DevLong)
		{
			throw new Exception("Trying to get long value from a " + getType() + " property");
		}
		return (Long) getValue();
	}

	public void setLongValue(long v) throws Exception
	{
		if(getType() != PropertyType.DevLong)
		{
			throw new Exception("Trying to set long value to a " + getType() + " property");
		}
		setValue(v);
	}
	
	public double getDoubleValue() throws Exception
	{
		if(getType() != PropertyType.DevDouble)
		{
			throw new Exception("Trying to get double value from a " + getType() + " property");
		}
		return (Double) getValue();
	}

	public void setDoubleValue(double v) throws Exception
	{
		if(getType() != PropertyType.DevLong)
		{
			throw new Exception("Trying to set double value to a " + getType() + " property");
		}
		setValue(v);
	}	
	
	public boolean getBooleanValue() throws Exception
	{
		if(getType() != PropertyType.DevBoolean)
		{
			throw new Exception("Trying to get boolean value from a " + getType() + " property");
		}
		return (Boolean) getValue();
	}

	public void setBooleanValue(boolean v) throws Exception
	{
		if(getType() != PropertyType.DevBoolean)
		{
			throw new Exception("Trying to set boolean value to a " + getType() + " property");
		}
		setValue(v);
	}
	
	public String getStringValue() throws Exception
	{
		if(getType() != PropertyType.DevString)
		{
			throw new Exception("Trying to get String value from a " + getType() + " property");
		}
		return (String) getValue();
	}

	public void setStringValue(String v) throws Exception
	{
		if(getType() != PropertyType.DevString)
		{
			throw new Exception("Trying to set String value to a " + getType() + " property");
		}
		setValue(v);
	}	
	
	public Object getDbValue()
	{
		return this.dbValue;
	}

	public void setValue(Object value)
	{
		this.value = value;
	}

	public void setValue(String value) 
	{
		this.value = DevicePoolUtils.toPropertyValue(propertyInfo.getType(),value);
	}	

	public void setDbValue(Object value)
	{
		this.dbValue = value;
	}

	public void setDbValue(String value) 
	{
		this.dbValue = DevicePoolUtils.toPropertyValue(propertyInfo.getType(),value);
	}
		
	// Utility methods that are forwarded to the PropertyInfo member
	
	public boolean hasDefaultValue()
	{
		return propertyInfo.hasDefaultValue();
	}
	
	public Object getDefaultValue() 
	{
		return propertyInfo.getDefaultValue();
	}
	
	public String getDescription() 
	{
		return propertyInfo.getDescription();
	}

	public String getName() 
	{
		return propertyInfo.getName();
	}
	
	public PropertyType getType() 
	{
		return propertyInfo.getType();
	}

	@Override
	public String toString()
	{
		return propertyInfo.toString();
	}

	public boolean isOverrideDefault() 
	{
		return overrideDefault;
	}

	public void setOverrideDefault(boolean overrideDefault)
	{
		this.overrideDefault = overrideDefault;
	}	
	
	
	
}
