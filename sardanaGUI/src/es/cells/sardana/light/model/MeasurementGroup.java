package es.cells.sardana.light.model;

import java.awt.Color;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Vector;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFormattedTextField;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingConstants;
import javax.swing.JSpinner.DefaultEditor;
import javax.swing.text.DefaultFormatterFactory;
import javax.swing.text.NumberFormatter;

import fr.esrf.tangoatk.core.AttributeSetException;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.IStringScalarListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.StringScalarEvent;
import fr.esrf.tangoatk.core.command.CommandFactory;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MeasurementGroup extends AquisitionElement 
{
	public static final ImageIcon abortIcon = new ImageIcon("res/24x24/stop.png");
	public static final ImageIcon copyIcon = new ImageIcon("res/16x16/editcopy.png");
	public static final ImageIcon startIcon = new ImageIcon("res/24x24/player_play.png");
	
	public String[] user_elems;
	public IEntity[] valueAttributes;
	
	public INumberScalar integrationTime;
	public INumberScalar integrationCount;
	public IStringScalar timer;
	public IStringScalar monitor;
	
	public IntegrationTimeListener integrationTimeListener = new IntegrationTimeListener();
	public IntegrationCountListener integrationCountListener = new IntegrationCountListener();
	public TimerListener timertListener = new TimerListener();
	public MonitorListener monitortListener = new MonitorListener();
	
	public ValueListener[] valueListeners;
	
	public JSpinner integrationTimeSpinner;
	public JSpinner integrationCountSpinner;
	public JButton applyIntegrationTime = new JButton(applyIcon);
	public JButton applyIntegrationCount = new JButton(applyIcon);
	
	public JComboBox timerCombo;
	public JComboBox monitorCombo;
	public JButton applyTimer = new JButton(applyIcon);
	public JButton applyMonitor = new JButton(applyIcon);
	
	enum MGMode { None, Timer, Monitor };
	
	public MGMode mode = MGMode.None;
	
	public ICommand startCmd;
	public ICommand abortCmd;

	public JButton startCommand = new JButton(startIcon);
	public JButton abortCommand = new JButton(abortIcon);
	
	class IntegrationTimeListener implements INumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent evt) 
		{
			double v  = evt.getValue();
			if(v == 0.0)
				integrationCountSpinner.setForeground(Color.LIGHT_GRAY);
			else 
				integrationCountSpinner.setForeground(Color.WHITE);
			integrationTimeSpinner.setValue(new Double(v));
			System.out.println("Received event on integration time with value " + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			integrationTimeSpinner.setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt)	{}
	}
	
	class IntegrationCountListener implements INumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent evt) 
		{
			double v  = evt.getValue();
			if(v == 0.0)
				integrationCountSpinner.setForeground(Color.LIGHT_GRAY);
			else 
				integrationCountSpinner.setForeground(Color.WHITE);
			integrationCountSpinner.setValue(new Double(v));
			System.out.println("Received event on integration count with value " + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			integrationCountSpinner.setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt)	{}
	}
	
	class TimerListener implements IStringScalarListener
	{
		public void stringScalarChange(StringScalarEvent evt) 
		{
			timerCombo.setSelectedItem(evt.getValue());
			System.out.println("Received event on timer with value " + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			//TODO
		}

		public void errorChange(ErrorEvent evt)	{}
	}

	class MonitorListener implements IStringScalarListener
	{
		public void stringScalarChange(StringScalarEvent evt) 
		{
			monitorCombo.setSelectedItem(evt.getValue());
			System.out.println("Received event on monitor with value " + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			//TODO
		}

		public void errorChange(ErrorEvent evt)	{}
	}

	public MeasurementGroup(String name, String deviceName, String[] user_elems) 
	{
		super(name, deviceName, 1, 1);
		this.user_elems = user_elems; 
		
		try
		{
			startCmd = CommandFactory.getInstance().getCommand(deviceName + "/Start");
			abortCmd = CommandFactory.getInstance().getCommand(deviceName + "/Abort");
		} 
		catch (Exception exp) 
		{
			exp.printStackTrace();
			System.exit(-5);
		}
		
		initComponents();
	}

	private void initComponents() 
	{		
		startCommand.setToolTipText("Start data aquisition");
		abortCommand.setToolTipText("Abort data aquisition");
		
		valueLabel = new JLabel[user_elems.length];
		valueListeners = new ValueListener[user_elems.length];

		integrationTimeSpinner = new JSpinner(new SpinnerNumberModel());
		integrationCountSpinner = new JSpinner(new SpinnerNumberModel());
		
		DefaultEditor editor = (DefaultEditor)integrationTimeSpinner.getEditor();
		JFormattedTextField textField = editor.getTextField();
		NumberFormatter nf = new NumberFormatter(valueFormat);
		DefaultFormatterFactory factory = new DefaultFormatterFactory(nf);
		textField.setFormatterFactory(factory);		
		
		editor = (DefaultEditor)integrationCountSpinner.getEditor();
		textField = editor.getTextField();
		nf = new NumberFormatter(valueFormat);
		factory = new DefaultFormatterFactory(nf);
		textField.setFormatterFactory(factory);			

		for(int i=0;i<user_elems.length;i++)
		{
			valueLabel[i] = new JLabel("not set");
			valueListeners[i] = new ValueListener();
			valueListeners[i].index = i;
		}
				
		startCommand.setMargin(new Insets(1,2,1,2));
		startCommand.addActionListener(new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				startCmd.execute();
			}
		});

		abortCommand.setMargin(new Insets(1,2,1,2));
		abortCommand.addActionListener(new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				abortCmd.execute();
			}
		});
		
		applyIntegrationTime.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				integrationTime.setValue(Double.valueOf(integrationTimeSpinner.getValue().toString()));
			}
		});
		
		applyIntegrationCount.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				integrationCount.setValue(Double.valueOf(integrationCountSpinner.getValue().toString()));
			}
		});

		applyTimer.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				try 
				{
					timer.setValue(timerCombo.getSelectedItem().toString());
				} 
				catch (AttributeSetException e1) 
				{
					e1.printStackTrace();
				}
			}
		});
		
		applyMonitor.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				try 
				{
					monitor.setValue(monitorCombo.getSelectedItem().toString());
				} 
				catch (AttributeSetException e1) 
				{
					e1.printStackTrace();
				}
			}
		});		
		
		Vector<String> chns = new Vector<String>(user_elems.length + 1);

		chns.add("Not Initialized");
		for(int i = 0 ; i < user_elems.length; i++)
			chns.add(user_elems[i]);	
		
		timerCombo = new JComboBox(chns);
		monitorCombo = new JComboBox(chns);
		
		
		
		elementPanel.setLayout( new GridBagLayout() );

		GridBagConstraints gbc = new GridBagConstraints(
				0, 0, // grid
				1, 1, // width,height
				1.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		JLabel nameLabel = new JLabel(name); 
		nameLabel.setHorizontalAlignment(SwingConstants.RIGHT);
		elementPanel.add(nameLabel, gbc);

		gbc = new GridBagConstraints(
				1, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(4,2,4,2),
				0,0 // pad
				);	
		
		JLabel stateTextLabel = new JLabel(" State: "); 
		elementPanel.add(stateTextLabel,gbc);

		gbc = new GridBagConstraints(
				2, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(stateLabel,gbc);
		
		JPanel channelPanel = new JPanel(new GridBagLayout());
		
		for(int i = 0; i < user_elems.length;i++)
		{
			gbc = new GridBagConstraints(
					0, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			channelPanel.add(new JLabel(user_elems[i]),gbc);
			
			gbc = new GridBagConstraints(
					1, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			
			JLabel valueTextLabel = new JLabel("value: "); 
			channelPanel.add(valueTextLabel,gbc);

			gbc = new GridBagConstraints(
					2, i, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			
			channelPanel.add(valueLabel[i],gbc);
		}
		
		gbc = new GridBagConstraints(
				3, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(0,0,0,0),
				0,0 // pad
				);
		
		elementPanel.add(channelPanel,gbc);
		
		gbc = new GridBagConstraints(
				4, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(startCommand,gbc);

		gbc = new GridBagConstraints(
				5, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(abortCommand,gbc);
		
		JPanel ctrlPanel = new JPanel(new GridBagLayout());
		
		gbc = new GridBagConstraints(
				0, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(new JLabel("Integration Time:"),gbc);

		gbc = new GridBagConstraints(
				1, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(integrationTimeSpinner,gbc);

		gbc = new GridBagConstraints(
				2, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.VERTICAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(applyIntegrationTime,gbc);

		gbc = new GridBagConstraints(
				3, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,12,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(timerCombo,gbc);

		gbc = new GridBagConstraints(
				4, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.VERTICAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(applyTimer,gbc);	
		//////////////////////////////////
		
		gbc = new GridBagConstraints(
				0, 1, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(new JLabel("Integration Count:"),gbc);

		gbc = new GridBagConstraints(
				1, 1, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(integrationCountSpinner,gbc);

		gbc = new GridBagConstraints(
				2, 1, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.VERTICAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(applyIntegrationCount,gbc);

		gbc = new GridBagConstraints(
				3, 1, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,12,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(monitorCombo,gbc);

		gbc = new GridBagConstraints(
				4, 1, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.VERTICAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		ctrlPanel.add(applyMonitor,gbc);			
		
		gbc = new GridBagConstraints(
				6, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(ctrlPanel,gbc);
		
	}

	
}
