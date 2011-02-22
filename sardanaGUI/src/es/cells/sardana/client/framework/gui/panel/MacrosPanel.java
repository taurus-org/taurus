package es.cells.sardana.client.framework.gui.panel;

import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.List;

import javax.swing.BorderFactory;
import javax.swing.DefaultComboBoxModel;
import javax.swing.DefaultListModel;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollBar;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import es.cells.sardana.client.framework.gui.atk.widget.DoorStateLabel;
import es.cells.sardana.client.framework.gui.atk.widget.MacroDescriptionPanel;
import es.cells.sardana.client.framework.gui.atk.widget.SimpleMultiOutputViewer;
import es.cells.sardana.client.framework.gui.atk.widget.SimpleOutputViewer;
import es.cells.sardana.client.framework.macroserver.Atribute;
import es.cells.sardana.client.framework.macroserver.AtributeRepeat;
import es.cells.sardana.client.framework.macroserver.Door;
import es.cells.sardana.client.framework.macroserver.MacroDescriptionModel;
import es.cells.sardana.client.framework.macroserver.MacroServer;
import es.cells.sardana.client.framework.macroserver.MacroServerUtils;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDeviceListener;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.StateEvent;
import fr.esrf.tangoatk.core.StatusEvent;
import fr.esrf.tangoatk.widget.attribute.SimpleStringSpectrumViewer;

public class MacrosPanel extends JPanel implements IDeviceListener {
	
	//LED icons
	public static final ImageIcon ON_STATUS_ICON = new ImageIcon("res/24x24/ledgreen.png");
	public static final ImageIcon OFF_STATUS_ICON = new ImageIcon("res/24x24/ledred.png");
	public static final ImageIcon RUNNING_STATUS_ICON = new ImageIcon("res/24x24/ledblue.png");
	public static final ImageIcon RUNNING_OFF_STATUS_ICON = new ImageIcon("res/24x24/ledblueoff.png");
	public static final ImageIcon UNKNOWN_STATUS_ICON = new ImageIcon("res/24x24/ledyellowoff.png");
	public static final ImageIcon INIT_STATUS_ICON = new ImageIcon("res/24x24/ledyellow.png");
	public static final ImageIcon ALARM_STATUS_ICON = new ImageIcon("res/24x24/ledorange.png");
	
	//button icons
	public static final ImageIcon PLAY_ICON = new ImageIcon("res/24x24/player_play.png");
	public static final ImageIcon STOP_ICON = new ImageIcon("res/24x24/player_stop.png");
	public static final ImageIcon PAUSE_ICON = new ImageIcon("res/24x24/player_pause.png");
	
	//-----------MODEL----------------
	
	private MacroServer macroServer;
	private Device doorDevice;
	
	//-----------VIEW-----------------
	
	//macros list	
	private JList       macroList;
	private JScrollPane macroListViewer;
	
	//macro description
	private MacroDescriptionPanel macroDescription;
	private JScrollPane macroDescriptionViewer;
	
	//macro execution
	private JPanel macroExecuterPanel;
	
	private JLabel doorLabel;
	private JComboBox doorCombo;
	private DoorStateLabel doorStateLED;
	
	private JLabel macroArgsLabel;
	private JTextField macroArgsText;
	
	private JPanel buttonsPanel;
	private JButton play_pauseMacroButton;
	private JButton stopMacroButton;
	
	//output panel
	private JTabbedPane outputTabbedPane;
	private JTextArea outTextArea;
	private JTextArea debTextArea;
	
	public MacrosPanel()
	{
		initComponents();
	}
	
	public void setMacroServer(MacroServer ms)
	{
		this.macroServer = ms;
		if(macroServer.isAvailable())
			this.macroServer.initDoors();
		refreshMacroList();
		refreshDoorList();
		play_pauseMacroButton.setEnabled(false);
		stopMacroButton.setEnabled(false);
	}
	
