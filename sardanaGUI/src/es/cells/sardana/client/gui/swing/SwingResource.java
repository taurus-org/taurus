package es.cells.sardana.client.gui.swing;

import java.awt.Color;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPopupMenu;
import javax.swing.JSeparator;
import javax.swing.filechooser.FileFilter;
import javax.swing.filechooser.FileView;

import es.cells.sardana.client.framework.SardanaConfigSaver;
import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.config.SardanaDocument;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.dialog.AddChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.AddComChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.AddControllerDialog;
import es.cells.sardana.client.framework.gui.dialog.AddIORegisterDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMeasurementGroupChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMeasurementGroupDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMotorDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMotorGroupDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMotorGroupElementDialog;
import es.cells.sardana.client.framework.gui.dialog.AddPoolDialog;
import es.cells.sardana.client.framework.gui.dialog.AddSimulatorDialog;
import es.cells.sardana.client.framework.gui.dialog.DevicePoolDetailsDialog;
import es.cells.sardana.client.framework.gui.dialog.RemoveMeasurementGroupChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.RemoveMotorGroupElementDialog;
import es.cells.sardana.client.framework.gui.dialog.SardanaConfigView;
import es.cells.sardana.client.framework.macroserver.MacroServer;
import es.cells.sardana.client.framework.pool.CommunicationChannel;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.ControllerClass;
import es.cells.sardana.client.framework.pool.CtrlState;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.IORegister;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.framework.pool.PseudoMotorClass;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.TangoDs.TangoConst;
import fr.esrf.tangoatk.core.AttributeSetException;
import fr.esrf.tangoatk.core.IBooleanScalar;
import fr.esrf.tangoatk.core.IBooleanSpectrum;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class SwingResource extends IImageResource 
{
	public static HashMap<String, ImageIcon> smallerIconMap = new HashMap<String, ImageIcon>(iconList.size());
	public static HashMap<String, ImageIcon> smallIconMap = new HashMap<String, ImageIcon>(iconList.size());
	public static HashMap<String, ImageIcon> normalIconMap = new HashMap<String, ImageIcon>(iconList.size());
	public static HashMap<String, ImageIcon> bigIconMap = new HashMap<String, ImageIcon>(iconList.size());
	
	static 
	{
		for(String iconName : iconList)
		{
			ImageIcon icon16 = new ImageIcon("res/16x16/"+iconName);
			ImageIcon icon24 = new ImageIcon("res/24x24/"+iconName);
			ImageIcon icon32 = new ImageIcon("res/32x32/"+iconName);
			ImageIcon icon64 = new ImageIcon("res/64x64/"+iconName);

			if(icon16 != null)
				smallerIconMap.put(iconName, icon16);
			if(icon24 != null)
				smallIconMap.put(iconName, icon24);
			if(icon32 != null)
				normalIconMap.put(iconName, icon32);
			if(icon64 != null)
				bigIconMap.put(iconName, icon64);
		}
	}
	
	public static void addResource(String name, ImageIcon obj)
	{
		ImageIcon smaller = new ImageIcon(obj.getImage().getScaledInstance(16, 16, Image.SCALE_SMOOTH));
		ImageIcon small = new ImageIcon(obj.getImage().getScaledInstance(24, 24, Image.SCALE_SMOOTH));
		ImageIcon normal = new ImageIcon(obj.getImage().getScaledInstance(32, 32, Image.SCALE_SMOOTH));
		ImageIcon big = new ImageIcon(obj.getImage().getScaledInstance(64, 64, Image.SCALE_SMOOTH));
		
		smallerIconMap.put(name, smaller);
		smallIconMap.put(name, small);
		normalIconMap.put(name, normal);
		bigIconMap.put(name, big);
	}
	
	public static FileView getPoolFileView()
	{
		return new PoolFileView();
	}
	
	public static Color getColorForElement(Object obj)
	{
		if(obj instanceof SardanaDevice)
		{
			return getColor4State(((SardanaDevice)obj).getState());
		}
		else if(obj instanceof Controller)
		{
			if(((Controller)obj).getState() == CtrlState.Ok)
				return getColor4State("ON");
			else
				return getColor4State("ALARM");
		}
		else
			return Color.black;
	}
	
	public static Color getColor4State(String state)
	{
		if(state.equalsIgnoreCase("ON"))
			return new Color(0,200,0);
		else
			return ATKConstant.getColor4State(state);
	}
	
	public static Object getEntityValue(IEntity entity, AttributeInfoEx info)
	{
		if(info == null || entity == null) 
		{
			return null;
		}
		else
		{
			if(entity instanceof INumberScalar)
				return ((INumberScalar)entity).getNumberScalarValue();
			else if(entity instanceof IStringScalar)
				return ((IStringScalar)entity).getStringValue();
			else if(entity instanceof IBooleanScalar)
				return ((IBooleanScalar)entity).getValue();
			else if(entity instanceof IBooleanSpectrum)
			{
				try 
				{
					return ((IBooleanSpectrum)entity).getValue();
				} 
				catch (DevFailed e) 
				{
					return null;
				}
			}
			else 
				return null;
		}
	}
	
	public static String setScalarEntityValue(IEntity entity, AttributeInfoEx info, String strValue)
	{
		if(info == null || entity == null || strValue == null) 
		{
			return "no information on this entity";
		}
		else
		{
			if(entity instanceof INumberScalar)
			{
				double d = Double.NaN;
				if(info.data_type == TangoConst.Tango_DEV_LONG)
				{
					try 
					{
						d = Integer.parseInt(strValue);
					} 
					catch (Exception e) 
					{
						return strValue + " is not a valid integer";
					}
				}
				else if(info.data_type == TangoConst.Tango_DEV_DOUBLE)
				{
					try 
					{
						d = Double.parseDouble(strValue);
					} 
					catch (Exception e) 
					{
						return strValue + " is not a valid number";
					}
				}
				((INumberScalar)entity).setValue(d);
				
			}
			else if(entity instanceof IStringScalar)
			{
				try 
				{
					((IStringScalar)entity).setValue(strValue);
				} 
				catch (AttributeSetException e) 
				{
					return e.getDescription();
				}
			}
			else if(entity instanceof IBooleanScalar)
			{
				boolean b;
				try 
				{
					b = Boolean.parseBoolean(strValue);
				} 
				catch (Exception e) 
				{
					return strValue + "is not a valid boolean";
				}
				((IBooleanScalar)entity).setValue(b);
			}
			else 
				return entity.getName() + "is not a scalar entity";
		}		
		return null;
	}
	
	public static String getToolTipForElement(Object o) 
	{
		if(o == null) 
			return "<html><i>no information available</i>";
		
		StringBuffer toolTipText = new StringBuffer();

		if(o instanceof CommunicationChannel)
		{
			CommunicationChannel dev = (CommunicationChannel) o;
			toolTipText.append("<html><b>Name:</b> " + dev.getName());
			toolTipText.append("<br><b>State:</b> " + dev.getState());
			if(dev.getController() != null)
				toolTipText.append("<br><b>Controller:</b> " + dev.getController());
			if(dev.getIdInController() != -1)
				toolTipText.append("<br><b>Index in controller:</b> " + dev.getIdInController());
			toolTipText.append("<br><b>Tango device name:</b> " + dev.getDeviceName());
		}
		else if(o instanceof IORegister)
		{
			IORegister dev = (IORegister) o;
			toolTipText.append("<html><b>Name:</b> " + dev.getName());
			toolTipText.append("<br><b>State:</b> " + dev.getState());
			if(dev.getController() != null)
				toolTipText.append("<br><b>Controller:</b> " + dev.getController());
			if(dev.getIdInController() != -1)
				toolTipText.append("<br><b>Index in controller:</b> " + dev.getIdInController());
			toolTipText.append("<br><b>Tango device name:</b> " + dev.getDeviceName());
		}
		else if(o instanceof Motor)
		{
			Motor dev = (Motor) o;
			
			toolTipText.append("<html><b>Name:</b> " + dev.getName());
			toolTipText.append("<br><b>State:</b> " + dev.getState());
			if(dev.getController() != null)
				toolTipText.append("<br><b>Controller:</b> " + dev.getController());
			if(dev.getIdInController() != -1)
				toolTipText.append("<br><b>Index in controller:</b> " + dev.getIdInController());
			toolTipText.append("<br><b>Tango device name:</b> " + dev.getDeviceName());
		}
		else if(o instanceof MotorGroup)
		{
			MotorGroup dev = (MotorGroup) o;
			toolTipText.append("<html><b>Name:</b> " + dev.getName());
			toolTipText.append("<br><b>State:</b> " + dev.getState());
			if(dev.getController() != null)
				toolTipText.append("<br><b>Controller:</b> " + dev.getController());
			if(dev.getIdInController() != -1)
				toolTipText.append("<br><b>Index in controller:</b> " + dev.getIdInController());
			toolTipText.append("<br><b>Tango device name:</b> " + dev.getDeviceName());
			return toolTipText.toString();	
		}
		else if(o instanceof ExperimentChannel)
		{
			ExperimentChannel dev = (ExperimentChannel) o;
			toolTipText.append("<html><b>Name:</b> " + dev.getName());
			toolTipText.append("<br><b>State:</b> " + dev.getState());
			if(dev.getController() != null)
				toolTipText.append("<br><b>Controller:</b> " + dev.getController());
			if(dev.getIdInController() != -1)
				toolTipText.append("<br><b>Index in controller:</b> " + dev.getIdInController());
			toolTipText.append("<br><b>Tango device name:</b> " + dev.getDeviceName());
		}
		else if(o instanceof MeasurementGroup)
		{
			MeasurementGroup dev = (MeasurementGroup) o;
			toolTipText.append("<html><b>Name:</b> " + dev.getName());
			toolTipText.append("<br><b>State:</b> " + dev.getState());
			if(dev.getController() != null)
				toolTipText.append("<br><b>Controller:</b> " + dev.getController());
			if(dev.getIdInController() != -1)
				toolTipText.append("<br><b>Index in controller:</b> " + dev.getIdInController());
			toolTipText.append("<br><b>Tango device name:</b> " + dev.getDeviceName());
			return toolTipText.toString();
		}
		else if(o instanceof Controller)
		{
			Controller ctrl = (Controller) o;
			toolTipText.append("<html><b>Name:</b> " + ctrl.getName());
			toolTipText.append("<br><b>Type:</b> " + ctrl.getType());
			toolTipText.append("<br><b>Name:</b> " + ctrl.getClassName());
			toolTipText.append("<br><b>Language:</b> " + ctrl.getLanguage());
			toolTipText.append("<br><b>File:</b> " + ctrl.getFileName());
		}
		else if(o instanceof PseudoMotorClass)
		{
			PseudoMotorClass ctrlClass = (PseudoMotorClass) o;
			toolTipText.append("<html><b>Name:</b> " + ctrlClass.getClassName());
			toolTipText.append("<br><b>File:</b> " + ctrlClass.getFileName());
			toolTipText.append("<br><b>Full path:</b> " + ctrlClass.getFullPathName());
			toolTipText.append("<br><b>Motor roles:</b> " + ctrlClass.getMotorRoles());
			toolTipText.append("<br><b>Pseudo motor roles:</b> " + ctrlClass.getPseudoMotorRoles());
			toolTipText.append("<br><b>Description:</b> " + ctrlClass.getDescription());
		}
		
		return toolTipText.toString();
	}
	
	public static JPopupMenu getPopupForElement(Object obj)
	{
		if(obj instanceof Machine)
			return getPopupMenuForMachine((Machine)obj);
		else if(obj instanceof DevicePool)
			return getPopupMenuForDevicePool((DevicePool)obj);
		else if(obj instanceof MacroServer)
			return getPopupMenuForMacroServer((MacroServer)obj);
		else if(obj instanceof ControllerClass)
			return getPopupMenuForControllerClass((ControllerClass)obj);
		else if(obj instanceof Controller)
			return getPopupMenuForController((Controller)obj);
		else if(obj instanceof CommunicationChannel)
			return getPopupMenuForCommunicationChannel((CommunicationChannel)obj);
		else if(obj instanceof IORegister)
			return getPopupMenuForIORegister((IORegister)obj);
		else if(obj instanceof Motor)
			return getPopupMenuForMotor((Motor)obj);
		else if(obj instanceof MotorGroup)
			return getPopupMenuForMotorGroup((MotorGroup)obj);
		else if(obj instanceof ExperimentChannel)
			return getPopupMenuForExpChannel((ExperimentChannel)obj);
		else if(obj instanceof MeasurementGroup)
			return getPopupMenuForMeasurementGroup((MeasurementGroup)obj);
		
		return null;
	}

	public static JPopupMenu getPopupMenuForMachine(Machine machine_obj) 
	{
		JPopupMenu menu = new JPopupMenu("Pool");
		final Machine machine = machine_obj;

		Action a = new AbstractAction(
				"Create pool",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddPoolDialog dialog = new AddPoolDialog(machine);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		return menu;
	}

	public static JPopupMenu getPopupMenuForDevicePool(DevicePool pool_obj)
	{
		JPopupMenu menu = new JPopupMenu("Pool");
		final DevicePool pool = pool_obj;
	
		Action a = new AbstractAction(
				"Save pool",
				SwingResource.smallerIconMap.get(IImageResource.IMG_FILE_SAVE_AS))
		{
			public void actionPerformed(ActionEvent e) 
			{
				JFileChooser fileChooser = new JFileChooser();
				
				FileFilter filter = new FileFilter() 
				{
					@Override
					public boolean accept(File f) 
					{
						if(f.isDirectory()) return true;
						return f.getName().endsWith(".xsr");
					}

					@Override
					public String getDescription() 
					{
						return "Sardana XML configuration file (*.xsr)";
					}
				};
				
				fileChooser.addChoosableFileFilter(filter);
				fileChooser.setFileSelectionMode(JFileChooser.FILES_ONLY);
				fileChooser.setFileView(SwingResource.getPoolFileView());
				int retval = fileChooser.showSaveDialog(null);
				
				if(retval == JFileChooser.APPROVE_OPTION)
				{
					File f = fileChooser.getSelectedFile();
					if( f != null )
					{
						List<DevicePool> pools = new ArrayList<DevicePool>();
						pools.add(pool);
						try 
						{
							SardanaConfigSaver saver = new SardanaConfigSaver(f,pools);
							SardanaDocument doc = saver.build(SardanaManager.getInstance().getLoadedPreferences());
							
							SardanaConfigView previewer = new SardanaConfigView(doc);
							previewer.setTitle("Preview");
							
							saver.save(doc);
							
							JOptionPane.showMessageDialog(null,	
									"Configuration saved to " + f.getName(), 
									"Success!", JOptionPane.INFORMATION_MESSAGE);
						} 
						catch (IOException e1) 
						{
							JOptionPane.showMessageDialog(null,	
									e1.getMessage(), 
									"Error trying to save configuration!", JOptionPane.ERROR_MESSAGE);
						}
					}
				}
			}
		};
		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		menu.addSeparator();
		
		a = new AbstractAction(
				"Clone pool",
				SwingResource.smallerIconMap.get(IImageResource.IMG_CLONE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				//TODO
			}
		};
		item = new JMenuItem(a);
		menu.add(item);
		
		menu.addSeparator();
		
		a = new AbstractAction(
				"Create simulator",
				SwingResource.smallerIconMap.get(IImageResource.IMG_SIMU))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddSimulatorDialog dialog = new AddSimulatorDialog(pool.getMachine(), pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);
		
		a = new AbstractAction(
				"Create controller",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_CTRL))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddControllerDialog dialog = new AddControllerDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Create motor",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_MOTOR))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddMotorDialog dialog = new AddMotorDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Create experiment channel",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_EXP_CHANNELS))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddChannelDialog dialog = new AddChannelDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Create motor group",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_MOTOR_GROUP))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddMotorGroupDialog dialog = new AddMotorGroupDialog(pool, null);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Create measurement group",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_MEASUREMENT_GROUP))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddMeasurementGroupDialog dialog = new AddMeasurementGroupDialog(pool, null);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Create communication channel",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_COM_CHANNELS))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddComChannelDialog dialog = new AddComChannelDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Create input/output register",
				SwingResource.smallerIconMap.get(IImageResource.IMG_POOL_IOREGISTERS))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddIORegisterDialog dialog = new AddIORegisterDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());

		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
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
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());

		a = new AbstractAction(
				"Preferences",
				SwingResource.smallerIconMap.get(IImageResource.IMG_PREFERENCES))
		{
			public void actionPerformed(ActionEvent e) 
			{
				DevicePoolDetailsDialog dialog = new DevicePoolDetailsDialog(pool);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);
		
		return menu;
	}
	
	public static JPopupMenu getPopupMenuForMacroServer(MacroServer ms_obj)
	{
		JPopupMenu menu = new JPopupMenu("Macro server");
		
		final MacroServer pool = ms_obj;
	
		Action a = new AbstractAction(
				"Create door",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DOOR))
		{
			public void actionPerformed(ActionEvent e)
			{
				JOptionPane.showMessageDialog(null, "sth to implement", "Add door", JOptionPane.PLAIN_MESSAGE);
			}
		};
		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		return menu;		
	}
	
	public static JPopupMenu getPopupMenuForCommunicationChannel(CommunicationChannel com_obj) 
	{
		JPopupMenu menu = new JPopupMenu("Communication Channel");
		final CommunicationChannel channel = com_obj;
		
		Action a = new AbstractAction(
				"Clone",
				SwingResource.smallerIconMap.get(IImageResource.IMG_CLONE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddComChannelDialog dialog = new AddComChannelDialog(channel.getPool(), channel);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		a = new AbstractAction(
				"Delete",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(channel.getName());

					channel.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_COM_CHANNEL, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete communication channel " + channel.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete experiment channel", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected communication channel");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize communication channel", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						channel.Init();
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize communication channel.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize communication channel", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		return menu;
	}
	
	public static JPopupMenu getPopupMenuForIORegister(IORegister com_obj) 
	{
		JPopupMenu menu = new JPopupMenu("Input/Output Register");
		final IORegister channel = com_obj;
		
		Action a = new AbstractAction(
				"Clone",
				SwingResource.smallerIconMap.get(IImageResource.IMG_CLONE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddIORegisterDialog dialog = new AddIORegisterDialog(channel.getPool(), channel);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		a = new AbstractAction(
				"Delete",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(channel.getName());

					channel.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_IOREGISTER, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete input/output register " + channel.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete input/output register", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected input/output register");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize input/output register", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						channel.Init();
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize input/output register.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize input/output register", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		return menu;
	}	
	
	public static JPopupMenu getPopupMenuForControllerClass(ControllerClass ctrlClass_obj) 
	{
		JPopupMenu menu = new JPopupMenu("Controller Class");
		final ControllerClass ctrlClass = ctrlClass_obj;
		
		Action a = new AbstractAction(
				"Create controller",
				SwingResource.smallerIconMap.get(IImageResource.IMG_NEW))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddControllerDialog dialog = new AddControllerDialog(ctrlClass.getPool(),ctrlClass);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		return menu;
	}
	
	public static JPopupMenu getPopupMenuForController(Controller ctrl_obj) 
	{	
		JPopupMenu menu = new JPopupMenu("Controller");
		final Controller ctrl = ctrl_obj;
		
		Action a = new AbstractAction(
				"Clone controller",
				SwingResource.smallerIconMap.get(IImageResource.IMG_CLONE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				ControllerClass ctrlClass = ctrl.getCtrlClass();
				AddControllerDialog dialog = new AddControllerDialog(ctrlClass.getPool(),ctrlClass);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		a = new AbstractAction(
				"Delete controller",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(ctrl.getName());
	
					ctrl.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_CTRL, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete Controller " + ctrl.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete controller", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize controller",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected controller");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize Controller", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						ctrl.getPool().initController(ctrl.getName());
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize controller.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize controller(s)", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Reload controller library",
				SwingResource.smallerIconMap.get(IImageResource.IMG_RELOAD))
		{
			public void actionPerformed(ActionEvent e) 
			{
				DevicePool devicePool = ctrl.getPool(); 
				String fileName = ctrl.getFileName();
				
				List<Controller> affectedCtrls = devicePool.getControllersInFile(fileName);

				StringBuffer msg = new StringBuffer("This action will affect the following controllers:");
				
				for(Controller thectrl : affectedCtrls)
					msg.append("\n" + thectrl.getName());
				
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reload controller library", JOptionPane.YES_NO_OPTION);
		    	
		    	if( res == JOptionPane.YES_OPTION)
				{
		    		try 
		    		{
						devicePool.reloadControllerFile(fileName);
					} 
		    		catch (DevFailed devFailed) 
		    		{
		    			StringBuffer buff = new StringBuffer("Failed to reload controller library.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reload controller library", JOptionPane.ERROR_MESSAGE);
					}
				}				
			}
		};
		item = new JMenuItem(a);
		menu.add(item);
		
		return menu;		
	}
	
	public static JPopupMenu getPopupMenuForExpChannel(ExperimentChannel ch_obj)
	{
		JPopupMenu menu = new JPopupMenu("Experiment Channel");
		final ExperimentChannel channel = ch_obj;
		
		Action a = new AbstractAction(
				"Clone",
				SwingResource.smallerIconMap.get(IImageResource.IMG_CLONE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddChannelDialog dialog = new AddChannelDialog(channel.getPool(), channel);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		a = new AbstractAction(
				"Delete",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(channel.getName());

					channel.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_EXP_CHANNEL, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete experiment channel " + channel.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete experiment channel", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected experiment channel");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize experiment channel", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						channel.Init();
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize experiment channel.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize experiment channel", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		return menu;
	}	

	public static JPopupMenu getPopupMenuForMeasurementGroup(MeasurementGroup mg_obj)
	{
		JPopupMenu menu = new JPopupMenu("Measurement Group");
		final MeasurementGroup mg = mg_obj;
		
		Action a = new AbstractAction(
				"Add channel",
				SwingResource.smallerIconMap.get(IImageResource.IMG_ADD))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddMeasurementGroupChannelDialog dialog = new AddMeasurementGroupChannelDialog(mg.getPool(),mg);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		JMenuItem item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Remove channel",
				SwingResource.smallerIconMap.get(IImageResource.IMG_REMOVE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				RemoveMeasurementGroupChannelDialog dialog = new RemoveMeasurementGroupChannelDialog(mg.getPool(),mg);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);
		
		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Delete",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(mg.getName());

					mg.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_MEASUREMENT_GROUP, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete measurement group " + mg.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete measurement group", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected measurement group");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize measurement group", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						mg.Init();
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize measurement group.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize measurement group", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		return menu;
	}		

	public static JPopupMenu getPopupMenuForMotorGroup(MotorGroup mg_obj) 
	{
		JPopupMenu menu = new JPopupMenu("Motor Group");
		final MotorGroup mg = mg_obj;
		
		Action a = new AbstractAction(
				"Add element",
				SwingResource.smallerIconMap.get(IImageResource.IMG_ADD))
		{
			public void actionPerformed(ActionEvent e) 
			{
				AddMotorGroupElementDialog dialog = new AddMotorGroupElementDialog(mg.getPool(),mg);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		JMenuItem item = new JMenuItem(a);
		menu.add(item);

		a = new AbstractAction(
				"Remove element",
				SwingResource.smallerIconMap.get(IImageResource.IMG_REMOVE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				RemoveMotorGroupElementDialog dialog = new RemoveMotorGroupElementDialog(mg.getPool(),mg);
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};
		item = new JMenuItem(a);
		menu.add(item);
		
		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Delete",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
             
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(mg.getName());

					mg.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_MOTOR_GROUP, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete motor group " + mg.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete motor group", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected motor group");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize motor group", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						mg.Init();
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize motor group.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize motor group", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		return menu;
	}	

	public static JPopupMenu getPopupMenuForMotor(Motor m_obj) 
	{
		JPopupMenu menu = new JPopupMenu("Motor");
		final Motor m = m_obj;
		
		Action a = new AbstractAction(
				"Clone",
				SwingResource.smallerIconMap.get(IImageResource.IMG_CLONE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				JDialog dialog;
				if(m instanceof PseudoMotor)
					dialog = new AddControllerDialog(m.getPool(),((PseudoMotor)m).getPseudoMotorClass());
				else
					dialog = new AddMotorDialog(m.getPool(),m);
				
				dialog.setLocationRelativeTo(null);
				dialog.setVisible(true);
			}
		};		
		JMenuItem item = new JMenuItem(a);
		menu.add(item);
		
		a = new AbstractAction(
				"Delete",
				SwingResource.smallerIconMap.get(IImageResource.IMG_DELETE))
		{
			public void actionPerformed(ActionEvent e) 
			{
				try
				{
					DeviceData args = new DeviceData();
	
					args.insert(m.getName());
					m.getPool().getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_MOTOR, args );
				}
				catch(DevFailed devFailed)
				{
					StringBuffer buff = new StringBuffer();
					
					buff.append("Failed to delete motor " + m.getName() + ".\nReason:");
					
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete motor", JOptionPane.ERROR_MESSAGE);
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		menu.add(new JSeparator());
		
		a = new AbstractAction(
				"Reinitialize",
				SwingResource.smallerIconMap.get(IImageResource.IMG_INIT))
		{
			public void actionPerformed(ActionEvent e) 
			{
				StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected motor");
				msg.append("\nAre you sure you want to continue?");
		    	
				int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize motor", JOptionPane.YES_NO_OPTION);

				if( res == JOptionPane.YES_OPTION)
				{
					try
					{
						m.Init();
					}
					catch(DevFailed devFailed)
					{
		    			StringBuffer buff = new StringBuffer("Failed to reinitialize motor.\nReason:");
						for(DevError elem : devFailed.errors)
							buff.append( elem.desc + "\n");
		    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize motor", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		};
		item = new JMenuItem(a);
		menu.add(item);

		return menu;
	}		
}

class PoolFileView extends FileView
{
    public String getName(File f) 
    {
        return null; //let the L&F FileView figure this out
    }

    public String getDescription(File f) 
    {
        return null; //let the L&F FileView figure this out
    }

    public Boolean isTraversable(File f) 
    {
        return null; //let the L&F FileView figure this out
    }

    public String getTypeDescription(File f) 
    {
        return "Pool configuration file";
    }

    public Icon getIcon(File f) 
    {
    	String s = f.getName();
    	int i = s.lastIndexOf(".");
    	
    	if(i < 0 || i > s.length() - 1)
    		return null;
    	
    	if(!s.substring(i+1).equalsIgnoreCase("xsr"))
    		return null;
    	
    	return SwingResource.smallerIconMap.get(IImageResource.IMG_POOL);
    }
}
