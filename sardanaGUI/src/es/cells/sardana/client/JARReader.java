package es.cells.sardana.client;

import java.io.IOException;
import java.util.EventListener;
import java.util.jar.Attributes;
import java.util.jar.JarFile;
import java.util.jar.Manifest;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class JARReader
{

	public static void main(String[] args)
	{
		
		patternMatcher();
	}
	
	public static void patternMatcher()
	{
		final String str = "Class: DummyController - File: /home/tcoutinho/ctrl/DummyCtrl.so";
		
		final String patternStr = "Class:\\s*(\\w+)\\s*-\\s*File:\\s*(.+)(.*)";
		
		final Pattern pattern = Pattern.compile(patternStr);
		
		Matcher m = pattern.matcher(str);
		
		System.out.println("Matches? " + m.matches());
		System.out.println("Group #" + m.groupCount());
		
		for(int i = 0; i < m.groupCount(); i++)
			System.out.println("#"+i + ":" + m.group(i));
	}
	
	public static void readJar(String[] args)
	{
		if(args.length != 1)
		{
			System.out.println("args: <jar filename>" );
			return;
		}
		
		try
		{
			JarFile jarFile = new JarFile(args[0]);
			Manifest manifest = jarFile.getManifest();
			
			if(manifest == null)
			{
				System.out.println("jar file " + args[0] + " does not contain a Manifest" );
				return;
			}
			
			Attributes attrs = manifest.getMainAttributes();
			for(Object attrName : attrs.keySet())
			{
				System.out.println(attrName + ": " + attrs.get(attrName));
			}
		}
		catch (IOException e)
		{
			System.out.println("jar file " + args[1] + " not found" );
			return;
		}

	}

	public class E implements EventListener
	{
		
	}
}
