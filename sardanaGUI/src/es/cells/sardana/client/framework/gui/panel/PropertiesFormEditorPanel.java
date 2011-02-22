package es.cells.sardana.client.framework.gui.panel;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.AbstractListModel;
import javax.swing.DefaultListCellRenderer;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.PropertyInfo;

public class PropertiesFormEditorPanel extends JPanel 
{
	PropListModel model;
	JList propertyList;
	
	JTextField typeText;
	JTextArea descrText;
	JTextArea dftValueText;
	JTextArea classValueText;
	JTextArea valueText;
        
	JPanel formPanel;    

    JLabel iconContainers[];
    ImageIcon propAddIcon = new ImageIcon("res/32x32/back.png");
    ImageIcon propRemoveIcon = new ImageIcon("res/32x32/editdelete.png");
    
	public PropertiesFormEditorPanel()
	{
		super(new GridBagLayout());
		initComponents();
	}

	public void setData(HashMap<String, PropertyInfo> dataSource, 
			            HashMap<String, Object> dataClassPropSource)
	{
		model.setData(dataSource, dataClassPropSource);
	}
	
	public ArrayList<PropertyInfo> getData()
	{
		return model.getData();
	}
	
	public ArrayList<String> getNewValueData()
	{
		return model.getNewValueData();
	}
	
	public ArrayList<Object> getClassPropertyValues()
	{
		return model.getClassPropertyValues();
	}
	
	private void initComponents() 
	{
		JScrollPane listPanel = createListPanel();
		formPanel = createFormPanel();
		
		listPanel.setPreferredSize(new Dimension(150,100));
		listPanel.setMinimumSize(new Dimension(150,100));
		GridBagConstraints gbc = new GridBagConstraints();
		gbc.insets = new Insets(0,2,0,0);
		gbc.anchor = GridBagConstraints.CENTER;
		gbc.fill = GridBagConstraints.BOTH;
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.weightx = 0.0;
		gbc.weighty = 1.0;
		add(listPanel,gbc);
		
		gbc.insets = new Insets(0,0,0,2);
		gbc.gridx = 1;
		gbc.weightx = 1.0;
		gbc.weighty = 1.0;
		add(formPanel,gbc);
	}

	public void propertyChanged()
	{
		int selIndex = propertyList.getSelectedIndex();
		PropertyInfo propInfo = (PropertyInfo)propertyList.getSelectedValue();
		
		if(selIndex >= 0 && propInfo != null)
		{
			typeText.setText(propInfo.getType().toSimpleString());
			descrText.setText(propInfo.getDescription());
			
			Object dftValue = propInfo.getDefaultValue();
			
			if(dftValue != null)
			{
				dftValueText.setText(DevicePoolUtils.toPropertyValueString(propInfo.getType(), dftValue));
				dftValueText.setFont(typeText.getFont());
			}
			else
			{
				dftValueText.setText("no default value");
				dftValueText.setFont(typeText.getFont().deriveFont(Font.ITALIC));
			}
			
			Object classValue = model.getClassPropertyValue(selIndex);
			
			if(classValue != null)
			{
				classValueText.setText(DevicePoolUtils.toPropertyValueString(propInfo.getType(), classValue));
				classValueText.setFont(typeText.getFont());
			}
			else
			{
				classValueText.setText("no value defined at the class level");
				classValueText.setFont(typeText.getFont().deriveFont(Font.ITALIC));
			}
			valueText.setText(model.getNewValueData().get(selIndex));
		}
		else
		{
			typeText.setText("");
			descrText.setText("");
			dftValueText.setText("");
			classValueText.setText("");
			valueText.setText("");
		}
		
		updateSelected();
	}

