package es.cells.sardana.client.framework.gui.panel;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;

import javax.swing.JPanel;

import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.tangoatk.utils.DefaultStringFilter;
import es.cells.tangoatk.utils.DefaultStringSplitter;
import es.cells.tangoatk.widget.attribute.FormStringSpectrumViewer;
import es.cells.tangoatk.widget.attribute.StringSpectrumDeviceTableViewer;
import fr.esrf.tangoatk.core.IStringSpectrum;


public class ControllerPanel extends JPanel
{
	protected Controller ctrl = null;
	protected DevicePool pool = null;
	
	protected FormStringSpectrumViewer ctrlPropertiesViewer;
	protected StringSpectrumDeviceTableViewer motorListViewer;
	protected PropertiesFormViewerPanel propertiesViewer;
	
	protected DefaultStringSplitter ctrlSplitter;
	protected DefaultStringSplitter motorSplitter;
	
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
			String[] motorData = str.split("/");
			
			//TODO: remove igoneCase comparison
			return motorData[1].equalsIgnoreCase(ctrl.getName());
		}
	}
	
	public ControllerPanel()
	{
		initComponents();
	}
	
	protected void initComponents()
	{	
		setLayout( new GridBagLayout() );
	
		String[] rows = new String[] {"Name", "Lib", "Class", "Type", "Language", "Lib File"}; 
		ctrlSplitter = new DefaultStringSplitter(
				DevicePoolUtils.CTRL_DESCRIPTION_PATTERN,
				DevicePoolUtils.CTRL_DESCRIPTION_ELEMS,
				new DefaultStringFilter(),
				0);
		
		ctrlPropertiesViewer = new FormStringSpectrumViewer(rows);
		ctrlPropertiesViewer.setSplitter(ctrlSplitter);
		ctrlPropertiesViewer.setCustomTitle("Details");
		
		GridBagConstraints gbc = new GridBagConstraints(
				0,0,
				1,1,
				1.0,0.0,
				GridBagConstraints.NORTH,
				GridBagConstraints.HORIZONTAL,
				new Insets(2,2,2,2),
				0,0);
		
		add( ctrlPropertiesViewer, gbc );
//		String[] cols = new String[] {"Name", "Device Name", "Motor Number"};
//		motorSplitter = new DefaultStringSplitter(
//				DevicePoolUtils.MOTOR_DESCRIPTION_PATTERN,
//				DevicePoolUtils.MOTOR_DESCRIPTION_ELEMS,
//				new MotorFilter(),
//				1);
//		
//		motorListViewer = new StringSpectrumDeviceTableViewer(
//				cols, 0, 1);
//		motorListViewer.setSplitter(motorSplitter);
//		motorListViewer.setCustomTitle("Motors");
//		
//		gbc = new GridBagConstraints(
//				0,1,
//				1,1,
//				1.0,0.5,
//				GridBagConstraints.NORTH,
//				GridBagConstraints.HORIZONTAL,
//				new Insets(2,2,2,2),
//				0,0);
//		add( motorListViewer, gbc );
		
		propertiesViewer = new PropertiesFormViewerPanel();

		gbc = new GridBagConstraints(
				0,2,
				1,1,
				1.0,0.5,
				GridBagConstraints.NORTH,
				GridBagConstraints.HORIZONTAL,
				new Insets(2,2,2,2),
				0,0);
		add( propertiesViewer, gbc);
	}

	public void setModel(Controller controller, DevicePool pool)
	{
		this.ctrl = controller;
		this.pool = pool;
		
		IStringSpectrum ctrlModel = pool.getControllerListAttributeModel();

		String filter = controller.getName();
		
		((DefaultStringFilter)ctrlSplitter.getFilter()).setFilter(filter);
		ctrlPropertiesViewer.setModel(ctrlModel);
		
		IStringSpectrum motorsModel = pool.getMotorListAttributeModel();
		
		if(motorsModel == null)
		{
			System.out.println("NULL motorGroup model!!!");
			return;
		}
		
		motorListViewer.setModel(motorsModel);
		propertiesViewer.setData(controller.getPropertyInstances());
	}
}
