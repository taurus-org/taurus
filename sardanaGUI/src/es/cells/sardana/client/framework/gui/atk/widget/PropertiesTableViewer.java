package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Font;
import java.awt.Rectangle;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.AbstractCellEditor;
import javax.swing.BoxLayout;
import javax.swing.DefaultListModel;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.UIManager;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import javax.swing.event.TableModelEvent;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableCellEditor;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;

import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.PropertyInfo;

public class PropertiesTableViewer extends JPanel {
 
	JTable table;
	PropertiesTableModel model;
	
	static String[] colNames = {"Name", "Type", "Default Value", "Value", "Description"};
	static int[] colWidths = {100,70,120,100,150}; 
	public PropertiesTableViewer()
	{
		super();
		model = new PropertiesTableModel();
		TableColumnModel cols  = createColumnModel(colNames, colWidths);
		table = new JTable(model,cols);
		table.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
		
		JScrollPane pane = new JScrollPane(table);
		
		setLayout( new BorderLayout(0,0) );
		add(pane,BorderLayout.CENTER);
	}

	protected TableColumnModel createColumnModel(String[] columnNames, int[] widths)
	{
		DefaultTableColumnModel columns  = new DefaultTableColumnModel();
		
		for(int count = columnNames.length, i = 0; i < count; i++)
		{
			TableColumn column = new TableColumn(i);
			column.setHeaderValue(columnNames[i]);
			column.setWidth(widths[i]);
			column.setPreferredWidth(widths[i]);
			if(i == 2 || i == 3)
				column.setCellRenderer(new MultiLineCRPanel());
			if(i == 3)
				column.setCellEditor( new XCellEditor() );
			columns.addColumn(column);
			
		}
		return columns;
	}
	
	public ArrayList<PropertyInfo> getData()
	{
		return model.getData();
	}
	
	public String[] getNewValueData()
	{
		return model.getNewValueData();
	}
	
	public void setData(HashMap<String, PropertyInfo> data) 
	{
		model.setData(data);
	}
	
	class PropertiesTableModel extends AbstractTableModel
	{
		ArrayList<PropertyInfo> data;
		String[] newValue;
		
		public PropertiesTableModel() {
			super();
			data = new ArrayList<PropertyInfo>();
		}

		public String[] getNewValueData() {
			return newValue;
		}

		public ArrayList<PropertyInfo> getData() {
			return data;
		}

		public void setData(HashMap<String, PropertyInfo> data) {
			this.data.clear();
			this.data.addAll(data.values());
			newValue = new String[this.data.size()];
			fireTableChanged( new TableModelEvent(this) );
		}

		public int getColumnCount() {
			return 5;
		}

		public int getRowCount() {
			return data.size();
		}

		public Object getValueAt(int row, int col) {
			
			if(row >= getRowCount() || col >= getColumnCount())
				return null;
			
			PropertyInfo prop = data.get(row);
			
			if(col == 0) return prop.getName();
			else if(col == 1) return prop.getType().toSimpleString();
			else if(col == 2)
			{
				return DevicePoolUtils.toPropertyValueString(prop.getType(), prop.getDefaultValue());
			}
			else if(col == 3)
			{
				if(newValue[row] == null)
					newValue[row] = "";
				return newValue[row];
			}
			else if(col == 4) return prop.getDescription();
			else return null;
		}

		@Override
		public void setValueAt(Object aValue, int rowIndex, int columnIndex)
		{
			if(columnIndex != 3)
				return;
			
			newValue[rowIndex] = (String)aValue;
		}

		@Override
		public boolean isCellEditable(int rowIndex, int columnIndex) {
			return columnIndex == 3;
		}
		
	}
	
	class XCellEditor extends AbstractCellEditor implements TableCellEditor 
	{
		JTextField component = new JTextField();
    
        public Component getTableCellEditorComponent(JTable table, Object value,
                boolean isSelected, int rowIndex, int vColIndex) {
    
            component.setText((String)value);
    
            return component;
        }
    
        public Object getCellEditorValue() 
        {
            return component.getText();
        }
    }
	
	class MultiLineCRPanel extends JPanel implements TableCellRenderer
	{
		public MultiLineCRPanel()
		{
			super();
			setLayout(new BoxLayout(this, BoxLayout.Y_AXIS));
			setOpaque(true);
		}
		
		@Override
		public void setBackground(Color bg) 
		{
			super.setBackground(bg);
		}

		@Override
		public void setForeground(Color fg) 
		{
			super.setForeground(fg);
			for(Component c : getComponents())
				if(c instanceof JLabel)
					c.setForeground(fg);
		}
		
