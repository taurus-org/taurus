package es.cells.sardana.client.framework.pool;

import fr.esrf.TangoApi.AttributeInfoEx;


public class CounterTimer extends ExperimentChannel 
{
	public CounterTimer(Machine machine, String name) 
	{
		super(machine, name);
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof CounterTimer)) 
			return false;
		return super.equals(obj); 
	}
	
	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.EXP_CHANNEL_VALUE);
		
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
			
			if(!nonPolledAttributeList.contains(attr.name))
				nonPolledAttributeList.add(attr.name);
		}
	}
}
