package es.cells.sardana.tests;

import java.awt.HeadlessException;

import javax.swing.JFormattedTextField;
import javax.swing.JFrame;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

public class SpinnerNumberTest extends JFrame
{
	public SpinnerNumberTest() throws HeadlessException
	{
		super("Spinner number test");
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		SpinnerNumberModel model = new SpinnerNumberModel(0.0,-9999.9,9999.9,1.0);
		JSpinner spinner = new JSpinner(model);
		 
		//DecimalFormat format = new DecimalFormat("%6.2f");
		
		SpinnerEditor textField = new SpinnerEditor("%6.1f");
		
		//DefaultFormatter fter = new NumberFormatter(format);
		//DefaultFormatterFactory tf = new DefaultFormatterFactory(fter,fter,fter);
		//textField.setFormatterFactory(tf);
		
		spinner.setEditor(textField);
		
		spinner.addChangeListener(textField);
		
		spinner.setValue(new Double(55.5));
		
		getContentPane().add(spinner);
		
		pack();
		setVisible(true);
	}

	public static void main(String[] args)
	{
		new SpinnerNumberTest();
	}
	
	protected class SpinnerEditor extends JFormattedTextField implements ChangeListener
	{
		String dspFormat = "%6.2f";
		
		public SpinnerEditor(String fmt)
		{
			super();
			dspFormat = fmt;
		}

		public void stateChanged(ChangeEvent e)
		{
			Object v = ((JSpinner)e.getSource()).getValue();
			
			setValue(String.format(dspFormat, v));
		}
		
		public void setFormat(String fmt)
		{
			this.dspFormat = fmt;
		}
	}
}
