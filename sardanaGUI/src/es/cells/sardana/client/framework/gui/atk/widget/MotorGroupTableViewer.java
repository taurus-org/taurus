package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Component;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableColumn;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MotorGroupTableViewer extends JPanel
{
	protected JScrollPane     pane;
	protected JTable          motorGroupTable;
	protected TableModel      model;
	
	DevicePool pool;
	
	MotorGroupListener motorGroupListener;
	
	public MotorGroupTableViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		model = new TableModel();
		
		//setBorder(BorderFactory.createTitledBorder("Motor Groups"));
		
		DefaultTableColumnModel colModel = new DefaultTableColumnModel();
		
		TableColumn column = new TableColumn(0);
		column.setHeaderValue("State");
		column.setPreferredWidth(50);
		column.setMaxWidth(50);
		column.setCellRenderer(new MGStateCellRenderer());
		colModel.addColumn(column);
		
		column = new TableColumn(1);
		column.setHeaderValue("Name");
		column.setPreferredWidth(120);
		column.setMaxWidth(120);
		colModel.addColumn(column);
		
		column = new TableColumn(2);
		column.setHeaderValue("Device");
		colModel.addColumn(column);

		column = new TableColumn(3);
		column.setHeaderValue("Motors");
		colModel.addColumn(column);

		setLayout(new BorderLayout());
		pane = new JScrollPane();
		motorGroupTable = new JTable(model, colModel);
		motorGroupListener = new MotorGroupListener();
		
		pane.setViewportView(motorGroupTable);
		
		add(pane, BorderLayout.CENTER);
	}

	public JTable getTable()
	{
		return motorGroupTable;
	}

	public MotorGroup getSelectedMotorGroup()
	{
		int row =  motorGroupTable.getSelectedRow();
		
		if(row < 0)
			return null;
		
		return (MotorGroup) motorGroupTable.getValueAt(row, 1);
	}
	
	public List<MotorGroup> getSelectedMotorGroups()
	{
		ArrayList<MotorGroup> ret = new ArrayList<MotorGroup>();
		int[] rows = motorGroupTable.getSelectedRows();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((MotorGroup) motorGroupTable.getValueAt(row, 1));
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
			pool.removeMotorGroupListListener(motorGroupListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addMotorGroupListListener(motorGroupListener);
			model.update(pool.getMotorGroups());
		}
	}
	

	
	class MotorGroupListener implements IStringSpectrumListener 
	{

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update(pool.getMotorGroups());
		}

		public void stateChange(AttributeStateEvent e)
		{
		}

		public void errorChange(ErrorEvent evt)
		{
		}
	}
	
	class TableModel extends AbstractTableModel implements IDevStateScalarListener 
	{
		List<MotorGroup> motorGroups;

		public int getColumnCount()
		{
			return 4;
		}

		public int getRowCount()
		{
			return motorGroups != null ? motorGroups.size() : 0;
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			MotorGroup mg = null;
		
			int motorGroupsLen = motorGroups.size();
			
			if(rowIndex < motorGroupsLen)
			{
				mg = motorGroups.get(rowIndex);
			}
			
			if(mg == null)
				return null;
			
			if(columnIndex == 0)
			{
				JLabel l = new JLabel(mg.getState());
				l.setOpaque(true);
				return l;
			}
			else if(columnIndex == 1)
				return mg;
			else if(columnIndex == 2)
				return mg.getDeviceName();
			else if(columnIndex == 3)
				return mg.getElements();
			else 
				return null;
		}
		
	    private void updateMotorGroupList(List<MotorGroup> newMotorGroups)
	    {
	    	if(motorGroups != null)
	    	{
	    		for(MotorGroup mg : motorGroups) mg.removeDevStateScalarListener(this);
	    	}
	    	if(newMotorGroups != null)
	    	{
	    		for(MotorGroup mg : newMotorGroups) mg.addDevStateScalarListener(this);
	    	}
	    	motorGroups = newMotorGroups;
	    }

	    public void update(List<MotorGroup> newMotorGroups)
	    {
	    	updateMotorGroupList(newMotorGroups);
	    	fireTableDataChanged();
	    }

		public void devStateScalarChange(DevStateScalarEvent e)
		{
			Device d = ((DevStateScalar)e.getSource()).getDevice();
			
			String devName = d.getName();
			
			int motorCount = motorGroups.size();
			for(int i = 0; i < motorCount; i++)
			{
				MotorGroup m = motorGroups.get(i);
				if(m.getDeviceName().equals(devName))
				{
					fireTableCellUpdated(i, 0);
					return;
				}
			}
		}

		public void stateChange(AttributeStateEvent e)
		{
			// TODO Auto-generated method stub
			
		}

		public void errorChange(ErrorEvent evt)
		{
			// TODO Auto-generated method stub
			
		}
	}
	
	//TODO: Substance look and feel
	//class MGStateCellRenderer extends SubstanceDefaultTableCellRenderer
	class MGStateCellRenderer extends DefaultTableCellRenderer
	{

		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			if(value instanceof JLabel)
			{
				JLabel l = (JLabel)value;
				l.setHorizontalAlignment(SwingConstants.CENTER);
				if(!isSelected && !hasFocus)
				{
					l.setBackground(SwingResource.getColor4State(l.getText()));
					l.setForeground(table.getForeground());
					return l;
				}
			
				else
				{
					l.setBackground(table.getSelectionBackground());
					l.setForeground(SwingResource.getColor4State(l.getText()));
					return l;
				}
			}
			
			return super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
					row, column);
		}
	}
}
