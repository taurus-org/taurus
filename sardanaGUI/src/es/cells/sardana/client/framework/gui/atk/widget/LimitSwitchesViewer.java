package es.cells.sardana.client.framework.gui.atk.widget;

import javax.swing.BoxLayout;
import javax.swing.JCheckBox;
import javax.swing.JPanel;

import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.BooleanSpectrumEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IBooleanSpectrum;
import fr.esrf.tangoatk.core.IBooleanSpectrumListener;

public class LimitSwitchesViewer extends JPanel implements IBooleanSpectrumListener
{
	JCheckBox homeCheckBox;
	JCheckBox lowerCheckBox;
	JCheckBox upperCheckBox;
	
	private IBooleanSpectrum   attModel=null;

	public LimitSwitchesViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		BoxLayout l = new BoxLayout(this, BoxLayout.Y_AXIS);
		setLayout(l);
		
		homeCheckBox = new JCheckBox();
		lowerCheckBox = new JCheckBox();
		upperCheckBox = new JCheckBox();

		homeCheckBox.setText("Home switch");
		lowerCheckBox.setText("Lower switch");
		upperCheckBox.setText("Upper switch");
		
		homeCheckBox.setEnabled(false);
		lowerCheckBox.setEnabled(false);
		upperCheckBox.setEnabled(false);
		
		add(homeCheckBox);
		add(lowerCheckBox);
		add(upperCheckBox);
	}

	public void setAttModel(IBooleanSpectrum boolModel)
	{
		if (attModel != null)
		{
			attModel.removeBooleanSpectrumListener(this);
			attModel = null;
		}

		if (boolModel != null)
		{
			attModel = boolModel;
			attModel.addBooleanSpectrumListener(this);
			attModel.refresh();
		}
	}
	
	private void setBoolValue(boolean[] value)
	{
		homeCheckBox.setSelected(value[0]);
		lowerCheckBox.setSelected(value[1]);
		upperCheckBox.setSelected(value[2]);
	}
	
	public void booleanSpectrumChange(BooleanSpectrumEvent evt)
	{
		setBoolValue(evt.getValue());
	}

	public void stateChange(AttributeStateEvent arg0)
	{
	}

	public void errorChange(ErrorEvent arg0)
	{
	}
}
