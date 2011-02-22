package es.cells.sardana.client.framework.gui.panel;

import java.awt.GridBagConstraints;
import java.awt.Insets;

import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.tangoatk.utils.DefaultStringSplitter;
import es.cells.tangoatk.widget.attribute.StringSpectrumDeviceTableViewer;

public class CoTiCtrlPanel extends ControllerPanel{
	
	public void initComponents(){
		super.initComponents();
		String[] cols = new String[] {"Name", "Device Name", "C/T Number"};
		motorSplitter = new DefaultStringSplitter(
				DevicePoolUtils.MOTOR_DESCRIPTION_PATTERN,
				DevicePoolUtils.MOTOR_DESCRIPTION_ELEMS,
				new MotorFilter(),
				1);
		
		motorListViewer = new StringSpectrumDeviceTableViewer(
				cols, 0, 1);
		motorListViewer.setSplitter(motorSplitter);
		motorListViewer.setCustomTitle("Motors");
		
		GridBagConstraints gbc = new GridBagConstraints(
				0,1,
				1,1,
				1.0,0.5,
				GridBagConstraints.NORTH,
				GridBagConstraints.HORIZONTAL,
				new Insets(2,2,2,2),
				0,0);
		add( motorListViewer, gbc );
		
	}

}
