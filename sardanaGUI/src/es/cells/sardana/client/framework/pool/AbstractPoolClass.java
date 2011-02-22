package es.cells.sardana.client.framework.pool;

import java.util.HashMap;
import java.util.Vector;
import java.util.regex.Matcher;

import fr.esrf.TangoApi.DbDatum;

public abstract class AbstractPoolClass
{
	/** Start of: Basic class data */
	
	/** the absolute path with the filename. Ex.: /home/homer/lib/HomerLib.py */
	protected String fullPathName;
	
	/** the filename with extension. */
	protected String fileName;
	
	/** the fileName without extension. */
	protected String moduleName;
	
	/** the filename extension. Examples: 'so', 'py'*/
	protected String fileExtension;
	
	/** the class name */
	protected String className;

	/** the pool device to which this class belongs */
	protected DevicePool pool;
	
	/** End of: Basic class data */

	
	/** class description */
	protected String description;

	/**
	 * A map of properties. 
	 * Key = property name, Value = property information 
	 */
	protected HashMap<String,PropertyInfo> propertiesInfo;
	
	/** 
	 * A map of class level properties. 
	 * Key = property name, Value = property value at the class level in the DB
	 */
	protected HashMap<String,Object> dbClassProperties;

	public AbstractPoolClass(String typee, String klass, String fullPath)
	{
		buildClassData(typee, klass, fullPath);
	}
	
	protected void buildClassData(String typee, String klass, String fullPath)
	{
//		Matcher m = DevicePoolUtils.LIST_PATTERN.matcher(classData);
//		
//		if(m.matches() && m.groupCount() >= 3) 
//		{
			setClassName(klass);
			setFullPathName(fullPath);
			
			String[] pathElems = fullPathName.split("\\/");
			
			setFileName(pathElems[pathElems.length-1]);
			
			String[] fileElems = fileName.split("\\.");
			
			setModuleName(fileElems[0]);
			setFileExtension(fileElems[1]);
//		}		
	}
	
	public String getClassNameWithModule()
	{
		return moduleName + "." + className;
	}
	
	public String getClassName()
	{
		return className;
	}

	public void setClassName(String className)
	{
		this.className = className;
	}

	public String getDescription()
	{
		return description;
	}

	public void setDescription(String description)
	{
		this.description = description;
	}

	public String getFileExtension()
	{
		return fileExtension;
	}

	public void setFileExtension(String fileExtension)
	{
		this.fileExtension = fileExtension;
	}

	public String getFileName()
	{
		return fileName;
	}

	public void setFileName(String fileName)
	{
		this.fileName = fileName;
	}

	public String getFullClassName()
	{
		return getFullFileName() + "/" + className;
	}
	
	public String getFullFileName()
	{
		return fullPathName + "/" + fileName;
	}
	
	public String getFullPathName()
	{
		return fullPathName;
	}

	public void setFullPathName(String fullPathName)
	{
		this.fullPathName = fullPathName;
	}

	public String getModuleName()
	{
		return moduleName;
	}

	public DevicePool getPool() 
	{
		return pool;
	}

	public void setPool(DevicePool pool) 
	{
		this.pool = pool;
	}

	public void setModuleName(String moduleName)
	{
		this.moduleName = moduleName;
	}

	public HashMap<String,PropertyInfo> getPropertiesInfo()
	{
		if(propertiesInfo == null) propertiesInfo = new HashMap<String,PropertyInfo>();
		return propertiesInfo; 
	}
	
	public PropertyInfo getPropertyInfo(String propName)
	{
		return propertiesInfo.get(propName); 
	}
	
	public void addPropertyInfo(PropertyInfo info)
	{
		if(propertiesInfo == null) propertiesInfo = new HashMap<String,PropertyInfo>();
		propertiesInfo.put(info.getName(), info);
	}
	
	public HashMap<String,Object> getDbClassProperties()
	{
		return dbClassProperties;
	}
	
	public Object getDbClassPropertyValue(String propName)
	{
		return dbClassProperties.get(propName);
	}
	
	public void addDbClassProperty(String propName, Object value)
	{
		if(value == null)
			return;
		
		if(dbClassProperties == null) dbClassProperties = new HashMap<String, Object>();
		dbClassProperties.put(propName, value);
	}
	
	public void addDbClassProperties(DbDatum[] properties)
	{
		if(properties == null)
			return;
		
		if(dbClassProperties == null) dbClassProperties = new HashMap<String, Object>();
		
		for(int i = 0; i < properties.length; i++)
		{
			String propName = properties[i].name.replace("\\", "");
			PropertyInfo info = getPropertyInfo(propName);
			
			if(info == null)
				continue;
			
			if(properties[i].is_empty())
				continue;
			
			if(info.type == PropertyType.DevBoolean)
				dbClassProperties.put(propName, properties[i].extractBoolean());
			else if(info.type == PropertyType.DevLong)
				dbClassProperties.put(propName, properties[i].extractLong());
			else if(info.type == PropertyType.DevDouble)
				dbClassProperties.put(propName, properties[i].extractDouble());
			else if(info.type == PropertyType.DevString)
				dbClassProperties.put(propName, properties[i].extractString());
			else if(info.type == PropertyType.DevVarBooleanArray)
			{
				String[] array = properties[i].extractStringArray();
				Vector<Boolean> vec = new Vector<Boolean>(array.length);
				for(String b: array) vec.add(Boolean.parseBoolean(b));
				dbClassProperties.put(propName, vec);
			}
			else if(info.type == PropertyType.DevVarLongArray)
			{
				int[] array = properties[i].extractLongArray();
				Vector<Integer> vec = new Vector<Integer>(array.length);
				for(int v: array) vec.add(v);
				dbClassProperties.put(propName, vec);
			}
			else if(info.type == PropertyType.DevVarDoubleArray)
			{
				double[] array = properties[i].extractDoubleArray();
				Vector<Double> vec = new Vector<Double>(array.length);
				for(double v: array) vec.add(v);
				dbClassProperties.put(propName, vec);
			}
			else if(info.type == PropertyType.DevVarStringArray)
			{
				String[] array = properties[i].extractStringArray();
				Vector<String> vec = new Vector<String>(array.length);
				for(String v: array) vec.add(v);
				dbClassProperties.put(propName, vec);
			}
		}
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(!(obj instanceof AbstractPoolClass))
			return false;
		
		AbstractPoolClass apc = (AbstractPoolClass) obj; 
		
		return  fullPathName.equals(apc.getFullPathName()) &&
				className.equals(apc.getClassName());
	}
	
	public boolean match(Object obj) 
	{
		if(!equals(obj))
			return false;
		
		AbstractPoolClass apc = (AbstractPoolClass) obj; 
		
		return description.equals(apc.description) &&
			propertiesInfo.equals(apc.propertiesInfo) &&
			dbClassProperties.equals(apc.dbClassProperties);
	}
	
	@Override
	public String toString() 
	{
		return className;
	}
	
}
