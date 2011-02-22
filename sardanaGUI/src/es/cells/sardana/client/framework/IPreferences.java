package es.cells.sardana.client.framework;

public interface IPreferences 
{
	enum PoolPropertySaveLevel 
	{
		never,		// don't save 
		essencial,	// essencial properties (PoolPath)
		exaustive,	// all except those used internally by the pool (ex.: Controller)
		all;		// all bloddy properties (allow save pool state for debugging)
	}

	enum ElementPropertySaveLevel 
	{
		never,						// don't save
		propsWithoutDefaultValue,	// props without default value
		propsWithOverwrittenValue,	// props that don't have dft value or which overwrite the dft value
		all;						// all bloddy properties (allow save pool state for debugging)
	}
	
	enum ElementAttributeSaveLevel
	{
		never,		// don't save
		writable, 	// only writable attributes
		exaustive,	// readable attributes also except State and Status
		all;		// all bloddy attributes (allow save pool state for debugging)
	}
	
	abstract String getTangoHostName();
	abstract String getTangoHostPort();
	
	abstract String getPoolFilter();
	
	abstract boolean supportsPseudoMotors();
	
	abstract boolean hideInternalMotorGroups();
	
	abstract PoolPropertySaveLevel getPoolPropSaveLevel(); 

	abstract ElementPropertySaveLevel getControllerPropSaveLevel();
	abstract ElementPropertySaveLevel getPseudoMotorPropSaveLevel();
	
	abstract ElementAttributeSaveLevel getMotorAttributeSaveLevel();
	abstract ElementAttributeSaveLevel getChannelAttributeSaveLevel();
}
