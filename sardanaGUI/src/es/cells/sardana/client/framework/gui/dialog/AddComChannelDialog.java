package es.cells.sardana.client.framework.gui.dialog;

import java.awt.Component;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.Arrays;
import java.util.List;
import java.util.logging.Logger;

import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JSpinner;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.pool.CommunicationChannel;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.ControllerClass;
import es.cells.sardana.client.framework.pool.ControllerType;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.Tango.DevVarLongStringArray;
import fr.esrf.TangoApi.DeviceData;


public class AddComChannelDialog extends JDialog 
{
	DevicePool devicePool;
	CommunicationChannel channel;

	private ButtonsPanel buttonsPanel;
    private JButton createButton;
    private JButton exitButton;

    private JComboBox controllerCombo;
    private JSpinner indexSpinner;
    private JTextField nameTextField;
    
	private static Logger log = SardanaManager.getInstance().getLogger(AddMotorDialogWizard.class.getName());
	
	public AddComChannelDialog()
	{
		super();
		setTitle("Create Communication Channel");
	}
			
	public AddComChannelDialog(DevicePool devicePool)
	{
		this();
		this.devicePool = devicePool;
		init();
	}
	
	public AddComChannelDialog(DevicePool devicePool, CommunicationChannel channel)
	{
		this();
		this.devicePool = devicePool;
		this.channel = channel;
		init();
	}
	
	protected void closeAndExit()
	{
		dispose();
	}
	
	protected void exitPressed(ActionEvent e)
	{
		closeAndExit();
	}
	
	protected void hideAndExit()
	{
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
	
	void updateControllers()
	{
		controllerCombo.removeAllItems();

		for(Controller ctrl : devicePool.getControllers() )
			if(ctrl.getType() == ControllerType.Communication)
				controllerCombo.addItem(ctrl);

		if(channel != null)
			controllerCombo.setSelectedItem(channel.getController());
		else if(controllerCombo.getItemCount() > 0)
			controllerCombo.setSelectedIndex(0);
	}
	
	protected void init()
	{
		setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});
		setLayout(new GridBagLayout());		
		
		controllerCombo = new JComboBox();
		
		if(channel != null)
		{
			controllerCombo.setEnabled(false);
		}
		
		indexSpinner = new JSpinner();
		nameTextField = new JTextField();
		
		ChannelNumberModel channelModel = new ChannelNumberModel();
		controllerCombo.addActionListener(channelModel);
		indexSpinner.setModel(channelModel);
		
        GridBagConstraints gbc;

