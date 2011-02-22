package es.cells.sardana.client.framework;


public class DefaultPreferences implements IPreferences 
{
	public static final PoolPropertySaveLevel DFT_PROP_SAVE_LEVEL = PoolPropertySaveLevel.essencial;
	public static final ElementPropertySaveLevel DFT_CTRL_PROP_SAVE_LEVEL = ElementPropertySaveLevel.all;
	public static final ElementPropertySaveLevel DFT_PSEUDO_MOTOR_PROP_SAVE_LEVEL = ElementPropertySaveLevel.all;
	public static final ElementAttributeSaveLevel DFT_MOTOR_ATTR_SAVE_LEVEL = ElementAttributeSaveLevel.exaustive;
	public static final ElementAttributeSaveLevel DFT_CHANNEL_ATTR_SAVE_LEVEL = ElementAttributeSaveLevel.exaustive;

	public String getTangoHostName() 
	{
		String hostName = System.getenv().get("TANGO_HOST");
		String[] parts = hostName.split(":");
		if(parts.length == 2)
			return parts[0];
		else
			return new String("127.0.0.1");
	}

	public String getTangoHostPort() 
	{
		String text = System.getenv().get("TANGO_HOST");
		String[] parts = text.split(":");
		if(parts.length == 2)
			return parts[1];
		else
			return new String("10000");
	}

	public boolean supportsPseudoMotors() 
	{
		return true;
	}

	public String getPoolFilter() 
	{
		return ".*";
	}

	public boolean hideInternalMotorGroups() 
	{
		return false;
	}
	
	public PoolPropertySaveLevel getPoolPropSaveLevel()
	{
		return DFT_PROP_SAVE_LEVEL;
	}

	public ElementPropertySaveLevel getControllerPropSaveLevel()
	{
		return DFT_CTRL_PROP_SAVE_LEVEL;
	}

	public ElementPropertySaveLevel getPseudoMotorPropSaveLevel() 
	{
		return DFT_PSEUDO_MOTOR_PROP_SAVE_LEVEL;
	}

	public ElementAttributeSaveLevel getMotorAttributeSaveLevel() 
	{
		return DFT_MOTOR_ATTR_SAVE_LEVEL;
	}

	public ElementAttributeSaveLevel getChannelAttributeSaveLevel() 
	{
		return DFT_CHANNEL_ATTR_SAVE_LEVEL;
	}
}
