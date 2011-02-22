package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import es.cells.sardana.client.framework.SardanaManager;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoApi.CommandInfo;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributePolledList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.CommandList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceProperty;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.IDevStateScalar;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.IStringScalarListener;
import fr.esrf.tangoatk.core.StringScalarEvent;

public class SardanaDevice implements IDevStateScalarListener, IStringScalarListener
{
	protected static Logger log = null;
	
	protected Machine machine;
	protected Device device;
	protected String name;
	protected String serverName;
	
	protected DevicePool pool;
	
	protected int idInController;
	protected Controller controller;
	
	AttributeList eventAttributes;
	AttributePolledList polledAttributes;
	AttributeList nonPolledAttributes;
	
	ArrayList<String> eventAttributeList;
	ArrayList<String> polledAttributeList;
	ArrayList<String> nonPolledAttributeList;
	
	CommandList commands;

	boolean available;
	
	List<AttributeInfoEx> attributeInfo;
	List<CommandInfo> commandInfo;
	
	String          strStateValue;
	String          strStateQuality;
	IDevStateScalar state;
	
	IStringScalar   status;
	
	ArrayList<IDevStateScalarListener> stateListeners;
	ArrayList<IStringScalarListener> statusListeners;
	
	protected HashMap<String, DeviceProperty> properties;
	
	public SardanaDevice(Machine machine, String name)
	{ 
		this.name = name;
		this.machine = machine;
		this.available = false;
		strStateValue = "UNKNOWN";
		strStateQuality = "UNKNOWN";
		controller = null;
		idInController = -1;
		stateListeners = new ArrayList<IDevStateScalarListener>();
		statusListeners = new ArrayList<IStringScalarListener>();
		properties = new HashMap<String, DeviceProperty>();
	}

	protected void init()
	{
		if(log == null)
			log = SardanaManager.getInstance().getLogger(this.getClass().getName() + "/" + name);
		
		if(device == null)
		{
			available = false;
			return;
		}
		
		available = device.isAlive();
		
		if(available)
		{	
			askForState();
			try
			{
				AttributeInfoEx[] attribs = device.get_attribute_info_ex();
				attributeInfo = new ArrayList<AttributeInfoEx>(attribs.length);
				for(AttributeInfoEx attrib : attribs) attributeInfo.add(attrib);
				
				CommandInfo[] commands = device.getCommandList();
				commandInfo = new ArrayList<CommandInfo>(commands.length);
				for(CommandInfo cmd : commands) commandInfo.add(cmd);
			
				initAttributeSemantics();
				initAttributes();
				initCommands();
			}
			catch (DevFailed e)	
			{
				
			}
			catch (ConnectionException e)
			{

			}
		}
		else
		{
			log.info("Device " + getName() + " was not available at creation time");
		}
		
	}	

	protected void init(String deviceName) throws ConnectionException
	{
		device = DevicePoolUtils.getInstance().askForDevice(machine, deviceName);
		init();
	}
	
	protected void initAttributeSemantics()
	{
		eventAttributeList = new ArrayList<String>();
		polledAttributeList = new ArrayList<String>();
		nonPolledAttributeList = new ArrayList<String>();
		
		eventAttributeList.add("State");
		
		nonPolledAttributeList.add("Status");
	}
	
	/**
	 * Override in the subclass
	 * @throws ConnectionException 
	 *
	 */
	protected void initAttributes() throws ConnectionException
	{
		eventAttributes = new AttributeList();
		polledAttributes = new AttributePolledList();
		nonPolledAttributes = new AttributeList();
		
		
		for(String eventAttr : eventAttributeList)
		{
			IEntity entity = eventAttributes.add(getDeviceName() + "/" + eventAttr);
			
			// We handle state attribute in a special case
			if(eventAttr.equalsIgnoreCase("State"))
			{
				state = (IDevStateScalar)entity;
				state.addDevStateScalarListener(this);
			}
		}
		
		for(String polledAttr : polledAttributeList)
			polledAttributes.add(getDeviceName() + "/" + polledAttr);

		for(String nonPolledAttr : nonPolledAttributeList)
		{
			IEntity entity = nonPolledAttributes.add(getDeviceName() + "/" + nonPolledAttr);
			
			// We handle state attribute in a special case
			if(nonPolledAttr.equalsIgnoreCase("Status"))
			{
				status = (IStringScalar)entity;
				status.addStringScalarListener(this);
			}
		}
		
	}
	
