package es.cells.sardana.client.framework.gui.dialog;


import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.ArrayList;

import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.atk.widget.SimuDevicesListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.tree.DevicePoolTreeNode;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.TangoApi.DeviceData;

public class AddSimulatorDialog extends JDialog 
{
	
	private final String [] simuTypes = { new String("Motor"),
										   new String("CounterTimer") };
										   //new String("ZeroDExpChannel"),
										   //new String("OneDExpChannel"),
										   //new String("Communication")}; 
	
	JLabel devicePoolsDropDownLabel = new JLabel("Device pool:");
	JLabel simuTypesDropDownLabel = new JLabel("Simulator type:");
	JLabel instanceNameLabel = new JLabel("Instance name:");
	JLabel sardanaNameLabel = new JLabel("Sardana name:");
	JLabel deviceNameLabel = new JLabel("Device name:");

	JComboBox devicePoolsDropDown;
	JComboBox simuTypesDropDown = new JComboBox(simuTypes);
	
	JTextField instanceNameText = new JTextField(20);
	JTextField deviceNameText = new JTextField(20);
	JTextField sardanaNameText = new JTextField(20);
	
	JCheckBox addControllerCheckBox = new JCheckBox("Automatically add controller to the Pool");
	JCheckBox sardanaNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox devicePoolsAutoCheckBox = new JCheckBox("Automatic");
	
	JButton sardanaNameClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	
	ButtonsPanel buttonsPanel = new ButtonsPanel();
	SimuDevicesListViewer simuDevicesListViewer = new SimuDevicesListViewer();
	
	private JButton createButton = new JButton("Create", SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
	private JButton exitButton = new JButton("Close", SwingResource.smallIconMap.get(IImageResource.IMG_CLOSE));
	
	private DevicePool devicePool;
	private Machine machine;

	public AddSimulatorDialog(Machine machine, DevicePool devicePool) 
	{
		super();
		this.devicePool = devicePool;
		this.machine = machine;
		if(devicePool != null)
			initComponents(true);
		else 
			initComponents(false);
	}

	private void initComponents(boolean fixedPool)
	{
		setTitle("Create Simulator on " + machine);
		setResizable(false);
		setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});
		
		JPanel mainPanel = new JPanel(new GridBagLayout());
		getContentPane().setLayout( new BorderLayout() );
		getContentPane().add(mainPanel, BorderLayout.CENTER);
		getContentPane().add(buttonsPanel, BorderLayout.SOUTH);
		
		devicePoolsDropDownLabel.setLabelFor(devicePoolsDropDown);
		simuTypesDropDownLabel.setLabelFor(simuTypesDropDown);
		instanceNameLabel.setLabelFor(instanceNameText);
		deviceNameLabel.setLabelFor(deviceNameText);
		sardanaNameLabel.setLabelFor(sardanaNameText);
		
		createButton.setToolTipText("Create a new Pool");
		exitButton.setToolTipText("Close window");

		sardanaNameClearButton.setMargin(new Insets(1,1,1,1));
		sardanaNameClearButton.setEnabled(false);
		
