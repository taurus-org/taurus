package es.cells.sardana.client.framework.pool;

import java.util.List;

import es.cells.sardana.client.framework.gui.atk.utils.AttributeNameSorter;
import es.cells.sardana.client.framework.gui.atk.utils.AttributePermissionSorter;
import es.cells.sardana.client.framework.gui.atk.utils.AttributeSorter;
import es.cells.sardana.client.framework.gui.atk.utils.AttributeTypeSorter;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.INumberScalar;

public class Motor extends SardanaDevice 
{
	public Motor(Machine machine, String name)
	{
		super(machine, name);
	}
	
	public INumberScalar getPositionAttributeModel()
	{
		return (INumberScalar) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MOTOR_ATTR_POSITION);
	}
	
	public void setPosition(double pos)
	{
		getPositionAttributeModel().setValue(pos);
	}
	
	public double getPosition()
	{
		return getPositionAttributeModel().getNumberScalarValue();
	}
	
	public ICommand getAbortCommandModel()
	{
		return (ICommand) commands.get(getDeviceName() + "/Abort");
	}
	
	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.MOTOR_ATTR_POSITION);
		
		AttributeSorter sorter = 
			    new AttributeTypeSorter(
			    new AttributePermissionSorter(
			    new AttributeNameSorter(null)));
		
		List<AttributeInfoEx> attrInfoList = sorter.sort(attributeInfo);
		
		for(AttributeInfoEx attr : attrInfoList)
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
			
			nonPolledAttributeList.add(attr.name);
		}
	}
	
	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof Motor)) 
			return false;
		return super.equals(obj); 
	}
}
