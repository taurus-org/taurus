package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.DefaultListModel;
import javax.swing.Icon;
import javax.swing.JButton;
import javax.swing.JOptionPane;
import javax.swing.JPanel;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.gui.swing.SwingResource;
import es.cells.tangoatk.utils.IStringSplitter;

public class PoolNamesListViewer extends DevicePropertyListViewer implements ActionListener{
	
	Machine machine;
	
	public PoolNamesListViewer(IStringSplitter splitter, Machine machine){
		super();
		this.splitter = splitter;
		this.machine = machine;
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
		refreshButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_REFRESH));

		addButton.setToolTipText("Add a new directory");
		removeButton.setToolTipText("Remove selected directory(ies)");
		applyButton.setToolTipText("Apply changes");
		refreshButton.setToolTipText("Refresh property contents");
		
		addButton.setMargin(new Insets(1,1,1,1));
		removeButton.setMargin(new Insets(1,1,1,1));
		applyButton.setMargin(new Insets(1,1,1,1));
		refreshButton.setMargin(new Insets(1,1,1,1));
		
		addButton.addActionListener(this);
		removeButton.addActionListener(this);
		refreshButton.addActionListener(this);
		applyButton.addActionListener(this);
		
		buttonsPanel.add(addButton);
		buttonsPanel.add(removeButton);
		buttonsPanel.add(refreshButton);
		buttonsPanel.add(applyButton);
		add(buttonsPanel, BorderLayout.EAST);
	}

	public void actionPerformed(ActionEvent e) {
		if(e.getSource() == applyButton)
		{
			int k=1;
		}
		if(e.getSource() == addButton)
		{
			Object[] model = ((DefaultListModel)listValue.getModel()).toArray();
			ArrayList<String> properties = new ArrayList<String>();
	
			for (Object pool : model) {
				if (pool != null) properties.add((String)pool);
			}
			HashMap<String, String> pools = DevicePoolUtils.getInstance().getPoolDevices(machine);
			
			ArrayList<String> poolDeviceNames = new ArrayList<String>();
		
			for (String pool : pools.values())
			{
				boolean add = true;
				for (String macroServerPool : properties)
					if (pool.toLowerCase().equals(macroServerPool.toLowerCase()))
						add = false;
				if(add)
					poolDeviceNames.add(pool);
			}
		
			String pool = (String)JOptionPane.showInputDialog(
                    this,
                    "Please choose the device pool:\n",
                    "Adding a device pool",
                    JOptionPane.PLAIN_MESSAGE,
                    SwingResource.smallIconMap.get(IImageResource.IMG_POOL),
                    poolDeviceNames.toArray(),
                    null);
			
			((DefaultListModel)listValue.getModel()).addElement(pool);
			propertyChanged = true;
	
		}
		if(e.getSource() == removeButton)
		{
			Object elems[] = listValue.getSelectedValues();
			
			for(Object elem : elems)
			{
				((DefaultListModel)listValue.getModel()).removeElement(elem);
				propertyChanged = true;
				propertyItemRemoved = true;
			}
		}
		if(e.getSource() == refreshButton)
		{
			refresh();
		}
		
	}
	
}
