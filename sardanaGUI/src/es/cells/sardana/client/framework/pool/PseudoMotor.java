package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.List;

public class PseudoMotor extends Motor 
{
	/** List of motors used by this pseudo motor */
	protected ArrayList<Motor> motors = new ArrayList<Motor>();

	protected PseudoMotorClass pmClass;

	/** List of motor groups that use this motor */
	/*
	protected ArrayList<MotorGroup> mgsThatUseThisMotor = new ArrayList<MotorGroup>();
	public List<MotorGroup> getMotorGroupsThatUseThisMotor()
	{
		return mgsThatUseThisMotor;
	}
	
	public void addMotorGroupThatUseThisMotor(MotorGroup motorGroup)
	{
		this.mgsThatUseThisMotor.add(motorGroup);
	}
	*/
	
	public PseudoMotor(Machine machine, String name)
	{
		super(machine, name);
	}

	@Override
	public boolean equals(Object obj)
	{
		if(! (obj instanceof PseudoMotor))
			return false;

		return super.equals(obj);
	}
	
	public void setPseudoMotorClass(PseudoMotorClass pmClass)
	{
		this.pmClass = pmClass;
	}
	
	public PseudoMotorClass getPseudoMotorClass()
	{
		return pmClass;
	}

	public String getFileName()
	{
		if(pmClass == null) return null;
		
		return pmClass.getFileName();
	}
	
	public String getFullPathName()
	{
		if(pmClass == null) return null;
		
		return pmClass.getFullPathName();
	}

	public String getFullClassName()
	{
		if(pmClass == null) return null;
		
		return pmClass.getFullClassName();
	}

	public String getClassNameWithModule()
	{
		if(pmClass == null) return null;
		
		return pmClass.getClassNameWithModule();
	}
	
	public String getClassName()
	{
		if(pmClass == null) return null;
		
		return pmClass.getClassName();
	}
	
	public List<Motor> getMotors() {
		return motors;
	}

	public void setMotors(ArrayList<Motor> motors) 
	{
		this.motors = motors;
	}

	public void addMotor(Motor motor) {
		motors.add(motor);
	}
}