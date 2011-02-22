package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.swing.AbstractCellEditor;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableCellEditor;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.framework.pool.PropertyType;
import es.cells.sardana.client.gui.swing.SwingResource;

public class PropertiesTableEditorPanel extends JPanel
{
	JTable table;
	
	ButtonsPanel buttonsPanel;
	
	JButton revertButton;
	
	int singleLineHeight;
	
	public PropertiesTableEditorPanel()
	{
		super();
		initComponents();
	}

	private void initComponents()
	{
		setLayout(new BorderLayout());
		PropertyTableModel model = new PropertyTableModel();
		
		DefaultTableColumnModel colModel = new DefaultTableColumnModel();
		
		TableColumn col = new TableColumn(0,75);
		col.setHeaderValue("Name");
		col.setCellRenderer(new PropertyCellRenderer());
		col.setMinWidth(100);
		colModel.addColumn(col);
		
		col = new TableColumn(1,200);
		col.setHeaderValue("Value");
		col.setCellRenderer(new PropertyValueCellRenderer());
		col.setCellEditor(new PropertyValueCellEditor());
		col.setMinWidth(100);
		colModel.addColumn(col);

		table = new JTable(model, colModel);
		table.setPreferredScrollableViewportSize(new Dimension(280,150));
		singleLineHeight = table.getRowHeight();
		
		JScrollPane pane = new JScrollPane(table);
		add(pane, BorderLayout.CENTER);
		
		buttonsPanel = new ButtonsPanel();
		
		revertButton = new JButton("Revert", SwingResource.smallIconMap.get(IImageResource.IMG_UNDO));
		revertButton.setToolTipText("<html>Revert changes made to the selected properties.<br>" +
				"If no property is selected, it will revert all properties");
		
		buttonsPanel.addRight(revertButton);
		
		revertButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				revertPressed();
			}
		});
		add(buttonsPanel,BorderLayout.SOUTH);
	}
	
	protected void revertPressed() 
	{
		PropertyTableModel model = (PropertyTableModel)table.getModel();
		
		model.revert(table.getSelectedRows());
	}

	protected PropertyTableModel getTableModel()
	{
		return (PropertyTableModel)table.getModel();
	}
	
	public void setData(HashMap<String, PropertyInfo> data, HashMap<String, Object> dbData)
	{
		getTableModel().setData(data, dbData);
	}
	
	public List<PropertyInfo> getData()
	{
		return getTableModel().getData();
	}
	
	public List<Object> getNewValueData()
	{
		return getTableModel().getNewValueData();
	}
	
	public List<Object> getClassPropertyValues()
	{
		return getTableModel().getClassPropertyValues();
	}	
	
	class PropertyValueCellEditor extends AbstractCellEditor implements TableCellEditor, ChangeListener, ActionListener
	{
		PropertyInstance currValue;
		int currRow = -1;
		JTextArea component = new JTextArea(); 
		
		public PropertyValueCellEditor()
		{
			super();
			component.setLineWrap(false);
		}
		
		public Component getTableCellEditorComponent(JTable table,
				Object value, boolean isSelected, int row, int column) 
		{
			currValue = (PropertyInstance) value;
			
			assert(currValue != null);
			
			component.setText(DevicePoolUtils.toPropertyValueString(currValue.getType(),currValue.getValue()));
			
			return component;
		}

		public Object getCellEditorValue() 
		{
			return currValue;
		}

		public void stateChanged(ChangeEvent e)
		{
			// TODO Auto-generated method stub
			
		}

		public void actionPerformed(ActionEvent e) 
		{
			String txt = component.getText();
			currValue.setValue(DevicePoolUtils.toPropertyValue(currValue.getType(),txt));
			currValue.setOverrideDefault(true);
		}

	}

	class PropertyCellRenderer extends DefaultTableCellRenderer
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{
			JLabel l = (JLabel) super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
					row, column);
			
			PropertyInstance p = (PropertyInstance) value;
			
			if(p.getDefaultValue() == null)
			{
				l.setFont(l.getFont().deriveFont(Font.BOLD));
				if(p.getValue() == null)
				{
					l.setForeground(Color.red);
				}
			}
			else
				l.setForeground(Color.black);
			
			StringBuffer buff = new StringBuffer();
			buff.append("<html><b>Name:</b> "+ p.getName());
			buff.append("<br><b>Default Value:</b> " + (p.getDefaultValue() == null ? "<i>None</i>" : p.getDefaultValue()));
			buff.append("<br><b>Type:</b> " + p.getType());
			buff.append("<br><b>Description:</b> " + p.getDescription());
			l.setToolTipText(buff.toString());
			
			return l;
		}
	}

	class PropertyValueCellRenderer extends JTextArea implements TableCellRenderer
	{
		public PropertyValueCellRenderer() 
		{
			setLineWrap(true);
			setWrapStyleWord(true);
			setOpaque(true);
		}
		
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{
			if (isSelected) 
			{
				setForeground(table.getSelectionForeground());
				setBackground(table.getSelectionBackground());
			} 
			else 
			{
				setForeground(table.getForeground());
				setBackground(table.getBackground());
			}			
			
			setFont(table.getFont());
			if (hasFocus) 
			{
				setBorder( UIManager.getBorder("Table.focusCellHighlightBorder") );
				if (table.isCellEditable(row, column)) 
				{
					setForeground( UIManager.getColor("Table.focusCellForeground") );
					setBackground( UIManager.getColor("Table.focusCellBackground") );
				}
			} 
			else 
			{
				setBorder(new EmptyBorder(1, 2, 1, 2));
			}			
			
			if(value == null) 
				setText("");
			else
			{
				PropertyInstance pi = (PropertyInstance) value;
				PropertyType type = pi.getType();
				Object v = pi.getValue();
				String str = DevicePoolUtils.toPropertyValueString(type, v);
				setText(str);
				
				int lineCount = DevicePoolUtils.getPropertyValueLineCount(type, v);
				if(lineCount == 0)
					lineCount = 1;
				table.setRowHeight(row, singleLineHeight * lineCount);
			}
		    return this;			
		}
	}	

	class PropertyTableModel extends AbstractTableModel
	{
		ArrayList<PropertyInstance> data = new ArrayList<PropertyInstance>();
		
		public int getColumnCount()
		{
			return 2;
		}

		public List<Object> getClassPropertyValues() 
		{
			ArrayList<Object> ret = new ArrayList<Object>(data.size());
			for(PropertyInstance p : data)
			{
				ret.add(p.getDbValue());
			}
			return ret;
		}

		public List<Object> getNewValueData() 
		{			
			ArrayList<Object> ret = new ArrayList<Object>(data.size());
			for(PropertyInstance p : data)
			{
				ret.add(p.isOverrideDefault() ? p.getValue() : null);
			}
			return ret;
		}

		public List<PropertyInfo> getData() 
		{
			ArrayList<PropertyInfo> ret = new ArrayList<PropertyInfo>(data.size());
			for(PropertyInstance p : data)
			{
				ret.add(p.getPropertyInfo());
			}
			return ret;
		}

		public void revert(int rowIndex[]) 
		{	
			if(rowIndex.length == 0)
			{
				for(PropertyInstance p : data)
				{
					Object dbValue = p.getDbValue();
					Object dftValue = p.getDefaultValue();
					Object value = dbValue != null ? dbValue : dftValue;
					p.setValue(value);
					p.setOverrideDefault(false);
				}
			}
			else
			{
				for(int idx : rowIndex)
				{
					PropertyInstance p = data.get(idx);
					Object dbValue = p.getDbValue();
					Object dftValue = p.getDefaultValue();
					Object value = dbValue != null ? dbValue : dftValue;
					p.setValue(value);
					p.setOverrideDefault(false);
				}
			}
			fireTableRowsUpdated(0, data.size()-1);
		}

		public void setData(HashMap<String, PropertyInfo> data, HashMap<String, Object> dbData)
		{
			this.data.clear();
			
			if(data == null)
			{
				fireTableDataChanged();
				return;
			}
			
			for(PropertyInfo info : data.values())
			{
				Object dbValue = dbData == null ? null : dbData.get(info.getName());
				Object dftValue = info.getDefaultValue();
				Object value = dbValue != null ? dbValue : dftValue;
				
				this.data.add(new PropertyInstance(info,dbValue,value));
			}
			fireTableDataChanged();
		}

		public int getRowCount()
		{
			return data.size();
		}

		@Override
		public boolean isCellEditable(int rowIndex, int columnIndex) 
		{
			return columnIndex == 1;
		}

		@Override
		public void setValueAt(Object aValue, int rowIndex, int columnIndex) 
		{
			super.setValueAt(aValue, rowIndex, columnIndex);
			/*
			PropertyInstance value = (PropertyInstance) aValue;
			
			if(value == null)
			{
				data.get(rowIndex).setValue(null);
				data.get(rowIndex).setOverrideDefault(false);
			}
			else
			{
				try
				{
					data.get(rowIndex).setValue(value);
					data.get(rowIndex).setOverrideDefault(true);
				}
				catch(NumberFormatException e)
				{
					JOptionPane.showMessageDialog(null, 
							"Please type a valid number",
							"Invalid number",
							JOptionPane.ERROR_MESSAGE);
				}
			}*/
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			PropertyInstance info = data.get(rowIndex);
			return info; 
		}
	}
	
	public static void main(String[] args) 
	{
		JFrame f = new JFrame("Properties Table Editor Panel Test");
		
		f.setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		PropertiesTableEditorPanel p = new PropertiesTableEditorPanel();
		
		HashMap<String, PropertyInfo> props = new HashMap<String, PropertyInfo>();
		
		PropertyInfo prop = new PropertyInfo("host");
		prop.setDescription("The host name of the Icepap controller");
		prop.setType(PropertyType.DevString);
		prop.setDefaultValue("icepap01");
		props.put(prop.getName(), prop);

		prop = new PropertyInfo("port");
		prop.setDescription("The TCP port of the Icepap controller");
		prop.setType(PropertyType.DevLong);
		props.put(prop.getName(), prop);
		
		prop = new PropertyInfo("AlternatePorts");
		prop.setDescription("Alternate TCP connection ports for the Icepap controller");
		prop.setType(PropertyType.DevVarLongArray);
		prop.setDefaultValue("2345\n3345\n4345");
		props.put(prop.getName(), prop);

		p.setData(props, new HashMap<String, Object>());
		
		JPanel panel = new JPanel(new BorderLayout());
		panel.add(p, BorderLayout.CENTER);
		
		f.getContentPane().add(panel);
		f.pack();
		f.setVisible(true);
	}
}

