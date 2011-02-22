package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.List;

import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class MotorGroup extends SardanaDevice 
{	
	protected ArrayList<Motor> motors = new ArrayList<Motor>();
	protected ArrayList<MotorGroup> motorGroups = new ArrayList<MotorGroup>();
	protected ArrayList<PseudoMotor> pseudoMotors = new ArrayList<PseudoMotor>();
	protected ArrayList<SardanaDevice> elements = new ArrayList<SardanaDevice>();
	
	protected ArrayList<IStringSpectrumListener> elementsListeners;
	
	protected ElementsListener elementListListener = new ElementsListener();

	public MotorGroup(Machine machine, String name)
	{
		super(machine, name);
		elementsListeners = new ArrayList<IStringSpectrumListener>();
	}

	public INumberSpectrum getPositionAttributeModel()
	{
		return (INumberSpectrum) eventAttributes.get(getDeviceName() + "/" +
				DevicePoolUtils.MOTOR_GROUP_ATTR_POSITION);
	}
	
	public IStringSpectrum getElementsAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MOTOR_GROUP_ATTR_ELEMENTS);
	}
	
	public ICommand getAbortCommandModel()
	{
		return (ICommand) commands.get(getDeviceName() + "/Abort");
	}
	
	
	
	@Override
	protected void initAttributes() throws ConnectionException 
	{
		super.initAttributes();
		
		getElementsAttributeModel().addListener(elementListListener);
	}

	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.MOTOR_GROUP_ATTR_POSITION);
		eventAttributeList.add(DevicePoolUtils.MOTOR_GROUP_ATTR_ELEMENTS);
		
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
			
			nonPolledAttributeList.add(attr.name);
		}
	}
	
	public void addNewElement(SardanaDevice dev) throws DevFailed
	{
		DeviceData data = new DeviceData();
		data.insert(dev.getName());
		getDevice().command_inout("AddElement",data);
	}
	
	public void removeElement(SardanaDevice dev) throws DevFailed
	{
		DeviceData data = new DeviceData();
		data.insert(dev.getName());
		getDevice().command_inout("RemoveElement",data);
	}
	
	public ArrayList<Motor> getMotors() 
	{
		return motors;
	}
	
	public void addMotor(Motor motor) 
	{
		motors.add(motor);
	}
	
	public ArrayList<MotorGroup> getMotorGroups() 
	{
		return motorGroups;
	}
	
	public void addMotorGroup(MotorGroup motorGroup) 
	{
		motorGroups.add(motorGroup);
	}	

	public ArrayList<PseudoMotor> getPseudoMotors() 
	{
		return pseudoMotors;
	}
	
	public void addPseudoMotor(PseudoMotor pseudoMotor) 
	{
		pseudoMotors.add(pseudoMotor);
	}
	
	public void addElement(SardanaDevice element)
	{
		elements.add(element);
	}
	
	public List<SardanaDevice> getElements()
	{
		return elements;
	}

	public void addGenericElement(SardanaDevice element)
	{
		if(element instanceof PseudoMotor)
			pseudoMotors.add((PseudoMotor) element);
		else if(element instanceof Motor)
			motors.add((Motor) element);
		else if(element instanceof MotorGroup)
			motorGroups.add((MotorGroup) element);
		else
		{
			log.warning("Trying to add invalid element to motor group: " + element);
			return;
		}
		elements.add(element);
	}
	
	public void addElementsListener(IStringSpectrumListener listener)
	{
		elementsListeners.add(listener);
	}

	public void removeElementsListener(IStringSpectrumListener listener)
	{
		elementsListeners.remove(listener);
	}

	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof MotorGroup)) 
			return false;
		return super.equals(obj); 
	}
	
	public boolean isInternal()
	{
		return getName().startsWith("_pm_");
	}
	
	protected class ElementsListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			elements.clear();
			
			String element_names[] = e.getValue();
			
			for(String element_name : element_names)
				elements.add(pool.getSardanaDevice(element_name));

			for(IStringSpectrumListener listener : elementsListeners)
				listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}	
}
