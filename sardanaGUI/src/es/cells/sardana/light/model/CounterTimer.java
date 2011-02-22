package es.cells.sardana.light.model;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFormattedTextField;
import javax.swing.JLabel;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.JSpinner.DefaultEditor;
import javax.swing.text.DefaultFormatterFactory;
import javax.swing.text.NumberFormatter;

import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.command.CommandFactory;

public class CounterTimer extends AquisitionElement 
{
	public static final ImageIcon copyIcon = new ImageIcon("res/16x16/editcopy.png");
	public static final ImageIcon startIcon = new ImageIcon("res/24x24/actions/player_play.png");
	public static final ImageIcon stopIcon = new ImageIcon("res/24x24/player_stop.png");
	
	public ICommand startCmd;
	public ICommand stopCmd;

	public JButton startCommand = new JButton(startIcon);
	public JButton stopCommand = new JButton(stopIcon);
	
	public CounterTimer(String name, String deviceName) 
	{
		super(name, deviceName, 1, 1);
		
		try
		{
			startCmd = CommandFactory.getInstance().getCommand(deviceName + "/Start");
			stopCmd = CommandFactory.getInstance().getCommand(deviceName + "/Stop");
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
		startCommand.setToolTipText("Send Start command");
		stopCommand.setToolTipText("Send Stop command");
		
		valueLabel = new JLabel[1];
		valueSpinner = new JSpinner[1];
		
		valueLabel[0] = new JLabel("not set");
		valueSpinner[0] = new JSpinner(new SpinnerNumberModel());
		
		DefaultEditor editor = (DefaultEditor)valueSpinner[0].getEditor();
		JFormattedTextField textField = editor.getTextField();
		NumberFormatter nf = new NumberFormatter(valueFormat);
		DefaultFormatterFactory factory = new DefaultFormatterFactory(nf);
		textField.setFormatterFactory(factory);

		copyValueButton = new JButton[1];
		copyValueButton[0] = new JButton(copyIcon);
		copyValueButton[0].setMargin( new Insets(1,1,1,1));
		copyValueButton[0].setToolTipText("Copy current value to editor field");
		copyValueButton[0].addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				valueSpinner[0].setValue(Double.valueOf(valueLabel[0].getText()));
			}
		});
		
		
		startCommand.setMargin(new Insets(1,2,1,2));
		startCommand.addActionListener(new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				startCmd.execute();
			}
		});

		stopCommand.setMargin(new Insets(1,2,1,2));
		stopCommand.addActionListener(new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				stopCmd.execute();
			}
		});
	
		elementPanel.setLayout( new GridBagLayout() );
		
		GridBagConstraints gbc = new GridBagConstraints(
				0, 0, // grid
				1, 1, // width,height
				1.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(4,2,4,2),
				0,0 // pad
				);	
		
		JLabel nameLabel = new JLabel(name); 
		elementPanel.add(nameLabel,gbc);

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
		
		gbc = new GridBagConstraints(
				3, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);

		JLabel valueNameLabel = new JLabel(" value: ");
		elementPanel.add(valueNameLabel,gbc);
		
		gbc = new GridBagConstraints(
				4, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(valueLabel[0],gbc);

		gbc = new GridBagConstraints(
				5, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(valueSpinner[0],gbc);

		gbc = new GridBagConstraints(
				6, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(copyValueButton[0],gbc);

		gbc = new GridBagConstraints(
				7, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(applyValueButton,gbc);
		
		
		gbc = new GridBagConstraints(
				8, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
				
		elementPanel.add(startCommand,gbc);

		gbc = new GridBagConstraints(
				9, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(stopCommand,gbc);

	}

}
