package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JPanel;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.gui.atk.widget.tree.DevicePoolTreeNode;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.widget.util.ATKDiagnostic;
import fr.esrf.tangoatk.widget.util.ErrorHistory;

public class SardanaPanel extends JPanel
{

	private JPanel buttonPanel;
	private JPanel propertiesPanel;
	
	private JButton refreshButton;
	private JButton diagnosticButton;
	private JButton errorButton;
	
	public SardanaPanel()
	{
		initComponents();
	}
	
	private void initComponents()
	{
		setLayout( new BorderLayout() );

		buttonPanel = createButtonPanel();
		propertiesPanel = createPropertiesPanel();
		
		add(buttonPanel, BorderLayout.NORTH);
		add(propertiesPanel, BorderLayout.CENTER);
	}

	private JPanel createPropertiesPanel()
	{
		JPanel panel = new JPanel();
		
		
		
		return panel;
	}

	private JPanel createButtonPanel()
	{
		JPanel panel = new JPanel( new BorderLayout() );
		JPanel leftPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
		JPanel rightPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
		
		panel.add(leftPanel, BorderLayout.WEST);
		panel.add(rightPanel, BorderLayout.EAST);

		refreshButton = new JButton("Refresh");
		
		refreshButton.addActionListener(new ActionListener() 
		{
            public void actionPerformed(ActionEvent evt) 
            {
                refreshButtonActionPerformed(evt);
            }
        });
		
		leftPanel.add(refreshButton);
		
		diagnosticButton = new JButton("Diagnostic...");

		diagnosticButton.addActionListener(new ActionListener() 
		{
            public void actionPerformed(ActionEvent evt) 
            {
                diagnosticButtonActionPerformed(evt);
            }
        });
		
		errorButton = new JButton("Errors...");

		errorButton.addActionListener(new ActionListener() 
		{
            public void actionPerformed(ActionEvent evt) 
            {
            	errorButtonActionPerformed(evt);
            }
        });
		
		rightPanel.add(diagnosticButton);
		rightPanel.add(errorButton);
		
		return panel;
	}
	
    private void refreshButtonActionPerformed(java.awt.event.ActionEvent evt) 
    {
    	SardanaManager.getInstance().refreshDataModel();
    }
    	
	
    private void diagnosticButtonActionPerformed(java.awt.event.ActionEvent evt) 
    {
    	ATKDiagnostic.showDiagnostic();
    }
    
    private void errorButtonActionPerformed(java.awt.event.ActionEvent evt) 
    {
    	ErrorHistory errorHistoryFrame = new ErrorHistory();
    	errorHistoryFrame.setVisible(true);

    	//TODO: Add error listener to the attributes
    	//SardanaManager.getInstance().getAttrList().addErrorListener(errorHistoryFrame);
    	
    	DevicePoolTreeNode[] poolNodes = SardanaManager.getInstance().getPoolNodes();
    	
    	for(DevicePoolTreeNode poolNode : poolNodes)
    	{
    		Device device = poolNode.getModel();
    		
    		if(device != null)
    			device.addErrorListener(errorHistoryFrame);
    	}
    }
}
