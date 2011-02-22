package es.cells.sardana.light.model;

import javax.swing.JLabel;
import javax.swing.JPanel;

import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class Element 
{
	public String name;
	public String deviceName;
	public JLabel stateLabel = new JLabel("not set");
	
	public JPanel elementPanel = new JPanel();
	
	public StateListener stateListener = new StateListener();
	
	class StateListener implements IDevStateScalarListener
	{
		public void devStateScalarChange(DevStateScalarEvent evt) 
		{
			stateLabel.setText(evt.getValue());
			stateLabel.setForeground(ATKConstant.getColor4State(evt.getValue()));
		}

		public void stateChange(AttributeStateEvent evt) {}

		public void errorChange(ErrorEvent evt) {}
	}

	public Element(String name, String deviceName)
	{
		this.name = name;
		this.deviceName = deviceName;
	}
	
	@Override
	public String toString() 
	{
		return deviceName;
	}
}
