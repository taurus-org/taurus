package es.cells.sardana.client.framework;

import es.cells.sardana.client.framework.IPreferences.ElementAttributeSaveLevel;
import es.cells.sardana.client.framework.IPreferences.ElementPropertySaveLevel;
import es.cells.sardana.client.framework.IPreferences.PoolPropertySaveLevel;


public class Preferences 
{
	private String tangoHostName;
	private String tangoHostPort;
	private String sardanaFilter;
	private boolean hideInternalMotorGroups;
	private PoolPropertySaveLevel poolPropSaveLevel;
	private ElementPropertySaveLevel controllerPropSaveLevel;
	private ElementPropertySaveLevel pseudoMotorPropSaveLevel;
	private ElementAttributeSaveLevel motorAttrSaveLevel;
	private ElementAttributeSaveLevel channelAttrSaveLevel;

	public Preferences(IPreferences prefs)
	{
		tangoHostName = prefs.getTangoHostName();
		tangoHostPort = prefs.getTangoHostPort();
		sardanaFilter = prefs.getPoolFilter();
		hideInternalMotorGroups = prefs.hideInternalMotorGroups();
		poolPropSaveLevel = prefs.getPoolPropSaveLevel();
		controllerPropSaveLevel = prefs.getControllerPropSaveLevel();
		pseudoMotorPropSaveLevel = prefs.getPseudoMotorPropSaveLevel();
		motorAttrSaveLevel = prefs.getMotorAttributeSaveLevel();
		channelAttrSaveLevel = prefs.getChannelAttributeSaveLevel();
	}

	public String getTangoHostName() {
		return tangoHostName;
	}

	public void setTangoHostName(String tangoHostName) {
		this.tangoHostName = tangoHostName;
	}

	public String getTangoHostPort() {
		return tangoHostPort;
	}

	public void setTangoHostPort(String tangoHostPort) {
		this.tangoHostPort = tangoHostPort;
	}

	public String getSardanaFilter() {
		return sardanaFilter;
	}

	public void setSardanaFilter(String poolFilter) {
		this.sardanaFilter = poolFilter;
	}

	public boolean isHideInternalMotorGroups() {
		return hideInternalMotorGroups;
	}

	public void setHideInternalMotorGroups(boolean hideInternalMotorGroups) {
		this.hideInternalMotorGroups = hideInternalMotorGroups;
	}

	public PoolPropertySaveLevel getPoolPropSaveLevel() {
		return poolPropSaveLevel;
	}

	public void setPoolPropSaveLevel(PoolPropertySaveLevel poolPropSaveLevel) {
		this.poolPropSaveLevel = poolPropSaveLevel;
	}

	public ElementPropertySaveLevel getControllerPropSaveLevel() {
		return controllerPropSaveLevel;
	}

	public void setControllerPropSaveLevel(
			ElementPropertySaveLevel controllerPropSaveLevel) {
		this.controllerPropSaveLevel = controllerPropSaveLevel;
	}

	public ElementPropertySaveLevel getPseudoMotorPropSaveLevel() {
		return pseudoMotorPropSaveLevel;
	}

	public void setPseudoMotorPropSaveLevel(
			ElementPropertySaveLevel pseudoMotorPropSaveLevel) {
		this.pseudoMotorPropSaveLevel = pseudoMotorPropSaveLevel;
	}

	public ElementAttributeSaveLevel getMotorAttrSaveLevel() {
		return motorAttrSaveLevel;
	}

	public void setMotorAttrSaveLevel(ElementAttributeSaveLevel motorAttrSaveLevel) {
		this.motorAttrSaveLevel = motorAttrSaveLevel;
	}

	public ElementAttributeSaveLevel getChannelAttrSaveLevel() {
		return channelAttrSaveLevel;
	}

	public void setChannelAttrSaveLevel(
			ElementAttributeSaveLevel channelAttrSaveLevel) {
		this.channelAttrSaveLevel = channelAttrSaveLevel;
	}
	
	
}
