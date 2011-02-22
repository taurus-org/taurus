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
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class RemoveMeasurementGroupChannelDialog extends JDialog implements IStringSpectrumListener
{
	DevicePool devicePool;
	MeasurementGroup measurementGroup;
	
	private JButton removeButton;
	private JButton exitButton;
	
	private JList availableChannels;
	
	public RemoveMeasurementGroupChannelDialog(DevicePool devicePool, MeasurementGroup measurementGroup)
	{
		super();
		
		this.devicePool = devicePool;
		this.measurementGroup = measurementGroup;
		
		setTitle("Remove channel from " + measurementGroup.getName());
		
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

		availableChannels = new JList( new DefaultListModel() );
		availableChannels.setCellRenderer(new ExpChannelListCellRenderer());
		availableChannels.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
		JScrollPane availableScroll = new JScrollPane(availableChannels);
		
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
		
		devicePool.addExperimentChannelListListener(this);
		measurementGroup.addChannelsListener(this);
		
		pack();
	}
	
	protected void removePressed()
	{
		if(availableChannels.getSelectedIndex() == -1)
			return;
		
		ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
		
		for(Object item : availableChannels.getSelectedValues())
		{
			try 
			{
				measurementGroup.removeExpChannel((ExperimentChannel) item);
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
					"Error trying to remove channel(s) from a measurement group", 
					JOptionPane.ERROR_MESSAGE);
		}
	}

	protected void updateChannels()
	{
		availableChannels.setSelectedIndex(-1);
		
		List<ExperimentChannel> availableChannelList = measurementGroup.getChannels();
		
		((DefaultListModel)availableChannels.getModel()).removeAllElements();
		
		for(ExperimentChannel channel : availableChannelList)
			((DefaultListModel)availableChannels.getModel()).addElement(channel);
	}
	
	protected void closeAndExit()
	{
		devicePool.removeExperimentChannelListListener(this);
		measurementGroup.removeChannelsListener(this);
		
		dispose();
	}
	
	protected class ExpChannelListCellRenderer extends DefaultListCellRenderer
	{
		@Override
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) 
		{
			Component c = super.getListCellRendererComponent(list, value, index, isSelected,
					cellHasFocus);
			
			ExperimentChannel channel = (ExperimentChannel) value;
			
			if(c instanceof JLabel)
			{
				JLabel l = (JLabel) c;
				l.setIcon(SwingResource.smallIconMap.get(IImageResource.getDeviceElementIcon(channel)));
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
