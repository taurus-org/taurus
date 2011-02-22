package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;

import javax.swing.JPanel;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.tangoatk.utils.DefaultStringFilter;
import es.cells.tangoatk.utils.DefaultStringSplitter;
import es.cells.tangoatk.widget.attribute.FormStringSpectrumViewer;
import es.cells.tangoatk.widget.attribute.StringSpectrumDeviceTableViewer;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.widget.device.DeviceViewer;

public class PseudoMotorPanel extends JPanel
{
	protected DeviceViewer deviceViewer;
	protected PseudoMotor pseudoMotor = null;
	protected DevicePool pool = null;
	
	protected DefaultStringSplitter pseudoMotorSplitter;
	
	protected FormStringSpectrumViewer pseudoMotorPropertiesViewer;
	
	protected StringSpectrumDeviceTableViewer motorListViewer;
	
	protected DefaultStringSplitter motorSplitter;
	
	protected PseudoMotorUsePanel pseudoMotorUsePanel;
	
	class MotorFilter extends DefaultStringFilter
	{
		public MotorFilter()
		{
			super();
		}

		public MotorFilter(String filter)
		{
			super(filter);
		}

		@Override
		public boolean isValid(String str)
		{
			for(Motor motor : pseudoMotor.getMotors())
				if(motor.getName().equals(str))
					return true;
			return false;
		}
	}
	
	public PseudoMotorPanel()
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
		
		String[] rows = new String[] {"Name", "Device Name", "Motors"}; 
		pseudoMotorSplitter = new DefaultStringSplitter(
				DevicePoolUtils.PSEUDO_MOTOR_DESCRIPTION_PATTERN,
				DevicePoolUtils.PSEUDO_MOTOR_DESCRIPTION_ELEMS,
				new DefaultStringFilter(),
				0);
		
		pseudoMotorPropertiesViewer = new FormStringSpectrumViewer(rows);
		pseudoMotorPropertiesViewer.setSplitter(pseudoMotorSplitter);
		pseudoMotorPropertiesViewer.setCustomTitle("Details");
		
		gbc.gridy = 1;
		mainPanel.add(pseudoMotorPropertiesViewer, gbc);
		
		String[] cols = new String[] {"Name", "Device Name", "Motor Number" };
		motorSplitter = new DefaultStringSplitter(
				DevicePoolUtils.MOTOR_DESCRIPTION_PATTERN,
				DevicePoolUtils.MOTOR_DESCRIPTION_ELEMS,
				new MotorFilter(),
				0);
		
		motorListViewer = new StringSpectrumDeviceTableViewer(
				cols, 0, 1);
		motorListViewer.setSplitter(motorSplitter);
		motorListViewer.setCustomTitle("Motors");
		
		gbc.gridy = 2;
		gbc.weighty = 0.5;
		mainPanel.add( motorListViewer, gbc );
		
		pseudoMotorUsePanel = new PseudoMotorUsePanel();
		
		gbc.gridy = 3;
		mainPanel.add(pseudoMotorUsePanel, gbc);
	}

	public void setModel(PseudoMotor pseudoMotor, DevicePool pool)
	{
		this.pseudoMotor = pseudoMotor;
		this.pool = pool;
		
		IStringSpectrum pseudoMotorsModel = pool.getPseudoMotorListAttributeModel();

		String filter = pseudoMotor.getName();
		
		((DefaultStringFilter)pseudoMotorSplitter.getFilter()).setFilter(filter);
		pseudoMotorPropertiesViewer.setModel(pseudoMotorsModel);
		
		deviceViewer.setModel(pseudoMotor.getDevice());
		
		IStringSpectrum motorsModel = pool.getMotorListAttributeModel();
		
		motorListViewer.setModel(motorsModel);
		
		pseudoMotorUsePanel.setModel(pseudoMotor, pool);
	}

}
