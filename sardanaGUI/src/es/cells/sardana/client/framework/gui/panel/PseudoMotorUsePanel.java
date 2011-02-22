package es.cells.sardana.client.framework.gui.panel;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;

public class PseudoMotorUsePanel extends MotorUsePanel
{
	
	PropertiesFormViewerPanel propertiesPanel;
	
	public PseudoMotorUsePanel()
	{
		super();
		
	}

	
	
	@Override
	protected void initComponents()
	{
		super.initComponents();
		
		propertiesPanel = new PropertiesFormViewerPanel();
		
		pane.addTab("Properties", propertiesPanel);
	}



	public void setModel(Motor motor, DevicePool pool)
	{
		super.setModel(motor, pool);
		
		//propertiesPanel.setData(((PseudoMotor)motor).getPropertyInstances());
	}
}
