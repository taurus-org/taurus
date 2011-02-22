package es.cells.sardana.light;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;

import es.cells.sardana.light.model.Motor;
import es.cells.sardana.light.model.MotorGroup;
import es.cells.sardana.light.model.MovElement;
import es.cells.sardana.light.model.PseudoMotor;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;

public class MotorPanel extends JPanel
{
	Device pool;
	
	HashMap<String, MovElement> movElements = new HashMap<String, MovElement>();
	ArrayList<MovElement> movElementArray = new ArrayList<MovElement>();
	ArrayList<Motor> motorDeviceNames = new ArrayList<Motor>();
	ArrayList<MotorGroup> motorGroupDeviceNames = new ArrayList<MotorGroup>();
	ArrayList<PseudoMotor> pseudoMotorDeviceNames = new ArrayList<PseudoMotor>();
	
	AttributeList stateAttributes;
	AttributeList positionAttributes;
	
	public MotorPanel(Device devicePool) 
	{
		super();
		
		this.pool = devicePool;
		
		try 
		{
			DeviceAttribute motor_list_attr = pool.read_attribute("MotorList");
			DeviceAttribute motor_group_list_attr = pool.read_attribute("MotorGroupList");
			DeviceAttribute pseudo_motor_list_attr = pool.read_attribute("PseudoMotorList");
			
			String[] full_motor_list = motor_list_attr.extractStringArray();
			String[] full_motor_group_list = motor_group_list_attr.extractStringArray();
			String[] full_pseudo_motor_list = pseudo_motor_list_attr.extractStringArray();
			
			for(String full_motor : full_motor_list)
			{
				int start = full_motor.indexOf("(");
				int end = full_motor.indexOf(")");
				String motorAlias = full_motor.substring(0, start).trim();
				String motorDeviceName = full_motor.substring(start+1,end);
								
				Motor m = new Motor(motorAlias, motorDeviceName);
				motorDeviceNames.add(m);
				movElements.put(motorAlias,m);
				movElementArray.add(m);
			}
			
			for(String full_pseudo_motor : full_pseudo_motor_list)
			{
				int start = full_pseudo_motor.indexOf("(");
				int end = full_pseudo_motor.indexOf(")");
				String pseudoMotorAlias = full_pseudo_motor.substring(0, start).trim();
				String pseudoMotorDeviceName = full_pseudo_motor.substring(start+1, end);
				
				PseudoMotor pm = new PseudoMotor(pseudoMotorAlias,pseudoMotorDeviceName);
				pseudoMotorDeviceNames.add(pm);
				movElements.put(pseudoMotorAlias,pm);
				movElementArray.add(pm);
			}
			
			final String motorListStr = "Motor list:";
			for(String full_motor_group : full_motor_group_list)
			{
				int start = full_motor_group.indexOf("(");
				int end = full_motor_group.indexOf(")");
				String motorGroupAlias = full_motor_group.substring(0, start).trim();
				String motorGroupDeviceName = full_motor_group.substring(start+1,end);
				
				//if(motorGroupAlias.startsWith("_pm"))
				//	continue;
				
				String tmp = full_motor_group.substring(end+1);
				start = tmp.indexOf(motorListStr);
				start += motorListStr.length() + 1;
				end = tmp.indexOf('(');
				
				if(end >=0)
					tmp = tmp.substring(start,end);
				else
					tmp = tmp.substring(start);
				
				String user_elems[] = tmp.split(",");
				
				int positionSize = 0;
				
				for(int i=0; i < user_elems.length; i++)
				{
					user_elems[i] = user_elems[i].trim();
					
					MovElement elem = movElements.get(user_elems[i]);
					
					positionSize += elem.positionSize;
				}
				
				MotorGroup mg = new MotorGroup(motorGroupAlias, motorGroupDeviceName, user_elems, positionSize);
				motorGroupDeviceNames.add(mg);
				movElements.put(motorGroupAlias,mg);
				movElementArray.add(mg);
			}			
		} 
		catch (DevFailed e) 
		{
			e.printStackTrace();
			System.exit(-2);
		}
		
		initComponents();
		initAttributes();
	}
	
