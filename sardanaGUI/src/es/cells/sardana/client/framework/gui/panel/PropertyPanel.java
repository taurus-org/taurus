package es.cells.sardana.client.framework.gui.panel;

import java.awt.Component;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingConstants;

import es.cells.sardana.client.framework.gui.component.PropertyComponentFactory;
import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;

public class PropertyPanel extends JPanel 
{
	List<PropertyInstance> props;
	List<Component> components;
	
	public PropertyPanel()
	{
		super();
		this.props = new ArrayList<PropertyInstance>(10);
		initComponents();
	}
	
	public void setModel(HashMap<String, PropertyInfo> data, HashMap<String, Object> dbData)
	{
		this.props.clear();
		removeAll();
		
		if(data == null)
		{
			return;
		}
		
		for(PropertyInfo info : data.values())
		{
			Object dbValue = dbData == null ? null : dbData.get(info.getName());
			Object dftValue = info.getDefaultValue();
			Object value = dbValue != null ? dbValue : dftValue;
			
			this.props.add(new PropertyInstance(info,dbValue,value));
		}
		initComponents();
		repaint();
	}
	
	public List<PropertyInfo> getData() 
	{
		ArrayList<PropertyInfo> ret = new ArrayList<PropertyInfo>(props.size());
		for(PropertyInstance p : props)
		{
			ret.add(p.getPropertyInfo());
		}
		return ret;
	}	
	
	public List<Object> getNewValueData() 
	{			
		ArrayList<Object> ret = new ArrayList<Object>(props.size());
		for(PropertyInstance p : props)
		{
			ret.add(p.getValue());
		}
		return ret;
	}
	
	public List<Object> getClassPropertyValues() 
	{
		ArrayList<Object> ret = new ArrayList<Object>(props.size());
		for(PropertyInstance p : props)
		{
			ret.add(p.getDbValue());
		}
		return ret;
	}	
	
	protected void initComponents()
	{
		setLayout(new GridBagLayout());
		
		GridBagConstraints gbc = null;
		int idx = 0;
		
		for(PropertyInstance p : props)
		{
			StringBuffer buff = new StringBuffer();
			buff.append("<html><b>Name:</b> "+ p.getName());
			buff.append("<br><b>Default Value:</b> " + (p.getDefaultValue() == null ? "<i>None</i>" : p.getDefaultValue()));
			buff.append("<br><b>Type:</b> " + p.getType());
			buff.append("<br><b>Description:</b> " + p.getDescription());

			Component c = PropertyComponentFactory.getInstance().getComponentForProperty(p);
			
			if(p.getType().isSimpleType())
			{
				JLabel lbl = new JLabel(p.getName()+":");
				lbl.setToolTipText(buff.toString());
				lbl.setHorizontalAlignment(SwingConstants.RIGHT);
				lbl.setLabelFor(c);
				
				gbc = new GridBagConstraints(
						0,idx, //grid x,y
						1,1, //width, height
						0.0,0.0, //weight x,y
						GridBagConstraints.WEST, //anchor
						GridBagConstraints.HORIZONTAL, // fill
						new Insets(2,2,2,2), //insets
						0,0 //pad x,y
						);
				add(lbl,gbc);
				
				gbc = new GridBagConstraints(
						1,idx, //grid x,y
						1,1, //width, height
						1.0,0.0, //weight x,y
						GridBagConstraints.EAST, //anchor
						GridBagConstraints.HORIZONTAL, // fill
						new Insets(2,2,2,2), //insets
						0,0 //pad x,y
						);
				add(c,gbc);
				
			}
			else
			{
				gbc = new GridBagConstraints(
						0,idx, //grid x,y
						2,1, //width, height
						1.0,1.0, //weight x,y
						GridBagConstraints.CENTER, //anchor
						GridBagConstraints.HORIZONTAL, // fill
						new Insets(2,2,2,2), //insets
						0,0 //pad x,y
						);
				add(c,gbc);
			}
			idx++;
		}
	}
}
