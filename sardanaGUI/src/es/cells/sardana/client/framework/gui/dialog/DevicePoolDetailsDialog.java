package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.HeadlessException;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JDialog;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.gui.atk.widget.DevicePropertyListViewer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.tangoatk.core.DeviceProperty;
import fr.esrf.tangoatk.widget.attribute.BooleanScalarCheckBoxViewer;

public class DevicePoolDetailsDialog extends JDialog 
{
	DevicePool pool;
	BooleanScalarCheckBoxViewer simulationMode;
	DevicePropertyListViewer poolPathViewer;
	
	ActionListener applyListener;
	
	boolean propertyChanged = false;
	
	public DevicePoolDetailsDialog(DevicePool pool) throws HeadlessException 
	{
		super();
		this.pool = pool;
		setTitle(pool.getName() + " Details");
		initComponents();
	}

	private void initComponents() 
	{
		setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});
		
		simulationMode = new BooleanScalarCheckBoxViewer("Simulation mode");
		poolPathViewer = new DevicePropertyListViewer(new IStringSplitter()
		{
			public String[] split(String str) 
			{
				return str.split(":");
			}

			public boolean isValid(String str) 
			{
				return true;
			}
		});
		
		applyListener = new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(!poolPathViewer.hasChanged())
					return;
				
				if(poolPathViewer.haveItemsBeenRemoved())
				{
					int res = JOptionPane.showConfirmDialog(null,
							"Some directories were removed from the PoolPath.\n" +
							"Some controllers and/or pseudo motors may become unavailable the next time the Pool is initialized or started\n" +
							"Are you sure you want to proceed?",
							"Warning: PoolPath directories removed",
							JOptionPane.YES_NO_OPTION);
					
					if(res != JOptionPane.YES_OPTION)
					{
						poolPathViewer.refresh();
						return;
					}
						
				}
				
				StringBuffer buff = new StringBuffer();
				
				boolean first = true;
				for(Object obj : poolPathViewer.getElements())
				{
					if(first)
					{
						buff.append(obj);
						first = false;
					}
					else
						buff.append(":" + obj);
				}
				String [] buffArray = buff.toString().split(":");
				
				DeviceProperty poolPath = pool.getProperty("PoolPath");
				
				if(poolPath != null)
				{
					poolPath.setValue(buffArray);
					poolPath.store();
				}
				else
				{
					DbDatum d = new DbDatum("PoolPath",buffArray);
					try {
						pool.getDevice().put_property(d);
						pool.getDevice().refreshPropertyMap();
						pool.setProperty(pool.getDevice().getProperty("PoolPath"));
					} catch (DevFailed e1) {
						// TODO Auto-generated catch block
						e1.printStackTrace();
					}
				}
				
				JOptionPane.showMessageDialog(null,
						"Some Pool properties have changed.\nChanges will only become available when an 'Init' command is performed on the pool.",
						"PoolPath property has changed",
						JOptionPane.INFORMATION_MESSAGE);

			}
		};
		poolPathViewer.addApplyListener(applyListener);
		
		simulationMode.setAttModel(pool.getSimulationModeAttributeModel());
		
		DeviceProperty prop = pool.getProperty("PoolPath");
		
		if(prop == null)
		{
			prop = new DeviceProperty(null,"PoolPath", null);
		}
		
		poolPathViewer.setModel(prop);
		
		JPanel mainPanel = new JPanel(new BorderLayout());
		
		mainPanel.add(simulationMode, BorderLayout.NORTH);
		mainPanel.add(poolPathViewer, BorderLayout.CENTER);
		
		getContentPane().add(mainPanel);
		pack();
		
	}

	protected void closeAndExit() 
	{
		poolPathViewer.removeApplyListener(applyListener);
	}

}
