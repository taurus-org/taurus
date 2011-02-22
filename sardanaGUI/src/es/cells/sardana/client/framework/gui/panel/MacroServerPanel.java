package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;

import javax.swing.JPanel;
import javax.swing.JTabbedPane;

import es.cells.sardana.client.framework.gui.atk.widget.MacroServerViewer;
import es.cells.sardana.client.framework.macroserver.MacroServer;

public class MacroServerPanel extends JPanel {

	private MacroServer macroServer;
	
	private JTabbedPane elementsPane;
	private MacrosPanel macrosPanel;
	private MacroServerViewer macroServerViewer;
	
	public MacroServerPanel()
	{	
		initComponents();
	}
	
	public void setMacroServer(MacroServer ms)
	{
		this.macroServer = ms;
		macrosPanel.setMacroServer(ms);
		macroServerViewer.setModel(ms);
	}
	
	
	
	private void initComponents() {
		
		elementsPane = new JTabbedPane();
		macrosPanel = new MacrosPanel();
	
        elementsPane.add(macrosPanel);
        
        macroServerViewer = new MacroServerViewer();
        
        setLayout(new BorderLayout());
        
        add(macroServerViewer,BorderLayout.NORTH);
        add(elementsPane);
        
    }
	
	
    
}
