package es.cells.sardana.client.framework.gui.component;

import java.awt.Color;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JTextArea;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.framework.pool.PropertyType;

public class StringPropertyValueComponent extends JTextArea implements IPropertyComponent, KeyListener, PropertyChangeListener 
{
	JLabel label;
	PropertyInstance model;

	public StringPropertyValueComponent(PropertyInstance model)
	{
		super();
		setWrapStyleWord(false);
		setLineWrap(true);
		setFont(new Font("Monospaced",Font.PLAIN, 12));
		this.model = model;
		setValue(model.getValue());
		addKeyListener(this);
		addPropertyChangeListener("labeledBy", this);
	}

	public Object getValue() 
	{
		updateModelValue();
		return model.getValue();
	}

	public void setValue(Object o) 
	{
		model.setValue(o);
		updateValue();
	}
	
	public PropertyInstance getPropertyModel()
	{
		return model;
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
		String str = getText();
		if(str != null && str.length() > 0)
			label.setForeground(Color.black);
		else
			label.setForeground(Color.red);
	}
	
	protected void updateValue()
	{
		if(model == null)
			return;
		Object v = model.getValue();
		if(v == null)
			v = model.getDbValue();
			if(v == null)
				v = model.getDefaultValue();
		
		setText(v == null ? null: v.toString());
	}
	
	protected void updateModelValue()
	{
		String o = getText();
		model.setValue(o);
	}

	public void keyTyped(KeyEvent e) {}
	public void keyPressed(KeyEvent e) {}

	public void keyReleased(KeyEvent e) 
	{
		updateLabel();
		String v = getText();
		if(label != null)
		{
			if(v != null && v.length() > 0)
				label.setForeground(Color.black);
			else
				label.setForeground(Color.red);
		}
		model.setValue(v);
	}

	public static void main(String[] args) 
	{
		JFrame f = new JFrame("Small test for component");
		f.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		GridLayout gl = new GridLayout(3,2);
		f.getContentPane().setLayout(gl);
	
		// P1
		PropertyInfo prop = new PropertyInfo("Host");
		prop.setDescription("The Host of the Icepap controller");
		prop.setType(PropertyType.DevString);
		prop.setDefaultValue("icepap01");
		final PropertyInstance p1 = new PropertyInstance(prop);
		StringPropertyValueComponent c = null;
		c = new StringPropertyValueComponent(p1);
		JLabel l = new JLabel(p1.getName());
		l.setLabelFor(c);
		f.getContentPane().add(l);
		f.getContentPane().add(c);
		
		// P2
		prop = new PropertyInfo("Host2");
		prop.setDescription("The Host of the Icepap controller");
		prop.setType(PropertyType.DevString);
		final PropertyInstance p2 = new PropertyInstance(prop);
		c = new StringPropertyValueComponent(p2);
		l = new JLabel(p2.getName());
		l.setLabelFor(c);
		f.getContentPane().add(l);
		f.getContentPane().add(c);

		JButton b = new JButton("dump");
		b.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				System.out.println(p1.getValue());
				System.out.println(p2.getValue());
			}
		});
		f.add(b);
		
		f.pack();
		f.setVisible(true);
	}
}
