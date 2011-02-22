package es.cells.sardana.client.framework.pool;


public class IORegister extends SardanaDevice 
{

	protected IORegisterClass ioClass;

	public IORegister(Machine machine, String name)
	{
		super(machine, name);
	}
	
	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof IORegister)) 
			return false;
		return super.equals(obj); 
	}

	public void setIORegisterClass(IORegisterClass ioClass)
	{
		this.ioClass = ioClass;
	}
	
	public IORegisterClass getIORegisterClass()
	{
		return ioClass;
	}


}