	public void start()
	{
		if(eventAttributes != null)
		{
			eventAttributes.setRefreshInterval(DevicePoolUtils.DFT_REFRESH_INTERVAL);
			eventAttributes.startRefresher();
		}
		if(polledAttributes != null)
		{
			polledAttributes.setRefreshInterval(DevicePoolUtils.DFT_REFRESH_INTERVAL);
			polledAttributes.startRefresher();
		}
		
		// Get the values one time at start time
		if(nonPolledAttributes != null)
			nonPolledAttributes.refresh();
	}
	
	protected void initCommands() throws ConnectionException
	{
		commands = new CommandList();
		
		String deviceName = getDeviceName();
		
		if(deviceName != null && deviceName.length() > 0)
		{
			deviceName += "/";
			for(CommandInfo command : commandInfo)
				commands.add(deviceName + command.cmd_name);
		}
	}
	
	public void Init() throws DevFailed
	{
		device.command_inout("Init");
	}
	
	public Machine getMachine() 
	{
		return machine;
	}

	public Database getDataBase()
	{
		if(machine == null) return null;
		return machine.getDataBase();
	}
	
	public DeviceAttribute getDeviceAttribute(String attrName)
	{
		IEntity attr = getAttribute(attrName);
		return attr == null ? null : ((IAttribute)attr).getAttribute();
	}
	
	public IAttribute getAttribute(String attrName)
	{
		if(attrName.indexOf('/') < 0)
			attrName = getDeviceName()+"/"+attrName;
		
		IEntity attr = eventAttributes.get(attrName);
		
		if(attr == null)
		{
			attr = polledAttributes.get(attrName);
			if(attr == null)
			{
				attr = nonPolledAttributes.get(attrName);
			}
		}
		return attr == null ? null : (IAttribute)attr;
	}
	
	public ICommand getCommandModel(String commandName)
	{
		String deviceName = getDeviceName();
		
		if(deviceName != null && deviceName.length() > 0)
		{
			deviceName += "/";
			return (ICommand) commands.get(deviceName + commandName);
		}
		return null;
	}

	public String getName()
	{
		return name;
	}

	public boolean isAvailable() 
	{
		return available;
	}
	
	public Device getDevice() 
	{
		return device;
	}
	
	public String getDeviceName()
	{
		return (device != null) ? device.getName() : "";
	}
	
	public Controller getController() 
	{
		return controller;
	}
	
	public void setController(Controller controller) 
	{
		this.controller = controller;
	}
	
	public DevicePool getPool() 
	{
		return pool;
	}

	public void setPool(DevicePool pool)
	{
		this.pool = pool;
	}

	public int getIdInController()
	{
		return idInController;
	}
	
	public void setIdInController(int ctrlId)
	{
		this.idInController = ctrlId;
	}	
	
	public boolean hasPendingControllerId()
	{
		return controller == null;
	}
	
	
	public List<AttributeInfoEx> getAttributeInfo()
	{
		return attributeInfo;
	}
	
	public AttributeInfoEx getAttributeInfo(String name)
	{
		if(attributeInfo == null)
			return null;
		
		for(AttributeInfoEx info : attributeInfo)
		{
			if(info.name.equalsIgnoreCase(name))
				return info;
		}
		return null;
	}
	
	public List<CommandInfo> getCommandInfo()
	{
		return commandInfo;
	}	
	
	public IDevStateScalar getStateAttributeModel()
	{
		return state;
	}
	
	public IStringScalar getStatusAttributeModel()
	{
		return status;
	}
	
	public String getState()
	{
		if(isAvailable() && strStateValue == "UNKNOWN")
		{
			// State is not consistent.
			log.info("The state for " + getName() + " is UNKNOWN although the device is available!" );
		}
		return strStateValue;
	}
	
	public String askForState()
	{
		if(isAvailable())
		{
			strStateValue = device.getState();
			return strStateValue;
		}
		return "";
	}
	
	/*
	public String askForStatus()
	{
		return device.getStatus();
	}	
	*/
	
	public void refresh() throws ConnectionException
	{
		String deviceName = getDeviceName();
		
		init(deviceName);
		
		device.refresh();
		
		start();
	}

	public void setDevice(Device device, boolean keep_beacon)
	{
		unregisterFromDevice(keep_beacon);
		this.device = device;
		init();
	}
	
