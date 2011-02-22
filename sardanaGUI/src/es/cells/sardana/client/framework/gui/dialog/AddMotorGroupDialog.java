package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

import javax.swing.BoxLayout;
import javax.swing.DefaultListCellRenderer;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.WindowConstants;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class AddMotorGroupDialog extends JDialog implements IStringSpectrumListener
{
	DevicePool devicePool;
	MotorGroup motorGroup;
	private JButton createButton;
	private JButton exitButton;
	
	private JTextField nameText;
	private JList availableMotors;
	private JList selectedMotors;
	private JButton selectMotorButton;
	private JButton unselectMotorButton;
	
	private static Logger log = SardanaManager.getInstance().getLogger(AddMotorGroupDialog.class.getName());
	
	public AddMotorGroupDialog(DevicePool devicePool, MotorGroup motorGroup)
	{
		super();
		
		this.devicePool = devicePool;
		this.motorGroup = motorGroup;
		
		initComponents();
	}
	
	protected void initComponents()
	{
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

		JLabel nameLabel = new JLabel("Motor Group Name:");
		nameText = new JTextField(20);

		GridBagConstraints gbc = new GridBagConstraints();

		gbc.insets = new Insets(2, 2, 2, 2);
		gbc.anchor = GridBagConstraints.EAST;
		gbc.fill = GridBagConstraints.HORIZONTAL;

		gbc.gridx = 0;
		gbc.gridy = 0;
		mainPanel.add(nameLabel, gbc);
		
		gbc.anchor = GridBagConstraints.WEST;
		gbc.gridx = 1;
		gbc.gridy = 0;
		mainPanel.add(nameText, gbc);
		
		JPanel motorsPanel = createMotorsPanel();
		
		gbc.gridx = 0;
		gbc.gridy = 1;
		gbc.gridwidth = 2;
		gbc.fill = GridBagConstraints.BOTH;
		gbc.anchor = GridBagConstraints.CENTER;
		gbc.weightx = 1.0;
		gbc.weighty = 1.0;
		mainPanel.add(motorsPanel, gbc);
		
		setTitle("Add new Motor Group");
		
		ButtonsPanel buttonsPanel = new ButtonsPanel();
		
		createButton = new JButton("Create", SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
		exitButton = new JButton("Close", SwingResource.smallIconMap.get(IImageResource.IMG_CLOSE));
		
		createButton.setToolTipText("Create a new measurement group");
		exitButton.setToolTipText("Close window");

		
		buttonsPanel.addRight(createButton);
		buttonsPanel.addRight(exitButton);
		
		createButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				createPressed(e);
			}
		});
		
		exitButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				exitPressed(e);
			}
		});
		
		getContentPane().add(buttonsPanel, BorderLayout.SOUTH);
		
		updateSelectionButtons();
		fillComponents();
		
		devicePool.addMotorListListener(this);
		devicePool.addPseudoMotorListListener(this);
		devicePool.addMotorGroupListListener(this);
		
		pack();
	}

	protected void updateElements(List<SardanaDevice> elements)
	{
		DefaultListModel availableModel = (DefaultListModel)availableMotors.getModel();
		DefaultListModel selectedModel = (DefaultListModel)selectedMotors.getModel();
		
		ArrayList<SardanaDevice> oldSelected = new ArrayList<SardanaDevice>(selectedModel.getSize());
		for(int i = 0; i < selectedModel.getSize();i++)
			oldSelected.add((SardanaDevice)selectedModel.getElementAt(i));
		
		availableModel.removeAllElements();
		selectedModel.removeAllElements();
		
		for(SardanaDevice elem : elements)
		{
			if(oldSelected.contains(elem))
				selectedModel.addElement(elem);
			else
				availableModel.addElement(elem);
		}
	}
	
	private void fillComponents()
	{
		DefaultListModel listModel = new DefaultListModel();
		
		for(Motor m : devicePool.getMotors())
			listModel.addElement(m);

		for(MotorGroup mg : devicePool.getMotorGroups())
			listModel.addElement(mg);
		
		for(PseudoMotor pm : devicePool.getPseudoMotors())
			listModel.addElement(pm);
		
		availableMotors.setModel(listModel);
	}

	private JPanel createMotorsPanel()
	{
		JPanel panel = new JPanel( new GridBagLayout() );
		
		GridBagConstraints gbc = new GridBagConstraints();

		availableMotors = new JList( );
		JScrollPane availableScroll = new JScrollPane(availableMotors);
		availableMotors.setCellRenderer(new ElementCellRenderer());
		availableMotors.addListSelectionListener( new ListSelectionListener()
		{
			public void valueChanged(ListSelectionEvent e)
			{
				updateSelectionButtons();
			}
		});
		
		selectedMotors = new JList( new DefaultListModel() );
		JScrollPane selectedScroll = new JScrollPane(selectedMotors);
		selectedMotors.setCellRenderer(new ElementCellRenderer());
		selectedMotors.addListSelectionListener( new ListSelectionListener()
		{
			public void valueChanged(ListSelectionEvent e)
			{
				updateSelectionButtons();
			}
		});
		
		selectMotorButton = new JButton(">>");
		unselectMotorButton = new JButton("<<");
		
		JPanel buttonPanel = new JPanel( );
		BoxLayout boxLayout = new BoxLayout(buttonPanel, BoxLayout.Y_AXIS);
		buttonPanel.setLayout(boxLayout);
		
		buttonPanel.add(selectMotorButton, 0);
		buttonPanel.add(unselectMotorButton, 1);
		
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;		
		panel.add( new JLabel("Available Motors"), gbc);

		gbc.gridx = 2;
		gbc.gridy = 0;
		panel.add( new JLabel("Selected Motors"), gbc);
		
		gbc.gridx = 0;
		gbc.gridy = 1;
		gbc.weightx = 0.0;
		gbc.weighty = 1.0;		
		gbc.insets = new Insets(2, 2, 2, 2);
		gbc.fill = GridBagConstraints.BOTH;
		panel.add(availableScroll, gbc);
		
		gbc.gridx = 1;
		gbc.gridy = 1;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;		
		gbc.fill = GridBagConstraints.NONE;
		panel.add(buttonPanel, gbc);
		
		gbc.gridx = 2;
		gbc.gridy = 1;
		gbc.weightx = 0.0;
		gbc.weighty = 1.0;		
		gbc.fill = GridBagConstraints.BOTH;
		panel.add(selectedScroll, gbc);
		
		selectMotorButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				selectMotor(e);
			}	
		});
		
		unselectMotorButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				unselectMotor(e);
			}	
		});		
		
		return panel;
	}

	protected void unselectMotor(ActionEvent e)
	{
		Object[] motors = selectedMotors.getSelectedValues();
		
		if(motors == null || motors.length == 0)
			return;
		
		for(Object motor : motors)
		{
			((DefaultListModel)availableMotors.getModel()).addElement(motor);
			((DefaultListModel)selectedMotors.getModel()).removeElement(motor);
		}
		
		updateSelectionButtons();
	}

	protected void selectMotor(ActionEvent e)
	{
		Object[] motors = availableMotors.getSelectedValues();

		if(motors == null || motors.length == 0)
			return;
		
		for(Object motor : motors)
		{
			((DefaultListModel)selectedMotors.getModel()).addElement(motor);
			((DefaultListModel)availableMotors.getModel()).removeElement(motor);
		}
		
		updateSelectionButtons();
	}

	private void updateSelectionButtons()
	{
		boolean selectEnabled = availableMotors.getModel().getSize() > 0;
		selectEnabled &= availableMotors.getSelectedIndex() >= 0;
		
		selectMotorButton.setEnabled(selectEnabled);
		
		boolean unselectEnabled = selectedMotors.getModel().getSize() > 0;
		unselectEnabled &= selectedMotors.getSelectedIndex() >= 0;
		
		unselectMotorButton.setEnabled(unselectEnabled);		
	}
	
	protected void closeAndExit()
	{
		devicePool.removeMotorListListener(this);
		devicePool.removePseudoMotorListListener(this);
		devicePool.removeMotorGroupListListener(this);
		
		dispose();
	}
	
	protected void hideAndExit()
	{
		motorGroup = null;
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
		closeAndExit();
	}
	
	protected void createPressed(ActionEvent e)
	{
		String name = nameText.getText();
		
		if(name == null || name.length() == 0)
		{
			JOptionPane.showMessageDialog(this, "Invalid Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}		

		if(selectedMotors.getModel().getSize() == 0)
		{
			JOptionPane.showMessageDialog(this, "You have to select at least one motor", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}
		
		int motorCount = selectedMotors.getModel().getSize();
		String[] strParams = new String[motorCount + 1];
		
		try
		{ 	
			strParams[0] = name;
			
			for(int i = 0; i < motorCount; i++)
			{
				strParams[i+1] = ((SardanaDevice)selectedMotors.getModel().getElementAt(i)).getName();
			}
			
			DeviceData args = new DeviceData();
			args.insert(strParams);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_MOTOR_GROUP,
					args);
			
			JOptionPane.showMessageDialog(this,
					"Motor group " + name + " sucessfully created","Sucess!", JOptionPane.INFORMATION_MESSAGE);
			
		}
		catch (DevFailed devFailed)
		{
			StringBuffer motors = new StringBuffer();
			
			for(int i = 0; i < strParams.length; i++)
				motors.append(strParams[i] + ", ");
			
			log.fine("User error trying to create Motor group with: " + name + " and motors: " + motors.toString());

			StringBuffer buff = new StringBuffer("Reason:\n");
			
			for(DevError elem : devFailed.errors)
			{
				buff.append( elem.desc + "\n");
			}
			
			JOptionPane.showMessageDialog(this, 
					buff.toString(),
					"Error trying to create a new motor group", 
					JOptionPane.ERROR_MESSAGE);
		}
	}
	
	class ElementCellRenderer extends DefaultListCellRenderer
	{
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) 
		{
			Component c = super.getListCellRendererComponent(
					list, value,
					index, isSelected, cellHasFocus);
			
			SardanaDevice sardanaDevice = (SardanaDevice) value;
			
			if(c instanceof JLabel)
			{
				JLabel l = (JLabel) c;
				//l.setVerticalTextPosition(SwingConstants.BOTTOM);
				//l.setHorizontalTextPosition(SwingConstants.RIGHT);
				l.setIcon(SwingResource.smallIconMap.get(IImageResource.getDeviceElementIcon(sardanaDevice)));
				l.setForeground(SwingResource.getColorForElement(value));
			}
			return c;
		}
	}

	public void stringSpectrumChange(StringSpectrumEvent evt) 
	{
		ArrayList<SardanaDevice> elems = new ArrayList<SardanaDevice>(devicePool.getMotors());
		elems.addAll(devicePool.getPseudoMotors());
		elems.addAll(devicePool.getMotorGroups());
		updateElements(elems);
	}

	public void stateChange(AttributeStateEvent evt) {}

	public void errorChange(ErrorEvent evt) {}	
}

