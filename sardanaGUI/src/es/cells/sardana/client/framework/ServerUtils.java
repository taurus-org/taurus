package es.cells.sardana.client.framework;

import java.util.logging.Logger;

import es.cells.sardana.client.framework.pool.Machine;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.Database;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceFactory;

public abstract class ServerUtils {
	
	public static final String
	MACROSERVER_CLASS_NAME = "MacroServer",
	DOOR_CLASS_NAME = "Door",
	POOL_CLASS_NAME = "Pool";
	
	protected static Logger log = null;
	
	public String getFullServerNameForDevice(Machine machine, 
											  String serverType, 
											  String deviceName) throws DevFailed
	{
		Database db = machine.getDataBase();
		String [] serverList = db.get_server_list(serverType + "/*");
		for (String serverName : serverList)
		{
			String [] serverDevices = db.get_device_class_list(serverName);
			for (int i = 0; i < serverDevices.length; i+=2 )
			{
				String devName = serverDevices[i];
				String deviceType = serverDevices[i+1];
				if(deviceType.equals(serverType) && devName.equalsIgnoreCase(deviceName))
					return serverName;
			}
		}
		return null;
	}
	
	public Device askForDevice(Machine machine, String deviceInstanceName)
	{
		log.entering("DPUtils", "askForDevice", deviceInstanceName);
		if( deviceInstanceName == null || deviceInstanceName.equals("") )
		{
			log.exiting("DPUtils", "askForDevice (no device name)");
			return null;
		}
		
		try
		{
			Device ret = DeviceFactory.getInstance().getDevice(deviceInstanceName);
			log.exiting("DPUtils", "askForDevice",ret);
			return ret;
		} 
		catch (ConnectionException e) 
		{
			log.severe("Failed to create device " + deviceInstanceName + ": " + e.getMessage());
			return null;
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
			log.severe("Failed to get Device " + fullServerInstanceName + " from database: " + e.getMessage());
			return new String[0];
		}			
	}
	
	public String[] getServerInstanceClasses(Machine machine, String fullServerInstanceName)
	{
		Database db = machine.getDataBase();
		
		if(db == null)
			return new String[0];
		
		try 
		{
			return db.get_server_class_list(fullServerInstanceName);
		} 
		catch (DevFailed e) 
		{
			log.severe("Failed to get Device Server " + fullServerInstanceName + " Classes: " + e.getMessage());
			return new String[0];
		}		
	}

}
