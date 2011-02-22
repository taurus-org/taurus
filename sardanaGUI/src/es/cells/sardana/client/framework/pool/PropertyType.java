package es.cells.sardana.client.framework.pool;


public enum PropertyType {

	InvalidPropertyType,
	DevLong,
	DevBoolean,
	DevDouble,
	DevString,
	DevVarLongArray,
	DevVarBooleanArray,
	DevVarDoubleArray,
	DevVarStringArray;

	public boolean isSimpleType()
	{
		return this == DevLong || this == DevBoolean || this == DevDouble || this == DevString;
	}
	
	public boolean isNumeric()
	{
		return this == DevLong || this == DevDouble || this == DevVarLongArray || this == DevVarDoubleArray;
	}
	
	public String toSimpleString()
	{
		String str = this.toString().substring(3);
		
		if(str.startsWith("Var"))
			str = str.substring(3);
		
		return str;
	}
	
	public PropertyType toSimpleType()
	{
		switch(this)
		{
			case DevVarLongArray: return DevLong;
			case DevVarBooleanArray: return DevBoolean;
			case DevVarDoubleArray: return DevDouble;
			case DevVarStringArray: return DevString;
			default: return this; 
		}
	}
	
}
