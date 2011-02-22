package es.cells.sardana.client.framework.pool;

import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberSpectrum;

public class TwoDExpChannel extends ExperimentChannel 
{

	public TwoDExpChannel(Machine machine, String name) 
	{
		super(machine, name);
	}

	public INumberSpectrum getSpectrumDataAttributeModel()
	{
		return (INumberSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.TWOD_CHANNEL_DATA);
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof TwoDExpChannel)) 
			return false;
		return super.equals(obj); 
	}
	
	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.EXP_CHANNEL_VALUE);
		eventAttributeList.add(DevicePoolUtils.TWOD_CHANNEL_DATA);
		
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
