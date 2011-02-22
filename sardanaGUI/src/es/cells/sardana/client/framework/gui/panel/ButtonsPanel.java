package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.FlowLayout;

import javax.swing.JPanel;

public class ButtonsPanel extends JPanel
{
	JPanel leftPanel;
	JPanel rightPanel;
	
	public ButtonsPanel()
	{
		initComponents();
	}
	
	protected void initComponents()
	{
		setLayout( new BorderLayout() );
		
		leftPanel = new JPanel( new FlowLayout(FlowLayout.LEFT) );
		rightPanel = new JPanel( new FlowLayout(FlowLayout.RIGHT) );
		
		add(leftPanel, BorderLayout.WEST);
		add(rightPanel, BorderLayout.EAST);
	}
	
	public void addLeft(Component component)
	{
		leftPanel.add(component);
	}
	
	public void addRight(Component component)
	{
		rightPanel.add(component);
	}	
}
