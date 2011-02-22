package es.cells.sardana.tests;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JPanel;

import fr.esrf.tangoatk.core.CommandList;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.DeviceFactory;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.widget.command.SimpleCommandViewer;
import fr.esrf.tangoatk.widget.device.DeviceViewer;
import fr.esrf.tangoatk.widget.device.StateViewer;
import fr.esrf.tangoatk.widget.util.ATKDiagnostic;

public class Testing01 extends JFrame
{

	public Testing01()
	{
		setTitle("Testing");
		
		System.setProperty("TANGO_HOST", "controls01:10000");
		
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		Device device;
		try
		{
			device = DeviceFactory.getInstance().getDevice("tcoutinho/pool/pool01");
		}
		catch (ConnectionException e)
		{
			e.printStackTrace();
			return;
		}
		
		DeviceViewer viewer = new DeviceViewer();
		
		viewer.setModel(device);

		StateViewer stateViewer = new StateViewer();
		
		stateViewer.setModel(device);
		
		//AttributeList attrList = new AttributeList();
		//attrList.add(device.getName() + "/" )
		
		JButton button = new JButton("Diagnostic...");
		
		button.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e)
			{
				ATKDiagnostic.showDiagnostic();
			}
			
		});
		
		JPanel panel = new JPanel(new BorderLayout());
		
		SimpleCommandViewer cmdViewer = new SimpleCommandViewer();
		
		CommandList cmdList = new CommandList();
		
		ICommand cmd;
		try
		{
			cmd = (ICommand) cmdList.add(device.getName() + "/" + "CreateController");
		}
		catch (ConnectionException e1)
		{
			return;
		}
		
		cmdViewer.setModel(cmd);
		//panel.add( stateViewer, BorderLayout.NORTH );
		panel.add( cmdViewer, BorderLayout.NORTH );
		panel.add( viewer, BorderLayout.CENTER );
		panel.add( button, BorderLayout.SOUTH );
		
		getContentPane().add(panel);
				
		pack();
		setVisible(true);
		
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		new Testing01();
	}

}
