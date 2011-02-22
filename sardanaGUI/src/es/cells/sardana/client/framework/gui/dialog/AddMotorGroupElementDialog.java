package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.ArrayList;
import java.util.List;

import javax.swing.DefaultListCellRenderer;
import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class AddMotorGroupElementDialog extends JDialog implements IStringSpectrumListener
{
	DevicePool devicePool;
	MotorGroup motorGroup;
	
	private JButton addButton;
	private JButton exitButton;
	
	private JList availableElements;
	
	public AddMotorGroupElementDialog(DevicePool devicePool, MotorGroup motorGroup)
	{
		super();
		
		this.devicePool = devicePool;
		this.motorGroup = motorGroup;
		
		setTitle("Add element to " + motorGroup.getName());
		
		initComponents();
	}

	private void initComponents() 
	{
		setResizable(false);
		setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});
		
		JPanel mainPanel = new JPanel(new BorderLayout());
		getContentPane().setLayout( new BorderLayout() );
		getContentPane().add(mainPanel, BorderLayout.CENTER);

		availableElements = new JList( new DefaultListModel() );
		availableElements.setCellRenderer(new MotorGroupElementListCellRenderer());
		availableElements.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
		JScrollPane availableScroll = new JScrollPane(availableElements);
		
		mainPanel.add(availableScroll, BorderLayout.CENTER);
		
		addButton = new JButton("Add");
		exitButton = new JButton("Close");
		
		addButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				addPressed();
			}
		});
		
		exitButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				closeAndExit();
			}
		});
		
		ButtonsPanel buttonsPanel = new ButtonsPanel();
		
		buttonsPanel.addRight(addButton);
		buttonsPanel.addRight(exitButton);
		
		getContentPane().add(buttonsPanel, BorderLayout.SOUTH);
		
		updateElements();
		
		devicePool.addMotorListListener(this);
		devicePool.addPseudoMotorListListener(this);
		devicePool.addMotorGroupListListener(this);
		motorGroup.addElementsListener(this);
		
		pack();
	}
	
	protected void addPressed()
	{
		if(availableElements.getSelectedIndex() == -1)
			return;
		
		ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
		
		for(Object item : availableElements.getSelectedValues())
		{
			try 
			{
				motorGroup.addNewElement((SardanaDevice) item);
			} 
			catch (DevFailed devFailed) 
			{
				failed.add(devFailed);
			}
		}
		
		if(failed.size() > 0)
		{
			StringBuffer buff = new StringBuffer("Reason(s):\n");
			
			for(DevFailed devFailed : failed)
			{
				for(DevError elem : devFailed.errors)
				{
					buff.append( elem.desc + "\n");
				}
				buff.append("---------------------");
			}
			
			JOptionPane.showMessageDialog(this, 
					buff.toString(),
					"Error trying to add element(s) to a motor group", 
					JOptionPane.ERROR_MESSAGE);
		}
	}

	protected void updateElements()
	{
		availableElements.setSelectedIndex(-1);
		
		List<SardanaDevice> availableElementList = 
			new ArrayList<SardanaDevice>(devicePool.getMotors());
		
		availableElementList.addAll(devicePool.getPseudoMotors());
		availableElementList.addAll(devicePool.getMotorGroups());
		
		List<SardanaDevice> reservedElementList = motorGroup.getElements();
		
		availableElementList.removeAll(reservedElementList);
		availableElementList.remove(motorGroup);
		
		((DefaultListModel)availableElements.getModel()).removeAllElements();
		
		for(SardanaDevice dev : availableElementList)
			((DefaultListModel)availableElements.getModel()).addElement(dev);
	}
	
	protected void closeAndExit()
	{
		devicePool.removeMotorListListener(this);
		devicePool.removePseudoMotorListListener(this);
		devicePool.removeMotorGroupListListener(this);
		motorGroup.removeElementsListener(this);
		
		dispose();
	}
	
	protected class MotorGroupElementListCellRenderer extends DefaultListCellRenderer
	{
		@Override
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) 
		{
			Component c = super.getListCellRendererComponent(list, value, index, isSelected,
					cellHasFocus);
			
			SardanaDevice dev = (SardanaDevice) value;
			
			if(c instanceof JLabel)
			{
				JLabel l = (JLabel) c;
				l.setIcon(SwingResource.smallIconMap.get(IImageResource.getDeviceElementIcon(dev)));
			}
			
			return c;
		}
		
	}

	public void stringSpectrumChange(StringSpectrumEvent e) 
	{
		updateElements();
	}

	public void stateChange(AttributeStateEvent e) {}
	public void errorChange(ErrorEvent e) {}
}
