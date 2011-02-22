package es.cells.sardana.client.framework.pool;

import java.util.Vector;

public class PseudoCounterClass extends ControllerClass 
{
	protected Vector<String> counterRoles;
	protected Vector<String> pseudoCounterRoles;
	
	public PseudoCounterClass(String typee, String klass, String fullPath)
	{
		super(typee, klass, fullPath);
	}
	
	public Vector<String> getCounterRoles() 
	{
		return counterRoles;
	}

	public Vector<String> getPseudoCounterRoles() 
	{
		return pseudoCounterRoles;
	}

	public void setPseudoCounterRoles(Vector<String> pseudoCounterRoles) 
	{
		this.pseudoCounterRoles = pseudoCounterRoles;
	}

	public void setCounterRoles(Vector<String> counterRoles) 
	{
		this.counterRoles = counterRoles;
	}
	
	public String getCounterRole(int index)
	{
		return counterRoles.get(index);
	}
	
	public String getPseudoCounterRole(int index)
	{
		return pseudoCounterRoles.get(index);
	}
	
	
	public boolean match(Object obj) 
	{
		if(!(obj instanceof PseudoCounterClass))
			return false;

		if(!super.match(obj))
			return false;
		
		PseudoCounterClass pcc = (PseudoCounterClass) obj; 
		
		return counterRoles.equals(pcc.counterRoles) &&
		   pseudoCounterRoles.equals(pcc.pseudoCounterRoles);
	}	
}
