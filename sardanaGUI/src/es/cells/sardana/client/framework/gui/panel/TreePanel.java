package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.logging.Logger;

import javax.swing.ImageIcon;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTree;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.tree.TreePath;

import es.cells.sardana.client.framework.GlobalDataModel;
import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.SardanasDataModel;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.atk.widget.tree.ComChannelsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.ControllersTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.DevicePoolTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.DoorTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.DoorsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.ElementListTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.ExpChannelsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.GenericSardanaTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.IORegistersTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MacroServerTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MeasurementGroupsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MotorGroupsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MotorsTreeNode;
import es.cells.sardana.client.framework.macroserver.Door;
import es.cells.sardana.client.framework.macroserver.MacroServer;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.ControllerType;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.gui.swing.SwingResource;

public class TreePanel extends JPanel {

	protected JTabbedPane pane;
	protected JTree globalTree;
	protected JTree sardanaTree;
	protected DisplayPanel target;

	protected JScrollPane scrolableGlobalTree;
	protected JScrollPane scrolableSardanaTree;

	
	protected static final Logger log = SardanaManager.getInstance().getLogger(TreePanel.class.getName());
	
	public TreePanel(DisplayPanel target)
	{
		super();
		this.target = target;
		
		initComponents();
	}

	private void initComponents() 
	{
		setLayout( new BorderLayout(0, 0) );
		
		pane = new JTabbedPane();

		add(pane, BorderLayout.CENTER);
		
		initSardanaTree();
		initGlobalTree();
		
		pane.setSelectedIndex(0);
	}
	
	private void initSardanaTree() 
	{
		SardanaManager manager = SardanaManager.getInstance();
		
		SardanasDataModel dataModel = manager.getSardanasDataModel();

		sardanaTree = new JTree(dataModel);
		
		sardanaTree.setCellRenderer(new SardanaTreeCellRenderer());
		sardanaTree.addTreeSelectionListener(new TreeSelection(target));
		sardanaTree.setRowHeight(24);
		GenericSardanaTreeNode lastNode = (GenericSardanaTreeNode)dataModel.getRoot();
		DevicePoolTreeNode dpNode = null;
		MacroServerTreeNode msNode = null;
		while(lastNode.getChildCount() > 0)
		{
			if(dpNode == null && lastNode instanceof DevicePoolTreeNode)
			{
				DevicePool dp = ((DevicePoolTreeNode)lastNode).getDevicePool();
				if(dp != null && dp.isAvailable())
					dpNode = (DevicePoolTreeNode)lastNode;
			}
			else
			if(msNode == null && lastNode instanceof MacroServerTreeNode)
			{
				MacroServer ms = ((MacroServerTreeNode)lastNode).getMacroServer();
				if(ms != null && ms.isAvailable())
					msNode = (MacroServerTreeNode)lastNode;
			}
			lastNode = (GenericSardanaTreeNode)lastNode.getChildAt(0);
		}
		
		TreePath path = new TreePath(lastNode.getPath());
		
		sardanaTree.makeVisible(path);
		
		if(dpNode != null)
		{
			sardanaTree.setSelectionPath(new TreePath(dpNode.getPath()));
		}

		if(msNode != null)
		{
			sardanaTree.setSelectionPath(new TreePath(msNode.getPath()));
		}

		sardanaTree.addMouseListener(new MouseAdapter()
		{
		    public void mousePressed(MouseEvent e) 
		    {
		        maybeShowPopup(e);
		    }

		    public void mouseReleased(MouseEvent e) 
		    {
		        maybeShowPopup(e);
		    }

		    private void maybeShowPopup(MouseEvent e) 
		    {
		        if (e.isPopupTrigger()) 
		        {
		            TreePath path = sardanaTree.getPathForLocation(e.getX(),e.getY());
		        	if(path != null)
		        	{
		        		GenericSardanaTreeNode node = (GenericSardanaTreeNode) path.getLastPathComponent();
		        		
			        	JPopupMenu menu = SwingResource.getPopupForElement(node.getUserObject());
		        		
			        	if(menu != null)
			        		menu.show(sardanaTree, e.getX(), e.getY());
		        	}
		        		
		        }
		    }			
		});
		scrolableSardanaTree = new JScrollPane(sardanaTree);
		pane.addTab("Sardana", scrolableSardanaTree);
	}

