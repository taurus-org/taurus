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
import java.util.Collection;
import java.util.HashMap;

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
import es.cells.sardana.client.framework.SardanaUtils;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.atk.widget.DevicePropertyListViewer;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.macroserver.MacroServer;
import es.cells.sardana.client.framework.macroserver.MacroServerCreationInfo;
import es.cells.sardana.client.framework.macroserver.MacroServerUtils;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.gui.swing.SwingResource;
import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.DeviceProperty;

public class AddMacroServerDialog extends JDialog 
{
	protected MacroServer macroServer;
	
	JLabel instanceNameLabel = new JLabel("Instance name:");
	JLabel poolNameLabel= new JLabel("Pool name:");
	JLabel macroServerNameLabel = new JLabel("MacroServer device name:");
	JLabel macroServerAliasLabel = new JLabel("MacroServer alias:");
	JLabel doorNameLabel= new JLabel("Door name:");
	JLabel doorAliasLabel= new JLabel("Door alias:");
	JLabel macroServerVersionLabel = new JLabel("MacroServer version:");
	
	JTextField instanceNameText = new JTextField(20);
	JComboBox poolNameComboBox;
	JTextField macroServerNameText = new JTextField(20);
	JTextField macroServerAliasText = new JTextField(20);
	JTextField doorNameText = new JTextField(20);
	JTextField doorAliasText = new JTextField(20);
	JTextField macroServerVersionText = new JTextField(20);
	
	JButton macroServerNameClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	JButton macroServerAliasClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	JButton doorNameClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	JButton doorAliasClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	JButton macroServerVersionClearButton = new JButton(SwingResource.smallerIconMap.get(IImageResource.IMG_CLEAR));
	
	JCheckBox macroServerNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox macroServerAliasNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox doorNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox doorAliasNameAutoCheckBox = new JCheckBox("Automatic");
	JCheckBox macroServerVersionAutoCheckBox = new JCheckBox("Automatic");
	
	DevicePropertyListViewer macroServerPathViewer = new DevicePropertyListViewer(new IStringSplitter()
	{
		public String[] split(String str) {	return str.split(":");	}
		public boolean isValid(String str) { return true; }
	});
	
	ButtonsPanel buttonsPanel = new ButtonsPanel();
	
