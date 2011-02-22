package es.cells.sardana.client.framework.macroserver;

import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;


public class Door extends SardanaDevice {

	MacroServer macroServer;
	
	DoorStateListener stateListener;
	
	public Door(Machine machine, String name) 
	{
		super(machine, name);
	}
	
	public void init(String deviceName)
	{
		try 
		{
			super.init(deviceName);
		}
		catch (ConnectionException e) 
		{

		}
	}
	
	public Device getDevice()
	{
		return super.getDevice();
	}

	public void setMacroServer(MacroServer macroServer) 
	{
		this.macroServer = macroServer;
	}

	public MacroServer getMacroServer() {
		return macroServer;
	}

	public DoorStateListener getStateListener() {
		return stateListener;
	}

	public void setStateListener(DoorStateListener stateListener) {
		this.stateListener = stateListener;
	}
	
	
	
}
