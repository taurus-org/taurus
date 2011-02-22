package es.cells.sardana.client.framework.gui.component;

import java.awt.Component;

import javax.swing.ImageIcon;
import javax.swing.JTree;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.tree.TreeSelectionModel;

import org.apache.xmlbeans.XmlObject;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.config.Controller;
import es.cells.sardana.client.framework.config.ExpChannel;
import es.cells.sardana.client.framework.config.LibElement;
import es.cells.sardana.client.framework.config.Library;
import es.cells.sardana.client.framework.config.MeasurementGroup;
import es.cells.sardana.client.framework.config.Motor;
import es.cells.sardana.client.framework.config.MotorGroup;
import es.cells.sardana.client.framework.config.Pool;
import es.cells.sardana.client.framework.config.PseudoMotor;
import es.cells.sardana.client.framework.config.ReferenceType;
import es.cells.sardana.client.framework.config.SardanaDocument;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.gui.swing.SwingResource;


/**
 * A tree view on XML, with nodes representing both elements and attributes. See
 * {@link XmlEntry}and {@link XmlModel}for information on how information
 * about the underlying XML is retrieved for use in the tree. Those classes use
 * XMLBeans to provide a wrapper by which the tree exposes the underlying XML.
 */
public class SardanaConfigTree extends JTree 
{
	SardanaDocument doc;
	
	/**
	 * Constructs the tree using <em>xmlFile</em> as an original source of
	 * nodes.
	 * 
	 * @param xmlFile The XML file the new tree should represent.
	 */
	public SardanaConfigTree(SardanaDocument doc)
	{
		this.doc = doc;
		initComponents();
	}

	/**
	 * Sets up the components that make up this tree.
	 * 
	 * @param xmlFile The XML file the new tree should represent.
	 */
	private void initComponents()
	{
		// Parse the XML create an XmlModel from its root.
		XmlEntry rootEntry = new XmlEntry(doc);
		XmlModel treemodel = new XmlModel(rootEntry);

		// Set UI properties.
		setModel(treemodel);
		setRootVisible(true);
		setShowsRootHandles(true);
		setAutoscrolls(true);
		setEditable(false);
		getSelectionModel().setSelectionMode(
				TreeSelectionModel.SINGLE_TREE_SELECTION);
		SardanaConfigTreeCellRenderer renderer = new SardanaConfigTreeCellRenderer();
		// Uncomment these lines to provide your own GIF files for
		// tree icons.
		//        renderer.setLeafIcon(createImageIcon("images/leaf.gif"));
		//        renderer.setOpenIcon(createImageIcon("images/minus.gif"));
		//        renderer.setClosedIcon(createImageIcon("images/plus.gif"));
		setCellRenderer(renderer);
		setRootVisible(false);
		setAutoscrolls(false);
	}

	class SardanaConfigTreeCellRenderer extends DefaultTreeCellRenderer
	{
		public Component getTreeCellRendererComponent(JTree tree, Object value,
				  boolean sel,
				  boolean expanded,
				  boolean leaf, int row,
				  boolean hasFocus) 
		{
			
			Component c = super.getTreeCellRendererComponent(tree, value, sel, expanded, leaf, row, hasFocus);

			if(value == null)
				return c;

			XmlEntry node = (XmlEntry)value;
			
			XmlObject xmlElement = node.getXml();
			
			String nodeName = xmlElement.getDomNode().getNodeName(); 
			
			if(SardanaManager.EXTENDED_LAF)
			{
				String strIcon = null;
				
				if(xmlElement instanceof Pool)
				{
					strIcon = IImageResource.IMG_POOL;
				} 
				else if(xmlElement instanceof Controller)
				{
					strIcon = IImageResource.IMG_POOL_CTRL;
				}
				else if(xmlElement instanceof Motor || 
						xmlElement instanceof PseudoMotor ||
						(xmlElement instanceof ReferenceType && 
								(nodeName.equalsIgnoreCase("MotorRef") ||
								 nodeName.equalsIgnoreCase("PseudoMotorRef"))))
				{
					strIcon = IImageResource.IMG_POOL_MOTOR;
				}
				else if(xmlElement instanceof MotorGroup ||
						(xmlElement instanceof ReferenceType && nodeName.equalsIgnoreCase("MotorRef")))
				{
					strIcon = IImageResource.IMG_POOL_MOTOR_GROUP;
				}
				else if(xmlElement instanceof ExpChannel)
				{
					ExpChannel channel = (ExpChannel) xmlElement;
					strIcon = IImageResource.IMG_POOL_ZEROD;
				}
				else if(xmlElement instanceof MeasurementGroup)
				{
					strIcon = IImageResource.IMG_POOL_MEASUREMENT_GROUP;
				}
				else if(xmlElement instanceof Library || xmlElement instanceof LibElement)
				{
					strIcon = IImageResource.IMG_LIBRARY;
				}
				
				if( strIcon != null && strIcon.length() > 0 )
				{
	            	setIcon( getImageIcon(strIcon) );
				}
			}
			
			return c;
		}
	}
	
    protected ImageIcon getImageIcon(String name) 
    {
    	return SwingResource.smallerIconMap.get(name);
    }
}
