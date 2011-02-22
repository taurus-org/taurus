package es.cells.sardana.client.framework.pool;

import java.util.Vector;

public class PseudoMotorClass extends ControllerClass {
	
	protected Vector<String> motorRoles;
	protected Vector<String> pseudoMotorRoles;
	
	public PseudoMotorClass(String typee, String klass, String fullPath) 
	{
		super(typee, klass, fullPath);
	}
	
	public Vector<String> getPseudoMotorRoles() 
	{
		return pseudoMotorRoles;
	}
	
	public void setPseudoMotorRoles(Vector<String> pseudoMotorRoles) 
	{
		this.pseudoMotorRoles = pseudoMotorRoles;
	}
	
	public Vector<String> getMotorRoles() 
	{
		return motorRoles;
	}
	
	public void setMotorRoles(Vector<String> motorRoles) 
	{
		this.motorRoles = motorRoles;
	}
	
	public String getMotorRoles(int index)
	{
		return motorRoles.get(index);
	}
	
	public String getPseudoMotorRoles(int index)
	{
		return pseudoMotorRoles.get(index);
	}
	
	public boolean match(Object obj) 
	{
		if(!(obj instanceof PseudoMotorClass))
			return false;

		if(!super.match(obj))
			return false;
		
		PseudoMotorClass pmc = (PseudoMotorClass) obj; 
		
		return motorRoles.equals(pmc.motorRoles) &&
			   pseudoMotorRoles.equals(pmc.pseudoMotorRoles);
	}
}
