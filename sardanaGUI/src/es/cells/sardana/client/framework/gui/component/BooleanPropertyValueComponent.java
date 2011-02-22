package es.cells.sardana.client.framework.gui.component;

import java.awt.Color;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.framework.pool.PropertyType;

public class BooleanPropertyValueComponent extends JComboBox implements IPropertyComponent, ActionListener, PropertyChangeListener
{
	JLabel label;
	PropertyInstance prop_model;

	public BooleanPropertyValueComponent(PropertyInstance prop_model)
	{
		super(new Object[] {null,false,true});
		this.prop_model = prop_model;
		addPropertyChangeListener("labeledBy", this);
		setValue(prop_model.getValue());
		addActionListener(this);
	}
		
	public PropertyInstance getPropertyModel()
	{
		return prop_model;
	}

	public void actionPerformed(ActionEvent e) 
	{
		updateModelValue();
		updateLabel();
	}

	public void propertyChange(PropertyChangeEvent evt) 
	{
		Object o = evt.getNewValue();
		if (o == null) label = null;
		else label = (JLabel) o;
		updateLabel();
	}
	
	protected void updateLabel()
	{
		if(label == null)
			return;
		int i = getSelectedIndex();
		if(i > 0)
			label.setForeground(Color.black);
		else
			label.setForeground(Color.red);
	}

	protected void updateModelValue()
	{
		prop_model.setValue(getSelectedItem());
	}

	public Object getValue() 
	{
		updateModelValue();
		return prop_model.getValue();
	}

	public void setValue(Object o) 
	{
		if(o == null)
		{
			setSelectedItem(null);
		}
		
		if(o instanceof Boolean)
			setSelectedItem((Boolean)o);
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		JFrame f = new JFrame("Small test for component");
		f.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		GridLayout gl = new GridLayout(2,2);
		f.getContentPane().setLayout(gl);
		PropertyInfo prop = new PropertyInfo("TrueOrFalse");
		prop.setDescription("The true or false question");
		prop.setType(PropertyType.DevBoolean);
		prop.setDefaultValue(true);
		final PropertyInstance p = new PropertyInstance(prop);
		BooleanPropertyValueComponent c = new BooleanPropertyValueComponent(p);
		JLabel l = new JLabel("P1:");
		l.setLabelFor(c);
		f.getContentPane().add(l);
		f.getContentPane().add(c);
		
		JButton b = new JButton("dump");
		b.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				System.out.println(p.getValue());
			}
		});
		f.add(b);
		
		f.pack();
		f.setVisible(true);
	}	
}
