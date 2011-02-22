package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;

import javax.swing.JPanel;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.tangoatk.utils.DefaultStringFilter;
import es.cells.tangoatk.utils.DefaultStringSplitter;
import es.cells.tangoatk.widget.attribute.FormStringSpectrumViewer;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.widget.device.DeviceViewer;

public class MotorPanel extends JPanel
{
	protected DeviceViewer deviceViewer;
	protected Motor motor = null;
	protected DevicePool pool = null;
	
	protected DefaultStringSplitter motorSplitter;
	protected FormStringSpectrumViewer motorPropertiesViewer;
	protected MotorUsePanel motorUsePanel;
	
	public MotorPanel()
	{
		initComponents();
	}
	
	private void initComponents()
	{	
		setLayout( new BorderLayout() );
		
		JPanel mainPanel = new JPanel( new GridBagLayout() );
				
		add(mainPanel, BorderLayout.NORTH);
	
		deviceViewer = new DeviceViewer();
	
		GridBagConstraints gbc = new GridBagConstraints();
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.fill = GridBagConstraints.HORIZONTAL;
		gbc.anchor = GridBagConstraints.NORTH;
		gbc.weightx = 1.0;		
		gbc.weighty = 0.0;
		mainPanel.add(deviceViewer, gbc);
		
		String[] rows = new String[] {"Name", "Device Name", "Motor Number"}; 
		motorSplitter = new DefaultStringSplitter(
				DevicePoolUtils.MOTOR_DESCRIPTION_PATTERN,
				DevicePoolUtils.MOTOR_DESCRIPTION_ELEMS,
				new DefaultStringFilter(),
				0);
		
		motorPropertiesViewer = new FormStringSpectrumViewer(rows);
		motorPropertiesViewer.setSplitter(motorSplitter);
		motorPropertiesViewer.setCustomTitle("Details");
		
		gbc = new GridBagConstraints();
		gbc.gridx = 0;
		gbc.gridy = 1;
		gbc.fill = GridBagConstraints.HORIZONTAL;
		gbc.anchor = GridBagConstraints.NORTH;
		gbc.weightx = 1.0;		
		gbc.weighty = 0.0;
		mainPanel.add(motorPropertiesViewer, gbc);
		
		motorUsePanel = new MotorUsePanel();
		
		gbc = new GridBagConstraints();
		gbc.gridx = 0;
		gbc.gridy = 2;
		gbc.fill = GridBagConstraints.HORIZONTAL;
		gbc.anchor = GridBagConstraints.NORTH;
		gbc.weightx = 1.0;		
		gbc.weighty = 1.0;
		mainPanel.add(motorUsePanel, gbc);
		
	}

	public void setModel(Motor motor, DevicePool pool)
	{
		this.motor = motor;
		this.pool = pool;
		
		IStringSpectrum motorsModel = pool.getMotorListAttributeModel();

		String filter = motor.getName();
		
		((DefaultStringFilter)motorSplitter.getFilter()).setFilter(filter);
		motorPropertiesViewer.setModel(motorsModel);
		
		deviceViewer.setModel(motor.getDevice());
		
		motorUsePanel.setModel(motor, pool);
	}

}
