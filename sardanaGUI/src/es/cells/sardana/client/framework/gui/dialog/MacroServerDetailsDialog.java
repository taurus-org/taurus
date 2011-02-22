package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JDialog;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.gui.atk.widget.DevicePropertyListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.PoolNamesListViewer;
import es.cells.sardana.client.framework.macroserver.MacroServer;
import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.tangoatk.core.DeviceProperty;

public class MacroServerDetailsDialog extends JDialog{
	
	MacroServer macroServer;
	
	DevicePropertyListViewer macroPathViewer;
	PoolNamesListViewer poolNamesViewer;
	
	ActionListener applyListener;
	
	public MacroServerDetailsDialog(MacroServer ms)
	{
		super();
		this.macroServer = ms;
		setTitle(macroServer.getName() + " Details");
		initComponents();
	}
	
	public void initComponents()
	{
		setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});

		//---------------------macro path viewer-----------------------------------------
		macroPathViewer = new DevicePropertyListViewer(new IStringSplitter()
		{
			public String[] split(String str) 
			{
				return str.split("\n");
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
				if(!macroPathViewer.hasChanged())
					return;
				
				if(macroPathViewer.haveItemsBeenRemoved())
				{
					int res = JOptionPane.showConfirmDialog(null,
							"Some directories were removed from the PoolPath.\n" +
							"Some controllers and/or pseudo motors may become unavailable the next time the Pool is initialized or started\n" +
							"Are you sure you want to proceed?",
							"Warning: PoolPath directories removed",
							JOptionPane.YES_NO_OPTION);
					
					if(res != JOptionPane.YES_OPTION)
					{
						macroPathViewer.refresh();
						return;
					}
						
				}
				
				StringBuffer buff = new StringBuffer();
				
				boolean first = true;
				for(Object obj : macroPathViewer.getElements())
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
				DeviceProperty poolPath = macroServer.getProperty("MacroPath");
				
				if(poolPath != null)
				{
					poolPath.setValue(buffArray);
					poolPath.store();
				}
				else
				{
					DbDatum d = new DbDatum("PoolPath",buffArray);
					try {
						macroServer.getDevice().put_property(d);
						macroServer.getDevice().refreshPropertyMap();
						macroServer.setProperty(macroServer.getDevice().getProperty("MacroPath"));
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
		macroPathViewer.addApplyListener(applyListener);
		
		DeviceProperty prop = macroServer.getProperty("MacroPath");
		
		if(prop == null)
		{
			prop = new DeviceProperty(null,"MacroPath", null);
		}
		
		macroPathViewer.setModel(prop);
		//-------------------------------------------------------------------------------
		
		//--------------------------pool names viewer-----------------------------------
		poolNamesViewer = new PoolNamesListViewer(new IStringSplitter()
		{
			public String[] split(String str) 
			{
				return str.split(":");
			}

			public boolean isValid(String str) 
			{
				return true;
			}
		},macroServer.getMachine());
		
		applyListener = new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(!poolNamesViewer.hasChanged())
					return;
				
				if(poolNamesViewer.haveItemsBeenRemoved())
				{
					int res = JOptionPane.showConfirmDialog(null,
							"Some pools were removed from the MacroServer.\n" +
							"Some doors  may become unavailable the next time the MacroServer is initialized or started\n" +
							"Are you sure you want to proceed?",
							"Warning: Pool removed",
							JOptionPane.YES_NO_OPTION);
					
					if(res != JOptionPane.YES_OPTION)
					{
						poolNamesViewer.refresh();
						return;
					}
						
				}
				
				StringBuffer buff = new StringBuffer();
				
				
				
				boolean first = true;
				for(Object obj : poolNamesViewer.getElements())
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
				
				DeviceProperty poolNames = macroServer.getProperty("PoolNames");
				
				if(poolNames != null)
				{
					poolNames.setValue(buffArray);
					poolNames.store();
				}
				else
				{
					DbDatum d = new DbDatum("PoolNames",buffArray);
					try {
						macroServer.getDevice().put_property(d);
						macroServer.getDevice().refreshPropertyMap();
						macroServer.setProperty(macroServer.getDevice().getProperty("PoolNames"));
					} catch (DevFailed e1) {
						
					}
				}
				
				JOptionPane.showMessageDialog(null,
						"Some MacroServer properties have changed.\nChanges will only become available when an 'Init' command is performed on the MacroServer.",
						"PoolNames property has changed",
						JOptionPane.INFORMATION_MESSAGE);
				
				//refresh sardana and global tree according to changes in macro server DevicePools property
				SardanaManager.getInstance().refreshDataModel();
			}
		};
		poolNamesViewer.addApplyListener(applyListener);
		
		
		prop = macroServer.getProperty("PoolNames");
		
		if(prop == null)
		{
			prop = new DeviceProperty(null,"PoolNames", null);
		}
		
		poolNamesViewer.setModel(prop);
		
		//-------------------------------------------------------------------------------
		
		JPanel mainPanel = new JPanel(new BorderLayout());
		mainPanel.add(macroPathViewer, BorderLayout.NORTH);
		mainPanel.add(poolNamesViewer, BorderLayout.CENTER);
		
		getContentPane().add(mainPanel);
		
		pack();
	}
	
	public void closeAndExit()
	{
		macroPathViewer.removeApplyListener(applyListener);
	}
	
	public void refreshPools()
	{
		
	}
}
