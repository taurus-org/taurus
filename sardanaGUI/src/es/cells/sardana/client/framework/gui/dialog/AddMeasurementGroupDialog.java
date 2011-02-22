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
import java.util.logging.Logger;

import javax.swing.BoxLayout;
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
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceData;

public class AddMeasurementGroupDialog extends JDialog
{
	DevicePool devicePool;
	MeasurementGroup measurementGroup;
	private JButton createButton;
	private JButton exitButton;
	
	private JTextField nameText;
	private JList availableChannels;
	private JList selectedChannels;
	private JButton selectChannelButton;
	private JButton unselectChannelButton;
	
	private static Logger log = SardanaManager.getInstance().getLogger(AddMeasurementGroupDialog.class.getName());
	
	public AddMeasurementGroupDialog(DevicePool devicePool, MeasurementGroup measurementGroup)
	{
		super();
		
		this.devicePool = devicePool;
		this.measurementGroup = measurementGroup;
		
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

		JLabel nameLabel = new JLabel("Measurement Group Name:");
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
		
		JPanel channelsPanel = createChannelsPanel();
		
		gbc.gridx = 0;
		gbc.gridy = 1;
		gbc.gridwidth = 2;
		gbc.fill = GridBagConstraints.BOTH;
		gbc.anchor = GridBagConstraints.CENTER;
		gbc.weightx = 100.0;
		gbc.weighty = 100.0;
		mainPanel.add(channelsPanel, gbc);
		
		setTitle("Add new Measurement Group");
		
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
		
		pack();
		
		fillComponents();
	}

	private void fillComponents()
	{
		DefaultListModel listModel = new DefaultListModel();
		
		for(ExperimentChannel channel : devicePool.getExperimentChannels())
			listModel.addElement(channel);
		
		availableChannels.setModel(listModel);
	}

	private JPanel createChannelsPanel()
	{
		JPanel panel = new JPanel( new GridBagLayout() );
		
		GridBagConstraints gbc = new GridBagConstraints();

		availableChannels = new JList( );
		JScrollPane availableScroll = new JScrollPane(availableChannels);
		availableChannels.addListSelectionListener( new ListSelectionListener()
		{
			public void valueChanged(ListSelectionEvent e)
			{
				updateSelectionButtons();
			}
		});
		
		selectedChannels = new JList( new DefaultListModel() );
		JScrollPane selectedScroll = new JScrollPane(selectedChannels);
		selectedChannels.addListSelectionListener( new ListSelectionListener()
		{
			public void valueChanged(ListSelectionEvent e)
			{
				updateSelectionButtons();
			}
		});
		
		selectChannelButton = new JButton(">>");
		unselectChannelButton = new JButton("<<");
		
		JPanel buttonPanel = new JPanel( );
		BoxLayout boxLayout = new BoxLayout(buttonPanel, BoxLayout.Y_AXIS);
		buttonPanel.setLayout(boxLayout);
		
		buttonPanel.add(selectChannelButton, 0);
		buttonPanel.add(unselectChannelButton, 1);
		
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;		
		panel.add( new JLabel("Available Channels"), gbc);

		gbc.gridx = 2;
		gbc.gridy = 0;
		panel.add( new JLabel("Selected Channels"), gbc);
		
		gbc.gridx = 0;
		gbc.gridy = 1;
		gbc.weightx = 50.0;
		gbc.weighty = 100.0;		
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
		gbc.weightx = 50.0;
		gbc.weighty = 100.0;		
		gbc.fill = GridBagConstraints.BOTH;
		panel.add(selectedScroll, gbc);
		
		selectChannelButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				selectChannel(e);
			}	
		});
		
		unselectChannelButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				unselectedChannel(e);
			}	
		});		
		
		return panel;
	}

	protected void unselectedChannel(ActionEvent e)
	{
		Object[] channels = selectedChannels.getSelectedValues();
		
		if(channels == null || channels.length == 0)
			return;
		
		for(Object channel : channels)
		{
			((DefaultListModel)availableChannels.getModel()).addElement(channel);
			((DefaultListModel)selectedChannels.getModel()).removeElement(channel);
		}
		
		updateSelectionButtons();
	}

	protected void selectChannel(ActionEvent e)
	{
		Object[] channels = availableChannels.getSelectedValues();

		if(channels == null || channels.length == 0)
			return;
		
		for(Object channel : channels)
		{
			((DefaultListModel)selectedChannels.getModel()).addElement(channel);
			((DefaultListModel)availableChannels.getModel()).removeElement(channel);
		}
		
		updateSelectionButtons();
	}

	private void updateSelectionButtons()
	{
		boolean selectEnabled = availableChannels.getModel().getSize() > 0;
		selectEnabled &= availableChannels.getSelectedIndex() >= 0;
		
		selectChannelButton.setEnabled(selectEnabled);
		
		boolean unselectEnabled = selectedChannels.getModel().getSize() > 0;
		unselectEnabled &= selectedChannels.getSelectedIndex() >= 0;
		
		unselectChannelButton.setEnabled(unselectEnabled);		
	}
	
	protected void closeAndExit()
	{
		dispose();
	}
	
	protected void hideAndExit()
	{
		measurementGroup = null;
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
	
	protected void createPressed(ActionEvent e)
	{
		String name = nameText.getText();
		
		if(name == null || name.length() == 0)
		{
			JOptionPane.showMessageDialog(this, "Invalid Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}		

		if(selectedChannels.getModel().getSize() == 0)
		{
			JOptionPane.showMessageDialog(this, "You have to select at least one channel", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}
		
		int channelCount = selectedChannels.getModel().getSize();
		String[] strParams = new String[channelCount + 1];
		
		try
		{ 	
			strParams[0] = name;
			
			for(int i = 0; i < channelCount; i++)
			{
				strParams[i+1] = ((ExperimentChannel)selectedChannels.getModel().getElementAt(i)).getName();
			}
			
			DeviceData args = new DeviceData();
			args.insert(strParams);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_MEASUREMENT_GROUP,
					args);
			
			JOptionPane.showMessageDialog(this,
					"Measurement group " + name + " sucessfully created","Sucess!", JOptionPane.INFORMATION_MESSAGE);

		}
		catch (DevFailed devFailed)
		{
			StringBuffer channels = new StringBuffer();
			
			for(int i = 0; i < strParams.length; i++)
				channels.append(strParams[i] + ", ");
			
			log.fine("User error trying to create Measurement group with: " + name + " and channels: " + channels.toString());

			StringBuffer buff = new StringBuffer("Reason:\n");
			
			for(DevError elem : devFailed.errors)
			{
				buff.append( elem.desc + "\n");
			}
			
			JOptionPane.showMessageDialog(this, 
					buff.toString(),
					"Error trying to create a new measurement group", 
					JOptionPane.ERROR_MESSAGE);
		}
	}
}

