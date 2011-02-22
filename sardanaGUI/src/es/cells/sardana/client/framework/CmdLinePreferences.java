package es.cells.sardana.client.framework;

public class CmdLinePreferences extends DefaultPreferences
{
	String hostname;
	String port;
	String poolFilter;
	
	public CmdLinePreferences(String[] args) 
	{
		if(args.length == 0)
			poolFilter = ".*";
		else
			poolFilter = args[0];
		
		if (!poolFilter.endsWith("*"))
			poolFilter += '*';
		
		String tango_host = args.length == 2 ? 
			args[1] :
			System.getenv("TANGO_HOST");
		
		String[] elems = tango_host.split(":");
		
		hostname = elems[0].trim();
		port = elems[1].trim();
		
	}

	public String getTangoHostName() 
	{
		return hostname;
	}

	public String getTangoHostPort() 
	{
		return port;
	}

	public boolean supportsPseudoMotors() 
	{
		return true;
	}

	public String getPoolFilter() 
	{
		return poolFilter;
	}

	public boolean hideInternalMotorGroups() 
	{
		return false;
	}
}
