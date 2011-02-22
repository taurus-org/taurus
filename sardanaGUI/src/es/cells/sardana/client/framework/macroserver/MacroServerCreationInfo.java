package es.cells.sardana.client.framework.macroserver;

import es.cells.sardana.client.framework.pool.Machine;

public class MacroServerCreationInfo 
{
	
	public static final String macroServerServerName = "MacroServer";
	public static final String doorServerName = "Door";
	
	Machine machine;
	String instanceName;
	String msDeviceName;
	String msAliasName;
	String msVersion;
	
	String[] macroPath;
	String[] poolNames;

	String doorName;
	String doorAlias;
	
	public String getInstanceName() {
		return instanceName;
	}

	public void setInstanceName(String instanceName) {
		this.instanceName = instanceName;
	}

	public String getMacroServerAliasName() {
		return msAliasName;
	}

	public void setMacroServerAlias(String aliasName) {
		this.msAliasName = aliasName;
	}

	public String getMsVersion() {
		return msVersion;
	}

	public void setMsVersion(String msVersion) {
		this.msVersion = msVersion;
	}

	public String[] getMacroPath() {
		return macroPath;
	}

	public void setMacroPath(String[] macroPath) {
		this.macroPath = macroPath;
	}

	public String getMacroServerDeviceName() {
		return msDeviceName;
	}

	public void setMacroServerDeviceName(String msDeviceName) {
		this.msDeviceName = msDeviceName;
	}

	public void setMacroPath(Object[] elements) 
	{
		if(elements == null)
			return;
		macroPath = new String[elements.length];
		
		for(int i = 0 ; i < elements.length ; i++)
			macroPath[i] = elements[i].toString();
	}
	
	public String[] getPoolNames() {
		return this.poolNames;
	}
	
	public void setPoolNames(String[] poolNames) {
		this.poolNames = poolNames;
	}
	
	public void setPoolNames(Object[] elements) 
	{
		if(elements == null)
			return;
		this.poolNames = new String[elements.length];
		
		for(int i = 0 ; i < elements.length ; i++)
			this.poolNames[i] = elements[i].toString();
	}
	public Machine getMachine() {
		return machine;
	}

	public void setMachine(Machine machine) {
		this.machine = machine;
	}

	public void setDoorDeviceName(String doorName) {
		this.doorName = doorName;
	}

	public String getDoorDeviceName()
	{
		return this.doorName;
	}

	public void setDoorAlias(String doorAlias) {
		this.doorAlias = doorAlias;
	}
	
	public String getDoorAlias()
	{
		return this.doorAlias;
	}
	
}