	private void initAttributes()
	{
		stateAttributes = new AttributeList();
		positionAttributes = new AttributeList();
		
		for(int i = 0; i < movElementArray.size(); i++)
		{
			MovElement m = movElementArray.get(i);
			
			try
			{   
				DevStateScalar state = (DevStateScalar) stateAttributes.add(m.deviceName + "/state");
				state.addDevStateScalarListener(m.stateListener);
			}
			catch (Exception e)
			{
				System.out.println("Error creating state attribute for " + m.deviceName);
				System.exit(-3);
			}
					
			try
			{
				//INumberScalar positionAttr = (INumberScalar) AttributeFactory.getInstance().getAttribute("motor/dummyctrl01/1/Velocity");
				IEntity entity = positionAttributes.add(m.deviceName + "/position");
				
				if(entity instanceof INumberScalar)
				{
					INumberScalar positionAttr = (INumberScalar)entity;
					positionAttr.addNumberScalarListener(m.positionListener);
				}
				else
				{
					INumberSpectrum positionAttr = (INumberSpectrum)entity;
					positionAttr.addSpectrumListener(m.positionArrayListener);
				}
				m.positionAttribute = entity;
			}
			catch (Exception e)
			{
				System.out.println("Error creating position attribute. Exiting...");
				System.exit(-4);
			}
		}
	}

	private void initComponents() 
	{
		setLayout(new BorderLayout());
		
		add(createElementPanel(), BorderLayout.CENTER);
		//add(createMotorGroupPanel());
		//add(createPseudoMotorPanel());
		
		add(createButtonsPanel(), BorderLayout.SOUTH);
		
		
	}

