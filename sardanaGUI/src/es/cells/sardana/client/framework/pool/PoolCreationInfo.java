package es.cells.sardana.client.framework.pool;

public class PoolCreationInfo 
{
	
	public static final String serverName = "Pool";
	
	Machine machine;
	String instanceName;
	String pooldeviceName;
	String aliasName;
	String version;
	
	String[] poolPath;

	public String getInstanceName() {
		return instanceName;
	}

	public void setInstanceName(String instanceName) {
		this.instanceName = instanceName;
	}

	public String getAliasName() {
		return aliasName;
	}

	public void setAliasName(String aliasName) {
		this.aliasName = aliasName;
	}
	
	public String getVersion() {
		return version;
	}

	public void setVersion(String version) {
		this.version = version;
	}
	

	public String[] getPoolPath() {
		return poolPath;
	}

	public void setPoolPath(String[] poolPath) {
		this.poolPath = poolPath;
	}

	public String getPooldeviceName() {
		return pooldeviceName;
	}

	public void setPooldeviceName(String pooldeviceName) {
		this.pooldeviceName = pooldeviceName;
	}

	public void setPoolPath(Object[] elements) 
	{
		if(elements == null)
			return;
		poolPath = new String[elements.length];
		
		for(int i = 0 ; i < elements.length ; i++)
			poolPath[i] = elements[i].toString();
	}

	public Machine getMachine() {
		return machine;
	}

	public void setMachine(Machine machine) {
		this.machine = machine;
	}
	
	
}