	private void initGlobalTree()
	{
		
		SardanaManager manager = SardanaManager.getInstance();
		
		GlobalDataModel dataModel = manager.getGlobalDataModel();

		globalTree = new JTree(dataModel);

		globalTree.setExpandsSelectedPaths(true);
		globalTree.addTreeSelectionListener(new TreeSelection(target));
		globalTree.setCellRenderer(new SardanaTreeCellRenderer());
		globalTree.setRowHeight(24);
		globalTree.setRootVisible(false);
		GenericSardanaTreeNode lastNode = (GenericSardanaTreeNode)dataModel.getRoot();
		DevicePoolTreeNode dpNode = null;
		MacroServerTreeNode msNode = null;
		while(lastNode.getChildCount() > 0)
		{
			if(dpNode == null && lastNode instanceof DevicePoolTreeNode)
			{
				DevicePool dp = ((DevicePoolTreeNode)lastNode).getDevicePool();
				if(dp != null && dp.isAvailable())
					dpNode = (DevicePoolTreeNode)lastNode;
			}
			else
			if(msNode == null && lastNode instanceof MacroServerTreeNode)
			{
				MacroServer ms = ((MacroServerTreeNode)lastNode).getMacroServer();
				if(ms != null && ms.isAvailable())
					msNode = (MacroServerTreeNode)lastNode;
			}
			lastNode = (GenericSardanaTreeNode)lastNode.getChildAt(0);
		}
		
		TreePath path = new TreePath(lastNode.getPath());
		
		globalTree.makeVisible(path);
		
		if(dpNode != null)
		{
			globalTree.setSelectionPath(new TreePath(dpNode.getPath()));
		}

		if(msNode != null)
		{
			globalTree.setSelectionPath(new TreePath(msNode.getPath()));
		}

		globalTree.addMouseListener(new MouseAdapter()
		{
		    public void mousePressed(MouseEvent e) 
		    {
		        maybeShowPopup(e);
		    }

		    public void mouseReleased(MouseEvent e) 
		    {
		        maybeShowPopup(e);
		    }

		    private void maybeShowPopup(MouseEvent e) 
		    {
		        if (e.isPopupTrigger()) 
		        {
		            TreePath path = globalTree.getPathForLocation(e.getX(),e.getY());
		        	if(path != null)
		        	{
		        		GenericSardanaTreeNode node = (GenericSardanaTreeNode) path.getLastPathComponent();
		        		
			        	JPopupMenu menu = SwingResource.getPopupForElement(node.getUserObject());
		        		
			        	if(menu != null)
			        		menu.show(globalTree, e.getX(), e.getY());
		        	}
		        		
		        }
		    }			
		});

		scrolableGlobalTree = new JScrollPane(globalTree);
		pane.addTab("Global", scrolableGlobalTree);

	}
    
    protected ImageIcon getImageIcon(String name) 
    {
    	return SwingResource.smallIconMap.get(name);
    }

    //TODO: Substance look and feel
	//class SardanaTreeCellRenderer extends SubstanceDefaultTreeCellRenderer
	class SardanaTreeCellRenderer extends DefaultTreeCellRenderer
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

			GenericSardanaTreeNode node = (GenericSardanaTreeNode) value;
			
			if(!(node instanceof ElementListTreeNode))
				c.setForeground(SwingResource.getColorForElement(node.getUserObject()));
			
			if(SardanaManager.EXTENDED_LAF)
			{
				String strIcon = null;
				
				if(value instanceof DevicePoolTreeNode)
				{
					DevicePoolTreeNode n = (DevicePoolTreeNode)value;
					String state = n.getState();
					strIcon = IImageResource.getDevicePoolTreeIcon(state);
				}
				else if(value instanceof MacroServerTreeNode)
				{
					MacroServerTreeNode n = (MacroServerTreeNode)value;
					String state = n.getState();
					strIcon = IImageResource.getMacroServerTreeIcon(state);
				}
				else if(value instanceof DoorsTreeNode)
				{
					DoorsTreeNode n = (DoorsTreeNode)value;
					strIcon = IImageResource.getDoorsTreeIcon();
				}
				else if(value instanceof DoorTreeNode)
				{
					DoorTreeNode n = (DoorTreeNode)value;
					String state = n.getState();
					strIcon = IImageResource.getDoorTreeIcon(state);
				}
				else if(value instanceof GenericSardanaTreeNode)
				{
					strIcon = IImageResource.getPoolTreeIcon((GenericSardanaTreeNode)value);
				}
				
				if( strIcon != null && strIcon.length() > 0 )
				{
	            	setIcon( getImageIcon(strIcon) );
				}
			}
			
