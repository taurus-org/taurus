package es.cells.sardana.light.model;

import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFormattedTextField;
import javax.swing.JLabel;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.JSpinner.DefaultEditor;
import javax.swing.text.DefaultFormatterFactory;
import javax.swing.text.NumberFormatter;

import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.ISpectrumListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.NumberSpectrumEvent;
import fr.esrf.tangoatk.core.command.CommandFactory;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MovElement extends Element
{
	public static final ImageIcon applyIcon = new ImageIcon("res/16x16/forward.png");
	public static final ImageIcon abortIcon = new ImageIcon("res/24x24/stop.png");
	public static final ImageIcon copyIcon = new ImageIcon("res/16x16/editcopy.png");
	
	public JLabel positionLabel[];
	public JSpinner positionSpinner[];
	public JButton copyPositionButton[];
	public JButton applyPositionButton = new JButton(applyIcon);
	public JButton abortCommand = new JButton("Abort", abortIcon);
	public JLabel positionEventCountLabel = new JLabel("not set");
	public PositionListener positionListener = new PositionListener();
	public PositionArrayListener positionArrayListener = new PositionArrayListener();
	
	public int positionSize = 1;
	
	public long positionEventCount = 0;
	
	public ICommand abortCmd;
	public IEntity positionAttribute;
	
	private DecimalFormat positionFormat = new DecimalFormat("0000.00");
	private DecimalFormat eventFormat = new DecimalFormat("#00");
	
	class PositionListener implements INumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent evt) 
		{
			positionEventCount++;
			positionEventCountLabel.setText(eventFormat.format(positionEventCount));
			positionLabel[0].setText(positionFormat.format(evt.getValue()));

			//System.out.println("received pos changed for " + name + " with value " + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			positionLabel[0].setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt)	{}
	}
	
	class PositionArrayListener implements ISpectrumListener
	{
		public void spectrumChange(NumberSpectrumEvent evt) 
		{
			positionEventCount++;
			positionEventCountLabel.setText(eventFormat.format(positionEventCount));
			StringBuffer b = new StringBuffer();
			
			double[] value = evt.getValue();
			for(int i = 0 ; i < positionSize; i++)
			{
				positionLabel[i].setText(positionFormat.format(value[i]));
				b.append(value[i] + ", ");
			}
			
			//System.out.println("received pos arry changed for " + name + " with value " + b.toString());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			for(JLabel lbl : positionLabel)
				lbl.setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt) {}
	}

	protected ActionListener getApplyPositionActionListener()
	{
		return new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				INumberScalar s = (INumberScalar) positionAttribute;
				s.setValue(Double.valueOf(positionSpinner[0].getValue().toString()));
			}
		};
	}

	public MovElement(String name, String deviceName, int posSize)
	{
		super(name,deviceName);
		this.positionSize = posSize;
		
		try 
		{
			abortCmd = CommandFactory.getInstance().getCommand(MovElement.this.deviceName + "/Abort");
		} 
		catch (Exception exp) 
		{
			exp.printStackTrace();
			System.exit(-5);
		}
		
		abortCommand.setMargin(new Insets(1,2,1,2));
		abortCommand.addActionListener(new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				abortCmd.execute();
			}
		});

		applyPositionButton.setMargin( new Insets(1,1,1,1));
		applyPositionButton.setToolTipText("Send new position");
		applyPositionButton.addActionListener(getApplyPositionActionListener());
		
		positionLabel = new JLabel[positionSize];
		for(int i = 0; i < positionSize;i ++)
			positionLabel[i] = new JLabel("not set");
		
		positionSpinner = new JSpinner[positionSize];
		copyPositionButton = new JButton[positionSize];
		for(int i = 0; i < positionSize;i ++)
		{
			positionSpinner[i] = new JSpinner(new SpinnerNumberModel());
			
			DefaultEditor editor = (DefaultEditor)positionSpinner[i].getEditor();
			JFormattedTextField textField = editor.getTextField();
			NumberFormatter nf = new NumberFormatter(positionFormat);
			DefaultFormatterFactory factory = new DefaultFormatterFactory(nf);
			textField.setFormatterFactory(factory);
			
			copyPositionButton[i] = new JButton(copyIcon);
			copyPositionButton[i].setMargin( new Insets(1,1,1,1));
			copyPositionButton[i].setToolTipText("Copy current position to editor field");
			final int pos = i;
			copyPositionButton[i].addActionListener( new ActionListener()
			{
				int idx = pos;
				public void actionPerformed(ActionEvent e) 
				{
					positionSpinner[idx].setValue(Double.valueOf(positionLabel[idx].getText()));
				}
			});
		}
	}
	
	
}
