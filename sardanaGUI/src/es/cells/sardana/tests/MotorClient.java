package es.cells.sardana.tests;

import java.awt.Container;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;

import javax.swing.JFrame;
import javax.swing.JLabel;

import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MotorClient extends JFrame
{
	Device device;
	AttributeList attrList;
	
	JLabel[] stateLabel;
	JLabel[] positionLabel;
	
	public MotorClient(String[] motorDeviceNames)
	{
		super("Motor Viewer");

		initComponents(motorDeviceNames);
		initAttributes(motorDeviceNames);
		
	}

	private void initComponents(String[] motorDeviceNames)
	{
		int len = motorDeviceNames.length;
		
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
		Container c = getContentPane();
		c.setLayout(new GridBagLayout());
		
		stateLabel = new JLabel[len];
		positionLabel = new JLabel[len];
		
		for(int i = 0; i < len; i++)
		{
			GridBagConstraints gbc = new GridBagConstraints(
					0, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.EAST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(2,2,2,2),
					0,0 // pad
					);
			
			JLabel stateNameLabel = new JLabel("Device State: "); 
			stateNameLabel.setToolTipText(motorDeviceNames[i]);
			c.add(stateNameLabel, gbc);

			gbc = new GridBagConstraints(
					1, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(2,2,2,2),
					0,0 // pad
					);
			
			stateLabel[i] = new JLabel("not set");
			c.add(stateLabel[i],gbc);
			
			gbc = new GridBagConstraints(
					2, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.EAST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(2,2,2,2),
					0,0 // pad
					);			
			
			JLabel positionNameLabel = new JLabel("Motor position: ");
			positionNameLabel.setToolTipText(motorDeviceNames[i]);
			c.add(positionNameLabel,gbc);
			
			gbc = new GridBagConstraints(
					3, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(2,2,2,2),
					0,0 // pad
					);				
			
			positionLabel[i] = new JLabel("not set");
			c.add(positionLabel[i],gbc);
		}
		pack();
		setVisible(true);
	}
	
	protected void initAttributes(String[] motorDeviceNames)
	{
		int len = motorDeviceNames.length;
		
		attrList = new AttributeList();
		
		for(int i = 0; i < len; i++)
		{
			DevStateScalar state = null;
			try
			{   
				state = (DevStateScalar) attrList.add(motorDeviceNames[i] + "/state");
			}
			catch (Exception e)
			{
				device = null;
				System.out.println("Error creating state attribute for " + motorDeviceNames[i]);
				System.exit(-1);
			}
			
			MotorStateScalarListener stateListener = new MotorStateScalarListener(stateLabel[i]);
			state.addDevStateScalarListener(stateListener);
					
			INumberScalar positionAttr = null;
			try
			{
				//INumberScalar positionAttr = (INumberScalar) AttributeFactory.getInstance().getAttribute("motor/dummyctrl01/1/Velocity");
				positionAttr = (INumberScalar) attrList.add(motorDeviceNames[i] + "/position");
			}
			catch (Exception e)
			{
				device = null;
				System.out.println("Error creating position attribute. Exiting...");
				System.exit(-1);
			}
			
			
			MotorPositionListener positionListener = new MotorPositionListener(positionLabel[i]);
			positionAttr.addNumberScalarListener(positionListener);
		}
		
		// No need to start the refresher because these are event attributes
		// Starting the refresher would have no impact whatsoever.
		//attrList.startRefresher();
		
	}

	class MotorPositionListener implements INumberScalarListener
	{
		JLabel positionLabel;
		
		public MotorPositionListener(JLabel positionLabel)
		{
			this.positionLabel = positionLabel;
		}
		
		public void numberScalarChange(NumberScalarEvent evt)
		{
			//System.out.println("\t[POSITION event] Changed to " + evt.getValue());
			positionLabel.setText("" + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt)
		{
			//System.out.println("\t[POSITION event] Quality to " + evt.getState());
			positionLabel.setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt)
		{
			//System.out.println("\t\t[POSITION event] Error: " + evt.toString());
		}
	}
	
	class MotorStateScalarListener implements IDevStateScalarListener 
	{
		JLabel stateLabel;
		
		public MotorStateScalarListener(JLabel stateLabel)
		{
			this.stateLabel = stateLabel;
		}
		
		public void stateChange(AttributeStateEvent evt) 
		{
			//System.out.println("\t[STATE event] Quality to " + evt.getState());
		}

		public void devStateScalarChange(DevStateScalarEvent evt)
		{
			//System.out.println("\t[STATE event] Changed to " + evt.getValue());
			stateLabel.setText(evt.getValue());
			stateLabel.setForeground(ATKConstant.getColor4State(evt.getValue()));
		}
		
		public void errorChange(ErrorEvent evt) 
		{
			//System.out.println("\t\t[STATE event] Error: " + evt.toString());
		}
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		new MotorClient(args);
	}

}
