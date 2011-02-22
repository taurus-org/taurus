package es.cells.sardana.client.framework.gui.panel;

import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.AbstractListModel;
import javax.swing.DefaultListCellRenderer;
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
import es.cells.sardana.client.framework.pool.PropertyInstance;

public class PropertiesFormViewerPanel extends JPanel
{
	PropListModel model;
	JList propertyList;
	
	JTextField typeText;
	JTextArea descrText;
	JTextArea valueText;
        
	JPanel formPanel;    

	public PropertiesFormViewerPanel()
	{
		super(new GridBagLayout());
		initComponents();
	}

	public void setData(HashMap<String, PropertyInstance> dataSource)
	{
		model.setData(dataSource);
	}
	
	public ArrayList<PropertyInstance> getData()
	{
		return model.getData();
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
		PropertyInstance propData = (PropertyInstance)propertyList.getSelectedValue();
		
		if(selIndex >= 0 && propData != null)
		{
			typeText.setText(propData.getType().toSimpleString());
			descrText.setText(propData.getDescription());
			
			Object value = propData.getValue();
			
			if(value != null)
			{
				valueText.setText(DevicePoolUtils.toPropertyValueString(propData.getType(), value));
				valueText.setFont(typeText.getFont());
			}
			else
			{
				valueText.setText("no value!");
				valueText.setFont(typeText.getFont().deriveFont(Font.ITALIC));
			}
		}
		else
		{
			typeText.setText("");
			descrText.setText("");
			valueText.setText("");
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
		
		typeText = new JTextField("");
		descrText = new JTextArea("");
		valueText = new JTextArea("");
		
		typeText.setEditable(false);
		descrText.setEditable(false);
		valueText.setEditable(false);
		
		typeText.setColumns(40);
		descrText.setColumns(40);
		valueText.setColumns(40);
		
		descrText.setRows(3);
		valueText.setRows(3);
		
		GridBagConstraints gbc = new GridBagConstraints();
		
		gbc.insets = new Insets(2,2,2,2);
		gbc.anchor = GridBagConstraints.SOUTHEAST;
		gbc.gridx = 0;
		gbc.gridy = 0;
		JLabel typeLabel = new JLabel("Type:");
		panel.add(typeLabel,gbc);
		
		gbc.anchor = GridBagConstraints.NORTHEAST;
		gbc.gridy = 1;
		JLabel descrLabel = new JLabel("Description:");
		panel.add(descrLabel,gbc);		
		
		gbc.gridy = 2;
		JLabel dftValueLabel = new JLabel("Value:");
		panel.add(dftValueLabel,gbc);		
		
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
		panel.add(new JScrollPane(valueText),gbc);		

		return panel;
	}
	
	class PropListModel extends AbstractListModel
	{
		ArrayList<PropertyInstance> dataSource;
		
		public PropListModel() 
		{
			super();
			dataSource = new ArrayList<PropertyInstance>();
		}

		public void setData(HashMap<String, PropertyInstance> data)
		{
			this.dataSource.clear();
			
			for(String propName : data.keySet())
			{
				this.dataSource.add(data.get(propName));
			}
			fireContentsChanged(this, 0, data.size()-1);
		}

		public ArrayList<PropertyInstance> getData() 
		{
			return dataSource;
		}		

		public Object getElementAt(int index) 
		{
			return index >= dataSource.size() ? null : dataSource.get(index);
		}

		public int getSize() 
		{
			return dataSource.size();
		}
	}
	
	//TODO: Substance look and feel 
	//class PropListRenderer extends SubstanceDefaultListCellRenderer
	class PropListRenderer extends DefaultListCellRenderer
	{

		@Override
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) {
			
			Component c = super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
			return c;
		}
		
	}

}
