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

import es.cells.sardana.client.framework.pool.IORegister;
import es.cells.sardana.client.framework.pool.DevicePool;
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

public class IORegisterTableViewer extends JPanel 
{
	protected JScrollPane     pane;
	protected JTable          ioregisterTable;
	protected TableModel      model;
	
	DevicePool pool;
	
	IORegisterListener ioregisterListener;
	
	public IORegisterTableViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		model = new TableModel();
		
		//setBorder(BorderFactory.createTitledBorder("Ioregisters"));
		
		DefaultTableColumnModel colModel = new DefaultTableColumnModel();
		
		TableColumn column = new TableColumn(0);
		column.setHeaderValue("State");
		column.setPreferredWidth(50);
		column.setMaxWidth(50);
		column.setCellRenderer(new MStateCellRenderer());
		colModel.addColumn(column);
		
		column = new TableColumn(1);
		column.setHeaderValue("Name");
		column.setPreferredWidth(120);
		column.setMaxWidth(120);
		colModel.addColumn(column);

		column = new TableColumn(2);
		column.setHeaderValue("Device");
		colModel.addColumn(column);

		setLayout(new BorderLayout());
		pane = new JScrollPane();
		ioregisterTable = new JTable(model, colModel);
		ioregisterListener = new IORegisterListener();
		
		pane.setViewportView(ioregisterTable);
		
		add(pane, BorderLayout.CENTER);
	}

	public JTable getTable()
	{
		return ioregisterTable;
	}

	public IORegister getSelectedIORegister()
	{
		int row =  ioregisterTable.getSelectedRow();
		
		if(row < 0)
			return null;
		
		return (IORegister) ioregisterTable.getValueAt(row, 1);
	}
	
	public List<IORegister> getSelectedIORegisters()
	{
		ArrayList<IORegister> ret = new ArrayList<IORegister>();
		int[] rows = ioregisterTable.getSelectedRows();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((IORegister) ioregisterTable.getValueAt(row, 1));
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
			pool.removeIORegisterListListener(ioregisterListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addIORegisterListListener(ioregisterListener);
			model.update(pool.getIORegisters());
		}
	}
	
	class IORegisterListener implements IStringSpectrumListener 
	{

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update(pool.getIORegisters());
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
		List<IORegister> ioRegisters;

		public int getColumnCount()
		{
			return 3;
		}

		public int getRowCount()
		{
			return ioRegisters != null ? ioRegisters.size() : 0;
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			IORegister m = null;
		
			int motorsLen = ioRegisters.size();
			
			if(rowIndex < motorsLen)
			{
				m = ioRegisters.get(rowIndex);
			}
			
			if(m == null)
				return null;
			
			if(columnIndex == 0)
			{
				JLabel l = new JLabel(m.getState());
				l.setOpaque(true);
				return l;
			}
			else if(columnIndex == 1)
				return m;
			else if(columnIndex == 2)
				return m.getDeviceName();
			else 
				return null;
		}
		
	    /**
	     *  Returns <code>Object.class</code> regardless of <code>columnIndex</code>.
	     *
	     *  @param columnIndex  the column being queried
	     *  @return the Object.class
	     */
	    public Class<?> getColumnClass(int columnIndex) 
	    {
	    	if(columnIndex == 0)
	    		return JLabel.class;
	    	else if(columnIndex == 1)
	    		return IORegister.class; 
	    	return Object.class;
	    }
		
	    private void updateIORegisterList(List<IORegister> newIORegisters)
	    {
	    	if(ioRegisters != null)
	    	{
	    		for(IORegister m : ioRegisters) m.removeDevStateScalarListener(this);
	    	}
	    	if(newIORegisters != null)
	    	{
	    		for(IORegister m : newIORegisters) m.addDevStateScalarListener(this);
	    	}
	    	ioRegisters = newIORegisters;
	    }
	    
	    public void update(List<IORegister> newIORegisters)
	    {
	    	updateIORegisterList(newIORegisters);
	    	fireTableDataChanged();
	    }
 
		public void devStateScalarChange(DevStateScalarEvent e)
		{
			Device d = ((DevStateScalar)e.getSource()).getDevice();
			
			String devName = d.getName();
			
			int ioregisterCount = ioRegisters.size();
			for(int i = 0; i < ioregisterCount; i++)
			{
				IORegister ioregister = ioRegisters.get(i);
				if(ioregister.getDeviceName().equals(devName))
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
	//class MStateCellRenderer extends SubstanceDefaultTableCellRenderer
	class MStateCellRenderer extends DefaultTableCellRenderer
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