		buttonsPanel.addRight(createButton);
		buttonsPanel.addRight(exitButton);
		sardanaNameText.setEditable(false);
		sardanaNameAutoCheckBox.setSelected(true);
		/*
		
		*/
		GridBagConstraints gbc = new GridBagConstraints(
				0,0, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(simuTypesDropDownLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,0, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(simuTypesDropDown, gbc);
		
		gbc = new GridBagConstraints(
				0,1, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(instanceNameLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,1, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(instanceNameText, gbc);
		
		gbc = new GridBagConstraints(
				0,2, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(deviceNameLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,2, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(deviceNameText, gbc);
		
		
		gbc = new GridBagConstraints(
				0,5, // x,y
				4,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);
		mainPanel.add(simuDevicesListViewer, gbc);
		
		gbc = new GridBagConstraints(
				0,6, // x,y
				4,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);
		mainPanel.add(addControllerCheckBox, gbc);
		
		gbc = new GridBagConstraints(
				0,7, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(devicePoolsDropDownLabel, gbc);
		devicePoolsDropDownLabel.setVisible(false);

		refreshDevicePoolsDropDown();
		if(fixedPool)
		{
			devicePoolsDropDown.setSelectedItem(devicePool);
			devicePoolsDropDown.setEnabled(false);
			devicePoolsAutoCheckBox.setSelected(true);
			
			devicePoolsAutoCheckBox.addActionListener(new ActionListener()
			{
				public void actionPerformed(ActionEvent e) 
				{
					if(devicePoolsAutoCheckBox.isSelected())
					{
						devicePoolsDropDown.setSelectedItem(devicePool);
						devicePoolsDropDown.setEnabled(false);
					}
					else
					{
						devicePoolsDropDown.setEnabled(true);
					}
				}
			});
			gbc = new GridBagConstraints(
					2,7, // x,y
					1,1, // width, height
					1.0, 0.0, //weight x,y
					GridBagConstraints.EAST, //anchor
					GridBagConstraints.HORIZONTAL, // fill
					new Insets(2, 2, 2, 2), // insets
					0,0 //pad x,y
					);		
			mainPanel.add(devicePoolsAutoCheckBox, gbc);
			devicePoolsAutoCheckBox.setVisible(false);
		}
		
		gbc = new GridBagConstraints(
				1,7, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(devicePoolsDropDown, gbc);
		devicePoolsDropDown.setVisible(false);
		
		gbc = new GridBagConstraints(
				0,8, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(sardanaNameLabel, gbc);
		sardanaNameLabel.setVisible(false);
		
		gbc = new GridBagConstraints(
				1,8, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(sardanaNameText, gbc);
		sardanaNameText.setVisible(false);
		
		gbc = new GridBagConstraints(
				2,8, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(sardanaNameAutoCheckBox, gbc);
		sardanaNameAutoCheckBox.setVisible(false);
		
		gbc = new GridBagConstraints(
				3,8, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(sardanaNameClearButton, gbc);
		sardanaNameClearButton.setVisible(false);		
		createButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				createPressed();
			}	
		});
		
		exitButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				exitPressed(e);
			}	
		});
		
		/*devicePoolsDropDown.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				JComboBox cb = (JComboBox)e.getSource();
				devicePool = (DevicePool)cb.getSelectedItem();
			}
		});*/
		
		sardanaNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(sardanaNameAutoCheckBox.isSelected())
				{
					sardanaNameText.setEditable(false);
					sardanaNameClearButton.setEnabled(false);
				}
				else
				{
					sardanaNameText.setEditable(true);
					sardanaNameClearButton.setEnabled(true);
				}
			}
		});	
		
		sardanaNameClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				sardanaNameText.setText("");
			}
		});
		
		instanceNameText.addKeyListener(new KeyListener()
		{
			public void keyPressed(KeyEvent e) {}
			public void keyTyped(KeyEvent e) {}
			public void keyReleased(KeyEvent e) 
			{
				if(sardanaNameAutoCheckBox.isSelected())
					sardanaNameText.setText(instanceNameText.getText());
			}
		}
		);
		
		addControllerCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				if(addControllerCheckBox.isSelected())
				{
					devicePoolsDropDownLabel.setVisible(true);
					devicePoolsDropDown.setVisible(true);
					devicePoolsAutoCheckBox.setVisible(true);
					sardanaNameLabel.setVisible(true);
					sardanaNameText.setVisible(true);
					sardanaNameText.setText(instanceNameText.getText());
					sardanaNameAutoCheckBox.setVisible(true);
					sardanaNameClearButton.setVisible(true);
					pack();
				}
				else
				{
					devicePoolsDropDownLabel.setVisible(false);
					devicePoolsDropDown.setVisible(false);
					devicePoolsAutoCheckBox.setVisible(false);
					sardanaNameLabel.setVisible(false);
					sardanaNameText.setVisible(false);
					sardanaNameAutoCheckBox.setVisible(false);
					sardanaNameClearButton.setVisible(false);
					pack();
				}
				
			}
		});
		
		pack();
	}
	
	public void refreshDevicePoolsDropDown()
	{
		DevicePoolTreeNode[] poolNodes = SardanaManager.getInstance().getPoolNodes();
		ArrayList<DevicePool> runningPools = new ArrayList<DevicePool>();

		for (int i = 0; i < poolNodes.length; i++)
		{
			if(poolNodes[i].getDevicePool().isAvailable())
				runningPools.add(poolNodes[i].getDevicePool());	
		}
		devicePoolsDropDown = new JComboBox(runningPools.toArray());
	}
		
	
	protected void createPressed()
	{
		String ctrlTypeName = (String)simuTypesDropDown.getSelectedItem();
		String instanceName = instanceNameText.getText();
		String deviceName = deviceNameText.getText();
		
		Object[] devices = simuDevicesListViewer.getElements();
		
		AddingSimulatorHandler handler;
		
		if(instanceName != null &&
		   !instanceName.equals("") && 
		   deviceName != null && 
		   !deviceName.equals("") &&
		   ctrlTypeName != null)
		{
			String [] parts = deviceName.split("/");
			if(parts.length != 3)
			{
				JOptionPane.showMessageDialog(this, 
						"The device name is in wrong format!",
						"Error trying to create a new simulator", 
						JOptionPane.ERROR_MESSAGE);
				return;
			}
			else
			{
				if(ctrlTypeName.equals("Motor"))
					handler = new AddingMotorSimulatorHandler();
				else if(ctrlTypeName.equals("CounterTimer"))
					handler = new AddingCoTiSimulatorHandler();
				else if(ctrlTypeName.equals("ZeroDExpChannel"))
				{
					JOptionPane.showMessageDialog(this, "This simulator has not been implementet yet.",
							   "Information message",
							   JOptionPane.INFORMATION_MESSAGE);
					//handler = new AddingZeroDExpChannelHandler();
					return;
				}
				else if(ctrlTypeName.equals("OneDExpChannel"))
				{
					JOptionPane.showMessageDialog(this, "This simulator has not been implementet yet.",
							   "Information message",
							   JOptionPane.INFORMATION_MESSAGE);
					//handler = new AddingOneDExpChannelHandler();
					return;
				}
				else if(ctrlTypeName.equals("Communication"))
				{
					JOptionPane.showMessageDialog(this, "This simulator has not been implementet yet.",
							   "Information message",
							   JOptionPane.INFORMATION_MESSAGE);
					//handler = new AddingZeroDExpChannelHandler();
					return;
				}
				else 
				{
					JOptionPane.showMessageDialog(this, 
							"Reason:\nUnsuported controller type",
							"Error trying to create a new simulator", 
							JOptionPane.ERROR_MESSAGE);
					return;
				}
				try
				{
					if(addControllerCheckBox.isSelected())		
					{
						DevicePool devicePool = (DevicePool)devicePoolsDropDown.getSelectedItem();
						String sardanaName = sardanaNameText.getText();
						
						if(devicePool != null &&
						   sardanaName != null &&
						   !sardanaName.equals(""))
						{
							handler.addSimulator(machine,
												 devicePool,
												 ctrlTypeName,
												 instanceName,
												 deviceName,
												 sardanaName,
												 devices);
						}
						else
						{
							JOptionPane.showMessageDialog(this, 
									"Controller's required fields missing!",
									"Error trying to create a new simulator", 
									JOptionPane.ERROR_MESSAGE);
							return;
						}	
					}
					else
						handler.addSimulator(machine,
					 			 null,
					 			 null,
					 			 instanceName,
					 			 deviceName,
					 			 null,
					 			 devices);
		
					JOptionPane.showMessageDialog(this,
							"Simulator " + instanceName + " sucessfully created","Sucess!",
							JOptionPane.PLAIN_MESSAGE);
				}
				
				catch (DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer("Reason:\n");
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}	
					JOptionPane.showMessageDialog(this, 
							buff.toString(),
							"Error trying to create a new simulator", 
							JOptionPane.ERROR_MESSAGE);
					return;
				}
			}
		}
		else
		{
			JOptionPane.showMessageDialog(this, 
					"Simulator's required fields missing!",
					"Error trying to create a new simulator", 
					JOptionPane.ERROR_MESSAGE);
			return;
		}
	}
	
	protected void hideAndExit()
	{
		machine = null;
		
		for(Component c : getComponents())
		{
			if(c instanceof JTextField)
				((JTextField)c).setText(null);
			else if(c instanceof JComboBox)
				((JComboBox)c).setSelectedIndex(0);
		}
		setVisible(false);
	}
	
	protected void exitPressed(ActionEvent e)
	{
		hideAndExit();
	}
	
	protected void closeAndExit()
	{
		dispose();
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		//new AddSimulatorDialog(new Machine("controls01","10000")).setVisible(true);
	}
}

interface AddingSimulatorHandler
{
	public void addSimulator(Machine machine,
							  DevicePool devicePool,
							  String ctrlTypeName,
							  String instanceName, 
							  String deviceName, 
							  String sardanaName,
							  Object [] devices
							  ) throws DevFailed;
}

