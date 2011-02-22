package es.cells.sardana.client.gui.swing;

import java.awt.Color;

import javax.swing.ImageIcon;

import es.cells.sardana.client.framework.SardanaManager;
import fr.esrf.tangoatk.widget.util.Splash;

public class SardanaApplication {

	protected static SardanaApplication instance = null;
	
	protected LogHandler logHandler;
	
	ImageIcon splashIcon = new ImageIcon("res/splash.jpg");
	
	SardanaFrame sardanaFrame;
	
	Splash splashScreen;
	
	public SardanaApplication(String[] args) 
	{
		// COMMENT TO REMOVE SPLASH SCREEN
		//setupSplashScreen();
		
		logHandler = new LogHandler(null);
		
		// It is imperative this is called first!!
		progress(1,"Aquiring data from Database and Device Pools...");
		
		SardanaManager.getInstance(args).init( logHandler );
		progress(4, "");
		
	}

	protected void progress(int v, String msg)
	{
		if(splashScreen != null)
		{
			splashScreen.setMessage(msg);
			splashScreen.progress(v);
		}
	}
	
	protected void setupSplashScreen()
	{
		splashScreen = new Splash(splashIcon,Color.black);
		splashScreen.setMaxProgress(10);
		splashScreen.setTitle("Sardana");
		splashScreen.setCopyright("(c) 2007 ALBA - CELLS");
		splashScreen.setVisible(true);
		splashScreen.setMessage("Building log system..");
		splashScreen.initProgress();
		splashScreen.setAlwaysOnTop(false);
	}
	
	public static SardanaApplication getInstance()
	{
		return getInstance(null);
	}
	
	public static SardanaApplication getInstance(String[] args)
	{
		if(instance == null)
			instance = new SardanaApplication(args);
		return instance;
	}
	
	public LogHandler getLogHandler()
	{
		return logHandler;
	}

	public void go()
	{
		sardanaFrame = new SardanaFrame(splashScreen);
		
		if(splashScreen != null)
			splashScreen.setVisible(false);
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		SardanaApplication.getInstance(args).go();
	}

}
