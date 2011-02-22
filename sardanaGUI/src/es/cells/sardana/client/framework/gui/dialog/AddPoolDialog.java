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
import java.util.HashMap;
import java.util.List;
import java.util.regex.Pattern;

import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.Preferences;
import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.SardanaUtils;
import es.cells.sardana.client.framework.SardanaUtils.DeviceInfo;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.atk.widget.DevicePropertyListViewer;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.framework.pool.PoolCreationInfo;
import es.cells.sardana.client.gui.swing.SwingResource;
import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.DeviceProperty;

public class AddPoolDialog extends JDialog 
{
	protected DevicePool pool;
	
	JLabel instanceNameLabel = new JLabel("Instance name:");
	JLabel poolDeviceNameLabel = new JLabel("Pool device name:");
	JLabel poolAliasLabel = new JLabel("Alias (optional):");
	JLabel poolVersionLabel = new JLabel("Pool version:");
	
	JTextField instanceNameText = new JTextField(20);
	JTextField poolDeviceNameText = new JTextField(20);
	JTextField poolAliasText = new JTextField(20);
	JTextField poolVersionText = new JTextField(20);
	
	JButton poolDeviceNameClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	JButton poolAliasClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	JButton poolVersionClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	
	JCheckBox poolDeviceNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox poolAliasNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox poolVersionAutoCheckBox = new JCheckBox("Automatic");
	
	DevicePropertyListViewer poolPathViewer = new DevicePropertyListViewer(new IStringSplitter()
	{
		public String[] split(String str) {	return str.split(":");	}
		public boolean isValid(String str) { return true; }
	});
	
	ButtonsPanel buttonsPanel = new ButtonsPanel();
	
