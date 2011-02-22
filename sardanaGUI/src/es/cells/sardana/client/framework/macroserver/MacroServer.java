package es.cells.sardana.client.framework.macroserver;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.DeviceProperty;


public class MacroServer extends SardanaDevice 
{
	protected List<Door> doors;
	protected List<DevicePool> pools;

	public MacroServer(Machine machine, String name) 
	{
		super(machine, name);
	}
	
	protected void init()
	{
		MacroServerUtils utils = MacroServerUtils.getInstance();
		
		properties = new HashMap<String,DeviceProperty>();
		doors = new ArrayList<Door>();
		pools = new ArrayList<DevicePool>();
		
		setProperties(utils.askForMacroServerProperties(this));
		try
		{
			setDoors(utils.askForMacroServerDoors(this));
		}
		catch (DevFailed e){ }

		
		super.init();
		initDoors();
	}
	
	//Properties methods --------------------------------------	
	public void setProperties(List<DeviceProperty> props) 
	{
		for(DeviceProperty prop : props)
		{
			setProperty(prop);
		}
	}
	
	// Door methods -------------------------------------------
	public List<Door> getDoors() 
	{
		return doors;
	}

	public void setDoors(List<Door> doors) 
	{
		this.doors = doors;
	}

	public void clearDoors()
	{
		doors.clear();
	}
	
	public void addDoor(Door door) 
	{
		doors.add(door);	
	}
	
	public boolean hasDoor(Door door) 
	{
		return doors.contains(door);
	}

	public Door getDoor(String door) 
	{
		for (Door doorElem : doors)
			if (doorElem.getName().equals(door))
				return doorElem;
		return null;
	}
	
	public boolean containsDoor(String door)
	{
		return getDoor(door) != null;
	}	

	public Door getDoorByDeviceName(String doorDeviceName) 
	{
		for(Door doorElem : doors)
			if(doorElem.getDeviceName().equalsIgnoreCase(doorDeviceName))
				return doorElem;
		return null;
	}	
	
	public void initDoors()
	{
		for (Door door : doors) 
		{
			door.init(door.getName());
		}
	}
	// Pools methods ----------------------------------------------

	public List<DevicePool> getPools() {
		return pools;
	}

	public void setPools(List<DevicePool> pools) {
		this.pools = pools;
	}
	
}