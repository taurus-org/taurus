package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.HeadlessException;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.dialog.MacroServerDetailsDialog;
import es.cells.sardana.client.framework.macroserver.MacroServer;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;

public class MacroServerViewer extends JPanel
{
		MacroServer macroServer;
		StateListener stateListener = new StateListener();
		
		JLabel aliasLabel = new JLabel("-");
		JLabel deviceNameLabel = new JLabel("-");
		JLabel iconLabel = new JLabel(SwingResource.bigIconMap.get(IImageResource.IMG_MACROSERVER_UNKNOWN));
		
		JButton details = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_PREFERENCES));
		JButton initButton = new JButton(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
		JButton why = new JButton("Why is the MacroServer in FAULT?", SwingResource.smallIconMap.get(IImageResource.IMG_MACROSERVER_UNKNOWN));
		
		public MacroServerViewer() 
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
			
			details.setToolTipText("Macro server details");
			initButton.setToolTipText("Perform an init on the macroserver");
			rightPanel.add(details);
			rightPanel.add(initButton);
			
			details.addActionListener(new ActionListener()
			{
				public void actionPerformed(ActionEvent e) 
				{
					MacroServerDetailsDialog dialog = new MacroServerDetailsDialog(macroServer);
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
							JOptionPane.showMessageDialog(null, 
									"This feature has not been implemented yet", 
									"Init pool",  
									JOptionPane.PLAIN_MESSAGE, 
									SwingResource.bigIconMap.get(IImageResource.IMG_REFRESH));
							//macroServer.Init();
					}
				}
			});
		}
		
		protected void whyPressed() 
		{
			if(macroServer == null)
			{
				JOptionPane.showMessageDialog(this, 
						"No macro server atached to the current view",
						"Unknown error",
						JOptionPane.ERROR_MESSAGE);
			}
			else
			{
				String state = macroServer.getState();
				if(state.equalsIgnoreCase("UNKNOWN"))
				{
					if(macroServer.isAvailable())
					//if(pool.getDevice().isAlive())
					{
						String status = macroServer.getDevice().getStatus();
						JOptionPane.showMessageDialog(this, 
								status,
								"Macro server is in UNKNOWN state",
								JOptionPane.ERROR_MESSAGE);
					}
					else 
					{
						StringBuffer msg = new StringBuffer();
						msg.append("<html>Unable to communicate with the macro server.<br>");
						msg.append("<ul><li>Check that the macro server device server is running</li>");
						msg.append("<li>Check that the notifd is running on the same machine as the macro server device server</li>");
						msg.append("<li>Check that the database device server is running</li>");
						msg.append("<li>Check that all cables are properly connected</li>");
						msg.append("<li>Check that the file /etc/hosts on the machine were the device server is running doesn't have the 127.0.0.2 <machine> line</li></ul>");
						
						JOptionPane.showMessageDialog(this, 
								msg.toString(),
								"Macro server is in UNKNOWN state",
								JOptionPane.ERROR_MESSAGE);
					}
				}
				else
				{
					String status = macroServer.getDevice().getStatus();
					JOptionPane.showMessageDialog(this, 
							status,
							"Macro server is in " + state + " state",
							JOptionPane.ERROR_MESSAGE);
					
				}
			}
		}

		public void setModel(MacroServer macroServer)
		{
			if(this.macroServer != null)
			{
				this.macroServer.removeDevStateScalarListener(stateListener);
			}
			
			this.macroServer = macroServer;
			
			if(macroServer != null)
			{
				iconLabel.setIcon(SwingResource.bigIconMap.get(IImageResource.IMG_MACROSERVER));
				
				if(macroServer.getName().equalsIgnoreCase(macroServer.getDeviceName()))
				{
					aliasLabel.setText(" ");
					deviceNameLabel.setText(macroServer.getDeviceName());
				}
				else
				{
					aliasLabel.setText(macroServer.getName());
					deviceNameLabel.setText(macroServer.getDeviceName());
				}
				this.macroServer.addDevStateScalarListener(stateListener);
				update(macroServer.getState());
			}
			else
			{
				iconLabel.setIcon(SwingResource.bigIconMap.get(IImageResource.IMG_MACROSERVER_UNKNOWN));
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
				why.setText("Why is the macro server in " + state + " state?");
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

