package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;

import javax.swing.JPanel;
import javax.swing.JTabbedPane;

import es.cells.sardana.client.framework.pool.Motor;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.widget.attribute.ScalarListViewer;

public class MotorSettingsPanel extends JPanel
{
	private Motor motor;
	
	JTabbedPane pane;
	
	JPanel attributesPanel, propertiesPanel, rangesPanel;
	
	ScalarListViewer attributesViewer;
	
	public MotorSettingsPanel()
	{
		super();
		initComponents();
	}
	
	
	
	private void initComponents()
	{
		setLayout(new BorderLayout());
		
		pane = new JTabbedPane();
		attributesPanel = new JPanel();
		propertiesPanel = new JPanel();
		rangesPanel = new JPanel();
		attributesViewer = new ScalarListViewer();
		
		attributesPanel.setName("Attributes");
		propertiesPanel.setName("Properties");
		rangesPanel.setName("Ranges");
		
		add(pane, BorderLayout.CENTER);
		
		pane.add(attributesPanel,0);
		pane.add(propertiesPanel,1);
		pane.add(rangesPanel,2);
	}

	public void setModel(Motor m)
	{
		motor = m;
		
		if(motor == null)
			return;
		
		AttributeList nonPolledAttrs = motor.getNonPolledAttributes();
		
		attributesViewer.setModel(nonPolledAttrs);
		
		
	}
	
	public void startRefresher()
	{
		if(motor != null)
			motor.getNonPolledAttributes().startRefresher();
	}
	
	public void stopRefresher()
	{
		if(motor != null)
			motor.getNonPolledAttributes().stopRefresher();
	}
	
}
