package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.io.IOException;
import java.util.List;

import javax.swing.Box;
import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextPane;
import javax.swing.WindowConstants;

import org.apache.xmlbeans.XmlCursor;
import org.apache.xmlbeans.XmlException;
import org.apache.xmlbeans.XmlObject;
import org.apache.xmlbeans.XmlOptions;

import es.cells.sardana.client.framework.SardanaConfigLoader;
import es.cells.sardana.client.framework.SardanaConfigLoader.AbstractItem;
import es.cells.sardana.client.framework.config.SardanaDocument;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.component.SardanaConfigTree;
import es.cells.sardana.client.framework.gui.component.XmlEntry;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.gui.swing.SwingResource;

public class SardanaConfigEditor extends JDialog
{
    // Variables for UI components.
    private SardanaConfigTree treeXmlTree;

    private ButtonsPanel toolBarPanel;
    
    private JPanel contentPanel;

    private JPanel treePanel;

    private JScrollPane contentScrollPane;

    private JScrollPane treeScrollPane;

    private JSplitPane treeContentSplitPane;

    private JTextPane xmlTextPane;
    
    private JButton saveButton;
    private JButton updateButton;
    
    SardanaConfigLoader loader;
	
    SardanaDocument doc;
    
    /**
     * Constructs the frame with an XML file to use for the tree.
     * 
     * @param xmlFile The file containing XML that the tree should represent.
     * @throws IOException 
     * @throws XmlException 
     */
	public SardanaConfigEditor(SardanaConfigLoader loader) throws XmlException, IOException
	{
		super();
		this.loader = loader;
		doc = loader.load();
		initComponents();
	}

    /**
     * Initializes UI components, setting properties and adding event listeners.
     * 
     * @param xmlFile The XML file to be represented by the tree.
     */
    private void initComponents()
    {
        // Set properties for this frame.
        getContentPane().setLayout(new BorderLayout());
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        setTitle("XML Tree View");
        setName("frmXmlTreeView");

        saveButton = new JButton(SwingResource.normalIconMap.get(IImageResource.IMG_FILE_SAVE));
        saveButton.setToolTipText("Load configuration into server");
        updateButton = new JButton(SwingResource.normalIconMap.get(IImageResource.IMG_REFRESH));
        updateButton.setToolTipText("Refresh rules");
        
        toolBarPanel = new ButtonsPanel();
        
        toolBarPanel.addLeft(saveButton);
        toolBarPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        toolBarPanel.addLeft(updateButton);
        
        updateButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				update();
			}
        });
        
        getContentPane().add(toolBarPanel,BorderLayout.NORTH);
        
        // Create the split plane that separates the tree and the content panes.
        treeContentSplitPane = new JSplitPane();

        // Create the components for the left side of the split pane:
        // the panel, scrolling panel, and the XML tree it will contain.
        treePanel = new JPanel();
        treeScrollPane = new JScrollPane();
        treeXmlTree = new SardanaConfigTree(doc);
        treeScrollPane.setViewportView(treeXmlTree);
        treePanel.setLayout(new GridBagLayout());
        GridBagConstraints gridBagConstraints = new GridBagConstraints();
        gridBagConstraints.fill = GridBagConstraints.BOTH;
        gridBagConstraints.anchor = GridBagConstraints.NORTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 1.0;
        treePanel.add(treeScrollPane, gridBagConstraints);

        // Put the tree panel in the left side of the split pane.
        treeContentSplitPane.setLeftComponent(treePanel);

        // Create the components for the left side of the split pane:
        // the panel, scrolling panel, and the XML tree it will contain.
        contentPanel = new JPanel();
        contentScrollPane = new JScrollPane();
        xmlTextPane = new JTextPane();
        contentScrollPane.setViewportView(xmlTextPane);
        contentPanel.setLayout(new GridBagLayout());
        gridBagConstraints = new GridBagConstraints();
        gridBagConstraints.fill = GridBagConstraints.BOTH;
        gridBagConstraints.anchor = GridBagConstraints.NORTHWEST;
        gridBagConstraints.weightx = 1;
        gridBagConstraints.weighty = 1;
        contentPanel.add(contentScrollPane, gridBagConstraints);

        // Put the content panel in the right side of the split pane.
        treeContentSplitPane.setRightComponent(contentPanel);

        // Set the rest of the split pane's properties,
        treeContentSplitPane.setDividerLocation(170);
        getContentPane().add(treeContentSplitPane, BorderLayout.CENTER);

        // Add a listener to get mouse clicks on the tree nodes.
        treeXmlTree.addMouseListener(new MouseListener()
        {
            public void mouseClicked(MouseEvent event)
            {
                if (event.getClickCount() == 1)
                {
                    XmlEntry selection = (XmlEntry) treeXmlTree
                            .getLastSelectedPathComponent();
                    // selection might be null if the user clicked one of the
                    // expandy/collapsy things without selecting a node.
                    if (selection == null)
                    {
                        return;
                    }
                    // Get the pretty-printed XML text and put it in the
                    // window on the right.
                    XmlObject node = selection.getXml();
                    XmlCursor nodeCursor = node.newCursor();
                    XmlOptions options = new XmlOptions();
                    options.setSavePrettyPrint();
                    options.setSavePrettyPrintIndent(4);
                    String xmlString = nodeCursor.xmlText(options);
                    xmlTextPane.setText(xmlString);
                }
            }

            // Don't respond to these events.
            public void mouseEntered(MouseEvent event){}
            public void mouseExited(MouseEvent event){}
            public void mousePressed(MouseEvent event){}
            public void mouseReleased(MouseEvent event){}
        });

        // Size all the components to their preferred size.
        pack();
        this.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});        
        this.setSize(600, 640);
        this.setVisible(true);
    }

    protected void update()
    {
    	List<AbstractItem> items = loader.check();
    	
    	
    }
    
	protected void closeAndExit()
	{
		dispose();
	}
}
