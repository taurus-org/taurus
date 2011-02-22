package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.JPanel;
import javax.swing.JTable;
import javax.swing.table.AbstractTableModel;

import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;

public class PropertiesTableViewerPanel extends JPanel
{
	JTable table;
	
	public PropertiesTableViewerPanel()
	{
		super();
		initComponents();
	}

	private void initComponents()
	{
		setLayout(new BorderLayout());
		PropertyTableModel model = new PropertyTableModel();
		table = new JTable(model);
		
		
		add(table, BorderLayout.CENTER);
	}
	
	protected PropertyTableModel getTableModel()
	{
		return (PropertyTableModel)table.getModel();
	}
	
	public void setData(HashMap<String, PropertyInfo> data)
	{
		getTableModel().setData(data);
	}
	
	class PropertyTableModel extends AbstractTableModel
	{
		ArrayList<PropertyInstance> data;
		
		public int getColumnCount()
		{
			return 5;
		}

		public void setData(HashMap<String, PropertyInfo> data)
		{
			this.data.clear();
			for(PropertyInfo info : data.values())
			{
				this.data.add(new PropertyInstance(info));
			}
			fireTableDataChanged();
		}

		public int getRowCount()
		{
			return data.size();
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			PropertyInstance info = data.get(rowIndex);
			
			if(columnIndex == 0)
				return info.getName();
			else if(columnIndex == 1)
				return info.getValue();
			else if(columnIndex == 2)
				return info.getDefaultValue();
			else if(columnIndex == 3)
				return info.getType();
			else if(columnIndex == 4)
				return info.getDescription();
			
			return null;
		}
	}
}