		public void setFont(Font font) 
		{
			super.setFont(font);
			for(Component c : getComponents())
				if(c instanceof JLabel)
					c.setFont(font);
		}

		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{
			removeAll();
			invalidate();
			
			if(value == null)
				return this;
			
			String[] elems = ((String)value).split("\n"); 
			
			int i = 0;
			for(String elem : elems)
			{
				JLabel lbl = new JLabel(elem);
				add(lbl);
				i++;
			}
			
			if(table.isCellEditable(row, column))
				setFont(table.getFont().deriveFont(Font.BOLD));
			else
				setFont(table.getFont());

			int height = Math.max(elems.length*16,  table.getRowHeight(row));
			
			table.setRowHeight(row, height);

			if(isSelected)
			{
				setBackground(table.getSelectionBackground());
				setForeground(table.getSelectionForeground());
			}
			else
			{
				setBackground(table.getBackground());
				setForeground(table.getForeground());				
			}
			
			if (hasFocus) 
			{
	            Border border = null;
	            if (isSelected) 
	                border = UIManager.getBorder("Table.focusSelectedCellHighlightBorder");
	            if (border == null) 
	                border = UIManager.getBorder("Table.focusCellHighlightBorder");
	            setBorder(border);

			    if (!isSelected && table.isCellEditable(row, column)) 
			    {
	                Color col;
	                col = UIManager.getColor("Table.focusCellForeground");
	                if (col != null) 
	                	super.setForeground(col);
	
	                col = UIManager.getColor("Table.focusCellBackground");
	                
	                if (col != null) 
	                	super.setBackground(col);
			    }
			} 
			else 
			{
	            setBorder(new EmptyBorder(1, 1, 1, 1));
			}			
			
			return this;
		}
	}
	
	class MultiLineCRTextArea extends JTextArea implements TableCellRenderer
	{
		
	    public MultiLineCRTextArea() 
	    {
			super();
		}
		public void invalidate() {}
	    public void validate() {}
	    public void revalidate() {}
	    public void repaint(long tm, int x, int y, int width, int height) {}
	    public void repaint(Rectangle r) {}
	    public void repaint() {}

		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{
			if(value == null)
				return this;
			setText(value.toString());
			int rows = value instanceof String ? ((String)value).split("\n").length : 1;
			setRows(rows);
			table.setRowHeight(row, rows*16);
		
			this.setFont(table.getFont());
			if(isSelected)
			{
				setBackground(table.getSelectionBackground());
				setForeground(table.getSelectionForeground());
			}
			else
			{
				setBackground(table.getBackground());
				setForeground(table.getForeground());				
			}
			
			if (hasFocus) 
			{
	            Border border = null;
	            if (isSelected) 
	                border = UIManager.getBorder("Table.focusSelectedCellHighlightBorder");
	            if (border == null) 
	                border = UIManager.getBorder("Table.focusCellHighlightBorder");
	            setBorder(border);

			    if (!isSelected && table.isCellEditable(row, column)) 
			    {
	                Color col;
	                col = UIManager.getColor("Table.focusCellForeground");
	                if (col != null) 
	                	super.setForeground(col);
	
	                col = UIManager.getColor("Table.focusCellBackground");
	                
	                if (col != null) 
	                	super.setBackground(col);
			    }
			} 
			else 
			{
	            setBorder(new EmptyBorder(1, 1, 1, 1));
			}
			return this;
		}
	}	
	
	class MultiLineCRLabel extends DefaultTableCellRenderer
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{

			JLabel c = (JLabel) super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
					row, column);
			if(value instanceof String)
				c.setToolTipText("<html>" + ((String)value).replaceAll("\n", "<br>"));
			return c;
		}
	}
	
	class MultiLineCRList extends JList implements TableCellRenderer
	{
	    public void invalidate() {}
	    public void validate() {}
	    public void revalidate() {}
	    public void repaint(long tm, int x, int y, int width, int height) {}
	    public void repaint(Rectangle r) {}
	    public void repaint() {}
	    
		public MultiLineCRList() 
		{
			super(new DefaultListModel());
		}

		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{
			DefaultListModel model = (DefaultListModel)this.getModel();
			model.removeAllElements();

			if(value == null)
				return this; 
			
			if(value instanceof String)
			{
				String[] elems = ((String)value).split("\n");
				for(String elem : elems)
					model.addElement(elem);
				this.setVisibleRowCount(elems.length);
				
				table.setRowHeight(row, elems.length > 0 ? elems.length*16 : 16);
			}
			
			return this;
		}
		
	}
	
}
