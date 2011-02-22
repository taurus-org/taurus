package es.cells.sardana.client.framework;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.logging.Logger;

import es.cells.sardana.client.framework.macroserver.MacroServerUtils;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Machine;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.Tango.DevVarLongStringArray;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.TangoDs.Except;

public class SardanaUtils extends ServerUtils{
	
	public static final String SARDANA_SERVICE_NAME = "Sardana"; 
	
	protected static Logger log = null;

	protected static SardanaUtils instance = null;
	
	
	protected SardanaUtils()
	{
	}
	
	static public SardanaUtils getInstance()
	{
		if(instance == null)
		{
			instance = new SardanaUtils();
			instance.init();
		}
		return instance;
	}
	
	protected void init()
	{
	}
		
	public void registerSardanaService(Machine machine, String instanceName, String deviceName) throws DevFailed
	{
		Database db = machine.getDataBase();
		db.registerService(SARDANA_SERVICE_NAME, instanceName, deviceName);
	}

	public HashMap<String, List<DeviceInfo>> getSardanas(Machine machine)
	{
		List<Machine> machines = new ArrayList<Machine>(1);
		machines.add(machine);
		return getSardanas(machines);
	}
	
	public HashMap<String, List<DeviceInfo>> getSardanas(List<Machine> machines)
	{
		HashMap<String, List<DeviceInfo>> ret = new HashMap<String, List<DeviceInfo>>();
		
		for(Machine machine : machines)
		{
			Database db = machine.getDataBase();
			DeviceInfo devInfo = null;
			try 
			{
				String [] sardanaSystems = db.getServices(SARDANA_SERVICE_NAME,"*");

				for(String s : sardanaSystems)
					System.out.println(s);
				
				String sardanaName = null;
				String fullInstanceName = null;
				
				for(String sardanaSystem : sardanaSystems)
				{
					String sardanaSystemClass;
					try
					{
						sardanaSystemClass = this.get_class_for_device(machine, sardanaSystem);
					}
					catch(DevFailed e)
					{
						continue;
					}
					fullInstanceName = getFullServerNameForDevice(machine,
																  sardanaSystemClass, 
																  sardanaSystem);
					if (fullInstanceName != null)
					{
						ArrayList<DeviceInfo> sardanaDevices = new ArrayList<DeviceInfo>();
						devInfo = new DeviceInfo(sardanaSystem,machine,sardanaSystemClass);
						sardanaDevices.add(devInfo);
						sardanaName = fullInstanceName.split("/")[1];
						if(sardanaSystemClass.equals(MACROSERVER_CLASS_NAME) && sardanaName != null)
						{
							DbDatum data = db.get_device_property(sardanaSystem, 
																  MacroServerUtils.MS_ATTR_POOL_NAMES);
							String [] pools = data.extractStringArray();
							for (String pool : pools)
							{
								fullInstanceName = getFullServerNameForDevice(machine,
																			  POOL_CLASS_NAME, 
																			  pool);
								if (fullInstanceName != null)
								{
									devInfo = new DeviceInfo(pool,machine,POOL_CLASS_NAME);
									sardanaDevices.add(devInfo);
								}
							}
						}
						ret.put(sardanaName, sardanaDevices);
					}
				}
			}
			catch (DevFailed e) 
			{
				e.printStackTrace();
			}			
		}
		
		return ret;
	}
	
	/**
	 * Wrapper method for the case where the Database server version
	 * is previous from 6.0
	 * 
	 * @param machine
	 * @param device_name
	 * @throws DevFailed 
	 */
	public String get_class_for_device(Machine machine, String device_name) throws DevFailed
	{
		Database db = machine.getDataBase();
		try
		{
			return db.get_class_for_device(device_name);
		}
		catch(DevFailed df)
		{
			for(DevError e : df.errors)
			{
				if(e.reason.equalsIgnoreCase("API_CommandNotFound"))
				{
					DeviceProxy db_dev = new DeviceProxy(db.get_device().name());
					DeviceData argin = new DeviceData();
					argin.insert(device_name);
					DeviceData argout = db_dev.command_inout("DbGetDeviceInfo",argin);
					String serv_name = argout.extractLongStringArray().svalue[3];
					String[] devs = db.get_device_class_list(serv_name);
					for(int i =0; i < devs.length/2; ++i)
					{
						int idx = 2*i;
						if(devs[idx].equalsIgnoreCase(device_name))
						{
							return devs[idx+1];
						}
					}
				}
			}
			System.out.println("Error get_class_for_device(" + machine.toString() + ", " + device_name);
			Except.print_exception(df);
			throw df;
		}
	}
	
	public class DeviceInfo
	{
		public String devName;
		public Machine machine;
		public String type; 
		
		public String getDevName() {
			return devName;
		}

		public void setDevName(String devName) {
			this.devName = devName;
		}

		public Machine getMachine() {
			return machine;
		}

		public void setMachine(Machine machine) {
			this.machine = machine;
		}

		public String getType() {
			return type;
		}

		public void setType(String type) {
			this.type = type;
		}

