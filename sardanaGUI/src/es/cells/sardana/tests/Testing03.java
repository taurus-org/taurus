package es.cells.sardana.tests;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JFrame;

import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceFactory;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class Testing03 extends JFrame
{
	IStringSpectrum motorListAttr = null;
	
	public Testing03()
	{
		setTitle("Testing 3");
		
		System.setProperty("TANGO_HOST", "controls01:10000");
		
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		Device device;
		try
		{
			device = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool01");
		}
		catch (ConnectionException e)
		{
			e.printStackTrace();
			return;
		}
		
		AttributeList attrList = new AttributeList();
		
		try 
		{
			motorListAttr = (IStringSpectrum) attrList.add(device.getName() + "/MotorList" );
			try {
				Thread.sleep(20);
			} catch (InterruptedException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
			motorListAttr.addListener(new MotorListListener());
		} 
		catch (ConnectionException e1) 
		{
			System.out.println("Failed to set MotorList attribute");
			e1.printStackTrace();
			System.exit(-1);
		}
		
		JButton button = new JButton("Add motor list listener...");
		
		button.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e)
			{
				motorListAttr.addListener(new MotorListListener());
			}
			
		});
		
		getContentPane().add(button);
				
		pack();
		setVisible(true);
		
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		new Testing03();
	}

	static int gid = 0;
	
	class MotorListListener implements IStringSpectrumListener
	{
		int id;
		
		public MotorListListener()
		{
			id = gid++;
		}
		
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			System.out.print("MotorList changed (" + id + "):\n\t");
			for(String elem : e.getValue())
				System.out.print(elem + ", ");
			System.out.println();
		}

		public void stateChange(AttributeStateEvent arg0) {}
		public void errorChange(ErrorEvent arg0) {}
		
	}
}
