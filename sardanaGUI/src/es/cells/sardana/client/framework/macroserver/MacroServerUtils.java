package es.cells.sardana.client.framework.macroserver;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import es.cells.sardana.client.framework.IPreferences;
import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.ServerUtils;
import es.cells.sardana.client.framework.pool.Machine;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceProperty;

public class MacroServerUtils extends ServerUtils {
	
	public static final String
	DOOR_CLASS_NAME = "Door",
	
	MS_ATTR_MACRO_LIST = "MacroList",
	MS_ATTR_DOOR_LIST = "DoorList",
	MS_ATTR_POOL_NAMES = "PoolNames",
	MS_ATTR_MACRO_PATH = "MacroPath",
	MS_ATTR_VERSION = "Version",
	DOOR_ATTR_MACRO_SERVER_NAME = "MacroServerName",	
	
	MS_CMD_GET_MACRO_INFO = "GetMacroInfo",
	DOOR_CMD_RUN_MACRO = "runMacro",
	DOOR_CMD_PAUSE_MACRO = "pauseMacro",
	DOOR_CMD_RESUME_MACRO = "resumeMacro",
	DOOR_CMD_ABORT_MACRO = "abortMacro";
	
	protected static MacroServerUtils instance = null;
	
	MacroServerUtils()
	{
	}
	
	static public MacroServerUtils getInstance()
	{
		if(instance == null)
		{
			instance = new MacroServerUtils();
			instance.init();
		}
		return instance;
	}
	
	protected void init()
	{
		log = SardanaManager.getInstance().getLogger(this.getClass().getName());
		log.setLevel(Level.ALL);
		
		if(System.getProperty("TANGO_HOST") == null)
		{
			IPreferences pref = SardanaManager.getInstance().getLoadedPreferences();
			String hostName = pref.getTangoHostName();
			String hostPort = pref.getTangoHostPort();
				
			System.setProperty("TANGO_HOST", hostName + ":" + hostPort);
			
			log.fine("Setting system property TANGO_HOST to " + hostName + ":" + hostPort);
		}
	}
	
	public String getMacroServerClassName()
	{
		return MACROSERVER_CLASS_NAME;
	}

	public String getDoorClassName()
	{
		return DOOR_CLASS_NAME;
	}
	
	public String[] getMacroServerInstances(Machine machine)
	{
		if(machine == null) return new String[0];
		
		Database db = machine.getDataBase();
		
		if(db == null)
			return new String[0];
		
		try 
		{
			return db.get_instance_name_list( getMacroServerClassName() );
		} 
		catch (DevFailed e) 
		{
			log.severe("Failed to get Macro servers from database: " + e.getMessage());
			return new String[0];
		}
	}
	
	public String[] getDevices(Machine machine, String fullServerInstanceName, String className)
	{
		Database db = machine.getDataBase();
		
		if(db == null)
			return new String[0];
		
		try 
		{
			return db.get_device_name(fullServerInstanceName, className);
		} 
		catch (DevFailed e) 
		{
			log.severe("Failed to get Device " + 
						fullServerInstanceName + 
						" from database: " + 
						e.getMessage());
			return new String[0];
		}			
	}
	
	public String[] getMacroServerDevices(Machine machine, String fullServerInstanceName)
	{
		return getDevices(machine, fullServerInstanceName, getMacroServerClassName());
	}
	
	public ArrayList<String> getMacroServerDevices(Machine machine)
	{
		String[] macroServers = getMacroServerInstances(machine);
		
		ArrayList<String> macroDevices = new ArrayList<String>();
		
		for(String macroServer : macroServers)
		{
			String[] serverMacroDevices = getMacroServerDevices(machine, 
												getMacroServerClassName() + "/" + macroServer);
			Collections.addAll(macroDevices, serverMacroDevices);
		}
		return macroDevices;
	}
	
	public ArrayList<String> getAvailableMacroServers(Machine machine)
	{
		Database db = machine.getDataBase();
		
		ArrayList<String> ret = new ArrayList<String>();
		
		if(db == null)
			return ret;
		
		try 
		{
			Collections.addAll( ret,	
					db.get_device_exported_for_class( getMacroServerClassName() ) );
			return ret;
		} 
		catch (DevFailed e) 
		{
			log.severe("Failed to get available Macro servers from database: " + e.getMessage());
			return ret;
		}
	}
	
	public List<Door> askForMacroServerDoors(MacroServer macroServer) throws DevFailed
	{
		Device device = macroServer.getDevice();
	
		DeviceAttribute argout = device.read_attribute(MS_ATTR_DOOR_LIST);
		
		String [] doorNames = argout.extractStringArray();
		
		ArrayList<Door> ret = new ArrayList<Door>();
		
		for(String doorName : doorNames)
		{
			Door door = getNewDoor(macroServer, doorName);
			ret.add(door);
		}
		return ret;
	}
	
	public String[] askForMacroServerMacros(MacroServer macroServer) 
									throws DevFailed, NumberFormatException
	{
		Device device = macroServer.getDevice();
		
		DeviceAttribute argout = device.read_attribute(MS_ATTR_MACRO_LIST);
		String [] macros = argout.extractStringArray();
				
		return macros;
	}
	
	
	public String askForMacroDescription(MacroServer macroServer, String macroName) 
															throws DevFailed
	{
		StringBuffer sb  = new StringBuffer();
		if(macroServer.isAvailable())
		{
			Device device = macroServer.getDevice();
			
			DeviceData argin = new DeviceData();
			String[] arg  = {macroName};
			argin.insert(arg);
		    DeviceData argout = device.command_inout(MS_CMD_GET_MACRO_INFO,argin);
		    
		    String [] descritprion = argout.extractStringArray();
		    for (String string : descritprion) 
		    {
		    	sb.append(string);
		    	sb.append("\n");
			}
		}
		
		return sb.toString();
	}
	