class AddingMotorSimulatorHandler implements AddingSimulatorHandler 
{	
	public void addSimulator(Machine machine, 
							  DevicePool devicePool,
							  String ctrlTypeName,
							  String instanceName, 
							  String deviceName, 
							  String sardanaName,
							  Object [] devices) throws DevFailed
	{
		
		final String simuClassName = "SimuMotorCtrl"; 
		final String simuDeviceClassName = "SimuMotor";
		
		final String ctrlClassName = "SimuMotorController";
		final String ctrlFileName = "SimuMotCtrl.py";
		
		String serverName = simuClassName + "/" + instanceName;
		
		Database db = machine.getDataBase();
		
    	db.add_device(deviceName, simuClassName, serverName);
    		  
		if (devices.length > 0)	
			for( Object device : devices)
				db.add_device((String)device, simuDeviceClassName, serverName);

		if(devicePool != null && sardanaName != null)
		{
			String objectName = ctrlClassName + "/" + sardanaName;
			DbDatum [] properties = {new DbDatum("DevName", deviceName)};
			db.put_property(objectName, properties);
			
			String[] params = new String [6];
			
			params[0] = ctrlTypeName;
			params[1] = ctrlFileName;
			params[2] = ctrlClassName;
			params[3] = sardanaName;
			params[4] = "DevName";
			params[5] = deviceName;
				
			DeviceData args = new DeviceData();
			args.insert(params);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_CTRL,args);
		}
				/*DevVarLongStringArray motorParams; 	
					for( int i = 1; i <= devices.length ; i++)
					{
						int[] iParams = new int[] { i };
						String[] strParams = new String[] { sardanaName + "Motor" + i, sardanaName};
						
						motorParams = new DevVarLongStringArray(
								iParams,
								strParams);
						
						args = new DeviceData();
						args.insert(motorParams);
						devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_MOTOR,args);
					}*/		
		
	}
}

class AddingCoTiSimulatorHandler implements AddingSimulatorHandler
{
	public void addSimulator(Machine machine, 
			  DevicePool devicePool,
			  String ctrlTypeName,
			  String instanceName, 
			  String deviceName, 
			  String sardanaName,
			  Object [] devices) throws DevFailed
	{
	
		final String simuClassName = "SimuCoTiCtrl"; 
		final String simuDeviceClassName = "SimuCounter";
		
		final String ctrlClassName = "SimuCoTiController";
		final String ctrlFileName = "SimuCTCtrl.py";
		
		String serverName = simuClassName + "/" + instanceName;
		
		Database db = machine.getDataBase();
		
		db.add_device(deviceName, simuClassName, serverName);
		
		if (devices.length > 0)	
			for( Object device : devices)
				db.add_device((String)device, simuDeviceClassName, serverName);
		
		if(devicePool != null && sardanaName != null)
		{
			String objectName = ctrlClassName + "/" + sardanaName;
			DbDatum [] properties = {new DbDatum("DevName", deviceName)};
			db.put_property(objectName, properties);
			
			String[] params = new String [6];
			
			params[0] = ctrlTypeName;
			params[1] = ctrlFileName;
			params[2] = ctrlClassName;
			params[3] = sardanaName;
			params[4] = "DevName";
			params[5] = deviceName;
			
			DeviceData args = new DeviceData();
			args.insert(params);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_CTRL,args);
		}
	}
}

class AddingZeroDExpChannelHandler implements AddingSimulatorHandler
{
	public void addSimulator(Machine machine, 
			  DevicePool devicePool,
			  String ctrlTypeName,
			  String instanceName, 
			  String deviceName, 
			  String sardanaName,
			  Object [] devices) throws DevFailed
	{
	/*
		final String simuClassName = "SimuZeroDCtrl"; 
		final String simuDeviceClassName = "SimuCounter";
		
		final String ctrlClassName = "SimuCoTiController";
		final String ctrlFileName = "SimuCTCtrl.py";
		
		String serverName = simuClassName + "/" + instanceName;
		
		Database db = machine.getDataBase();
		
		db.add_device(deviceName, simuClassName, serverName);
		
		if (devices.length > 0)	
			for( Object device : devices)
				db.add_device((String)device, simuDeviceClassName, serverName);
		
		if(devicePool != null && sardanaName != null)
		{
			String objectName = ctrlClassName + "/" + sardanaName;
			DbDatum [] properties = {new DbDatum("DevName", deviceName)};
			db.put_property(objectName, properties);
			
			String[] params = new String [6];
			
			params[0] = ctrlTypeName;
			params[1] = ctrlFileName;
			params[2] = ctrlClassName;
			params[3] = sardanaName;
			params[4] = "DevName";
			params[5] = deviceName;
			
			DeviceData args = new DeviceData();
			args.insert(params);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_CTRL,args);
		}*/
	}
}
