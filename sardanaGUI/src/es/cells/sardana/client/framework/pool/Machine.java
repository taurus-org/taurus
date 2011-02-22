package es.cells.sardana.client.framework.pool;

import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.Database;


public class Machine
{
	String hostName;
	String hostPort;

	Database dataBase;
	
	public Machine(String hostName, String hostPort) 
	{
		this.hostName = hostName;
		this.hostPort = hostPort;
		
		try 
		{
			dataBase = new Database(hostName, hostPort);
		} 
		catch (DevFailed e)	{}
	}

	@Override
	public String toString() 
	{
		return hostName + ":" + hostPort;
	}

	public Database getDataBase() {
		return dataBase;
	}

	public void setDataBase(Database dataBase) {
		this.dataBase = dataBase;
	}
	

	
}
