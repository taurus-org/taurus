package es.cells.sardana.client.framework.pool;

import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.INumberScalar;

public class ZeroDExpChannel extends ExperimentChannel 
{

	public ZeroDExpChannel(Machine machine, String name) 
	{
		super(machine, name);
	}

	public INumberScalar getCumulatedValueAttributeModel()
	{
		return (INumberScalar)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.ZEROD_CHANNEL_CUMULATED_VALUE);
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof ZeroDExpChannel)) 
			return false;
		return super.equals(obj); 
	}
	
	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.EXP_CHANNEL_VALUE);
		eventAttributeList.add(DevicePoolUtils.ZEROD_CHANNEL_CUMULATED_VALUE);
		eventAttributeList.add(DevicePoolUtils.ZEROD_CHANNEL_CUMULATION_TIME);
		eventAttributeList.add(DevicePoolUtils.ZEROD_CHANNEL_CUMULATION_TYPE);
		
		for(AttributeInfoEx attr : attributeInfo)
		{
			boolean is_event_attr = false;
			for(String eventAttr : eventAttributeList)
			{
				if(eventAttr.equalsIgnoreCase(attr.name))
				{
					is_event_attr = true;
					break;
				}	
			}
			
			if(is_event_attr == true)
				continue;
			
			if(!nonPolledAttributeList.contains(attr))
				nonPolledAttributeList.add(attr.name);
		}
	}	
}
