package es.cells.sardana.client.framework.pool;


public class CommunicationChannel extends SardanaDevice 
{
	public CommunicationChannel(Machine machine, String name)
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
		if(! (obj instanceof CommunicationChannel)) 
			return false;
		return super.equals(obj); 
	}
}
