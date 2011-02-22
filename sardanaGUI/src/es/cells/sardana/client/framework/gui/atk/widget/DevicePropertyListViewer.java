package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.border.TitledBorder;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.gui.swing.SwingResource;
import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.tangoatk.core.DeviceProperty;

public class DevicePropertyListViewer extends JPanel {

	DeviceProperty                     model;
	JList		                       listValue;
	JScrollPane                        scrollPane;
	IStringSplitter                    splitter = null;

	JButton                            upButton;
	JButton                            downButton;
	JButton							   editButton;
	JButton                            addButton;
	JButton                            removeButton;
	JButton                            applyButton;
	JButton                            refreshButton;
    
	PropChangeListener changeListener = new PropChangeListener();
	
	boolean propertyChanged = false;
	boolean propertyItemRemoved = false;
	
	public DevicePropertyListViewer()
	{
		super();
	}
	
	public DevicePropertyListViewer(IStringSplitter splitter) 
	{
		super();
		this.splitter = splitter;
		initComponents();
	}
	
	private void initComponents() 
	{
		setLayout(new BorderLayout());
		
		setBorder(BorderFactory.createTitledBorder("Property name"));
		
		listValue = createListElement();
		
		add(listValue, BorderLayout.CENTER);
		
		JPanel buttonsPanel = new JPanel();
		
		buttonsPanel.setLayout(new BoxLayout(buttonsPanel,BoxLayout.Y_AXIS));
		
		addButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_ADD));
		removeButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_REMOVE));
		applyButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
		upButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_UP));
		downButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_DOWN));
		editButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_EDIT));
		refreshButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_REFRESH));

		addButton.setToolTipText("Add a new directory");
		removeButton.setToolTipText("Remove selected directory(ies)");
		applyButton.setToolTipText("Apply changes");
		refreshButton.setToolTipText("Refresh property contents");
		upButton.setToolTipText("Move directory up (increase priority)");
		editButton.setToolTipText("Edit current selection");
		downButton.setToolTipText("Move directory down (decrease priority)");
		
		addButton.setMargin(new Insets(1,1,1,1));
		removeButton.setMargin(new Insets(1,1,1,1));
		applyButton.setMargin(new Insets(1,1,1,1));
		refreshButton.setMargin(new Insets(1,1,1,1));
		upButton.setMargin(new Insets(1,1,1,1));
		editButton.setMargin(new Insets(1,1,1,1));
		downButton.setMargin(new Insets(1,1,1,1));
		
		applyButton.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{

			}
		});

		refreshButton.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				refresh();
			}
		});
		
		addButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				String elem = (String)JOptionPane.showInputDialog(
						addButton,
						"Type directory to be added",
						"Input",
						JOptionPane.INFORMATION_MESSAGE,
						SwingResource.bigIconMap.get(IImageResource.IMG_ADD),
						null, null);
				if(elem != null && elem.length() > 0)
				{
					if(!elem.startsWith("/"))
					{
						JOptionPane.showMessageDialog(addButton, "Path must be absolute (has to start with '/')");
						return;
					}
					
					((DefaultListModel)listValue.getModel()).addElement(elem);
					propertyChanged = true;
				}
			}
		});
		
		editButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				int idx = listValue.getSelectedIndex();
				if(idx < 0) return;
				
				Object selection = listValue.getModel().getElementAt(idx);
				if(selection == null) return;
				
				String elem = (String)JOptionPane.showInputDialog(
						null,
						"Type directory to be added",
						"Input",
						JOptionPane.INFORMATION_MESSAGE,
						SwingResource.bigIconMap.get(IImageResource.IMG_EDIT),
						null, selection);
				if(elem != null && elem.length() > 0)
				{
					if(!elem.startsWith("/"))
					{
						JOptionPane.showMessageDialog(null, "Path must be absolute (has to start with '/')");
						return;
					}
					
					((DefaultListModel)listValue.getModel()).set(idx, elem);
					propertyChanged = true;
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
					propertyChanged = true;
					propertyItemRemoved = true;
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
				}
			}
		});	
		
		buttonsPanel.add(editButton);
		buttonsPanel.add(addButton);
		buttonsPanel.add(removeButton);
		buttonsPanel.add(upButton);
		buttonsPanel.add(downButton);
		buttonsPanel.add(refreshButton);
		buttonsPanel.add(applyButton);
		add(buttonsPanel, BorderLayout.EAST);
	}
	
	public void refresh()
	{
		if(model != null)
			model.refresh();
		propertyChanged = false;
		propertyItemRemoved = false;		
	}
	
	public IStringSplitter getSplitter() 
	{
		return splitter;
	}

	public void setSplitter(IStringSplitter splitter) 
	{
		this.splitter = splitter;
	}

	protected JList createListElement()
	{
		JList ret = new JList(new DefaultListModel());
		ret.setVisibleRowCount(10);
		ret.setPreferredSize(new Dimension(200,100));
		return ret;
	}
	
	public DeviceProperty getModel() 
	{
		return model;
	}

	public void setModel(DeviceProperty model) 
	{
		if(this.model != null)
		{
			this.model.removePresentationListener(changeListener);
		}
		
		this.model = model;
		
		if(this.model != null)
		{
			this.model.addPresentationListener(changeListener);
			this.model.refresh();
			((TitledBorder)getBorder()).setTitle(model.getName());
		}
		else
		{
			((TitledBorder)getBorder()).setTitle("No property associated");
		}
	}
	
	public void setModelName(String name)
	{
		((TitledBorder)getBorder()).setTitle(name);
	}

	class PropChangeListener implements PropertyChangeListener
	{
		public void propertyChange(PropertyChangeEvent evt) 
		{
			DefaultListModel model = (DefaultListModel)listValue.getModel();
			model.removeAllElements();
			
			Object val = evt.getNewValue();
			
			String elems[] = val == null ? new String[0] : (String[])evt.getNewValue();
			
			for(String elem : elems)
				model.addElement(elem);
		}
	}
	
	public void addApplyListener(ActionListener listener)
	{
		applyButton.addActionListener(listener);
	}
	
	public void removeApplyListener(ActionListener listener)
	{
		applyButton.removeActionListener(listener);
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
	
	public boolean hasChanged()
	{
		return propertyChanged;
	}
	
	public boolean haveItemsBeenRemoved()
	{
		return propertyItemRemoved;
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

	public JButton getApplyButton() {
		return applyButton;
	}

	public JButton getRefreshButton() {
		return refreshButton;
	}

	public PropChangeListener getChangeListener() {
		return changeListener;
	}
	
	
}
