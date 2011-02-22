package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.List;

public class PseudoCounter extends ExperimentChannel 
{

	/** List of motors used by this pseudo motor */
	protected ArrayList<ExperimentChannel> counters = new ArrayList<ExperimentChannel>();

	protected PseudoCounterClass pcClass;
	
	
	public PseudoCounter(Machine machine, String name) 
	{
		super(machine, name);
	}
	
	public List<ExperimentChannel> getCounters() {
		return counters;
	}

	public void setCounters(ArrayList<ExperimentChannel> counters) 
	{
		this.counters = counters;
	}

	public void addCounter(ExperimentChannel counter) {
		counters.add(counter);
	}

	@Override
	public boolean equals(Object obj)
	{
		if(! (obj instanceof PseudoMotor))
			return false;

		return super.equals(obj);
	}
	
	public void setPseudoCounterClass(PseudoCounterClass pcClass)
	{
		this.pcClass = pcClass;
	}
	
	public PseudoCounterClass getPseudoCounterClass()
	{
		return pcClass;
	}

	public String getFileName()
	{
		if(pcClass == null) return null;
		
		return pcClass.getFileName();
	}
	
	public String getFullPathName()
	{
		if(pcClass == null) return null;
		
		return pcClass.getFullPathName();
	}

	public String getFullClassName()
	{
		if(pcClass == null) return null;
		
		return pcClass.getFullClassName();
	}

	public String getClassNameWithModule()
	{
		if(pcClass == null) return null;
		
		return pcClass.getClassNameWithModule();
	}
	
	public String getClassName()
	{
		if(pcClass == null) return null;
		
		return pcClass.getClassName();
	}	
}
