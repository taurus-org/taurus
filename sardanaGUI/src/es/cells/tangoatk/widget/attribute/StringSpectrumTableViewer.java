package es.cells.tangoatk.widget.attribute;

import java.awt.Dimension;
import java.util.Vector;

import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.border.TitledBorder;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.table.TableModel;

import es.cells.tangoatk.utils.IStringFilter;
import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class StringSpectrumTableViewer extends JPanel implements IStringSpectrumListener
{
	protected JScrollPane     jScrollPane1;
	protected JTable          strSpectTable;
	
	protected IStringSpectrum model;

	protected int             columnIndex = -1;
	
	protected IStringSplitter splitter;
	
	protected IStringFilter   filter;
	protected int             columnFilterIndex = -1;
	
	protected String          customTitle;
	
	/**
	 * This contructor will create a single column table view of
	 * the string spectrum.
	 */
	public StringSpectrumTableViewer()
	{
		this(new Object[]{"Value"});
	}
	
	/**
	 * This constructor will create a table view of the 
	 * string spectrum with different columns.
	 * 
	 * @param columnNames Array containing the column titles
	 */
	public StringSpectrumTableViewer(Object[] columnNames)
	{
		this(columnNames, 0);
	}
	
	/**
	 * This constructor will create a multiple column table view of the 
	 * string spectrum. 
	 * 
	 * @param columnNames Array containing the column titles
	 * @param columnIndex The column that will represent the primary key/indentifier of the
	 *                    table. If set to -1 the complete string will be used as the identifier.
	 */
	public StringSpectrumTableViewer(Object[] columnNames, int columnIndex)
	{
		this.columnIndex = columnIndex;
		
		initComponents(columnNames);
	}
	
	public String getCustomTitle() {
		return customTitle;
	}

	public void setCustomTitle(String customTitle) 
	{
		this.customTitle = customTitle;
		((TitledBorder)getBorder()).setTitle(customTitle);
	}

	@Override
	public void setPreferredSize(Dimension preferredSize)
	{
		super.setPreferredSize(preferredSize);
		jScrollPane1.setPreferredSize(preferredSize);
	}

	protected void initComponents(Object[] columnNames)
	{
		jScrollPane1 = new javax.swing.JScrollPane();
		jScrollPane1.setPreferredSize(new Dimension(375,125));
		
		TableModel data = createTableModel(columnNames.length);
		TableColumnModel columns  = createColumnModel(columnNames);
		
		strSpectTable = new JTable(data, columns);
		//strSpectTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
		strSpectTable.setRowSelectionAllowed(true);
		strSpectTable.setColumnSelectionAllowed(false);
	
		setLayout(new java.awt.BorderLayout());
		
		setBorder(new javax.swing.border.TitledBorder("StringSpectrum"));
		jScrollPane1.setVerticalScrollBarPolicy(javax.swing.JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		
		strSpectTable.setBackground(new java.awt.Color(204, 204, 204));
		jScrollPane1.setViewportView(strSpectTable);

		add(jScrollPane1, java.awt.BorderLayout.CENTER);
	}
	
	protected TableModel createTableModel(int columnCount)
	{
		TableModel data = new StringSpectrumTableModel(0, columnCount);
		return data;
	}
	
	protected TableColumnModel createColumnModel(Object[] columnNames)
	{
		DefaultTableColumnModel columns  = new DefaultTableColumnModel();
		
		for(int count = columnNames.length, i = 0; i < count; i++)
		{
			TableColumn column = new TableColumn(i);
			column.setHeaderValue(columnNames[i]);
			columns.addColumn(column);
		}
		return columns;
	}
	
	protected DefaultTableModel getTableModel()
	{ 
		return (DefaultTableModel) strSpectTable.getModel();
	}
	
	public void clearTable()
	{
		int rowCount = getTableModel().getRowCount();
		for(int i = 0; i < rowCount; i++)
			getTableModel().removeRow(0);
	}

	/**
	 * Sets a string filter for this table viewer
	 * @param filter the string filter
	 * @param columnIndex the column index for which the filter will be applied
	 */
	public void setFilter(IStringFilter filter, int columnIndex)
	{
		this.filter = filter;
		columnFilterIndex = columnIndex;
	}
	
	public IStringSplitter getSplitter()
	{
		return splitter;
	}

	public void setSplitter(IStringSplitter splitter)
	{
		this.splitter = splitter;
	}

	public void setModel(IStringSpectrum  strSpectAtt)
	{
		if (model != null)
		{
			model.removeListener(this);
		}
		
		clearTable();
		
		this.model = strSpectAtt;

		if ( model != null )
		{
			if(customTitle == null)
				((TitledBorder)getBorder()).setTitle(model.getNameSansDevice());
			model.addListener(this);
			
			update(model.getStringSpectrumValue());
		}
	}

	/**
	 * <code>getModel</code> gets the model of this SimpleStringSpectrumViewer.
	 *
	 * @return a <code>IStringSpectrum</code> value
	 */
	public IStringSpectrum getModel()
	{
		return model;
	}

	public int getColumnIndex()
	{
		return columnIndex;
	}

	public void setColumnIndex(int columnIndex)
	{
		this.columnIndex = columnIndex;
	}

	public int getRowCount()
	{
		return strSpectTable.getRowCount();
	}

	public JTable getTable()
	{
		return strSpectTable;
	}
	
	public Object getRowIndex(int row)
	{
		return strSpectTable.getValueAt(row, columnIndex >= 0 ? columnIndex : 0);
	}
	
	public Object getSelectedRowIndex()
	{
		int row = strSpectTable.getSelectedRow();
		return row>=0 ? getRowIndex(row) : null;
	}

	public Object[] getSelectedRowsIndexes()
	{
		int[] rows = strSpectTable.getSelectedRows();
		
		if(rows == null || rows.length == 0)
			return null;
		
		Object ret[] = new Object[rows.length];
		
		int i = 0;
		for(int row : rows)
			ret[i++] = getRowIndex(row);
		
		return ret; 
	}
	
	protected void update(String[] strArray)
	{	
		if (strArray == null)
		{
			getTableModel().addRow(new String[]{"StringSpectrumAttribute is null.\n"});
		}
		else
		{
			clearTable();
			
			for(String elem : strArray)
			{
				Object[] row = getCells(elem);
				
				if(row == null)
					continue;
				
				if(columnFilterIndex >=0 && filter != null)
				{
					if(!filter.isValid(row[columnFilterIndex].toString()))
						continue;
				}
				getTableModel().addRow(row);				
			}
		}
	}
	
	public void stringSpectrumChange(StringSpectrumEvent evt)
	{
		update(evt.getValue());
	}
	
	protected Object[] getCells(String row)
	{
		return splitter.split(row);
	}
	
	protected int rowIndex(Object[] row) 
	{
		DefaultTableModel tableModel = getTableModel();
		
		// We have to match the whole row
		if(columnIndex < 0)
		{
			for(int i = 0; i < tableModel.getRowCount(); i++)
			{
				boolean match = true;
				for(int j = 0; j < row.length ; j++) 
				{
					Object currCellValue = tableModel.getValueAt(i, j);
					if(!currCellValue.equals(row[j]))
					{
						match = false;
						j = row.length;
					}
				}
				if(match)
					return i;
			}
		}
		else 
		{
			for(int i = 0; i < strSpectTable.getRowCount(); i++)
			{
				Object currCellValue = strSpectTable.getValueAt(i, columnIndex);
				if(currCellValue.equals(row[columnIndex]))
					return i;
			}
		}
		return -1;
	}
	
	public void errorChange(ErrorEvent evt)
	{

	}

	public void stateChange(AttributeStateEvent evt)
	{

	}

	class StringSpectrumTableModel extends DefaultTableModel
	{
	    public StringSpectrumTableModel()
		{
			super();

		}
		public StringSpectrumTableModel(int rowCount, int columnCount)
		{
			super(rowCount, columnCount);
		}

		public StringSpectrumTableModel(Object[] columnNames, int rowCount)
		{
			super(columnNames, rowCount);
		}

		public StringSpectrumTableModel(Object[][] data, Object[] columnNames)
		{
			super(data, columnNames);
		}

		public StringSpectrumTableModel(Vector columnNames, int rowCount)
		{
			super(columnNames, rowCount);
		}

		public StringSpectrumTableModel(Vector data, Vector columnNames)
		{
			super(data, columnNames);
		}

		public boolean isCellEditable(int row, int column)
	    {
	        return false;
	    }
	}
}