		public DeviceInfo(String d, Machine m, String type)
		{ this.devName = d; this.machine = m; this.type = type; }
	}
}
//	public HashMap<String, List<DeviceInfo>> findSardanas(Machine machine)
//	{
//		List<Machine> machines = new ArrayList<Machine>(1);
//		machines.add(machine);
//		return findSardanas(machines);
//	}
//	
//	/**
//	 * Tries to find Sardana systems from devices and properties in the 
//	 * database 
//	 * Return is:
//	 *   key = Sardana name
//	 *   value = list of devices that belong to the Sardana given by the key   
//	 * 
//	 * @param machines list of machines that have tango databases
//	 * @return
//	 */
//	public HashMap<String, List<DeviceInfo>> findSardanas(List<Machine> machines)
//	{
//		HashMap<String, List<DeviceInfo>> ret = new HashMap<String, List<DeviceInfo>>();
//		
//		for(Machine machine : machines)
//		{
//			Database db = machine.getDataBase();
//			
//			try 
//			{
//				String[] doors = db.get_device_name("*","Door");
//
//				// List of doors and the macro server they connect to. 
//				HashMap<String,String> door_ms = new HashMap<String,String>(doors.length);
//				
//				String[] prop = new String[] {"MacroServerName"};
//				for(String door : doors)
//				{
//					DbDatum[] res = db.get_device_property(door, prop);
//					door_ms.put(door, res[0].extractString());
//				}
//
//				String[] dbPoolServers = db.get_server_list("Pool/*");
//				String[] dbMSServers = db.get_server_list("MacroServer/*");
//				String[] dbSimuMotorServers = db.get_server_list("SimuMotorCtrl/*");
//				String[] dbSimuCoTiServers = db.get_server_list("SimuCoTiCtrl/*");
//				
//				// Do not consider servers that do not contain Pool or MacroServer devices
//				List<String> poolServers = new ArrayList<String>(dbPoolServers.length);
//				List<String> msServers = new ArrayList<String>(dbMSServers.length);
//				for(String dbPoolServer : dbPoolServers)
//				{
//					String[] pools = db.get_device_name(dbPoolServer, "Pool");
//					if(pools.length == 0)
//						continue;
//					String pool_dev_name = pools[0];
//					String[] servinst = dbPoolServer.split("/");
//					String instname = servinst[1];
//					List<DeviceInfo> devs = null;
//					if(!ret.containsKey(instname))
//					{
//						devs = new ArrayList<DeviceInfo>();
//						ret.put(instname, devs); 
//					}
//					else
//					{
//						devs = ret.get(instname);
//					}
//					devs.add(new DeviceInfo(pool_dev_name, machine, SardanaServer.PoolServer));
//				}
//				
//				for(String dbMSServer : dbMSServers)
//				{
//					String[] mss = db.get_device_name(dbMSServer, "MacroServer");
//					if(mss.length == 0)
//						continue;
//					String ms_dev_name = mss[0];
//					String[] servinst = dbMSServer.split("/");
//					String instname = servinst[1];
//					List<DeviceInfo> devs = null;
//					if(!ret.containsKey(instname))
//					{
//						devs = new ArrayList<DeviceInfo>();
//						ret.put(instname, devs); 
//					}
//					else
//					{
//						devs = ret.get(instname);
//					}
//					devs.add(new DeviceInfo(ms_dev_name, machine, SardanaServer.MSServer));
//					
//					// Find out which doors are connected to this MS
//					
//					for(String door : door_ms.keySet())
//					{
//						String ms = door_ms.get(door);
//						if (ms.equalsIgnoreCase(ms_dev_name))
//						{
//							devs.add(new DeviceInfo(door, machine, SardanaServer.DoorServer));
//						}
//					}
//				}
//				
//				for(String dbSimuMotorServer : dbSimuMotorServers)
//				{
//					String[] ctrls = db.get_device_name(dbSimuMotorServer, "SimuMotorCtrl");
//					if(ctrls.length == 0)
//						continue;
//					String[] servinst = dbSimuMotorServer.split("/");
//					String instname = servinst[1];
//					if(ret.containsKey(servinst[1]))
//					{
//						List<DeviceInfo> devs = ret.get(servinst[1]);
//					    devs.add(new DeviceInfo(ctrls[0], machine, SardanaServer.SimuMotorServer));
//					}
//				}
//				
//				for(String dbSimuCoTiServer : dbSimuCoTiServers)
//				{
//					String[] ctrls = db.get_device_name(dbSimuCoTiServer, "SimuCoTiCtrl");
//					if(ctrls.length == 0)
//						continue;
//					String[] servinst = dbSimuCoTiServer.split("/");
//					String instname = servinst[1];
//					if(ret.containsKey(servinst[1]))
//					{
//						List<DeviceInfo> devs = ret.get(servinst[1]);
//					    devs.add(new DeviceInfo(ctrls[0], machine, SardanaServer.SimuMotorServer));
//					}
//				}				
//			} 
//			catch (DevFailed e) 
//			{
//				e.printStackTrace();
//			}
//		}
//
//		
//		return ret;
//	}
//	
//	public static void main(String[] args) 
//	{
//		SardanaUtils utils = SardanaUtils.getInstance();
//		
//		Machine m1 = new Machine("controls01", "10000");
//		Machine m2 = new Machine("localhost", "10000");
//		
//		HashMap<String, List<DeviceInfo>> ret = utils.getSardanas(m1);
//		
//		for(String sardana : ret.keySet())
//		{
//			System.out.println("Found Sardana '" + sardana + "' with:");
//			List<DeviceInfo> devs = ret.get(sardana);
//			for(DeviceInfo d : devs)
//			{
//				System.out.println("\t" + d.machine + "/" + d.devName + "(" + d.type + ")");
//			}
//		}
//		
//	}

