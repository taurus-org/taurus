package es.cells.sardana.client.framework;

import java.io.IOException;
import java.net.JarURLConnection;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.jar.Attributes;

import es.cells.sardana.client.igui.IGUIPlugin;

public class PluginLoader extends URLClassLoader 
{
	private static final String MANIFEST_CLASS_PROPERTY = "Sardana-GUIPlugin-Class";
	
	private URL url;
	private String pluginClassName;
	private boolean valid;
	
	public PluginLoader(URL url) 
	{
		super(new URL[] { url });
		this.url = url;
		this.valid = false;
		this.pluginClassName = null;
		
		try 
		{
			pluginClassName = buildClassName();
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
		
		valid = assertValid();
	}
	
	private boolean assertValid() 
	{
		if(pluginClassName == null) 
			return false;
		
		Class c;
		try {
			c = loadClass(pluginClassName);
		}
		catch(ClassNotFoundException e) {
			return false;
		}
		catch(NoClassDefFoundError e) {
			return false;
		}
		catch(Exception e) {
			return false;
		}
		
		Class[] interfaces = c.getInterfaces();
		
		for(int i = 0; i < interfaces.length; i++) 
		{
			if(interfaces[i].equals(IGUIPlugin.class)) return true;
		}
		return false;		
	}

	public String getPluginClassName() {
		return pluginClassName;
	}
	
	public URL getUrl() {
		return url;
	}
	
	public boolean isValid() {
		return valid;
	}

	protected String buildClassName() throws IOException 
	{
	    URL u = new URL("jar", "", url + "!/");
	    
	    JarURLConnection uc = (JarURLConnection)u.openConnection();
	    
	    Attributes attr = uc.getMainAttributes();
	    
	    return attr != null ? attr.getValue(MANIFEST_CLASS_PROPERTY) : null;
	}
	
	
}
