package es.cells.tangoatk.widget.attribute;

import java.awt.Color;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.text.ParseException;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFormattedTextField;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JSlider;
import javax.swing.JSpinner;
import javax.swing.SpinnerNumberModel;
import javax.swing.JFormattedTextField.AbstractFormatter;
import javax.swing.JSpinner.DefaultEditor;
import javax.swing.JSpinner.NumberEditor;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.text.DefaultFormatterFactory;

import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.ISpectrumListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.NumberSpectrumEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class NumberScalarViewer extends JPanel implements INumberScalarListener, ISpectrumListener
{
	
	protected JLabel     label;
	protected JSpinner   spinner; 
	protected JButton    menuButton;
	protected JButton    sliderButton;
	protected JButton    applyButton;
	protected JSlider    slider;
	
	protected JPopupMenu menu;
	JMenuItem undoMenuItem = new JMenuItem("Undo", undoIcon);
	JMenuItem refreshMenuItem = new JMenuItem("Refresh", refreshIcon);
	JMenuItem detailsMenuItem = new JMenuItem("Details", detaisIcon);
	
	protected static final ImageIcon applyIcon = new ImageIcon("res/24x24/go-jump.png");
	protected static final ImageIcon undoIcon = new ImageIcon("res/24x24/undo.png");
	protected static final ImageIcon refreshIcon = new ImageIcon("res/24x24/reload.png");
	protected static final ImageIcon detaisIcon = new ImageIcon("res/24x24/editpaste.png");
	
	protected static final ImageIcon menuIcon = new ImageIcon("res/16x16/up.png");
	protected static final ImageIcon scrollIcon = new ImageIcon("res/16x16/down.png");
	
	protected INumberScalar numberModel = null;
	protected INumberSpectrum spectrumModel = null;
	
	
	/** 
	 * The index in the number array for which this viewer is interested
	 */
	protected int modelIndex;	
	
	protected double modelValue;
	
	public NumberScalarViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		setLayout(new GridBagLayout());
		
		label = new JLabel();
		spinner = new JSpinner(new SpinnerNumberModel());
		menuButton = new JButton();
		sliderButton = new JButton();
		applyButton = new JButton();
		
		DefaultEditor editor = (DefaultEditor)spinner.getEditor();
		JFormattedTextField textField = editor.getTextField();
		
		SpinnerFormatter fmt = new SpinnerFormatter("%6.2f");
		DefaultFormatterFactory factory = new DefaultFormatterFactory(fmt,fmt,fmt);

		textField.setFormatterFactory(factory);
		spinner.setFont(spinner.getFont().deriveFont(18.0f));
		
		menuButton.setMargin(new Insets(1,1,1,1));
		sliderButton.setMargin(new Insets(1,1,1,1));
		applyButton.setMargin(new Insets(2,2,2,2));
		
		applyButton.setIcon(applyIcon);

		/*
		Component upButton = spinner.getComponent(0);
		Component downButton = spinner.getComponent(1);
		
		
		if(upButton instanceof JButton && downButton instanceof JButton)
		{
			menuButton.setIcon(((JButton)upButton).getIcon());
			sliderButton.setIcon(((JButton)downButton).getIcon());
		}
		else
		{
		*/
			menuButton.setIcon(menuIcon);
			sliderButton.setIcon(scrollIcon);
		//}
		
		slider = new JSlider(JSlider.HORIZONTAL);
		slider.setVisible(false);
		
		GridBagConstraints gbc = new GridBagConstraints(
				0,0,
				1,2,
				0.0,0.0,
				GridBagConstraints.CENTER, 
				GridBagConstraints.BOTH, 
				new Insets(0,0,0,0),0,0);
		add(label, gbc);
		
		gbc = new GridBagConstraints(
				1,0, // x,y
				1,2, // width,height
				1.0,0.0,  // weight
				GridBagConstraints.EAST, 
				GridBagConstraints.BOTH, 
				new Insets(0,0,0,0),0,0);
		add(spinner,gbc);
		
		gbc = new GridBagConstraints(
				2,0,
				1,1,
				0.0,0.5,
				GridBagConstraints.CENTER, 
				GridBagConstraints.BOTH, 
				new Insets(0,0,0,0),0,0);
		add(menuButton, gbc);
		
		gbc = new GridBagConstraints(
				2,1,
				1,1,
				0.0,0.5,
				GridBagConstraints.CENTER, 
				GridBagConstraints.BOTH, 
				new Insets(0,0,0,0),0,0);
		add(sliderButton, gbc);
		
		gbc = new GridBagConstraints(
				3,0,
				1,2,
				0.0,0.0,
				GridBagConstraints.WEST, 
				GridBagConstraints.BOTH, 
				new Insets(0,0,0,0),0,0);
		add(applyButton, gbc);
		
		menu = new JPopupMenu();
		
		undoMenuItem = new JMenuItem("Undo", undoIcon);
		refreshMenuItem = new JMenuItem("Refresh", refreshIcon);
		detailsMenuItem = new JMenuItem("Details", detaisIcon);
		
		menu.add(undoMenuItem);
		menu.addSeparator();
		menu.add(refreshMenuItem);
		menu.addSeparator();
		menu.add(detailsMenuItem);
		
		sliderButton.addMouseListener( new MouseAdapter() 
		{
			public void mouseReleased(MouseEvent e) 
			{
		        if(e.getButton() == MouseEvent.BUTTON1)
		        {
		        	slider.setVisible(true);
		        }
		    }
		});
		
		menuButton.addMouseListener( new MouseAdapter() 
		{
			public void mouseReleased(MouseEvent e) 
			{
		        if(e.getButton() == MouseEvent.BUTTON1)
		        {
		        	if(menu.isVisible())
		        		menu.setVisible(false);
		        	else
		        		menu.show(menuButton, e.getX(),e.getY());
		        }
		    }
		});
		
		spinner.addChangeListener(new ChangeListener()
		{
			public void stateChanged(ChangeEvent e)
			{
				if(numberModel != null)
				{
					if(modelValue != getSpinnerValue())
					{
						label.setBorder(BorderFactory.createLineBorder(Color.blue, 1));
						spinner.setForeground(Color.blue);
					}
					else
					{
						label.setBorder(null);
						spinner.setForeground(Color.black);
					}
				}
			}
		});
		
		applyButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				applyPressed();
			}
		});
	}

	public void setLabelVisible(boolean v)
	{
		label.setVisible(v);
	}
	
	public void setApplyVisible(boolean v)
	{
		applyButton.setVisible(v);
	}
	
	protected void applyPressed()
	{
		if(modelValue == getSpinnerValue())
			return;
		
		numberModel.setValue(getSpinnerValue());
	}
	
	public void setModel(INumberSpectrum model, int index, AttributeInfoEx info)
	{
		if(this.numberModel != null)
		{
			this.numberModel.removeNumberScalarListener(this);
			this.numberModel = null;
		}
		
		if(this.spectrumModel != null)
		{
			this.spectrumModel.removeSpectrumListener(this);
			this.spectrumModel = null;
		}
		
		modelIndex = index;
		
		if(modelIndex < 0)
			modelIndex = 0;
		
		this.spectrumModel = model;
		
		if(this.spectrumModel != null)
		{
			spectrumModel.addSpectrumListener(this);
			
			boolean hasInvalidRange = false;
			
			double minValue, maxValue;
			try
			{
				minValue = Double.parseDouble(info.min_value);
			}
			catch(NumberFormatException e)
			{
				minValue = Double.MIN_VALUE;
				hasInvalidRange = true;
			}

			try
			{
				maxValue = Double.parseDouble(info.max_value);
			}
			catch(NumberFormatException e)
			{
				maxValue = Double.MAX_VALUE;
				hasInvalidRange = true;
			}
		
			//double precision = getPrecision(this.numberModel.getFormat());
			
			spinner.setModel(new SpinnerNumberModel(minValue,minValue,maxValue,1.0));
			
			SpinnerFormatter fmt = new SpinnerFormatter(info.format);
			DefaultFormatterFactory factory = new DefaultFormatterFactory(fmt,fmt,fmt);
			((NumberEditor)spinner.getEditor()).getTextField().setFormatterFactory(factory);

			
			label.setText(info.label);
			label.setBorder(null);
			boolean writable = spectrumModel.isWritable();
			spinner.setEnabled(writable);
			applyButton.setEnabled(writable);
			undoMenuItem.setEnabled(writable);
			sliderButton.setEnabled(writable);
			this.spectrumModel.refresh();
		}
		else
		{
			label.setText("No data associated");
			label.setBorder(null);
			spinner.setEnabled(false);
			applyButton.setEnabled(false);
			sliderButton.setEnabled(false);
			menu.setEnabled(false);
		}
	}	
	
	public void setModel(INumberScalar numberModel)
	{
		if(this.numberModel != null)
		{
			this.numberModel.removeNumberScalarListener(this);
			this.numberModel = null;
		}
		
		if(this.spectrumModel != null)
		{
			this.spectrumModel.removeSpectrumListener(this);
			this.spectrumModel = null;
		}
		
		this.numberModel = numberModel;
		
		if(this.numberModel != null)
		{
			this.numberModel.addNumberScalarListener(this);
			
			double minValue = this.numberModel.getMinValue();
			
			boolean validRange = true;
			
			if(minValue == Double.NaN)
			{
				minValue = Double.MIN_VALUE;
				validRange = false;
			}
			
			double maxValue = this.numberModel.getMaxValue();

			if(maxValue == Double.NaN)
			{
				maxValue = Double.MAX_VALUE;
				validRange = false;
			}
		
			//double precision = getPrecision(this.numberModel.getFormat());
			
			spinner.setModel(new SpinnerNumberModel(minValue,minValue,maxValue,1.0));
			
			SpinnerFormatter fmt = new SpinnerFormatter(this.numberModel.getFormat());
			DefaultFormatterFactory factory = new DefaultFormatterFactory(fmt,fmt,fmt);
			((NumberEditor)spinner.getEditor()).getTextField().setFormatterFactory(factory);

			
			label.setText(this.numberModel.getLabel());
			label.setBorder(null);
			boolean writable = this.numberModel.isWritable();
			spinner.setEnabled(writable);
			applyButton.setEnabled(writable);
			undoMenuItem.setEnabled(writable);
			sliderButton.setEnabled(writable);
			this.numberModel.refresh();
		}
		else
		{
			label.setText("No data associated");
			label.setBorder(null);
			spinner.setEnabled(false);
			applyButton.setEnabled(false);
			sliderButton.setEnabled(false);
			menu.setEnabled(false);
		}
	}
	
	protected double getPrecision(String format)
	{
		int dot = format.indexOf('.');
		if(dot < 0)
			return 1;
		
		try
		{
			int enddot = format.indexOf('f');
			if(enddot < 0)
				enddot = format.indexOf('F');
			if(enddot < 0)
				enddot = format.indexOf('e');
			if(enddot < 0)
				enddot = format.indexOf('E');
			
			int decimalPlaces = Integer.parseInt(format.substring(dot+1,enddot));
			return Math.pow(10, -decimalPlaces);
		}
		catch(NumberFormatException e)
		{
			return 1;
		}
	}
	
	public void numberScalarChange(NumberScalarEvent evt)
	{
		modelValue = evt.getValue();
		spinner.setValue(modelValue);
	}
	

	public void spectrumChange(NumberSpectrumEvent evt)
	{
		modelValue = evt.getValue()[modelIndex];
		spinner.setValue(modelValue);
	}	

	public void stateChange(AttributeStateEvent e)
	{

		((DefaultEditor)spinner.getEditor()).getTextField().setBackground(ATKConstant.getColor4Quality(e.getState()));
	}

	public void errorChange(ErrorEvent evt)
	{
	}
	
	public double getModelValue()
	{
		return modelValue;
	}
	
	protected double getSpinnerValue()
	{
		return ((Number) spinner.getValue()).doubleValue();
	}

	protected class SpinnerFormatter extends AbstractFormatter
	{
		String dspFormat = "%6.2f";
		
		public SpinnerFormatter(String fmt)
		{
			super();
			dspFormat = fmt;
		}
		
		@Override
		public Object stringToValue(String text) throws ParseException
		{
			try
			{
				return Double.valueOf(text);
			}
			catch (NumberFormatException e)
			{
				return Double.NaN;
			}
		}

		@Override
		public String valueToString(Object value) throws ParseException
		{
			if(value == null)
				return "-.-";
			
			return String.format(dspFormat, Double.valueOf(value.toString()));
		}
		
		public void setFormat(String fmt)
		{
			this.dspFormat = fmt;
		}
	}
}