        gbc = new GridBagConstraints(
        		0, 0, //grid
        		1, 1, // width, height
        		0.0, 0.0, // weight
        		GridBagConstraints.EAST, // anchor
        		GridBagConstraints.NONE, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(new JLabel("Controller:"), gbc);
        
        gbc = new GridBagConstraints(
        		1, 0, //grid
        		1, 1, // width, height
        		0.0, 0.0, // weight
        		GridBagConstraints.WEST, // anchor
        		GridBagConstraints.HORIZONTAL, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(controllerCombo, gbc);
        
        gbc = new GridBagConstraints(
        		0, 1, //grid
        		1, 1, // width, height
        		0.0, 0.0, // weight
        		GridBagConstraints.EAST, // anchor
        		GridBagConstraints.NONE, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(new JLabel("Index in controller:"), gbc);
        
        gbc = new GridBagConstraints(
        		1, 1, //grid
        		1, 1, // width, height
        		0.0, 0.0, // weight
        		GridBagConstraints.WEST, // anchor
        		GridBagConstraints.HORIZONTAL, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(indexSpinner, gbc);
        
        gbc = new GridBagConstraints(
        		0, 2, //grid
        		1, 1, // width, height
        		0.0, 0.0, // weight
        		GridBagConstraints.EAST, // anchor
        		GridBagConstraints.NONE, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(new JLabel("Name:"), gbc);
        
        gbc = new GridBagConstraints(
        		1, 2, //grid
        		1, 1, // width, height
        		0.0, 0.0, // weight
        		GridBagConstraints.WEST, // anchor
        		GridBagConstraints.HORIZONTAL, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(nameTextField, gbc);        
        
		createButton = new JButton("Create", SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
		exitButton = new JButton("Close", SwingResource.smallIconMap.get(IImageResource.IMG_CLOSE));
		
		createButton.setToolTipText("Create a new communication channel");
		exitButton.setToolTipText("Close window");

		buttonsPanel = new ButtonsPanel();
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
		
        gbc = new GridBagConstraints(
        		0, 3, //grid
        		2, 1, // width, height
        		1.0, 0.0, // weight
        		GridBagConstraints.CENTER, // anchor
        		GridBagConstraints.HORIZONTAL, // fill
        		new Insets(2,2,2,2),
        		0, 0 // pad
        		);
        add(buttonsPanel, gbc);        
		
        updateControllers();
        
		pack();
		setVisible(true);
	}
	
	protected void createPressed(ActionEvent e)
	{
		Controller ctrl = (Controller) controllerCombo.getSelectedItem();
		
		if(ctrl == null)
		{
			JOptionPane.showMessageDialog(this, "Invalid Controller!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}
		
		int index = (Integer) indexSpinner.getValue();
		
		String name = nameTextField.getText();
		
		if(name == null || name.length() == 0)
		{
			JOptionPane.showMessageDialog(this, "Invalid Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}		
		
		try
		{
			int[] iParams = new int[] { index };
			String[] strParams = new String[] { name, ctrl.getName() };
			
			DevVarLongStringArray params = new DevVarLongStringArray(
					iParams,
					strParams);
			
			DeviceData args = new DeviceData();
			args.insert(params);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_COM_CHANNEL,args);
			
			JOptionPane.showMessageDialog(this,
					"Communication channel " + name + " sucessfully created","Sucess!", JOptionPane.INFORMATION_MESSAGE);

		}
		catch (DevFailed devFailed)
		{
			log.fine("User error trying to create communication channel with: " + ctrl.getName() + ", " + index + ", " + name);
			StringBuffer buff = new StringBuffer("Reason:\n");
			
			for(DevError elem : devFailed.errors)
			{
				buff.append( elem.desc + "\n");
			}
			
			JOptionPane.showMessageDialog(this, 
					buff.toString(),
					"Error trying to create a new communication channel", 
					JOptionPane.ERROR_MESSAGE);
		}
		
		//force update of the spinner
		((ChannelNumberModel)indexSpinner.getModel()).actionPerformed( new ActionEvent(controllerCombo,0,"") );		
	}
	
	class ChannelNumberModel extends SpinnerNumberModel implements ActionListener 
	{
		protected int[] invalidChannelNumbers;
		
		
		public ChannelNumberModel()
		{
			super(new Integer(1), null, null, new Integer(1));
			invalidChannelNumbers = new int[0];
		}
		
		public Object getNextValue()
		{
			int currValue = getNumber().intValue();
			int step = getStepSize().intValue();
			int nextValue = currValue;

			do
			{
				nextValue += step;
			}
			while(Arrays.binarySearch(invalidChannelNumbers, nextValue) >= 0); 

			return nextValue;
		}

		public Object getPreviousValue()
		{
			int currValue = getNumber().intValue();
			int step = getStepSize().intValue();
			int previousValue = currValue;
			
			do
			{
				previousValue -= step;
			}
			while(Arrays.binarySearch(invalidChannelNumbers, previousValue) >= 0); 

			if(previousValue < 1)
				previousValue = findFirstAvailable();
			
			return previousValue;
		}

		protected int findFirstAvailable()
		{
			if(invalidChannelNumbers.length == 0)
				return 1;
			if(invalidChannelNumbers.length == 1)
				return invalidChannelNumbers[0] > 1 ? 1 : 2;
				
			for(int index = 1 ; index < invalidChannelNumbers.length ; index++)
			{
				if(invalidChannelNumbers[index] - invalidChannelNumbers[index-1] > 1)
					return invalidChannelNumbers[index-1]+1;
			}
			return invalidChannelNumbers[invalidChannelNumbers.length-1]+1;
		}
		
		public void actionPerformed(ActionEvent e)
		{
			Controller ctrl = (Controller) controllerCombo.getSelectedItem();
		
			if(ctrl == null)
			{
				invalidChannelNumbers = new int[0];
				return;
			}
			
			List<SardanaDevice> channels = ctrl.getElements();
			
			invalidChannelNumbers = new int[channels.size()];
			
			int i = 0;
			for(SardanaDevice elem : channels)
			{
				CommunicationChannel comChannel = (CommunicationChannel)elem;
				invalidChannelNumbers[i++] = comChannel.getIdInController();
			}
			
			Arrays.sort(invalidChannelNumbers);
			
			setValue(findFirstAvailable());
		}		
	}	
}
