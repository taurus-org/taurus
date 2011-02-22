package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextPane;
import javax.swing.WindowConstants;

import org.apache.xmlbeans.XmlCursor;
import org.apache.xmlbeans.XmlObject;
import org.apache.xmlbeans.XmlOptions;

import es.cells.sardana.client.framework.config.SardanaDocument;
import es.cells.sardana.client.framework.gui.component.SardanaConfigTree;
import es.cells.sardana.client.framework.gui.component.XmlEntry;

public class SardanaConfigView extends JDialog
{
    // Variables for UI components.
    private SardanaConfigTree treeXmlTree;

    private JPanel pnlContent;

    private JPanel pnlTree;

    private JScrollPane scrContent;

    private JScrollPane scrTree;

    private JSplitPane splTreeContent;

    private JTextPane txtpnlContent;
    
    SardanaDocument doc;
	



    /**
     * Constructs the frame with an XML file to use for the tree.
     * 
     * @param xmlFile The file containing XML that the tree should represent.
     */
	public SardanaConfigView(SardanaDocument doc)
	{
		super();
		this.doc = doc;
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
        setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("XML Tree View");
        setName("frmXmlTreeView");

        // Create the split plane that separates the tree and the content panes.
        splTreeContent = new JSplitPane();

        // Create the components for the left side of the split pane:
        // the panel, scrolling panel, and the XML tree it will contain.
        pnlTree = new JPanel();
        scrTree = new JScrollPane();
        treeXmlTree = new SardanaConfigTree(doc);
        scrTree.setViewportView(treeXmlTree);
        pnlTree.setLayout(new GridBagLayout());
        GridBagConstraints gridBagConstraints = new GridBagConstraints();
        gridBagConstraints.fill = GridBagConstraints.BOTH;
        gridBagConstraints.anchor = GridBagConstraints.NORTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 1.0;
        pnlTree.add(scrTree, gridBagConstraints);

        // Put the tree panel in the left side of the split pane.
        splTreeContent.setLeftComponent(pnlTree);

        // Create the components for the left side of the split pane:
        // the panel, scrolling panel, and the XML tree it will contain.
        pnlContent = new JPanel();
        scrContent = new JScrollPane();
        txtpnlContent = new JTextPane();
        scrContent.setViewportView(txtpnlContent);
        pnlContent.setLayout(new GridBagLayout());
        gridBagConstraints = new GridBagConstraints();
        gridBagConstraints.fill = GridBagConstraints.BOTH;
        gridBagConstraints.anchor = GridBagConstraints.NORTHWEST;
        gridBagConstraints.weightx = 1;
        gridBagConstraints.weighty = 1;
        pnlContent.add(scrContent, gridBagConstraints);

        // Put the content panel in the right side of the split pane.
        splTreeContent.setRightComponent(pnlContent);

        // Set the rest of the split pane's properties,
        splTreeContent.setDividerLocation(170);
        gridBagConstraints = new GridBagConstraints();
        gridBagConstraints.gridx = 0;
        gridBagConstraints.gridy = 1;
        gridBagConstraints.weightx = 1;
        gridBagConstraints.weighty = 1;
        gridBagConstraints.fill = GridBagConstraints.BOTH;
        gridBagConstraints.gridheight = GridBagConstraints.REMAINDER;
        gridBagConstraints.anchor = GridBagConstraints.NORTH;
        getContentPane().add(splTreeContent, BorderLayout.CENTER);

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
                    txtpnlContent.setText(xmlString);
                }
            }

            // Don't respond to these events.
            public void mouseEntered(MouseEvent event)
            {}

            public void mouseExited(MouseEvent event)
            {}

            public void mousePressed(MouseEvent event)
            {}

            public void mouseReleased(MouseEvent event)
            {}
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

	protected void closeAndExit()
	{
		dispose();
	}
}