			return c;
		}
	}
	
	class TreeSelection implements TreeSelectionListener 
	{
		DisplayPanel target;

		public TreeSelection(DisplayPanel target)
		{
			this.target = target;
		}
		
		public void valueChanged(TreeSelectionEvent e)
		{
			TreePath selection = e.getNewLeadSelectionPath();
			
   
			if(selection == null)
			{
				target.showEmptyPanel();
				return;
			}
			GenericSardanaTreeNode node = ((GenericSardanaTreeNode)selection.getLastPathComponent());

			if(node == null)
			{
				target.showEmptyPanel();
				return;
			}
			
			Object usrObj = node.getUserObject();

			if(usrObj == null)
			{
				target.showEmptyPanel();
				return;
			}
//			if(usrObj.equals("Sardana"))
//			{
//				target.showSardanaPanel();
//				return;
//			}
			if(usrObj instanceof Controller)
			{
				DevicePoolTreeNode poolNode = (DevicePoolTreeNode) selection.getPathComponent( selection.getPathCount() - 3 );
				DevicePool pool = poolNode.getDevicePool();
				Controller controller = (Controller)usrObj;
				if (controller.getType() == ControllerType.Motor)
					target.showMotorController(controller, pool);
				else if(controller.getType() == ControllerType.CounterTimer)
					target.showCoTiController(controller, pool);
			}
			else if(usrObj instanceof PseudoMotor)
			{
				DevicePoolTreeNode poolNode = (DevicePoolTreeNode) selection.getPathComponent( selection.getPathCount() - 3 );
				DevicePool pool = poolNode.getDevicePool();

				target.showPseudoMotor((PseudoMotor)usrObj, pool);
			}
			else if(usrObj instanceof Motor)
			{
				DevicePoolTreeNode poolNode = (DevicePoolTreeNode) selection.getPathComponent( selection.getPathCount() - 3 );
				DevicePool pool = poolNode.getDevicePool();

				target.showMotor((Motor)usrObj, pool);
			}
			else if(usrObj instanceof MotorGroup)
			{
				DevicePoolTreeNode poolNode = (DevicePoolTreeNode) selection.getPathComponent( selection.getPathCount() - 3 );
				DevicePool pool = poolNode.getDevicePool();

				target.showMotorGroup((MotorGroup)usrObj, pool);
			}
            
			else if(usrObj instanceof DevicePool)
			{
				int index = -1;
				if(node instanceof DevicePoolTreeNode)
					index = DevicePoolPanel.CTRLS_INDEX;
				else if(node instanceof ControllersTreeNode)
					index = DevicePoolPanel.CTRLS_INDEX;
				else if(node instanceof MotorsTreeNode)
					index = DevicePoolPanel.MOTORS_INDEX;
				else if(node instanceof MotorGroupsTreeNode)
					index = DevicePoolPanel.MOTOR_GROUPS_INDEX;
				else if(node instanceof ExpChannelsTreeNode)
					index = DevicePoolPanel.EXP_CHANNELS_INDEX;
				else if(node instanceof ComChannelsTreeNode)
					index = DevicePoolPanel.COM_CHANNELS_INDEX;
				else if(node instanceof IORegistersTreeNode)
					index = DevicePoolPanel.IOREGISTERS_INDEX;
				else if(node instanceof MeasurementGroupsTreeNode)
					index = DevicePoolPanel.MEASUREMENT_GROUPS_INDEX;

				target.showDevicePoolPanel((DevicePool)usrObj, index);
			}
			
			else if (usrObj instanceof Door)
			{
				MacroServerTreeNode macroServerNode = (MacroServerTreeNode) selection.getPathComponent(selection.getPathCount() -3);
				MacroServer macroServer = macroServerNode.getMacroServer();
				target.showEmptyPanel();
			}
			
			else if (usrObj instanceof MacroServer)
				target.showMacroServerPanel((MacroServer)usrObj);
			
			else 
			{
				target.showEmptyPanel();
				return;
			}
			
		}
	}
	
	public JTree getGlobalTree()
	{
		return globalTree;
	}
	
	
}