	public void initComponents()
	{
		setName("Macros");
		setLayout(new GridBagLayout());
		
		macroList = new JList();
		macroList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		macroList.addListSelectionListener(new ListSelectionListener()
			{
				public void valueChanged(ListSelectionEvent e){
					if(macroList.getSelectedValue() != null)
						refreshMacroDescription((String)macroList.getSelectedValue());
					
					JScrollBar verticalScrollBar = macroDescriptionViewer.getVerticalScrollBar();
					JScrollBar horizontalScrollBar = macroDescriptionViewer.getHorizontalScrollBar();
					verticalScrollBar.setValue(verticalScrollBar.getMinimum());
					horizontalScrollBar.setValue(horizontalScrollBar.getMinimum());
				}
			});
		
		macroListViewer = new JScrollPane(macroList);
		macroListViewer.setBorder(BorderFactory.createTitledBorder("List of macros"));
		
		macroDescription = new MacroDescriptionPanel();
		macroDescriptionViewer = new JScrollPane(macroDescription);
		macroDescriptionViewer.setBorder(BorderFactory.createTitledBorder("Macro description"));
		
		macroExecuterPanel = new JPanel();
		macroExecuterPanel.setLayout(new GridBagLayout());
		macroExecuterPanel.setBorder(BorderFactory.createTitledBorder("Execute macro"));
		
		doorLabel = new JLabel("Door:");
		doorCombo = new JComboBox();
		doorCombo.addActionListener(new ActionListener()
			{
				public void actionPerformed(ActionEvent e)
				{
					outputTabbedPane.removeAll();
					Device doorDevice = ((Door)doorCombo.getSelectedItem()).getDevice();
					setModel(doorDevice);
					if(doorDevice.isAlive())
						createAllOutputTabs();
				}
			});
		doorLabel.setLabelFor(doorCombo);
		doorStateLED = new DoorStateLabel();
		
		macroArgsText = new JTextField(50);
		macroArgsLabel = new JLabel("Macro arguments:");
		macroArgsLabel.setLabelFor(macroArgsText);
		
		
		play_pauseMacroButton = new JButton(PLAY_ICON);
		play_pauseMacroButton.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent e){
				if(doorDevice.getState().equals(Device.STANDBY))
					resumeMacro();
				else
				if(doorDevice.getState().equals(Device.ON)) 
					executeMacro();
				else
				if(doorDevice.getState().equals(Device.RUNNING))
					pauseMacro();
			 }
		});
		stopMacroButton = new JButton(STOP_ICON);
		stopMacroButton.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent e){
				abortMacro();
			}
		});
		buttonsPanel = new JPanel(new FlowLayout());
		buttonsPanel.add(play_pauseMacroButton);
		buttonsPanel.add(stopMacroButton);
		
		outputTabbedPane = new JTabbedPane();
		
		GridBagConstraints gbc;
		
		// Components of Macro Executer Panel
		gbc = new GridBagConstraints(
				0,0, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		macroExecuterPanel.add(doorLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,0, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		macroExecuterPanel.add(doorCombo, gbc);
		
		gbc = new GridBagConstraints(
				2,0, // x,y
				1,1, // width, height
				1.0, 1.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		macroExecuterPanel.add(doorStateLED, gbc);
		
		gbc = new GridBagConstraints(
				0,1, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		macroExecuterPanel.add(macroArgsLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,1, // x,y
				2,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		macroExecuterPanel.add(macroArgsText, gbc);
		
		gbc = new GridBagConstraints(
				1,2, // x,y
				2,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		macroExecuterPanel.add(buttonsPanel, gbc);
		
		//Components of Main Panel
		gbc = new GridBagConstraints(
				0,0, // x,y
				1,3, // width, height
				0.5, 1.0, //weight x,y
				GridBagConstraints.LINE_START, //anchor
				GridBagConstraints.BOTH, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		this.add(macroListViewer, gbc);
		
		gbc = new GridBagConstraints(
				1,0, // x,y
				1,1, // width, height
				1.0, 1.0, //weight x,y
				GridBagConstraints.FIRST_LINE_END, //anchor
				GridBagConstraints.BOTH, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		this.add(macroDescriptionViewer, gbc);
		
		gbc = new GridBagConstraints(
				1,1, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.LAST_LINE_END, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		this.add(macroExecuterPanel, gbc);
		
		gbc = new GridBagConstraints(
				1,2, // x,y
				1,1, // width, height
				1.0, 1.0, //weight x,y
				GridBagConstraints.LAST_LINE_END, //anchor
				GridBagConstraints.BOTH, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		this.add(outputTabbedPane, gbc);
	}
	// ------------------macro methods----------------------
	
	public void executeMacro()
	{
		if(doorCombo.getSelectedItem()!=null &&
		   (String)macroList.getSelectedValue() != null)
		{
			String macroName = (String)macroList.getSelectedValue();
			Door door = (Door)doorCombo.getSelectedItem();
				
			String arguments = macroArgsText.getText();
			
			String[] macroArgs = null;
			
			if(!(arguments == null || arguments.equals("")))	
				macroArgs = arguments.split("\\s+");
			
			try 
			{			
				DeviceData returnValues = MacroServerUtils.getInstance().
												executeMacro(door, macroName, macroArgs);
			} 
			catch (DevFailed e) 
			{
				JOptionPane.showMessageDialog(this, 
											  "Macro could not be executed.", 
											  "Error", 
											  JOptionPane.ERROR_MESSAGE);
			}
		}
		else
			JOptionPane.showMessageDialog(this, 
					  "No macro was selected,\n" +
					  "First, please select the macro from the list", 
					  "Macro execution info.", 
					  JOptionPane.INFORMATION_MESSAGE);
	}
	
	public void pauseMacro()
	{
		Door door = (Door)doorCombo.getSelectedItem();
		try 
		{			
			MacroServerUtils.getInstance().pauseMacro(door);
		} 
		catch (DevFailed e) 
		{
			JOptionPane.showMessageDialog(this, 
										  "Macro could not be paused.", 
										  "Error", 
										  JOptionPane.ERROR_MESSAGE);
		}
		
	}
	
	public void resumeMacro()
	{
		Door door = (Door)doorCombo.getSelectedItem();
		try 
		{			
			MacroServerUtils.getInstance().resumeMacro(door);
		} 
		catch (DevFailed e) 
		{
			JOptionPane.showMessageDialog(this, 
										  "Macro could not be resumed.", 
										  "Error", 
										  JOptionPane.ERROR_MESSAGE);
		}
		
	}
	
	public void abortMacro()
	{
		Door door = (Door)doorCombo.getSelectedItem();
		try 
		{			
			MacroServerUtils.getInstance().abortMacro(door);
		} 
		catch (DevFailed e) 
		{
			JOptionPane.showMessageDialog(this, 
										  "Macro could not be aborted.", 
										  "Error", 
										  JOptionPane.ERROR_MESSAGE);
		}
		
	}
	
	
	//-----------------refresh methods--------------------------
	public void refreshDoorList()
	{
		outputTabbedPane.removeAll();
		ArrayList<Door> doors = (ArrayList<Door>)macroServer.getDoors();
		if(doors != null && doors.size() > 0)
		{
			doorCombo.setModel(new DefaultComboBoxModel(doors.toArray()));
			doorCombo.setSelectedIndex(0);
			doorStateLED.setIcon(UNKNOWN_STATUS_ICON);
			setModel(((Door)doorCombo.getSelectedItem()).getDevice());
			doorStateLED.setVisible(true);
		}
		else
		{
			doorCombo.setModel(new DefaultComboBoxModel());
			setModel(null);
			doorStateLED.setVisible(false);
		}
	}
	
	public void refreshMacroList()
	{
		String [] macrosNames;
		DefaultListModel ml = new DefaultListModel();
		if(macroServer.isAvailable())
		{
			try
			{
				macrosNames = MacroServerUtils.getInstance().askForMacroServerMacros(macroServer);
			}
			catch (DevFailed e)
			{
				JOptionPane.showMessageDialog(this, 
											  "Error while asking macro server about macros", 
											  "Error", 
											  JOptionPane.ERROR_MESSAGE);
				return;
			}
			java.util.Arrays.sort(macrosNames);
			for (String string : macrosNames) {
				ml.addElement(string);
				
			}
			
			JScrollBar verticalScrollBar = macroListViewer.getVerticalScrollBar();
			JScrollBar horizontalScrollBar = macroListViewer.getHorizontalScrollBar();
			verticalScrollBar.setValue(verticalScrollBar.getMinimum());
			horizontalScrollBar.setValue(horizontalScrollBar.getMinimum());
		}
		else
		{
			ml = new DefaultListModel();
		}
		
		macroList.setModel(ml);
		macroDescription.setModel(null);
		
	}
	
	public void refreshMacroDescription(String macroName)
	{
		String plainDescription;
		MacroDescriptionModel macroDescriptionModel;
		
		plainDescription = getPlainMacroDescription(macroName);
		
		if (plainDescription != null)
			macroDescriptionModel = createMacroDescriptionModel(plainDescription);
		else
			macroDescriptionModel = null;
		
		macroDescription.setModel(macroDescriptionModel);	
	}
	
	//asking for macro description 
	public String getPlainMacroDescription(String macroName)
	{
		String text;
		try
		{
			text = MacroServerUtils.getInstance().
									askForMacroDescription(macroServer, macroName);
		}
		catch(DevFailed e)
		{
			JOptionPane.showMessageDialog(this, 
					  "Error while asking macro server about macro description", 
					  "Error", 
					  JOptionPane.ERROR_MESSAGE);
			text = null;
		}
		return text;
	}
	// parse macro description
	public MacroDescriptionModel createMacroDescriptionModel(String plainDescription)
	{
		MacroDescriptionModel model = new MacroDescriptionModel();
		
		String parts [] = plainDescription.split("\\{");
			String nameDescription [] = parts[0].split("\n"); 
			model.setName(nameDescription[0]);
			model.setDescription(nameDescription[1]);
		
		parts = parts[1].split("\\}");
		model.setAdvices(parts[0]);
		
		parts = parts[1].split("\n");
		
		int nrOfArgs = Integer.parseInt(parts[1]);
		
		model.setNrOfArgs(String.valueOf(nrOfArgs));
		if(nrOfArgs > 0)
		{
			Atribute atributes [] = new Atribute [nrOfArgs];
			Atribute atribute;
			int i = 2;
			for(int a = 0; a < nrOfArgs; a++ )
			{
				if(parts[i+1].equals("ParamRepeat"))
				{
					atribute = new AtributeRepeat();
					
					atribute.setName(parts[i]);
					i++;
					atribute.setType(parts[i]);
					i++;
					atribute.setDescription(parts[i]);
					i++;
					atribute.setDefaultValue(parts[i]);
					i++;
					int nrOfRepeatAtribs = Integer.parseInt(parts[i]);
					i++;
					
					Atribute [] repeatAtributes = new Atribute [nrOfRepeatAtribs];
					Atribute repeatAtribute;
					
					for(int j = 0; j < nrOfRepeatAtribs; j++)
					{
						repeatAtribute = new Atribute();
						
						repeatAtribute.setName(parts[i]);
						i++;
						repeatAtribute.setType(parts[i]);
						i++;
						repeatAtribute.setDescription(parts[i]);
						i++;
						repeatAtribute.setDefaultValue(parts[i]);
						i++;
						
						repeatAtributes[j] = repeatAtribute;
					}
					((AtributeRepeat)atribute).setAtributes(repeatAtributes);
				}
				else
				{
					atribute = new Atribute();
					
					atribute.setName(parts[i]);
					i++;
					atribute.setType(parts[i]);
					i++;
					atribute.setDescription(parts[i]);
					i++;
					atribute.setDefaultValue(parts[i]);
					i++; 
				}
				atributes[a] = atribute;					
			}		
			model.setAtributes(atributes);
		}
		return model;
	}
	
	// IDeviceListener methods
	
	public void setModel(Device door)
	{
		if(this.doorDevice != null)
		{
			this.doorDevice.removeListener(this);
		}
		if(door != null)
		{
			this.doorDevice = door;
			this.doorDevice.addListener(this);
		}
		else 
			this.doorDevice = null;
	}
	
	public void stateChange(StateEvent e) 
	{
		if(e.getState() == Device.ON)
		{
			doorStateLED.setBlinking(false);
			doorStateLED.timer.stop();
			doorStateLED.setIcon(ON_STATUS_ICON);
			play_pauseMacroButton.setIcon(PLAY_ICON);
			play_pauseMacroButton.setEnabled(true);
			play_pauseMacroButton.setToolTipText("Start macro");
			stopMacroButton.setEnabled(false);
		}
		if(e.getState() == Device.OFF)
		{
			doorStateLED.setIcon(OFF_STATUS_ICON);
			play_pauseMacroButton.setIcon(PLAY_ICON);
			play_pauseMacroButton.setEnabled(false);
			stopMacroButton.setEnabled(false);
		}
		if(e.getState() == Device.RUNNING)
		{
			doorStateLED.setBlinking(false);
			doorStateLED.timer.stop();
			doorStateLED.setIcon(RUNNING_STATUS_ICON);
			play_pauseMacroButton.setIcon(PAUSE_ICON);
			play_pauseMacroButton.setToolTipText("Pause macro");
			stopMacroButton.setEnabled(true);
			stopMacroButton.setToolTipText("Stop macro");
			
		}
		if(e.getState() == Device.STANDBY)
		{
			doorStateLED.setOnIcon(RUNNING_STATUS_ICON);
			doorStateLED.setOffIcon(RUNNING_OFF_STATUS_ICON);
			doorStateLED.setBlinking(true);
			doorStateLED.timer.start();
			play_pauseMacroButton.setIcon(PLAY_ICON);
			play_pauseMacroButton.setEnabled(true);
			play_pauseMacroButton.setToolTipText("Resume macro");
		}
		if(e.getState() == Device.UNKNOWN)
		{
			doorStateLED.setIcon(UNKNOWN_STATUS_ICON);
			play_pauseMacroButton.setIcon(PLAY_ICON);
			play_pauseMacroButton.setEnabled(false);
			stopMacroButton.setEnabled(false);
		}
		if(e.getState() == Device.INIT)
		{
			doorStateLED.setIcon(INIT_STATUS_ICON);
			play_pauseMacroButton.setIcon(PLAY_ICON);
			play_pauseMacroButton.setEnabled(false);
			stopMacroButton.setEnabled(false);
		}
		if(e.getState() == Device.ALARM)
		{
			doorStateLED.setIcon(ALARM_STATUS_ICON);
			play_pauseMacroButton.setIcon(PLAY_ICON);
			play_pauseMacroButton.setEnabled(false);
			stopMacroButton.setEnabled(false);
		}
	}

	public void errorChange(ErrorEvent arg0) 
	{
	
	}
	
	public void statusChange(StatusEvent arg0) 
	{
		
	}
	
	
    private void createAllOutputTabs() 
    {
    	AttributeList outputAtts = new AttributeList();
    	AttributeList debugAtts = new AttributeList();
    	AttributeList resultAtts = new AttributeList();
    	
    	IStringSpectrum strSpectrumAtt;
    	
    	try 
		{	
			outputAtts.add(doorDevice.getName() + "/Output");
			outputAtts.add(doorDevice.getName() + "/Error");
			outputAtts.add(doorDevice.getName() + "/Warning");
			outputAtts.add(doorDevice.getName() + "/Info");
			
			debugAtts.add(doorDevice.getName() + "/Debug");
			
			resultAtts.add(doorDevice.getName() + "/Result");
		} 
		catch (ConnectionException e) 
		{
			e.printStackTrace();
		}
		
    	List<IStringSpectrum> stringSpectrums = new ArrayList<IStringSpectrum>();
  
    	if(outputAtts.size() > 0)
    	{
			for (int i = 0; i < outputAtts.getSize(); i++) 
			{
				strSpectrumAtt = (IStringSpectrum) outputAtts.getElementAt(i);
				stringSpectrums.add(strSpectrumAtt);	
			}
			SimpleMultiOutputViewer outputMultiSpViewer= new SimpleMultiOutputViewer(10000);
			outputMultiSpViewer.setModels(stringSpectrums);	
			outputMultiSpViewer.setBorder(null);
			outputTabbedPane.add(outputMultiSpViewer,"Output");
    	}
		
		if(debugAtts.size() > 0)
		{
			strSpectrumAtt = (IStringSpectrum) debugAtts.getElementAt(0);
			SimpleOutputViewer debugViewer = new SimpleOutputViewer(10000);
			debugViewer.setModel(strSpectrumAtt);
			outputTabbedPane.add(debugViewer,"Debug");
		}
		
		if(resultAtts.size() > 0)
		{
			strSpectrumAtt = (IStringSpectrum) resultAtts.getElementAt(0);
			SimpleOutputViewer resultViewer = new SimpleOutputViewer(10000);
			resultViewer.setModel(strSpectrumAtt);
			outputTabbedPane.add(resultViewer,"Result");
		}
	}
}
