package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;

import javax.swing.ImageIcon;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;

import es.cells.sardana.client.framework.gui.atk.widget.VerticalPositionViewer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Motor;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.widget.attribute.ScalarListViewer;
import fr.esrf.tangoatk.widget.command.VoidVoidCommandViewer;

public class MotorUsePanel extends JPanel
{
	protected Motor motor = null;
	protected DevicePool pool = null;
	
	JTabbedPane pane;
	
	VerticalPositionViewer vertPositionViewer;
	VoidVoidCommandViewer abortCmdViewer;
	ScalarListViewer attributeListViewer;
	
	JScrollPane attributesSrollPane;
	
	protected static ImageIcon abortIcon = new ImageIcon("res/64x64/stop.png"); 
	
	public MotorUsePanel()
	{
		initComponents();
	}
	
	protected void initComponents()
	{	
		setLayout(new BorderLayout());
		
		pane = new JTabbedPane();
		
		add(pane, BorderLayout.CENTER);
		
		JPanel mainPanel = new JPanel(new GridBagLayout());
		mainPanel.setName("Movement");
		
		vertPositionViewer = new VerticalPositionViewer();
		vertPositionViewer.setLabelVisible(true);
		
		abortCmdViewer = new VoidVoidCommandViewer();
		abortCmdViewer.setExtendedParam("text", " ", false);
		abortCmdViewer.setIcon(abortIcon);

		
		GridBagConstraints gbc = new GridBagConstraints(
			0,0,
			1,1,
			0.0,1.0,
			GridBagConstraints.CENTER,
			GridBagConstraints.BOTH,
			new Insets(2,2,2,2),
			0,0
		);
		mainPanel.add(vertPositionViewer, gbc);

		gbc = new GridBagConstraints(
				1,0,
				1,1,
				0.0,0.0,
				GridBagConstraints.CENTER,
				GridBagConstraints.HORIZONTAL,
				new Insets(2,2,2,2),
				0,0
		);
		mainPanel.add(abortCmdViewer, gbc);
		
		attributeListViewer = new ScalarListViewer();
		
		attributesSrollPane = new JScrollPane();
		attributesSrollPane.setViewportView(attributeListViewer);
		
		pane.addTab("Movement",mainPanel);
		pane.addTab("Attributes", attributesSrollPane);
		pane.setPreferredSize(new Dimension(250,250));
		
		attributesSrollPane.addComponentListener(new ComponentListener()
		{
			public void componentHidden(ComponentEvent e)
			{
				if(motor != null)
					motor.getNonPolledAttributes().stopRefresher();
			}

			public void componentMoved(ComponentEvent e)
			{
			}

			public void componentResized(ComponentEvent e)
			{
			}

			public void componentShown(ComponentEvent e)
			{
				if(motor != null)
					motor.getNonPolledAttributes().startRefresher();
			}
		});
	}
	
	public void setModel(Motor motor, DevicePool pool)
	{
		if(this.motor != null)
		{
			this.motor.getNonPolledAttributes().stopRefresher();
		}
		
		if(attributeListViewer != null)
			attributesSrollPane.remove(attributeListViewer);
		attributeListViewer = new ScalarListViewer();
		attributesSrollPane.setViewportView(attributeListViewer);
		
		this.motor = motor;
		this.pool = pool;
		
		INumberScalar posModel = motor.getPositionAttributeModel();
		
		AttributeInfoEx positionInfo = motor.getAttributeInfo(DevicePoolUtils.MOTOR_ATTR_POSITION);
		
		vertPositionViewer.setModel(positionInfo, posModel);
		abortCmdViewer.setModel(motor.getAbortCommandModel());

		AttributeList nonPolledAttributes = motor.getNonPolledAttributes();
		attributeListViewer.setModel(nonPolledAttributes);
		
		if(pane.getSelectedComponent() == attributesSrollPane)
		{
			if(this.motor != null)
				nonPolledAttributes.startRefresher();
		}
			
	}
}
