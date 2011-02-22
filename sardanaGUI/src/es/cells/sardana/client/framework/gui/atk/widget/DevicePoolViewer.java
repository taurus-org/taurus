package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.dialog.DevicePoolDetailsDialog;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;

public class DevicePoolViewer extends JPanel 
{
	DevicePool pool;
	StateListener stateListener = new StateListener();
	
	JLabel aliasLabel = new JLabel("-");
	JLabel deviceNameLabel = new JLabel("-");
	JLabel iconLabel = new JLabel(SwingResource.bigIconMap.get(IImageResource.IMG_POOL_UNKNOWN));
	
	JButton details = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_PREFERENCES));
	JButton initButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
	JButton why = new JButton("Why is the Pool in FAULT?", SwingResource.smallIconMap.get(IImageResource.IMG_POOL_UNKNOWN));
	
	public DevicePoolViewer() 
	{
		super( new BorderLayout() );
		
		JPanel leftPanel = new JPanel( new FlowLayout(FlowLayout.LEFT) );
		JPanel rightPanel = new JPanel( new FlowLayout(FlowLayout.RIGHT) );
		
		add(leftPanel, BorderLayout.WEST);
		add(rightPanel, BorderLayout.EAST);
		
		leftPanel.add(iconLabel);
		
		aliasLabel.setFont(aliasLabel.getFont().deriveFont(Font.BOLD, 24.0f));
		deviceNameLabel.setFont(aliasLabel.getFont().deriveFont(Font.ITALIC, 14.0f));
		
		JPanel infoPanel = new JPanel();
		infoPanel.setLayout(new BoxLayout(infoPanel, BoxLayout.Y_AXIS));
		
		infoPanel.add(aliasLabel);
		infoPanel.add(deviceNameLabel);
		infoPanel.add(why);
		
		why.setVisible(false);
		
		why.addActionListener(new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				whyPressed();
			}
		});
		
		leftPanel.add(infoPanel);
		
		details.setToolTipText("Device pool details");
		initButton.setToolTipText("Perform an init on the device pool");
		rightPanel.add(details);
		rightPanel.add(initButton);
		
		details.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				DevicePoolDetailsDialog dialog = new DevicePoolDetailsDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		});
		
		initButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				int res = JOptionPane.showConfirmDialog(null, 
						"This will perform an Init on the pool.\nAre you sure?", 
						"Init pool", 
						JOptionPane.YES_NO_OPTION, 
						JOptionPane.QUESTION_MESSAGE, 
						SwingResource.bigIconMap.get(IImageResource.IMG_REFRESH));
				
				if(res == JOptionPane.YES_OPTION)
				{
					try 
					{
						pool.Init();
					} 
					catch (DevFailed e1) 
					{
						JOptionPane.showMessageDialog(null, 
								e1.getMessage(),
								"Failed to Init the pool", 
								JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		});
	}
	
	protected void whyPressed() 
	{
		if(pool == null)
		{
			JOptionPane.showMessageDialog(this, 
					"No pool atached to the current view",
					"Unknown error",
					JOptionPane.ERROR_MESSAGE);
		}
		else
		{
			String state = pool.getState();
			if(state.equalsIgnoreCase("UNKNOWN"))
			{
				if(pool.isAvailable())
				//if(pool.getDevice().isAlive())
				{
					String status = pool.getDevice().getStatus();
					JOptionPane.showMessageDialog(this, 
							status,
							"Pool is in UNKNOWN state",
							JOptionPane.ERROR_MESSAGE);
				}
				else 
				{
					StringBuffer msg = new StringBuffer();
					msg.append("<html>Unable to communicate with the Pool.<br>");
					msg.append("<ul><li>Check that the Pool device server is running</li>");
					msg.append("<li>Check that the notifd is running on the same machine as the Pool device server</li>");
					msg.append("<li>Check that the database device server is running</li>");
					msg.append("<li>Check that all cables are properly connected</li>");
					msg.append("<li>Check that the file /etc/hosts on the machine were the device server is running doesn't have the 127.0.0.2 <machine> line</li></ul>");
					
					JOptionPane.showMessageDialog(this, 
							msg.toString(),
							"Pool is in UNKNOWN state",
							JOptionPane.ERROR_MESSAGE);
				}
			}
			else
			{
				String status = pool.getDevice().getStatus();
				JOptionPane.showMessageDialog(this, 
						status,
						"Pool is in " + state + " state",
						JOptionPane.ERROR_MESSAGE);
				
			}
		}
	}

	public void setModel(DevicePool pool)
	{
		if(this.pool != null)
		{
			this.pool.removeDevStateScalarListener(stateListener);
		}
		
		this.pool = pool;
		
		if(pool != null)
		{
			iconLabel.setIcon(SwingResource.bigIconMap.get(IImageResource.IMG_POOL));
			
			if(pool.getName().equalsIgnoreCase(pool.getDeviceName()))
			{
				aliasLabel.setText(" ");
				deviceNameLabel.setText(pool.getDeviceName());
			}
			else
			{
				aliasLabel.setText(pool.getName());
				deviceNameLabel.setText(pool.getDeviceName());
			}
			this.pool.addDevStateScalarListener(stateListener);
			update(pool.getState());
		}
		else
		{
			iconLabel.setIcon(SwingResource.bigIconMap.get(IImageResource.IMG_POOL_UNKNOWN));
			aliasLabel.setText("-");
			deviceNameLabel.setText("-");
			update("UNKNOWN");
		}
	}

	protected void update(String state)
	{
		aliasLabel.setForeground(SwingResource.getColor4State(state));
		deviceNameLabel.setForeground(SwingResource.getColor4State(state));
		
		why.setVisible(!state.equalsIgnoreCase("ON"));
		
		if(!state.equalsIgnoreCase("ON"))
		{
			why.setText("Why is the pool in " + state + " state?");
		}
	}
	
	class StateListener implements IDevStateScalarListener
	{
		public void devStateScalarChange(DevStateScalarEvent e) 
		{
			update(e.getValue());
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
		
	}
}