	protected void updateSelected()
	{
		int index = -1;
		int selIndex = propertyList.getSelectedIndex();
		PropertyInfo propInfo = (PropertyInfo)propertyList.getSelectedValue();
		
		if(selIndex >= 0 && propInfo != null)
		{
			Object dftValue = propInfo.getDefaultValue();
			Object classValue = model.getClassPropertyValue(selIndex);
			String valueStr = valueText.getText();
	
			if(valueStr != null && valueStr.length() > 0)
				index = 2;
			else if(classValue != null)
				index = 1;
			else if(dftValue != null)
				index = 0;
		}
		
		for(int i = 0; i < iconContainers.length; i++)
			iconContainers[i].setIcon((i!=index) ? propRemoveIcon : propAddIcon);
	}
	
	protected void storeValue()
	{
		String value = valueText.getText();

		int selectedIndex = propertyList.getSelectedIndex();
		
		for(int i = 0; i < iconContainers.length; i++)
			iconContainers[i].setIcon( propRemoveIcon );

		if(value!= null && value.length() > 0 && selectedIndex >= 0)
		{
			model.getNewValueData().set(selectedIndex, value);
		}
		
		if(selectedIndex >= 0)
		{
			PropertyInfo propInfo = (PropertyInfo)propertyList.getSelectedValue();
			if(propInfo != null)
			{
				int index = -1;
				Object dftValue = propInfo.getDefaultValue();
				Object classValue = model.getClassPropertyValue(selectedIndex);
				String valueStr = valueText.getText();
		
				if(valueStr != null && valueStr.length() > 0)
					index = 2;
				else if(classValue != null)
					index = 1;
				else if(dftValue != null)
					index = 0;
				iconContainers[index].setIcon( propAddIcon );
			}
		}
	}
	
	protected JScrollPane createListPanel()
	{
		model = new PropListModel();
		propertyList = new JList(model);

		propertyList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		propertyList.addListSelectionListener(new ListSelectionListener()
		{
			public void valueChanged(ListSelectionEvent e) 
			{
				propertyChanged();
			}
		});
		propertyList.setCellRenderer(new PropListRenderer());
		
		JScrollPane propListPane = new JScrollPane(propertyList);
		return propListPane;
	}
	
	protected JPanel createFormPanel()
	{
		JPanel panel = new JPanel( new GridBagLayout() );

		iconContainers = new JLabel[]{new JLabel(""),new JLabel(""),new JLabel("")};

		for(JLabel l : iconContainers) l.setIcon(propRemoveIcon);
		
		typeText = new JTextField("");
		descrText = new JTextArea("");
		dftValueText = new JTextArea("");
		classValueText = new JTextArea("");
		valueText = new JTextArea("");		
		
		typeText.setEditable(false);
		descrText.setEditable(false);
		classValueText.setEditable(false);
		dftValueText.setEditable(false);
		
		typeText.setColumns(40);
		descrText.setColumns(40);
		dftValueText.setColumns(40);
		classValueText.setColumns(40);
		valueText.setColumns(40);
		
		descrText.setRows(3);
		dftValueText.setRows(3);
		classValueText.setRows(3);
		valueText.setRows(3);
		
		valueText.addKeyListener(new KeyListener() 
		{
			public void keyPressed(KeyEvent evt) {}
			public void keyReleased(KeyEvent evt) {storeValue();}
			public void keyTyped(KeyEvent evt)	{ }
		});
		
		GridBagConstraints gbc = new GridBagConstraints();
		
		gbc.insets = new Insets(2,2,2,2);
		gbc.anchor = GridBagConstraints.EAST;
		gbc.gridx = 0;
		gbc.gridy = 0;
		JLabel typeLabel = new JLabel("Type:");
		panel.add(typeLabel,gbc);
		
		gbc.anchor = GridBagConstraints.NORTHEAST;
		gbc.gridy = 1;
		JLabel descrLabel = new JLabel("Description:");
		panel.add(descrLabel,gbc);		
		
		gbc.gridy = 2;
		JLabel dftValueLabel = new JLabel("Default value:");
		panel.add(dftValueLabel,gbc);		
		
		gbc.gridy = 3;
		JLabel classLevelValueLabel = new JLabel("Db Class Level value:");
		panel.add(classLevelValueLabel,gbc);		
		
		gbc.gridy = 4;
		JLabel valueLabel = new JLabel("Overwrite Value:");
		panel.add(valueLabel,gbc);
		
		gbc.anchor = GridBagConstraints.SOUTH;
		gbc.fill = GridBagConstraints.HORIZONTAL;
		gbc.gridx = 1;
		gbc.gridy = 0;
		gbc.weightx = 1.0;
		gbc.weighty = 1.0;
		gbc.gridwidth = 2;
		panel.add(typeText,gbc);		
		
		gbc.fill = GridBagConstraints.BOTH;
		gbc.gridy = 1;
		gbc.weightx = 1.0;
		panel.add(new JScrollPane(descrText),gbc);		
		
		gbc.gridy = 2;
		gbc.gridwidth = 1;
		panel.add(new JScrollPane(dftValueText),gbc);		

		gbc.gridy = 3;
		panel.add(new JScrollPane(classValueText),gbc);		

		gbc.gridy = 4;
		panel.add(new JScrollPane(valueText),gbc);		

		gbc.anchor = GridBagConstraints.CENTER;
		gbc.fill = GridBagConstraints.NONE;
		gbc.gridx = 2;
		gbc.gridy = 2;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;		
		panel.add(iconContainers[0], gbc);
		gbc.gridy = 3;
		panel.add(iconContainers[1], gbc);
		gbc.gridy = 4;
		panel.add(iconContainers[2], gbc);

		return panel;
	}
	
