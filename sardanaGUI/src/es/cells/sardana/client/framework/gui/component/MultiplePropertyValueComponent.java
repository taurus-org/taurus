/**
 * 
 */
package es.cells.sardana.client.framework.gui.component;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Vector;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.border.TitledBorder;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.gui.swing.SwingResource;

public class MultiplePropertyValueComponent extends JPanel 
{
	PropertyInstance	propInstance;
	JList				listValue;
	JScrollPane			scrollPane;

	JButton				upButton;
	JButton				downButton;
	JButton				addButton;
	JButton				removeButton;
	JButton				refreshButton;


	public MultiplePropertyValueComponent(PropertyInstance propInstance) 
	{
		super();
		this.propInstance = propInstance;
		initComponents();
		setModel(propInstance);
	}

	protected void updateLabel()
	{
		TitledBorder border = ((TitledBorder)getBorder());
		if(((DefaultListModel)listValue.getModel()).isEmpty())
		{
			border.setTitleColor(Color.red);
		}
		else
		{
			border.setTitleColor(Color.black);
		}
		repaint();
	}

	protected void updateModelValue()
	{
		DefaultListModel listModel = (DefaultListModel)listValue.getModel();

		if(listModel.isEmpty())
		{
			propInstance.setValue((Object)null);
			return;
		}

		StringBuffer b = new StringBuffer();
		for(int i = 0 ; i < listModel.size() ; i++)
		{
			b.append(listModel.elementAt(i));
			if(i < listModel.size() -1)
				b.append("\n");
		}
		propInstance.setValue(b.toString());
	}

	private void initComponents() 
	{
		setLayout(new BorderLayout());
		String title = this.propInstance != null ? this.propInstance.getName() : "No prop";
		this.setBorder(BorderFactory.createTitledBorder(title));

		if(this.propInstance != null)
			setModelName(this.propInstance.getName());

		listValue = createListElement();

		JPanel buttonsPanel = new JPanel();

		buttonsPanel.setLayout(new BoxLayout(buttonsPanel,BoxLayout.Y_AXIS));

		addButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_ADD));
		removeButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_REMOVE));
		upButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_UP));
		downButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_DOWN));
		refreshButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_REFRESH));

		addButton.setMargin(new Insets(1,1,1,1));
		removeButton.setMargin(new Insets(1,1,1,1));
		upButton.setMargin(new Insets(1,1,1,1));
		downButton.setMargin(new Insets(1,1,1,1));
		refreshButton.setMargin(new Insets(1,1,1,1));

		addButton.setToolTipText("Add a new item");
		removeButton.setToolTipText("Remove selected item(s)");

		refreshButton.setToolTipText("Refresh property contents");
		upButton.setToolTipText("Move item up");
		downButton.setToolTipText("Move item down");

		refreshButton.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) {}
		});

		addButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				Object elem = PropertyComponentFactory.getInstance().getDialogValueForProperty(propInstance);
				if(elem != null)
				{
					((DefaultListModel)listValue.getModel()).addElement(elem);
					updateModelValue();
					updateLabel();
				}

			}
		});

		removeButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				Object elems[] = listValue.getSelectedValues();

				for(Object elem : elems)
				{
					((DefaultListModel)listValue.getModel()).removeElement(elem);
					updateModelValue();
					updateLabel();
				}
			}
		});

		upButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(listValue.getSelectedIndices().length != 1)
					return;

				int idx = listValue.getSelectedIndex();

				if(idx >= 1)
				{
					DefaultListModel model = (DefaultListModel)listValue.getModel();
					Object previous = model.getElementAt(idx-1);
					model.set(idx-1, listValue.getSelectedValue());
					model.set(idx, previous);
					listValue.setSelectedIndex(idx-1);
					updateModelValue();
				}
			}
		});

		downButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(listValue.getSelectedIndices().length != 1)
					return;

				int idx = listValue.getSelectedIndex();

				DefaultListModel model = (DefaultListModel)listValue.getModel();

				if(idx < model.getSize()-1)
				{
					Object previous = model.getElementAt(idx+1);
					model.set(idx+1, listValue.getSelectedValue());
					model.set(idx, previous);
					listValue.setSelectedIndex(idx+1);
					updateModelValue();
				}
			}
		});	

		buttonsPanel.add(addButton);
		buttonsPanel.add(removeButton);
		buttonsPanel.add(upButton);
		buttonsPanel.add(downButton);
		buttonsPanel.add(refreshButton);

		JScrollPane pane = new JScrollPane(listValue);

		add(pane, BorderLayout.CENTER);
		add(buttonsPanel, BorderLayout.EAST);
	}

	protected JList createListElement()
	{
		JList ret = new JList(new DefaultListModel());
		return ret;
	}

	public PropertyInstance getModel() 
	{
		return propInstance;
	}

	public void setModel(PropertyInstance propInstance) 
	{
		((DefaultListModel)listValue.getModel()).removeAllElements();

		this.propInstance = propInstance;
		if(propInstance != null)
		{
			Object v = propInstance.getValue();
			if(v != null)
			{
				Vector<?> elems = (Vector<?>)v;
				for(Object e : elems)
				{
					((DefaultListModel)listValue.getModel()).addElement(e);
				}
			}
		}
		updateLabel();
	}

	public void setModelName(String name)
	{
		((TitledBorder)this.getBorder()).setTitle(name);
	}

	public void addRefreshListener(ActionListener listener)
	{
		refreshButton.addActionListener(listener);
	}

	public void removeRefreshListener(ActionListener listener)
	{
		refreshButton.removeActionListener(listener);
	}

	public Object[] getElements()
	{
		DefaultListModel model = (DefaultListModel)listValue.getModel();
		Object elems[] = new Object[model.getSize()];
		model.copyInto(elems);
		return elems;
	}

	public JButton getUpButton() {
		return upButton;
	}

	public JButton getDownButton() {
		return downButton;
	}

	public JButton getAddButton() {
		return addButton;
	}

	public JButton getRemoveButton() {
		return removeButton;
	}

	public JButton getRefreshButton() {
		return refreshButton;
	}
}