	private JPanel createButtonsPanel()
	{
		JPanel ret = new JPanel(new FlowLayout(FlowLayout.RIGHT));
		
		JButton clearEvents = new JButton("Clear events");
		
		clearEvents.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				for(MovElement el : movElements.values())
				{
					el.positionEventCount = 0;
					el.positionEventCountLabel.setText("0");
				}
			}
		});
		
		
		ret.add(clearEvents);
		
		
		return ret;
	}

	private JPanel createElementPanel()
	{
		JPanel ret = new JPanel();
		
		ret.setLayout(new BoxLayout(ret, BoxLayout.Y_AXIS));
		
		for(int i = 0; i < movElementArray.size(); i++)
		{
			MovElement m = movElementArray.get(i);
			
			ret.add(m.elementPanel);
		}
			
		return ret;
	}
	
	private JPanel createElementPanelOld() 
	{
		JPanel ret = new JPanel(new GridBagLayout());
	
		for(int i = 0; i < movElementArray.size(); i++)
		{
			MovElement m = movElementArray.get(i);
		
			//int height = m.positionSize;
			
			GridBagConstraints gbc = new GridBagConstraints(
					0, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.EAST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			
			JLabel stateNameLabel = new JLabel(m.name + " State: "); 
			stateNameLabel.setToolTipText(m.name);
			ret.add(stateNameLabel, gbc);

			gbc = new GridBagConstraints(
					1, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			
			ret.add(m.stateLabel,gbc);
			
			if(m.positionSize == 1)
			{
				gbc = new GridBagConstraints(
						2, i, // grid
						1, 1, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.EAST, // anchor
						GridBagConstraints.HORIZONTAL,
						new Insets(4,2,4,2),
						0,0 // pad
						);		
			
				JLabel positionNameLabel = new JLabel(" position: ");
				positionNameLabel.setToolTipText(m.name);
				ret.add(positionNameLabel,gbc);
				
				gbc = new GridBagConstraints(
						3, i, // grid
						1, 1, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.EAST, // anchor
						GridBagConstraints.HORIZONTAL,
						new Insets(4,2,4,2),
						0,0 // pad
						);				
	
				ret.add(m.positionLabel[0],gbc);
				
				gbc = new GridBagConstraints(
						4, i, // grid
						1, 1, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.WEST, // anchor
						GridBagConstraints.HORIZONTAL,
						new Insets(4,2,4,2),
						0,0 // pad
						);				
				
				ret.add(m.positionSpinner[0],gbc);

				gbc = new GridBagConstraints(
						5, i, // grid
						1, 1, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.CENTER, // anchor
						GridBagConstraints.BOTH,
						new Insets(4,2,4,2),
						0,0 // pad
						);
				ret.add(m.copyPositionButton[0],gbc);
				
				gbc = new GridBagConstraints(
						6, i, // grid
						1, 1, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.CENTER, // anchor
						GridBagConstraints.BOTH,
						new Insets(4,2,4,2),
						0,0 // pad
						);				
				
				ret.add(m.applyPositionButton,gbc);

			}
			else
			{
				JPanel p = new JPanel(new GridBagLayout());
				
				for(int pos = 0; pos < m.positionSize; pos++)
				{
					gbc = new GridBagConstraints(
							0, pos, // grid
							1, 1, // width,height
							0.0, 0.0, // weight
							GridBagConstraints.EAST, // anchor
							GridBagConstraints.HORIZONTAL,
							new Insets(4,2,4,2),
							0,0 // pad
							);	
					
					JLabel positionNameLabel = new JLabel(m.name + " position #" + pos + ": ");
					p.add(positionNameLabel, gbc);
					
					gbc = new GridBagConstraints(
							1, pos, // grid
							1, 1, // width,height
							0.0, 0.0, // weight
							GridBagConstraints.EAST, // anchor
							GridBagConstraints.HORIZONTAL,
							new Insets(4,2,4,2),
							0,0 // pad
							);
					p.add(m.positionLabel[pos],gbc);
					
					gbc = new GridBagConstraints(
							2, pos, // grid
							1, 1, // width,height
							0.0, 0.0, // weight
							GridBagConstraints.WEST, // anchor
							GridBagConstraints.HORIZONTAL,
							new Insets(4,2,4,2),
							0,0 // pad
							);
					p.add(m.positionSpinner[pos],gbc);
					
					gbc = new GridBagConstraints(
							3, pos, // grid
							1, 1, // width,height
							0.0, 0.0, // weight
							GridBagConstraints.CENTER, // anchor
							GridBagConstraints.BOTH,
							new Insets(4,2,4,2),
							0,0 // pad
							);
					p.add(m.copyPositionButton[pos],gbc);
				}
				
				gbc = new GridBagConstraints(
						4, 0, // grid
						1, m.positionSize, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.CENTER, // anchor
						GridBagConstraints.BOTH,
						new Insets(4,2,4,2),
						0,0 // pad
						);
				p.add(m.applyPositionButton,gbc);
				
				gbc = new GridBagConstraints(
						2, i, // grid
						5, 1, // width,height
						0.0, 0.0, // weight
						GridBagConstraints.EAST, // anchor
						GridBagConstraints.HORIZONTAL,
						new Insets(0,0,0,0),
						0,0 // pad
						);
				ret.add(p,gbc);
			}
			
			gbc = new GridBagConstraints(
					7, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.CENTER, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			
			ret.add(m.abortCommand,gbc);
			
			JLabel eventLabel = new JLabel("pos event #:");
			ret.add(eventLabel,gbc);
			
			gbc = new GridBagConstraints(
					8, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);				

			ret.add(eventLabel,gbc);
			
			gbc = new GridBagConstraints(
					9, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.CENTER, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);			
			
			ret.add(m.positionEventCountLabel,gbc);
			
		}	
		return ret;
	}
}
