package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;

import javax.swing.JPanel;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.tangoatk.utils.DefaultStringFilter;
import es.cells.tangoatk.utils.DefaultStringSplitter;
import es.cells.tangoatk.widget.attribute.FormStringSpectrumViewer;
import es.cells.tangoatk.widget.attribute.StringSpectrumDeviceTableViewer;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.widget.device.DeviceViewer;

public class MotorGroupPanel extends JPanel
{
	protected DeviceViewer deviceViewer;
	protected MotorGroup motorGroup = null;
	protected DevicePool pool = null;
	
	protected DefaultStringSplitter motorGroupSplitter;
	
	protected FormStringSpectrumViewer motorGroupPropertiesViewer;
	
	protected StringSpectrumDeviceTableViewer motorListViewer;
	
	protected DefaultStringSplitter motorSplitter;
	
	protected MotorGroupUsePanel usePanel;
	
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
			for(Motor motor : motorGroup.getMotors())
				if(motor.getName().equals(str))
					return true;
			return false;
		}
	}
	
	public MotorGroupPanel()
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
		motorGroupSplitter = new DefaultStringSplitter(
				DevicePoolUtils.MOTOR_GROUP_DESCRIPTION_PATTERN,
				DevicePoolUtils.MOTOR_GROUP_DESCRIPTION_ELEMS,
				new DefaultStringFilter(),
				0);
		
		motorGroupPropertiesViewer = new FormStringSpectrumViewer(rows);
		motorGroupPropertiesViewer.setSplitter(motorGroupSplitter);
		motorGroupPropertiesViewer.setCustomTitle("Details");
		gbc.gridy = 1;
		mainPanel.add(motorGroupPropertiesViewer, gbc);
		
		String[] cols = new String[] {"Name", "Device Name", "Motor Number"};
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
		
		
		usePanel = new MotorGroupUsePanel();
		gbc.gridy = 3;
		gbc.weighty = 0.5;
		mainPanel.add( usePanel, gbc );
	}

	public void setModel(MotorGroup motorGroup, DevicePool pool)
	{
		this.motorGroup = motorGroup;
		this.pool = pool;
		
		IStringSpectrum motorGroupsModel = pool.getMotorGroupListAttributeModel();

		String filter = motorGroup.getName();
		
		((DefaultStringFilter)motorGroupSplitter.getFilter()).setFilter(filter);
		motorGroupPropertiesViewer.setModel(motorGroupsModel);
		
		deviceViewer.setModel(motorGroup.getDevice());
		
		IStringSpectrum motorsModel = pool.getMotorListAttributeModel();
		
		if(motorsModel == null)
		{
			System.out.println("NULL motorGroup model!!!");
			return;
		}
		
		motorListViewer.setModel(motorsModel);		
		usePanel.setModel(motorGroup, pool);
	}

}