	public DeviceData executeMacro(Door door, String macroName, String [] macroArgs) 
																	throws DevFailed
	{
		String[] args;
		if(macroArgs!=null)
		{	
			args = new String[macroArgs.length+1];
			for(int i = 0; i < macroArgs.length; i++)
				args[i+1] = macroArgs[i];
		}
		else
			args = new String[1];
		
		args[0] = macroName;
		
		DeviceData argin = new DeviceData();
		argin.insert(args);
		
		DeviceData returnValues = door.getDevice().command_inout(DOOR_CMD_RUN_MACRO,argin);
		
		return returnValues;
	}
	
	public void pauseMacro(Door door) throws DevFailed
	{
		door.getDevice().command_inout(DOOR_CMD_PAUSE_MACRO);
	}
	
	public void resumeMacro(Door door) throws DevFailed
	{
		door.getDevice().command_inout(DOOR_CMD_RESUME_MACRO);
	}
	
	public void abortMacro(Door door) throws DevFailed
	{
		door.getDevice().command_inout(DOOR_CMD_ABORT_MACRO);
	}
	
	public String getDoorState(Door door)
	{
		 
		return new String();
	}
	private Door getNewDoor(MacroServer macroServer, String doorName) 
	{
		Door ret = new Door(macroServer.getMachine(),doorName);
		ret.setMacroServer(macroServer);
		return ret;
	}
	
	public List<DeviceProperty> askForMacroServerProperties(MacroServer macroServer)
	{
		log.entering("DPUtils","askForDevicePoolProperties",macroServer);
		List<DeviceProperty> ret = new ArrayList<DeviceProperty>();
		
		Device device = macroServer.getDevice();
		
		if(device == null)
			device = askForDevice(macroServer.getMachine(), macroServer.getName());
		
		if(device == null)
		{
			log.exiting("DPUtils","askForDevicePoolProperties (no device)");
			return ret;
		}
		
		device.refreshPropertyMap();
		Map props = device.getPropertyMap();
		
		for(Object obj : props.values())
		{
			DeviceProperty prop = (DeviceProperty) obj;
			ret.add(prop);
		}
		log.exiting("DPUtils","askForDevicePoolProperties",ret);
		return ret;
	}
	
	public MacroServer getNewMacroServer(Machine machine, 
										  String deviceName, 
										  boolean available)
	{
		log.entering("DPUtils", "getNewMacroServer", deviceName);
		if(deviceName == null || deviceName.equals(""))
		{
			log.exiting("DPUtils", "getNewMacroServer (no device name)");
			return null;
		}
		
		MacroServer macroServer = null;
		if(available == true)
		{			
			Device device = askForDevice(machine, deviceName);
			
			String alias = device.getAlias();
			
			//TODO URGENT see problem happening with tango alias "nada" problem 
			//alias = null;
			
			if(alias == null || alias.length() == 0)
				alias = deviceName;
			
			macroServer = new MacroServer(machine, alias);
	
			macroServer.setDevice(device,false);
		}
		else
		{
			macroServer = new MacroServer(machine,deviceName);
		}
		
		macroServer.start();
		
		log.exiting("DPUtils", "getNewMacroServer",macroServer);
		
		return macroServer;
	}	
	
	public void createMacroServer(MacroServerCreationInfo info) throws DevFailed
	{
		Database db = info.getMachine().getDataBase();
    	
		try
		{
			String msName = info.getMacroServerDeviceName();
			String msAlias = info.getMacroServerAliasName();
			db.add_device(msName, ServerUtils.MACROSERVER_CLASS_NAME,
								  ServerUtils.MACROSERVER_CLASS_NAME + "/" + info.getInstanceName());
						
			if(msAlias != null && msAlias.length() > 0)
			{
				db.put_device_alias(msName,msAlias);
			}
			
			DbDatum msProps[] = new DbDatum[] { 
					new DbDatum(MS_ATTR_MACRO_PATH,info.getMacroPath()),
					new DbDatum(MS_ATTR_POOL_NAMES,info.getPoolNames()),
					new DbDatum(MS_ATTR_VERSION,info.getMsVersion())
			};
			db.put_device_property(msName, msProps);
			
			String doorName = info.getDoorDeviceName();
			if(doorName != null && doorName.length() > 0)
			{
				db.add_device(info.getDoorDeviceName(),
						ServerUtils.DOOR_CLASS_NAME,
						ServerUtils.MACROSERVER_CLASS_NAME + "/" + info.getInstanceName());
				
				String doorAlias = info.getDoorAlias();
				
				if(doorAlias != null && doorAlias.length() > 0)
				{
					db.put_device_alias(info.getDoorDeviceName(),info.getDoorAlias());
				}
			}

			DbDatum doorProps[] = new DbDatum[] { new DbDatum(DOOR_ATTR_MACRO_SERVER_NAME, msName) };
			db.put_device_property(doorName, doorProps);
			
		}
		catch(DevFailed e)
		{
			throw e;
		}
	}

	
	
}
