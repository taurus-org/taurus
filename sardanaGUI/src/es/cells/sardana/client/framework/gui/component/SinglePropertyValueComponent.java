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
import java.text.ParseException;

import javax.swing.InputVerifier;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JFormattedTextField;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.framework.pool.PropertyType;


public class SinglePropertyValueComponent extends JFormattedTextField implements IPropertyComponent, KeyListener, PropertyChangeListener 
{
	JLabel label;
	PropertyInstance model;
	
	public SinglePropertyValueComponent(PropertyInstance model) throws Exception
	{
		super(PropertyComponentFactory.getTextFormatForProperty(model));
		this.model = model;
		setFont(new Font("Monospaced",Font.PLAIN, 12));
		setFocusLostBehavior(JFormattedTextField.COMMIT_OR_REVERT);
		setInputVerifier(new Verifier());
		addPropertyChangeListener("labeledBy", this);
		addKeyListener(this);
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
		setValue(v);
	}
	
	protected void updateModelValue()
	{
		try 
		{
			commitEdit();
			Object o = getValue();
			model.setValue(o);
			
		} 
		catch (ParseException e1) 
		{
			model.setValue(null);
		}
	}
	
	
	public void keyPressed(KeyEvent e) {}

	public void keyReleased(KeyEvent e) 
	{
		updateModelValue();
		updateLabel(); 
	}

	public void keyTyped(KeyEvent e) {}	
	
	class Verifier extends InputVerifier
	{
		@Override
		public boolean verify(JComponent input) 
		{
			JFormattedTextField ftf = (JFormattedTextField) input;
			JFormattedTextField.AbstractFormatter fter = ftf.getFormatter();
			if(fter == null)
				return true;
		
			try 
			{
				fter.stringToValue(ftf.getText());
				return true;
			} 
			catch (ParseException e) 
			{
				return false;
			}
		}
	}	
	
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		JFrame f = new JFrame("Small test for component");
		f.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		GridLayout gl = new GridLayout(5,2);
		f.getContentPane().setLayout(gl);
	
		// P1
		PropertyInfo prop = new PropertyInfo("Port");
		prop.setDescription("The port number of the Icepap controller");
		prop.setType(PropertyType.DevLong);
		prop.setDefaultValue(10000);
		final PropertyInstance p1 = new PropertyInstance(prop);
		SinglePropertyValueComponent c = null;
		try { c = new SinglePropertyValueComponent(p1); } catch (Exception e1) {}
		JLabel l = new JLabel(p1.getName());
		l.setLabelFor(c);
		f.getContentPane().add(l);
		f.getContentPane().add(c);

		// P2
		prop = new PropertyInfo("Port2");
		prop.setDescription("The port number of the Icepap controller");
		prop.setType(PropertyType.DevLong);
		final PropertyInstance p2 = new PropertyInstance(prop);
		try { c = new SinglePropertyValueComponent(p2); } catch (Exception e1) {}
		l = new JLabel(p2.getName());
		l.setLabelFor(c);
		f.getContentPane().add(l);
		f.getContentPane().add(c);
		
		// P3
		prop = new PropertyInfo("PI");
		prop.setDescription("The math constant PI");
		prop.setType(PropertyType.DevDouble);
		prop.setDefaultValue(3.1415926);
		final PropertyInstance p3 = new PropertyInstance(prop);
		try { c = new SinglePropertyValueComponent(p3); } catch (Exception e1) {}
		l = new JLabel(p3.getName());
		l.setLabelFor(c);
		f.getContentPane().add(l);
		f.getContentPane().add(c);

		// P4
		prop = new PropertyInfo("PI2");
		prop.setDescription("The double PI2");
		prop.setType(PropertyType.DevDouble);
		final PropertyInstance p4 = new PropertyInstance(prop);
		try { c = new SinglePropertyValueComponent(p4); } catch (Exception e1) {}
		l = new JLabel(p4.getName());
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
				System.out.println(p3.getValue());
				System.out.println(p4.getValue());
			}
		});
		f.add(b);
		
		f.pack();
		f.setVisible(true);
	}
	
}
