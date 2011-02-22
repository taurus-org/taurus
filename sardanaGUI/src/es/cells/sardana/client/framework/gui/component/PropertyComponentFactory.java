package es.cells.sardana.client.framework.gui.component;

import java.text.Format;
import java.text.NumberFormat;

import javax.swing.JComponent;
import javax.swing.JOptionPane;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.framework.pool.PropertyType;
import es.cells.sardana.client.gui.swing.SwingResource;

public class PropertyComponentFactory 
{
	protected static PropertyComponentFactory instance = null;
	
	protected PropertyComponentFactory()
	{
		
	}
	
	public static PropertyComponentFactory getInstance()
	{
		if(instance == null)
			instance = new PropertyComponentFactory();
		return instance;
	}
	
	public static Format getTextFormatForProperty(PropertyInstance model) throws Exception
	{
		PropertyType type = model.getType().toSimpleType();
		
		if(type == PropertyType.DevDouble)
			return NumberFormat.getNumberInstance();
		else if(type == PropertyType.DevLong)
			return NumberFormat.getIntegerInstance();
		
		throw new Exception("No valid text format for " + type.toString());
	}
	
	public JComponent getComponentForProperty(PropertyInstance model)
	{
		if(model == null)
			return null;
		
		PropertyType type = model.getType();
		if(type == PropertyType.DevBoolean)
			return new BooleanPropertyValueComponent(model);
		else if(type == PropertyType.DevDouble || type == PropertyType.DevLong)
		{
			try 
			{
				return new SinglePropertyValueComponent(model);
			} 
			catch (Exception e) 
			{
				return null;
			}
		}
		else if(type == PropertyType.DevString)
			return new StringPropertyValueComponent(model);
		else
			return new MultiplePropertyValueComponent(model);
	}
	
	public Object getDialogValueForProperty(PropertyInstance model)
	{
		Object[] possible_vals = null;
		Object dft_val = null;
		
		if(model == null)
			return null;
		
		PropertyType t = model.getType().toSimpleType(); 
		
		if(t == PropertyType.DevBoolean)
		{
			possible_vals = new Object[]{true,false};
			dft_val = true;
		}
			
		Object o = JOptionPane.showInputDialog(
				null,
				"Type in a valid " + t.toSimpleString() + " to be added",
				"Add new element",
				JOptionPane.INFORMATION_MESSAGE,
				SwingResource.bigIconMap.get(IImageResource.IMG_ADD),
				possible_vals, dft_val);

		if(o != null)
		{
			if(model.getType().toSimpleType() == PropertyType.DevLong)
			{
				try
				{
					o = Long.decode((String)o);
				}
				catch (NumberFormatException e) 
				{
					JOptionPane.showMessageDialog(null, "Invalid Long value");
					return null;
				}
			}
			else if(model.getType().toSimpleType() == PropertyType.DevDouble)
			{
				o = Double.valueOf((String)o);
			}
			else if(model.getType().toSimpleType() == PropertyType.DevString)
			{
				o = o.toString();
			}
		}
		return o;
	}
}
