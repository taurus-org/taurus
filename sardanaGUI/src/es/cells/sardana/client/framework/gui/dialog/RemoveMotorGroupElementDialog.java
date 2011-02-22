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

public class RemoveMotorGroupElementDialog extends JDialog implements IStringSpectrumListener
{
	DevicePool devicePool;
	MotorGroup motorGroup;
	
	private JButton removeButton;
	private JButton exitButton;
	
	private JList availableElements;
	
	public RemoveMotorGroupElementDialog(DevicePool devicePool, MotorGroup motorGroup)
	{
		super();
		
		this.devicePool = devicePool;
		this.motorGroup = motorGroup;
		
		setTitle("Remove element from " + motorGroup.getName());
		
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
		
		removeButton = new JButton("Remove");
		exitButton = new JButton("Close");
		
		removeButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				removePressed();
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
		
		buttonsPanel.addRight(removeButton);
		buttonsPanel.addRight(exitButton);
		
		getContentPane().add(buttonsPanel, BorderLayout.SOUTH);
		
		updateChannels();
		
		devicePool.addMotorListListener(this);
		devicePool.addPseudoMotorListListener(this);
		devicePool.addMotorGroupListListener(this);
		motorGroup.addElementsListener(this);
		
		pack();
	}
	
	protected void removePressed()
	{
		if(availableElements.getSelectedIndex() == -1)
			return;
		
		ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
		
		for(Object item : availableElements.getSelectedValues())
		{
			try 
			{
				motorGroup.removeElement((SardanaDevice) item);
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
					"Error trying to remove element(s) from a motor group", 
					JOptionPane.ERROR_MESSAGE);
		}
	}

	protected void updateChannels()
	{
		availableElements.setSelectedIndex(-1);
		
		List<SardanaDevice> availableChannelList = motorGroup.getElements();
		
		((DefaultListModel)availableElements.getModel()).removeAllElements();
		
		for(SardanaDevice dev : availableChannelList)
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
				l.setForeground(SwingResource.getColorForElement(value));
			}
			
			return c;
		}
		
	}

	public void stringSpectrumChange(StringSpectrumEvent e) 
	{
		updateChannels();
	}

	public void stateChange(AttributeStateEvent e) {}
	public void errorChange(ErrorEvent e) {}
}