	private JButton createButton = new JButton("Create", SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
	private JButton exitButton = new JButton("Close", SwingResource.smallIconMap.get(IImageResource.IMG_CLOSE));
	
	private Machine machine;

	public AddPoolDialog(Machine machine) 
	{
		super();
		this.machine = machine;
		initComponents();
	}
	
	public AddPoolDialog(Machine machine, DevicePool pool) 
	{
		super();
		this.machine = machine;
		this.pool = pool;
		
		initComponents();
	}	

	private void initComponents() 
	{
		setTitle("Create Pool on " + machine);
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
		
		poolDeviceNameClearButton.setMargin(new Insets(1,1,1,1));
		poolDeviceNameClearButton.setEnabled(false);
		
		poolAliasClearButton.setMargin(new Insets(1,1,1,1));
		poolAliasClearButton.setEnabled(false);
		
		poolVersionClearButton.setMargin(new Insets(1,1,1,1));
		poolVersionClearButton.setEnabled(false);
		
		poolDeviceNameAutoCheckBox.setSelected(true);
		poolAliasNameAutoCheckBox.setSelected(true);
		poolVersionAutoCheckBox.setSelected(true);
		
		poolDeviceNameText.setEditable(false);
		poolAliasText.setEditable(false);
		poolVersionText.setEditable(false);
		
		instanceNameLabel.setLabelFor(instanceNameText);
		poolDeviceNameLabel.setLabelFor(poolDeviceNameText);
		poolAliasLabel.setLabelFor(poolAliasText);
		poolVersionLabel.setLabelFor(poolVersionText);
		poolVersionText.setText(getDefaultVersion());

		String[] value = pool != null ? pool.getProperty("PoolPath").getValue() : null; 
		
		DeviceProperty prop = new DeviceProperty(null,"PoolPath",value);
		poolPathViewer.setModel(prop);
		poolPathViewer.getRefreshButton().setVisible(false);
		poolPathViewer.getApplyButton().setVisible(false);
		
		createButton.setToolTipText("Create a new Pool");
		exitButton.setToolTipText("Close window");

		buttonsPanel.addRight(createButton);
		buttonsPanel.addRight(exitButton);
		
		GridBagConstraints gbc = new GridBagConstraints(
				0,0, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(instanceNameLabel, gbc);

		gbc = new GridBagConstraints(
				1,0, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(instanceNameText, gbc);
		
		 gbc = new GridBagConstraints(
				0,1, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolDeviceNameLabel, gbc);

		gbc = new GridBagConstraints(
				1,1, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolDeviceNameText, gbc);

		gbc = new GridBagConstraints(
				2,1, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolDeviceNameClearButton, gbc);

		gbc = new GridBagConstraints(
				3,1, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolDeviceNameAutoCheckBox, gbc);
		
		gbc = new GridBagConstraints(
					0,2, // x,y
					1,1, // width, height
					0.0, 0.0, //weight x,y
					GridBagConstraints.EAST, //anchor
					GridBagConstraints.HORIZONTAL, // fill
					new Insets(2, 2, 2, 2), // insets
					0,0 //pad x,y
					);		
		mainPanel.add(poolAliasLabel, gbc);

		gbc = new GridBagConstraints(
				1,2, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolAliasText, gbc);

		gbc = new GridBagConstraints(
				2,2, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolAliasClearButton, gbc);			

		gbc = new GridBagConstraints(
				3,2, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolAliasNameAutoCheckBox, gbc);
		//
		gbc = new GridBagConstraints(
				0,3, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolVersionLabel, gbc);
	
		gbc = new GridBagConstraints(
				1,3, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolVersionText, gbc);
	
		gbc = new GridBagConstraints(
				2,3, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolVersionClearButton, gbc);			
	
		gbc = new GridBagConstraints(
				3,3, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolVersionAutoCheckBox, gbc);
		//
		gbc = new GridBagConstraints(
				0,4, // x,y
				4,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(poolPathViewer, gbc);
		
		poolDeviceNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(poolDeviceNameAutoCheckBox.isSelected())
				{
					poolDeviceNameText.setEditable(false);
					poolDeviceNameClearButton.setEnabled(false);
				}
				else
				{
					poolDeviceNameText.setEditable(true);
					poolDeviceNameClearButton.setEnabled(true);
				}
			}
		});

		poolAliasNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(poolAliasNameAutoCheckBox.isSelected())
				{
					poolAliasText.setEditable(false);
					poolAliasClearButton.setEnabled(false);
				}
				else
				{
					poolAliasText.setEditable(true);
					poolAliasClearButton.setEnabled(true);
				}
			}
		});	
		
		poolVersionAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(poolVersionAutoCheckBox.isSelected())
				{
					poolVersionText.setText(getDefaultVersion());
					poolVersionText.setEditable(false);
					poolVersionClearButton.setEnabled(false);
				}
				else
				{
					poolVersionText.setEditable(true);
					poolVersionClearButton.setEnabled(true);
				}
			}
		});	

		poolDeviceNameClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				poolDeviceNameText.setText("");
			}
		});

		poolAliasClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				poolAliasText.setText("");
			}
		});
		
		poolVersionClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				poolVersionText.setText("");
			}
		});

		instanceNameText.addKeyListener(new KeyListener()
		{
			public void keyPressed(KeyEvent e) {}
			public void keyTyped(KeyEvent e) {}
			public void keyReleased(KeyEvent e) 
			{
				if(poolDeviceNameAutoCheckBox.isSelected())
				{
					calculatePoolDeviceName();
				}
				if(poolAliasNameAutoCheckBox.isSelected())
				{
					calculateAlias();
				}
			}
		}
		);

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
		
		pack();
	}

	protected void createPressed() 
	{
		String instanceName = instanceNameText.getText();
		if(instanceName == null || instanceName.length() == 0 ||
		   instanceName.contains("/"))
		{
			JOptionPane.showMessageDialog(null, 
					"Invalid instance name", 
					"Invalid field", JOptionPane.ERROR_MESSAGE);
			return;
		}
		
		String poolDeviceName = poolDeviceNameText.getText();
		if(poolDeviceName == null || poolDeviceName.split("/").length != 3)
		{
			JOptionPane.showMessageDialog(null, 
					"Invalid pool device name", 
					"Invalid field", JOptionPane.ERROR_MESSAGE);
			return;
		}

		String aliasName = poolAliasText.getText();
		if(aliasName.contains("/"))
		{
			JOptionPane.showMessageDialog(null, 
					"Invalid alias name", 
					"Invalid field", JOptionPane.ERROR_MESSAGE);
			return;
		}
		
		String version = poolVersionText.getText();
		//checking if the version format is correct 
		//it has to be in following format x.x.x
		//where each x is a integer number
		boolean isVersionCorrect = true;
		if(version == null || version.length() == 0)
		{
			isVersionCorrect = false;
		}else
		{
			String [] parts = version.split("\\.");
			if(parts.length!=3)
			{
				isVersionCorrect = false;
			}else 
			{
				for(String part : parts)
				{
					try
					{
						Integer p = Integer.parseInt(part);
					}
					catch(NumberFormatException e)
					{
						isVersionCorrect = false;
					}
				}
			}
		}
		if(!isVersionCorrect)
		{
			JOptionPane.showMessageDialog(null, 
					"Invalid version", 
					"Invalid field", JOptionPane.ERROR_MESSAGE);
			return;
		}
			
		
		PoolCreationInfo info = new PoolCreationInfo();
		info.setInstanceName(instanceName);
		info.setPooldeviceName(poolDeviceName);
		info.setAliasName(aliasName);
		info.setVersion(version);
		info.setPoolPath(poolPathViewer.getElements());
		info.setMachine(machine);
		
		try
		{
			DevicePoolUtils.getInstance().createPool(info);
			
			//checking if on machine already exist sardana system with this name
			//if not creates new sardana system
			HashMap<String,List<DeviceInfo>> sardanas = SardanaUtils.getInstance().
																	getSardanas(machine);
			boolean createSardanaSystem = true;
			for (String sardanaName : sardanas.keySet())
			{
				if(instanceName.equals(sardanaName))
				{
					createSardanaSystem = false;
					break;
				}
			}
			String additionalMessage = "";
			if (createSardanaSystem)
			{
				SardanaUtils.getInstance().registerSardanaService(machine,
																  instanceName, 
																  poolDeviceName);
				additionalMessage = " and coresponding Sardana System";
			}
			
			JOptionPane.showMessageDialog(null, "DevicePool server" +
													additionalMessage +
													" successfully created",
					"Success!",
					JOptionPane.INFORMATION_MESSAGE);
			
			SardanaManager.getInstance().refreshDataModel();
				
		}
		catch(DevFailed devFailed)
		{
			StringBuffer buff = new StringBuffer("Reason:\n");
			
			for(DevError elem : devFailed.errors)
			{
				buff.append( elem.desc + "\n");
			}
	    	JOptionPane.showMessageDialog(null, buff.toString(),
				"Error trying to register device in the database",
				JOptionPane.ERROR_MESSAGE);
		}
	}

	protected void calculateAlias() 
	{
		poolAliasText.setText("Pool_"+instanceNameText.getText());
	}

	protected void calculatePoolDeviceName() 
	{
		poolDeviceNameText.setText("pool/" + instanceNameText.getText() + "/1");
	}

	protected void closeAndExit()
	{
		dispose();
	}
	
	protected String getDefaultVersion()
	{
		return new String("0.2.0");
	}
	
	protected void hideAndExit()
	{
		machine = null;
		
		for(Component c : getComponents())
		{
			if(c instanceof JTextField)
			{
				((JTextField)c).setText(null);
			}
			else if(c instanceof JComboBox)
			{
				((JComboBox)c).setSelectedIndex(0);
			}
		}
		setVisible(false);
	}
	
	protected void exitPressed(ActionEvent e)
	{
		hideAndExit();
	}
	
	public static void main(String[] args) 
	{
		new AddPoolDialog(new Machine("controls01","10000")).setVisible(true);
	}
}