	private JButton createButton = new JButton("Create", SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
	private JButton exitButton = new JButton("Close", SwingResource.smallIconMap.get(IImageResource.IMG_CLOSE));
	
	private Machine machine;

	public AddMacroServerDialog(Machine machine) 
	{
		super();
		this.machine = machine;
		initComponents();
	}
	
	public AddMacroServerDialog(Machine machine, MacroServer ms) 
	{
		super();
		this.machine = machine;
		this.macroServer = ms;
		
		initComponents();
	}	

	private void initComponents() 
	{
		setTitle("Create MacroServer on " + machine);
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

		HashMap<String, String> poolserverdevs = DevicePoolUtils.getInstance().getPoolDevices(this.machine);
		Collection<String> pools = poolserverdevs.values(); 
		poolNameComboBox = new JComboBox(pools.toArray());
		
		macroServerNameClearButton.setMargin(new Insets(1,1,1,1));
		macroServerNameClearButton.setEnabled(false);
		
		macroServerAliasClearButton.setMargin(new Insets(1,1,1,1));
		macroServerAliasClearButton.setEnabled(false);
		
		macroServerVersionClearButton.setMargin(new Insets(1,1,1,1));
		macroServerVersionClearButton.setEnabled(false);

		doorNameClearButton.setMargin(new Insets(1,1,1,1));
		doorNameClearButton.setEnabled(false);
		
		doorAliasClearButton.setMargin(new Insets(1,1,1,1));
		doorAliasClearButton.setEnabled(false);
		
		macroServerNameAutoCheckBox.setSelected(true);
		macroServerAliasNameAutoCheckBox.setSelected(true);
		macroServerVersionAutoCheckBox.setSelected(true);

		doorNameAutoCheckBox.setSelected(true);
		doorAliasNameAutoCheckBox.setSelected(true);
		
		macroServerNameText.setEditable(false);
		macroServerAliasText.setEditable(false);
		macroServerVersionText.setEditable(false);

		doorNameText.setEditable(false);
		doorAliasText.setEditable(false);

		instanceNameLabel.setLabelFor(instanceNameText);
		poolNameLabel.setLabelFor(poolNameComboBox);
		macroServerNameLabel.setLabelFor(macroServerNameText);
		macroServerAliasLabel.setLabelFor(macroServerAliasText);
		macroServerVersionLabel.setLabelFor(macroServerVersionText);
		doorNameLabel.setLabelFor(doorNameText);
		doorAliasLabel.setLabelFor(doorAliasText);
		macroServerVersionText.setText(getDefaultVersion());
		
		String[] value = macroServer != null ? macroServer.getProperty("MacroPath").getValue() : null; 
		
		DeviceProperty prop = new DeviceProperty(null,"MacroPath",value);
		macroServerPathViewer.setModel(prop);
		macroServerPathViewer.getRefreshButton().setVisible(false);
		macroServerPathViewer.getApplyButton().setVisible(false);
		
		createButton.setToolTipText("Create a new MacroServer");
		exitButton.setToolTipText("Close window");

		buttonsPanel.addRight(createButton);
		buttonsPanel.addRight(exitButton);
		
//
// Instance name
//		
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
		
//
// Pool name
//				
		gbc = new GridBagConstraints(
				0,1, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolNameLabel, gbc);

		gbc = new GridBagConstraints(
				1,1, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(poolNameComboBox, gbc);
		
//
// Macro server device name
//
		 gbc = new GridBagConstraints(
				0,2, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(macroServerNameLabel, gbc);

		gbc = new GridBagConstraints(
				1,2, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(macroServerNameText, gbc);
		
		gbc = new GridBagConstraints(
				2,2, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(macroServerNameClearButton, gbc);

		gbc = new GridBagConstraints(
				3,2, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(macroServerNameAutoCheckBox, gbc);
		
//
// Macro alias
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
		mainPanel.add(macroServerAliasLabel, gbc);

		gbc = new GridBagConstraints(
				1,3, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerAliasText, gbc);

		gbc = new GridBagConstraints(
				2,3, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerAliasClearButton, gbc);			

		gbc = new GridBagConstraints(
				3,3, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerAliasNameAutoCheckBox, gbc);			
//
// Macro server version
//
		gbc = new GridBagConstraints(
				0,4, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(macroServerVersionLabel, gbc);

		gbc = new GridBagConstraints(
				1,4, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerVersionText, gbc);

		gbc = new GridBagConstraints(
				2,4, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerVersionClearButton, gbc);			

		gbc = new GridBagConstraints(
				3,4, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerVersionAutoCheckBox, gbc);
		
		
//
// Door device name
//
		 gbc = new GridBagConstraints(
				0,5, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(doorNameLabel, gbc);

		gbc = new GridBagConstraints(
				1,5, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(doorNameText, gbc);
		
		gbc = new GridBagConstraints(
				2,5, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(doorNameClearButton, gbc);

		gbc = new GridBagConstraints(
				3,5, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(doorNameAutoCheckBox, gbc);
		
//
// Door alias
//				
		gbc = new GridBagConstraints(
				0,6, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(doorAliasLabel, gbc);

		gbc = new GridBagConstraints(
				1,6, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(doorAliasText, gbc);

		gbc = new GridBagConstraints(
				2,6, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(doorAliasClearButton, gbc);			

		gbc = new GridBagConstraints(
				3,6, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(doorAliasNameAutoCheckBox, gbc);	
				
//
// MacroPath
//		
		gbc = new GridBagConstraints(
				0,7, // x,y
				4,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
		);		
		mainPanel.add(macroServerPathViewer, gbc);
		
		macroServerNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(macroServerNameAutoCheckBox.isSelected())
				{
					macroServerNameText.setEditable(false);
					macroServerNameClearButton.setEnabled(false);
				}
				else
				{
					macroServerNameText.setEditable(true);
					macroServerNameClearButton.setEnabled(true);
				}
			}
		});

		macroServerAliasNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(macroServerAliasNameAutoCheckBox.isSelected())
				{
					macroServerAliasText.setEditable(false);
					macroServerAliasClearButton.setEnabled(false);
				}
				else
				{
					macroServerAliasText.setEditable(true);
					macroServerAliasClearButton.setEnabled(true);
				}
			}
		});	
		
		macroServerVersionAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(macroServerVersionAutoCheckBox.isSelected())
				{
					macroServerVersionText.setText(getDefaultVersion());
					macroServerVersionText.setEditable(false);
					macroServerVersionClearButton.setEnabled(false);					
				}
				else
				{
					macroServerVersionText.setEditable(true);
					macroServerVersionClearButton.setEnabled(true);
				}
			}
		});	

		macroServerNameClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				macroServerNameText.setText("");
			}
		});

		macroServerAliasClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				macroServerAliasText.setText("");
			}
		});
		
		macroServerVersionClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				macroServerVersionText.setText("");
			}
		});
		
		doorNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(doorNameAutoCheckBox.isSelected())
				{
					doorNameText.setEditable(false);
					doorNameClearButton.setEnabled(false);
				}
				else
				{
					doorNameText.setEditable(true);
					doorNameClearButton.setEnabled(true);
				}
			}
		});

		doorAliasNameAutoCheckBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(doorAliasNameAutoCheckBox.isSelected())
				{
					doorAliasText.setEditable(false);
					doorAliasClearButton.setEnabled(false);
				}
				else
				{
					doorAliasText.setEditable(true);
					doorAliasClearButton.setEnabled(true);
				}
			}
		});	

		doorNameClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				doorNameText.setText("");
			}
		});

		doorAliasClearButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				doorAliasText.setText("");
			}
		});
		
		instanceNameText.addKeyListener(new KeyListener()
		{
			public void keyPressed(KeyEvent e) {}
			public void keyTyped(KeyEvent e) {}
			public void keyReleased(KeyEvent e) 
			{
				if(macroServerNameAutoCheckBox.isSelected())
				{
					calculateMacroServerDeviceName();
				}
				if(macroServerAliasNameAutoCheckBox.isSelected())
				{
					calculateMacroServerAlias();
				}
				if(doorNameAutoCheckBox.isSelected())
				{
					calculateDoorDeviceName();
				}
				if(doorAliasNameAutoCheckBox.isSelected())
				{
					calculateDoorAlias();
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
		
		String macroServerDeviceName = macroServerNameText.getText();
		if(macroServerDeviceName == null || macroServerDeviceName.split("/").length != 3)
		{
			JOptionPane.showMessageDialog(null, 
					"Invalid MacroServer device name", 
					"Invalid field", JOptionPane.ERROR_MESSAGE);
			return;
		}

		String aliasName = macroServerAliasText.getText();
		if(aliasName.contains("/"))
		{
			JOptionPane.showMessageDialog(null, 
					"Invalid alias name", 
					"Invalid field", JOptionPane.ERROR_MESSAGE);
			return;
		}
		
		String version = macroServerVersionText.getText();
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
		
		MacroServerCreationInfo info = new MacroServerCreationInfo();
		info.setInstanceName(instanceName);
		info.setMacroServerDeviceName(macroServerDeviceName);
		info.setPoolNames(new Object[]{poolNameComboBox.getSelectedItem()});
		info.setMacroServerAlias(aliasName);
		info.setMsVersion(version);
		info.setMacroPath(macroServerPathViewer.getElements());
		info.setMachine(machine);
		
		String doorName = doorNameText.getText();
		String doorAlias = doorAliasText.getText();
		
		if(doorName.length() > 0)
		{
			info.setDoorDeviceName(doorName);
			info.setDoorAlias(doorAlias);
		}
		
		try
		{
			MacroServerUtils.getInstance().createMacroServer(info);
			SardanaUtils.getInstance().registerSardanaService(info.getMachine(), 
																 info.getInstanceName(), 
																 info.getMacroServerDeviceName());
			JOptionPane.showMessageDialog(null, "MacroServer server and coresponding " +
														"Sardana system successfully created",
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

	protected void calculateMacroServerAlias() 
	{
		macroServerAliasText.setText("MS_" + instanceNameText.getText());
	}

	protected void calculateMacroServerDeviceName() 
	{
		macroServerNameText.setText("macroserver/" + instanceNameText.getText() + "/1");
	}

	protected void calculateDoorAlias() 
	{
		doorAliasText.setText("Door_" + instanceNameText.getText());
	}

	protected void calculateDoorDeviceName() 
	{
		doorNameText.setText("door/" + instanceNameText.getText() + "/1");
	}
	
	protected String getDefaultVersion()
	{
		return new String("0.2.0");
	}

	protected void closeAndExit()
	{
		dispose();
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
		new AddMacroServerDialog(new Machine("controls01","10000")).setVisible(true);
	}
}
