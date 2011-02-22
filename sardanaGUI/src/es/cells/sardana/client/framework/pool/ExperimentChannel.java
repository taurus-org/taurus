package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;

import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.INumberImage;

public abstract class ExperimentChannel extends SardanaDevice 
{
	protected ArrayList<MeasurementGroup> mgs = new ArrayList<MeasurementGroup>();
	
	public ExperimentChannel(Machine machine, String name)
	{
		super(machine, name);
	}

	public INumberImage getValueAttributeModel()
	{
		return (INumberImage)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.EXP_CHANNEL_VALUE);
	}

	public ICommand getAbortCommandModel()
	{
		return (ICommand) commands.get(getDeviceName() + "/Abort");
	}

	public ICommand getStopCommandModel()
	{
		return (ICommand) commands.get(getDeviceName() + "/Stop");
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof ExperimentChannel)) 
			return false;
		return super.equals(obj); 
	}
	
	public void addMeasurementGroup(MeasurementGroup mg)
	{
		if(!mgs.contains(mg))
			mgs.add(mg);
	}
	
	public void removeMeasurementGroup(MeasurementGroup mg)
	{
		mgs.remove(mg);
	}
	
	public boolean hasMeasurementGroup(MeasurementGroup mg)
	{
		return mgs.contains(mg);
	}
	
	public ArrayList<MeasurementGroup> getMeasurementGroups()
	{
		return mgs;
	}
}