	class PropListModel extends AbstractListModel
	{
		ArrayList<PropertyInfo> dataSource;
		ArrayList<String> newValues;
		ArrayList<Object> classPropertyValues;
		
		public PropListModel() 
		{
			super();
			dataSource = new ArrayList<PropertyInfo>();
			classPropertyValues = new ArrayList<Object>();
		}

		public void setData(HashMap<String, PropertyInfo> data, HashMap<String, Object> dataClassPropSource)
		{
			this.dataSource.clear();
			this.classPropertyValues.clear();
			
			for(String propName : data.keySet())
			{
				this.dataSource.add(data.get(propName));
				
				Object classValue = dataClassPropSource.get(propName);
				
				if(classValue != null)
					classPropertyValues.add(classValue);
				else
					classPropertyValues.add(null);
			}
			
			newValues = new ArrayList<String>(this.dataSource.size());
			for(int i = 0; i < this.dataSource.size();i++) newValues.add("");

			fireContentsChanged(this, 0, data.size()-1);
		}
		
		public ArrayList<String> getNewValueData() {
			return newValues;
		}

		public ArrayList<PropertyInfo> getData() {
			return dataSource;
		}		

		public ArrayList<Object> getClassPropertyValues()
		{
			return classPropertyValues;
		}
		
		public Object getElementAt(int index) 
		{
			return index >= dataSource.size() ? null : dataSource.get(index);
		}

		public int getSize() 
		{
			return dataSource.size();
		}
		
		public String getNewValue(int index)
		{
			return newValues.get(index);
		}
		
		public Object getClassPropertyValue(int index)
		{
			return classPropertyValues.get(index);
		}
	}
	
	//TODO: Substance look and feel 
	//class PropListRenderer extends SubstanceDefaultListCellRenderer
	class PropListRenderer extends DefaultListCellRenderer
	{

		@Override
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
			
			Component c = super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
			
			if(value instanceof PropertyInfo)
			{
				if(((PropertyInfo)value).hasDefaultValue() ||
						model.getClassPropertyValue(index) != null)
					c.setFont(c.getFont().deriveFont(Font.PLAIN));
				else
					c.setFont(c.getFont().deriveFont(Font.BOLD));
			}
			
			return c;
		}
		
	}
}
