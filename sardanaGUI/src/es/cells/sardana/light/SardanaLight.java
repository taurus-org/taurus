package es.cells.sardana.light;

import java.awt.BorderLayout;
import java.awt.Container;

import javax.swing.JFrame;
import javax.swing.JTabbedPane;

import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceFactory;

public class SardanaLight extends JFrame {

	Device pool;
	String poolDeviceName;

	JTabbedPane folderPanel;
	MotorPanel motorPanel;
	DataAquisitionPanel aqPanel;
	
	public SardanaLight(String poolDeviceName) 
	{
		super("Sardana Light");
		
		this.poolDeviceName = poolDeviceName;
		
		try 
		{
			pool = DeviceFactory.getInstance().getDevice(poolDeviceName);
		} 
		catch (ConnectionException e) 
		{
			e.printStackTrace();
			System.exit(-1);
		}
		
		initComponents();
	}

	private void initComponents() 
	{
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
		Container c = getContentPane();
		
		c.setLayout(new BorderLayout());
		
		folderPanel = new JTabbedPane();
		
		motorPanel = new MotorPanel(pool);
		aqPanel = new DataAquisitionPanel(pool);
		
		folderPanel.add("Motors",motorPanel);
		folderPanel.add("Data Aquisition", aqPanel);
		
		c.add(folderPanel, BorderLayout.CENTER);
		
		folderPanel.setSelectedIndex(1);
		pack();
		setVisible(true);
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		new SardanaLight(args[0]);
	}

}
