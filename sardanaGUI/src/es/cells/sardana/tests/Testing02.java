package es.cells.sardana.tests;

import java.awt.GridLayout;

import javax.swing.JFrame;

import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceFactory;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;
import fr.esrf.tangoatk.widget.attribute.StateViewer;

public class Testing02 extends JFrame
{
	
	public Testing02()
	{
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		System.setProperty("TANGO_HOST", "controls01:10000");

		Device 
			device1 = null, 
			device2 = null, 
			device3 = null, 
			device4 = null,
			device5 = null;
		
		try
		{
			device1 = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool01");
			device2 = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool02");
			device3 = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool03");
			device4 = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool04");
			device5 = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool05");
		}
		catch (ConnectionException e)
		{
			System.out.println("At least one device has errors");
			System.exit(0);
		}
		
		AttributeList attrList = new AttributeList();
		
		DevStateScalar 
			state1 = null,
			state2 = null,
			state3 = null,
			state4 = null,
			state5 = null;
		try
		{
			state1 = (DevStateScalar) attrList.add(device1.getName() + "/" + "State");
			state2 = (DevStateScalar) attrList.add(device2.getName() + "/" + "State");
			state3 = (DevStateScalar) attrList.add(device3.getName() + "/" + "State");
			state4 = (DevStateScalar) attrList.add(device4.getName() + "/" + "State");
			state5 = (DevStateScalar) attrList.add(device5.getName() + "/" + "State");
		}
		catch (ConnectionException e)
		{
			System.out.println("At least one device is not available\nExiting...");
			System.exit(0);
		}
		
		state1.addDevStateScalarListener( new DListener() );
		state2.addDevStateScalarListener( new DListener() );
		state3.addDevStateScalarListener( new DListener() );
		state4.addDevStateScalarListener( new DListener() );
		state5.addDevStateScalarListener( new DListener() );
		
		getContentPane().setLayout( new GridLayout(5,1,2,2) );
				
		StateViewer v1 = new StateViewer();
		v1.setModel(state1);
		
		StateViewer v2 = new StateViewer();
		v2.setModel(state2);

		StateViewer v3 = new StateViewer();
		v3.setModel(state3);

		StateViewer v4 = new StateViewer();
		v4.setModel(state4);

		StateViewer v5 = new StateViewer();
		v5.setModel(state5);

		getContentPane().add(v1);
		getContentPane().add(v2);
		getContentPane().add(v3);
		getContentPane().add(v4);
		getContentPane().add(v5);
		
		pack();
		setVisible(true);
	}
	
	public static void main(String[] args)
	{
		new Testing02();
	}
	
	public class DListener implements IDevStateScalarListener
	{

		public void devStateScalarChange(DevStateScalarEvent e)
		{
			System.out.println("Device state event received for " + e.getSource() + " with value " + e.getValue());
		}

		public void stateChange(AttributeStateEvent e)
		{
			//System.out.println("Attribute state event received for " + e.getSource() + " with state " + e.getState());
		}

		public void errorChange(ErrorEvent e)
		{
			//System.out.println("Error state event received for " + e.getSource() + " with state " + e.toString());
		}
		
	}
}
