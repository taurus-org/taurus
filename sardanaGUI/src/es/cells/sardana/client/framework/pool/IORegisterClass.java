package es.cells.sardana.client.framework.pool;

import java.util.Vector;

public class IORegisterClass extends ControllerClass 
{
    protected int nbPredefinedValues;
	protected Vector<Long> predefinedValues;
	protected Vector<String> predefinedValuesDesc;
	
	public IORegisterClass(String typee,String klass,String fullPath)
	{
		super(typee, klass, fullPath);
	}
	
	public Vector<Long> getPredefinedValues() 
	{
		return predefinedValues;
	}

	public Vector<String> getPredefinedValuesDesc() 
	{
		return predefinedValuesDesc;
	}

	public void setPredefinedValues(Vector<Long> predefinedValues) 
	{
		this.predefinedValues = predefinedValues;
	}

	public void setPredefinedValuesDesc(Vector<String> predefinedValuesDesc) 
	{
		this.predefinedValuesDesc = predefinedValuesDesc;
	}
	
    public void setNbPredefinedValues(int nbPredefinedValues)
	{
		this.nbPredefinedValues = nbPredefinedValues;
	}
  
	public Long getPredefinedValue(int index)
	{
		return predefinedValues.get(index);
	}
	
	public String getPredefinedValueDesc(int index)
	{
		return predefinedValuesDesc.get(index);
	}
	
    public int getNbPredefinedValues()
	{
		return nbPredefinedValues;
	}
	
	public boolean match(Object obj) 
	{
		if(!(obj instanceof IORegisterClass))
			return false;

		if(!super.match(obj))
			return false;
		
		IORegisterClass pcc = (IORegisterClass) obj; 
		
		return predefinedValues.equals(pcc.predefinedValues) &&
		   predefinedValuesDesc.equals(pcc.predefinedValuesDesc);
	}	
}
