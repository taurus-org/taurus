package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Component;
import java.util.ArrayList;
import java.util.List;

import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableColumn;

import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.ControllerStateListener;
import es.cells.sardana.client.framework.pool.CtrlState;
import es.cells.sardana.client.framework.pool.DevicePool;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class ControllerTableViewer extends JPanel
{
	protected JScrollPane     pane;
	protected JTable          ctrlTable;
	protected TableModel      model;
	
	DevicePool pool;
	
	CtrlListener ctrlListener;
	
	protected static final ImageIcon ctrlOkIcon = new ImageIcon("res/24x24/up.png");
	protected static final ImageIcon ctrlErrorIcon = new ImageIcon("res/24x24/important.png");
	
	public ControllerTableViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		model = new TableModel();
		
		//setBorder(BorderFactory.createTitledBorder("Controllers"));
		
		DefaultTableColumnModel colModel = new DefaultTableColumnModel();
		
		TableColumn column = new TableColumn(0);
		column.setHeaderValue("State");
		column.setPreferredWidth(50);
		column.setMaxWidth(50);
		column.setCellRenderer(new CtrlStateCellRenderer());
		colModel.addColumn(column);
		
		column = new TableColumn(1);
		column.setHeaderValue("Name");
		column.setPreferredWidth(120);
		column.setMaxWidth(120);
		colModel.addColumn(column);
		
		column = new TableColumn(2);
		column.setHeaderValue("Type");
		column.setPreferredWidth(60);
		column.setMaxWidth(60);
		colModel.addColumn(column);

		column = new TableColumn(3);
		column.setHeaderValue("Library");
		colModel.addColumn(column);

		column = new TableColumn(4);
		column.setHeaderValue("Class");
		colModel.addColumn(column);

		column = new TableColumn(5);
		column.setHeaderValue("Language");
		colModel.addColumn(column);

		column = new TableColumn(6);
		column.setHeaderValue("Source");
		colModel.addColumn(column);
		
		setLayout(new BorderLayout());
		pane = new JScrollPane();
		ctrlTable = new JTable(model, colModel);
		ctrlTable.setRowHeight(ctrlOkIcon.getIconHeight() + 2);
		
		ctrlListener = new CtrlListener();
		
		pane.setViewportView(ctrlTable);
		
		add(pane, BorderLayout.CENTER);
	}

	public JTable getTable()
	{
		return ctrlTable;
	}

	public Controller getSelectedController()
	{
		int row =  ctrlTable.getSelectedRow();
		
		if(row < 0)
			return null;
		
		return (Controller) ctrlTable.getValueAt(row, 1);
	}
	
	public List<Controller> getSelectedControllers()
	{
		ArrayList<Controller> ret = new ArrayList<Controller>();
		int[] rows = ctrlTable.getSelectedRows();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((Controller) ctrlTable.getValueAt(row, 1));
		}
		
		return ret;
	}
	
	/*
	public void setCustomTitle(String customTitle) 
	{
		((TitledBorder)getBorder()).setTitle(customTitle);
	}
	*/

	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeControllerListListener(ctrlListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addControllerListListener(ctrlListener);
			model.update(pool.getControllers());
		}
	}
	
	class CtrlListener implements IStringSpectrumListener
	{
		public void stateChange(AttributeStateEvent e)
		{
		}

		public void errorChange(ErrorEvent evt)
		{
		}

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update(pool.getControllers());
		}
	}
	
	class TableModel extends AbstractTableModel implements ControllerStateListener 
	{
		List<Controller> controllers;

		public int getColumnCount()
		{
			return 7;
		}

		public int getRowCount()
		{
			return controllers != null ? controllers.size() : 0;
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			Controller ctrl = null;
		
			int controllersLen = controllers.size();
			
			if(rowIndex < controllersLen)
			{
				ctrl = controllers.get(rowIndex);
			}
			
			if(ctrl == null)
				return null;
			
			if(columnIndex == 0)
				return ctrl.getState();
			else if(columnIndex == 1)
				return ctrl;
			else if(columnIndex == 2)
				return ctrl.getType();
			else if(columnIndex == 3)
				return ctrl.getCtrlClass().getModuleName();
			else if(columnIndex == 4)
				return ctrl.getCtrlClass().getClassName();
			else if(columnIndex == 5)
				return ctrl.getLanguage();
			else if(columnIndex == 6)
				return ctrl.getCtrlClass().getFileName();
			else 
				return null;
		}
		
	    private void updateControllerList(List<Controller> newControllers)
	    {
	    	if(controllers != null)
	    	{
	    		for(Controller ctrl : controllers) ctrl.removeControllerStateListener(this);
	    	}
	    	if(newControllers != null)
	    	{
	    		for(Controller ctrl : newControllers) ctrl.addControllerStateListener(this);
	    	}
	    	controllers = newControllers;
	    }

	    public void update(List<Controller> newControllers)
	    {
	    	updateControllerList(newControllers);
	    	fireTableDataChanged();
	    }

		public void controllerStateChanged(Controller c)
		{
			int index = controllers.indexOf(c);
			
			if(index < 0)
				return;
			
			fireTableCellUpdated(index, 0);
		}
	}
	
	//TODO: Substance look and feel
	//class CtrlStateCellRenderer extends SubstanceDefaultTableCellRenderer
	class CtrlStateCellRenderer extends DefaultTableCellRenderer 
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			if(value instanceof CtrlState)
			{
				CtrlState state = (CtrlState)value;
				JLabel l = (JLabel) super.getTableCellRendererComponent(table, "", isSelected, hasFocus,
						row, column);
				l.setIcon( state == CtrlState.Ok ? ctrlOkIcon : ctrlErrorIcon );
				l.setHorizontalAlignment(SwingConstants.CENTER);
				return l;
			}
			
			return super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
					row, column);
		}
	}
}
