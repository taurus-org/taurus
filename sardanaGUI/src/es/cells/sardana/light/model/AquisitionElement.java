package es.cells.sardana.light.model;

import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JSpinner;

import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.ISpectrumListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.NumberSpectrumEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;


public class AquisitionElement extends Element
{
	public static final ImageIcon applyIcon = new ImageIcon("res/16x16/forward.png");
	
	public JLabel valueLabel[];
	public JSpinner valueSpinner[];
	public JButton copyValueButton[];
	public JButton applyValueButton = new JButton(applyIcon);
	public JLabel valueEventCountLabel = new JLabel("not set");
	public ValueListener valueListener = new ValueListener();
	public ValueArrayListener valueArrayListener = new ValueArrayListener();
	
	public long valueEventCount = 0;
	
	public int valueSizeX = 1;
	public int valueSizeY = 1;
	
	public IEntity valueAttribute;
	
	protected DecimalFormat valueFormat = new DecimalFormat("0000.00");
	protected DecimalFormat eventFormat = new DecimalFormat("#00");
	
	class ValueListener implements INumberScalarListener
	{
		public int index = 0;
		public void numberScalarChange(NumberScalarEvent evt) 
		{
			valueEventCount++;
			valueEventCountLabel.setText(eventFormat.format(valueEventCount));
			valueLabel[index].setText(valueFormat.format(evt.getValue()));

			//System.out.println("received value " + index + " changed for " + name + " with value " + evt.getValue());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			valueLabel[index].setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt)	{}
	}
	
	class ValueArrayListener implements ISpectrumListener
	{
		public void spectrumChange(NumberSpectrumEvent evt) 
		{
			valueEventCount++;
			valueEventCountLabel.setText(eventFormat.format(valueEventCount));
			StringBuffer b = new StringBuffer();
			
			double[] value = evt.getValue();
			for(int i = 0 ; i < valueSizeX; i++)
			{
				valueLabel[i].setText(valueFormat.format(value[i]));
				b.append(value[i] + ", ");
			}
			
			//System.out.println("received pos arry changed for " + name + " with value " + b.toString());
		}

		public void stateChange(AttributeStateEvent evt) 
		{
			for(JLabel lbl : valueLabel)
				lbl.setForeground(ATKConstant.getColor4Quality(evt.getState()));
		}

		public void errorChange(ErrorEvent evt) {}
	}
	
	protected ActionListener getApplyValueActionListener()
	{
		return new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				INumberScalar s = (INumberScalar) valueAttribute;
				s.setValue(Double.valueOf(valueSpinner[0].getValue().toString()));
			}
		};
	}	
	
	public AquisitionElement(String name, String deviceName, int valueSizeX, int valueSizeY)
	{
		super(name, deviceName);
		this.valueSizeX = valueSizeX;
		this.valueSizeY = valueSizeY;
		
		applyValueButton.setMargin( new Insets(1,1,1,1));
		applyValueButton.setToolTipText("Send new value");
		applyValueButton.addActionListener(getApplyValueActionListener());		
	}
}