	public void cleanup(boolean keep_beacon)
	{
		setDevice(null, keep_beacon);
	}
	
	/**
	 * Override as necessary in subclass
	 *
	 */
	protected void unregisterFromDevice(boolean keep_beacon)
	{
		if(state != null && (!keep_beacon))
		{
			state.removeDevStateScalarListener(this);
		}
		
		if(eventAttributes != null)
		{
			if(keep_beacon)
			{
				// We know the state is the first attribute that was registered
				if(eventAttributes.size() > 1)
					eventAttributes.removeRange(1, eventAttributes.size()-1);
			}
			else
				eventAttributes.removeAllElements();
		}

		if(polledAttributes != null)
			polledAttributes.removeAllElements();
		
		if(nonPolledAttributes != null)
			nonPolledAttributes.removeAllElements();
	}
	
	public void addDevStateScalarListener(IDevStateScalarListener listener)
	{	
		if(listener != null)
		{
			if(!stateListeners.contains(listener))
				stateListeners.add(listener);
		}
	}
	
	public void removeDevStateScalarListener(IDevStateScalarListener listener)
	{
		if(listener != null)
			stateListeners.remove(listener);
	}
	
	public void addStatusListener(IStringScalarListener listener)
	{
		if(listener != null)
			statusListeners.add(listener);
	}

	public void removeStatusListener(IStringScalarListener listener)
	{
		if(listener != null)
			statusListeners.remove(listener);
	}
	
	public void devStateScalarChange(DevStateScalarEvent e)
	{
		if(strStateValue.equals(e.getValue()))
			return;
		
		String old_state = strStateValue;
		strStateValue = e.getValue();
		
		if(strStateValue == null || strStateValue.length() == 0 )
		{
			log.warning("Received invalid state event");
		}
		
		if(strStateValue.equalsIgnoreCase("UNKNOWN") && isAvailable())
			available = false;
		else if(!isAvailable() && !strStateValue.equalsIgnoreCase("UNKNOWN"))
			available = true;
		
		for(IDevStateScalarListener listener : stateListeners)
			listener.devStateScalarChange(e);
	}

	public void stateChange(AttributeStateEvent e)
	{
		if(strStateQuality.equals(e.getState()))
			return;

		strStateQuality = e.getState();

		if(strStateQuality == null || strStateQuality.length() == 0 )
		{
			log.warning("Received invalid state quality event");
		}
		
		// State quality changed
		for(IDevStateScalarListener listener : stateListeners)
			listener.stateChange(e);
	}

	public void errorChange(ErrorEvent evt)
	{
		log.warning("Received state error event event");
		
		available = false;
		
		// Error change
		for(IDevStateScalarListener listener : stateListeners)
			listener.errorChange(evt);
	}

	// Status Change
	public void stringScalarChange(StringScalarEvent e)
	{
		if(e.getSource() == null)
			return;
		
		// Error change
		for(IStringScalarListener listener : statusListeners)
			listener.stringScalarChange(e);
	}

	public List<String> getEventAttributeList() 
	{
		return eventAttributeList;
	}

	public List<String> getPolledAttributeList() 
	{
		return polledAttributeList;
	}

	public List<String> getNonPolledAttributeList() 
	{
		return nonPolledAttributeList;
	}
	
	public AttributeList getEventAttributes()
	{
		return eventAttributes;
	}

	public AttributeList getNonPolledAttributes()
	{
		return nonPolledAttributes;
	}

	public AttributeList getPolledAttributes()
	{
		return polledAttributes;
	}

	public void setProperty(DeviceProperty prop)
	{
		properties.put(prop.getName().toLowerCase(), prop);
	}
	
	public DeviceProperty getProperty(String name)
	{
		return properties.get(name.toLowerCase());
	}
	
	public Map<String,DeviceProperty> getProperties()
	{
		return properties;
	}
	
	public void setServerName(String fullServerName) 
	{
		this.serverName = fullServerName;
	}
	
	public String getServerName()
	{
		return this.serverName;
	}
	
	@Override
	public boolean equals(Object obj)
	{
		if(obj == null || !(obj instanceof SardanaDevice) )
			return false;
		
		return name.equalsIgnoreCase(((SardanaDevice)obj).getName());
	}

	@Override
	public String toString()
	{
		return name;
	}

	
	
}
