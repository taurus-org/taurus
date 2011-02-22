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


public class SimuDevicesListViewer extends JPanel {

	JList                              listValue;
	JScrollPane                        scrollPane;

	JButton							   editButton;
	JButton                            addButton;
	JButton                            removeButton;
	
	boolean propertyItemRemoved = false;
	
	public SimuDevicesListViewer() 
	{
		super();
		initComponents();
	}
	
	private void initComponents() 
	{
		setLayout(new BorderLayout());
		
		setBorder(BorderFactory.createTitledBorder("Devices:"));
		
		listValue = createListElement();
		
		add(listValue, BorderLayout.CENTER);
		
		JPanel buttonsPanel = new JPanel();
		
		buttonsPanel.setLayout(new BoxLayout(buttonsPanel,BoxLayout.Y_AXIS));
		
		addButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_ADD));
		removeButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_REMOVE));
		editButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_EDIT));

		addButton.setToolTipText("Add a new device");
		removeButton.setToolTipText("Remove selected device(s)");
		editButton.setToolTipText("Edit current selection");
		
		addButton.setMargin(new Insets(1,1,1,1));
		removeButton.setMargin(new Insets(1,1,1,1));
		editButton.setMargin(new Insets(1,1,1,1));
		
		addButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				String elem = (String)JOptionPane.showInputDialog(
						addButton,
						"Type device name to be added",
						"Input",
						JOptionPane.INFORMATION_MESSAGE,
						SwingResource.bigIconMap.get(IImageResource.IMG_ADD),
						null, null);
				if(elem != null && elem.length() > 0)
				{
					String[] parts = elem.split("/");
					if(parts.length!=3)
					{
						JOptionPane.showMessageDialog
								(addButton, "Device name has to fulfil the pattern x...x/x...x/x...x ");
						return;
					}
					
					((DefaultListModel)listValue.getModel()).addElement(elem);
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
						"Type device name to be added",
						"Input",
						JOptionPane.INFORMATION_MESSAGE,
						SwingResource.bigIconMap.get(IImageResource.IMG_EDIT),
						null, selection);
				if(elem != null && elem.length() > 0)
				{
					String[] parts = elem.split("/");
					if(parts.length!=3)
					{
						JOptionPane.showMessageDialog
								(addButton, "Device name has to fulfil the pattern x...x/x...x/x...x ");
						return;
					}
					((DefaultListModel)listValue.getModel()).set(idx, elem);
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
				}
			}
		});
			
		buttonsPanel.add(editButton);
		buttonsPanel.add(addButton);
		buttonsPanel.add(removeButton);
		add(buttonsPanel, BorderLayout.EAST);
	}
	
	protected JList createListElement()
	{
		JList ret = new JList(new DefaultListModel());
		ret.setVisibleRowCount(8);
		ret.setPreferredSize(new Dimension(200,100));
		return ret;
	}
	
	public void setModelName(String name)
	{
		((TitledBorder)getBorder()).setTitle(name);
	}
	
	public Object[] getElements()
	{
		DefaultListModel model = (DefaultListModel)listValue.getModel();
		Object elems[] = new Object[model.getSize()];
		model.copyInto(elems);
		return elems;
	}
	
	public JButton getAddButton() {
		return addButton;
	}

	public JButton getRemoveButton() {
		return removeButton;
	}
		
}
