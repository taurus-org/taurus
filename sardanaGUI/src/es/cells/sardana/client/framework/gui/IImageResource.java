package es.cells.sardana.client.framework.gui;

import java.lang.reflect.Field;
import java.util.ArrayList;

import es.cells.sardana.client.framework.gui.atk.widget.tree.ComChannelsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.ControllersTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.DevicePoolTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.ExpChannelsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.GenericSardanaTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.GlobalViewRootTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.IORegistersTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MachineTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MeasurementGroupsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MotorGroupsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.MotorsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.PseudoMotorsTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.SardanaTreeNode;
import es.cells.sardana.client.framework.gui.atk.widget.tree.SardanasViewRootTreeNode;
import es.cells.sardana.client.framework.pool.CommunicationChannel;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.ControllerClass;
import es.cells.sardana.client.framework.pool.ControllerType;
import es.cells.sardana.client.framework.pool.CounterTimer;
import es.cells.sardana.client.framework.pool.CtrlState;
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.OneDExpChannel;
import es.cells.sardana.client.framework.pool.PseudoCounter;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import es.cells.sardana.client.framework.pool.TwoDExpChannel;
import es.cells.sardana.client.framework.pool.ZeroDExpChannel;

public class IImageResource {

	public static final String
		IMG_SARDANA = "sardana.png",
		IMG_SARDANAS = "sardanas.png",
		IMG_MACHINE_RUN = "computer.png",
		IMG_MACHINE_STOP = "computer_na.png",
		IMG_POOL = "pool.png",
		IMG_POOL_NA = "pool_na.png",
		IMG_POOL_WARNING = "pool_warning.png",
		IMG_POOL_CTRLS = "controllers.png",
		IMG_POOL_COM_CHANNELS  = "communication_channels.png",
		IMG_POOL_IOREGISTERS  = "communication_channels.png",
		IMG_POOL_MOTORS  = "motors.png",
		IMG_POOL_MOTOR_GROUPS = "motorgroup.png",
		IMG_POOL_PSEUDO_MOTORS = "motors.png",
		IMG_POOL_MEASUREMENT_GROUPS = "measurementgroups.png",
		IMG_POOL_EXP_CHANNELS  = "experimentchannels.png",
		IMG_POOL_CTRL = "controller.png",
		IMG_POOL_CTRL_NA = "controller_na.png",
		IMG_POOL_CTRL_COM_CHANNEL = "controller_comchannel.png",
		IMG_POOL_CTRL_COM_CHANNEL_NA = "controller_comchannel_na.png",
		IMG_POOL_CTRL_COM_CHANNEL_WARNING = "controller_comchannel_warning.png",
		IMG_POOL_CTRL_IOREGISTER = "controller_comchannel.png",
		IMG_POOL_CTRL_IOREGISTER_NA = "controller_comchannel_na.png",
		IMG_POOL_CTRL_IOREGISTER_WARNING = "controller_comchannel_warning.png",
		IMG_POOL_CTRL_MOTOR = "controller_motor.png",
		IMG_POOL_CTRL_MOTOR_NA = "controller_motor_na.png",
		IMG_POOL_CTRL_MOTOR_WARNING = "controller_motor_warning.png",
		IMG_POOL_CTRL_PSEUDO_MOTOR = "controller_pseudo_motor.png",
		IMG_POOL_CTRL_PSEUDO_MOTOR_NA = "controller_pseudo_motor_na.png",
		IMG_POOL_CTRL_PSEUDO_MOTOR_WARNING = "controller_pseudo_motor_warning.png",
		IMG_POOL_CTRL_PSEUDO_COUNTER = "controller_pseudo_counter.png",
		IMG_POOL_CTRL_PSEUDO_COUNTER_NA = "controller_pseudo_counter_na.png",
		IMG_POOL_CTRL_PSEUDO_COUNTER_WARNING = "controller_pseudo_counter_warning.png",
		IMG_POOL_CTRL_CT = "controller_ct.png",
		IMG_POOL_CTRL_CT_NA = "controller_ct_na.png",
		IMG_POOL_CTRL_CT_WARNING = "controller_ct_warning.png",
		IMG_POOL_CTRL_0D = "controller_zerod.png",
		IMG_POOL_CTRL_0D_NA = "controller_zerod_na.png",
		IMG_POOL_CTRL_0D_WARNING = "controller_zerod_warning.png",
		IMG_POOL_CTRL_1D = "controller_zerod.png",
		IMG_POOL_CTRL_1D_NA = "controller_zerod_na.png",
		IMG_POOL_CTRL_1D_WARNING = "controller_zerod_warning.png",
		IMG_POOL_CTRL_2D = "controller_zerod.png",
		IMG_POOL_CTRL_2D_NA = "controller_zerod_na.png",
		IMG_POOL_CTRL_2D_WARNING = "controller_zerod_warning.png",
		IMG_POOL_COM_CHANNEL = "communication_channel.png",
		IMG_POOL_COM_CHANNEL_NA = "communication_channel_na.png",
		IMG_POOL_COM_CHANNEL_WARNING = "communication_channel_warning.png",
		IMG_POOL_IOREGISTER = "communication_channel.png",
		IMG_POOL_IOREGISTER_NA = "communication_channel_na.png",
		IMG_POOL_IOREGISTER_WARNING = "communication_channel_warning.png",
		IMG_POOL_MOTOR = "motor.png",
		IMG_POOL_MOTOR_MOVING = "motor_moving.png",
		IMG_POOL_MOTOR_NA = "motor_na.png",
		IMG_POOL_MOTOR_WARNING = "motor_warning.png",
		IMG_POOL_MOTOR_GROUP = "motorgroup.png",
		IMG_POOL_MOTOR_GROUP_NA = "motorgroup_na.png",
		IMG_POOL_MOTOR_GROUP_WARNING = "motorgroup_warning.png",
		IMG_POOL_MOTOR_GROUP_MOVING = "motorgroup_moving.png",
		IMG_POOL_PSEUDO_MOTOR = "pseudo_motor.png",
		IMG_POOL_PSEUDO_MOTOR_NA = "pseudo_motor_na.png",
		IMG_POOL_PSEUDO_MOTOR_WARNING = "pseudo_motor_warning.png",
		IMG_POOL_PSEUDO_MOTOR_MOVING = "pseudo_motor_moving.png",
		IMG_POOL_PSEUDO_COUNTER = "pseudo_counter.png",
		IMG_POOL_PSEUDO_COUNTER_NA = "pseudo_counter_na.png",
		IMG_POOL_PSEUDO_COUNTER_WARNING = "pseudo_counter_warning.png",
		IMG_POOL_CT = "countertimer.png",
		IMG_POOL_CT_NA = "countertimer_na.png",
		IMG_POOL_CT_WARNING = "countertimer_warning.png",
		IMG_POOL_MEASUREMENT_GROUP = "measurementgroup.png",
		IMG_POOL_MEASUREMENT_GROUP_NA = "measurementgroup_na.png",
		IMG_POOL_MEASUREMENT_GROUP_WARNING = "measurementgroup_warning.png",
		IMG_POOL_ZEROD = "zerod.png",
		IMG_POOL_ZEROD_NA = "zerod_na.png",
		IMG_POOL_ZEROD_WARNING = "zerod_warning.png",
		IMG_POOL_ONED = "zerod.png",
		IMG_POOL_ONED_NA = "zerod_na.png",
		IMG_POOL_ONED_WARNING = "zerod_warning.png",
		IMG_POOL_TWOD = "zerod.png",
		IMG_POOL_TWOD_NA = "zerod_na.png",
		IMG_POOL_TWOD_WARNING = "zerod_warning.png",
		IMG_POOL_UNKNOWN = "unknown.png",
		IMG_POOL_PSEUDO_MOT_CTRL_CLASS = "library_motor_controller.png",
		IMG_POOL_COM_CHANNEL_CLASS = "library_comchannel_controller.png",
		IMG_POOL_MOT_CTRL_CLASS = "library_motor_controller.png",
		IMG_POOL_CT_CTRL_CLASS = "library_ct_controller.png",
		IMG_POOL_ZEROD_CTRL_CLASS = "library_zerod_controller.png",
		IMG_POOL_ONED_CTRL_CLASS = "library_zerod_controller.png",
		IMG_POOL_TWOD_CTRL_CLASS = "library_zerod_controller.png",
		IMG_POOL_PSEUDO_CO_CTRL_CLASS = "library_zerod_controller.png",
		IMG_POOL_UNKNOWN_CTRL_CLASS = "library_unknown_controller.png",
		IMG_CTRL_OK = "res/ctrl_ok.gif",
		IMG_CTRL_ERROR = "res/ctrl_error.gif",

		IMG_ADD = "add.png",
		IMG_REMOVE = "remove.png",
		IMG_NEW = "filenew.png",
		IMG_CLONE = "editcopy.png",
		IMG_DELETE = "editdelete.png",
		IMG_RELOAD = "reload.png",
		IMG_ICON_VIEW = "iconview.png",
		IMG_LIST_VIEW = "listview.png",
		IMG_REFRESH = "refresh.png",
		IMG_UP = "up.png",
		IMG_DOWN = "down.png",
		IMG_BACK = "back.png",
		IMG_FORWARD = "forward.png",
		IMG_APPLY = "apply.png",
		IMG_PREFERENCES = "preferences.png",
		IMG_UNDO = "undo.png",
		IMG_STOP = "stop.png",
		IMG_RETURN = "return.png",
		IMG_OK = "ok.png",
		IMG_CLOSE = "close.png",
		IMG_INIT = "init.png",
		IMG_CLEAR = "clear.png",
		IMG_FILE_NEW = "filenew.png",
		IMG_FILE_OPEN = "fileopen.png",
		IMG_FILE_SAVE = "filesave.png",
		IMG_FILE_SAVE_AS = "filesaveas.png",
		IMG_LIBRARY = "library.png",
		IMG_EDIT = "edit.png",
			
		IMG_MACROSERVER = "macroserver.png",
		IMG_MACROSERVER_NA = "macroserver.png",
		IMG_MACROSERVER_WARNING = "macroserver.png",
		IMG_MACROSERVER_UNKNOWN = "macroserver.png",
		
		IMG_DOOR = "door.png",
		IMG_DOOR_NA = "door.png",
		IMG_DOOR_WARNING = "door.png",
		IMG_DOOR_UNKNOWN = "door.png",
		IMG_DOORS = "doors.png",
		
		IMG_SIMU = "simu.png"
		;
			
	public static ArrayList<String> iconList = new ArrayList<String>(50);
	
	static {
		Field[] fields = IImageResource.class.getDeclaredFields();
		for(int i = 0; i < fields.length; i++) {		
			if(fields[i].getName().startsWith("IMG_")) {
				try	{
					Object fieldValue = fields[i].get(null);
					if( fieldValue instanceof String )
					{
						String filename = (String)fieldValue;
						iconList.add(filename);
					}
				} catch (Exception e) {e.printStackTrace();}
			}
		}
	}

	public static String getControllerIcon(Controller ctrl)
	{
		if(ctrl.getState() == CtrlState.Error)
			return IMG_CTRL_ERROR;
		else
			return IMG_CTRL_OK;
	}
	
	
	public static String getNonDeviceElementIcon(Object elem)
	{
		if(elem instanceof Controller)
		{
			Controller c = (Controller) elem;
			
			return c.getClassName();
		}
		else if(elem instanceof ControllerClass)
		{
			ControllerClass c = (ControllerClass) elem;
			if(c.getType() == ControllerType.Motor)
				return IMG_POOL_MOT_CTRL_CLASS;
			else if(c.getType() == ControllerType.PseudoMotor)
				return IMG_POOL_PSEUDO_MOT_CTRL_CLASS;
			else if(c.getType() == ControllerType.PseudoCounter)
				return IMG_POOL_PSEUDO_CO_CTRL_CLASS;
			else if(c.getType() == ControllerType.CounterTimer)
				return IMG_POOL_CT_CTRL_CLASS;
			else if(c.getType() == ControllerType.ZeroDExpChannel)
				return IMG_POOL_ZEROD_CTRL_CLASS;
			else if(c.getType() == ControllerType.OneDExpChannel)
				return IMG_POOL_ONED_CTRL_CLASS;
			else if(c.getType() == ControllerType.TwoDExpChannel)
				return IMG_POOL_TWOD_CTRL_CLASS;
			else if(c.getType() == ControllerType.Communication)
				return IMG_POOL_COM_CHANNEL_CLASS;
			else
				return IMG_POOL_UNKNOWN_CTRL_CLASS;
		}
		else if(elem instanceof SardanaDevice)
		{
			return getDeviceElementIcon((SardanaDevice)elem);
		}
		else if(elem instanceof Machine)
		{
			return IMG_MACHINE_RUN;
		}
		else
			return IMG_POOL_UNKNOWN;	
	}
	
	public static String getControllerTypeIcon(ControllerType type)
	{
		return getControllerTypeIcon(type,CtrlState.Ok);
	}
	
	public static String getControllerTypeIcon(ControllerType type, CtrlState state)
	{
		if(state == CtrlState.Ok)
		{
			if(type == ControllerType.Motor)
				return IMG_POOL_CTRL_MOTOR;
			else if(type == ControllerType.PseudoMotor)
				return IMG_POOL_CTRL_PSEUDO_MOTOR;
			else if(type == ControllerType.PseudoCounter)
				return IMG_POOL_CTRL_PSEUDO_COUNTER;
			else if(type == ControllerType.CounterTimer)
				return IMG_POOL_CTRL_CT;
			else if(type == ControllerType.ZeroDExpChannel)
				return IMG_POOL_CTRL_0D;
			else if(type == ControllerType.OneDExpChannel)
				return IMG_POOL_CTRL_1D;
			else if(type == ControllerType.TwoDExpChannel)
				return IMG_POOL_CTRL_2D;
			else if(type == ControllerType.Communication)
				return IMG_POOL_CTRL_COM_CHANNEL;
			else
				return IMG_POOL_CTRL;
		}
		else
		{
			if(type == ControllerType.Motor)
				return IMG_POOL_CTRL_MOTOR_NA;
			else if(type == ControllerType.PseudoMotor)
				return IMG_POOL_CTRL_PSEUDO_MOTOR_NA;
			else if(type == ControllerType.PseudoCounter)
				return IMG_POOL_CTRL_PSEUDO_COUNTER_NA;
			else if(type == ControllerType.CounterTimer)
				return IMG_POOL_CTRL_CT_NA;
			else if(type == ControllerType.ZeroDExpChannel)
				return IMG_POOL_CTRL_0D_NA;
			else if(type == ControllerType.OneDExpChannel)
				return IMG_POOL_CTRL_1D_NA;
			else if(type == ControllerType.TwoDExpChannel)
				return IMG_POOL_CTRL_2D_NA;
			else if(type == ControllerType.Communication)
				return IMG_POOL_CTRL_COM_CHANNEL_NA;
			else
				return IMG_POOL_CTRL_NA;
		}
	}
	
	public static String getDeviceElementIcon(SardanaDevice sardanaDevice)
	{
		if(sardanaDevice instanceof CommunicationChannel)
		{
			CommunicationChannel comChannel = (CommunicationChannel)sardanaDevice; 
			if(comChannel.isAvailable())
			{
				if(comChannel.getState() == "ALARM")
					return IMG_POOL_COM_CHANNEL_WARNING;
				else if(comChannel.getState() == "FAULT")
					return IMG_POOL_COM_CHANNEL_WARNING;
				else if(comChannel.getState() == "UNKNOWN")
					return IMG_POOL_COM_CHANNEL_NA;
				else
					return IMG_POOL_COM_CHANNEL;
			}
			else
				return IMG_POOL_COM_CHANNEL_NA;
		}		
		// Pseudo motor test must be before motor case because Pseudo Motor
		// is an instance of Motor
		else if(sardanaDevice instanceof PseudoMotor)
		{
			PseudoMotor m = (PseudoMotor)sardanaDevice; 
			if(m.isAvailable())
			{
				if(m.getState() == "ALARM")
					return IMG_POOL_PSEUDO_MOTOR_WARNING;
				else if(m.getState() == "MOVING")
					return IMG_POOL_PSEUDO_MOTOR_MOVING;
				else if(m.getState() == "UNKNOWN")
					return IMG_POOL_PSEUDO_MOTOR_NA;				
				else
					return IMG_POOL_PSEUDO_MOTOR;
			}
			else
				return IMG_POOL_PSEUDO_MOTOR_NA;
		}			
		else if(sardanaDevice instanceof Motor)
		{
			Motor m = (Motor)sardanaDevice; 
			if(m.isAvailable())
			{
				if(m.getState() == "ALARM")
					return IMG_POOL_MOTOR_WARNING;
				else if(m.getState() == "MOVING")
					return IMG_POOL_MOTOR_MOVING;
				else if(m.getState() == "UNKNOWN")
					return IMG_POOL_MOTOR_NA;
				else
					return IMG_POOL_MOTOR;
			}
			else
				return IMG_POOL_MOTOR_NA;
		}
		else if(sardanaDevice instanceof MotorGroup)
		{
			MotorGroup mg = (MotorGroup)sardanaDevice;
			if(mg.isAvailable())
			{
				if(mg.getState() == "ALARM")
					return IMG_POOL_MOTOR_GROUP_WARNING;
				else if(mg.getState() == "MOVING")
					return IMG_POOL_MOTOR_GROUP_MOVING;
				else if(mg.getState() == "UNKNOWN")
					return IMG_POOL_MOTOR_GROUP_NA;				
				else
					return IMG_POOL_MOTOR_GROUP;
			}
			else
				return IMG_POOL_MOTOR_GROUP_NA;
		}
		else if(sardanaDevice instanceof ExperimentChannel)
		{
			if(sardanaDevice instanceof CounterTimer)
			{
				CounterTimer ct = (CounterTimer)sardanaDevice; 
				if(ct.isAvailable())
				{
					if(ct.getState() == "ALARM")
						return IMG_POOL_CT_WARNING;
					else if(ct.getState() == "UNKNOWN")
						return IMG_POOL_CT_NA;
					else
						return IMG_POOL_CT;
				}
				else
					return IMG_POOL_CT_NA;
			}
			else if(sardanaDevice instanceof PseudoCounter)
			{
				PseudoCounter m = (PseudoCounter)sardanaDevice; 
				if(m.isAvailable())
				{
					if(m.getState() == "ALARM")
						return IMG_POOL_ZEROD_WARNING;
					else if(m.getState() == "UNKNOWN")
						return IMG_POOL_ZEROD_NA;				
					else
						return IMG_POOL_ZEROD;
				}
				else
					return IMG_POOL_ZEROD_NA;
			}			
			else if(sardanaDevice instanceof ZeroDExpChannel)
			{
				ZeroDExpChannel zerod = (ZeroDExpChannel)sardanaDevice; 
				if(zerod.isAvailable())
				{
					if(zerod.getState() == "ALARM")
						return IMG_POOL_ZEROD_WARNING;
					else if(zerod.getState() == "UNKNOWN")
						return IMG_POOL_ZEROD_NA;
					else
						return IMG_POOL_ZEROD;
				}
				else
					return IMG_POOL_ZEROD_NA;
			}			
			else if(sardanaDevice instanceof OneDExpChannel)
			{
				OneDExpChannel oned = (OneDExpChannel)sardanaDevice; 
				if(oned.isAvailable())
				{
					if(oned.getState() == "ALARM")
						return IMG_POOL_ONED_WARNING;
					else if(oned.getState() == "UNKNOWN")
						return IMG_POOL_ONED_NA;
					else
						return IMG_POOL_ONED;
				}
				else
					return IMG_POOL_ONED_NA;
			}			
			else if(sardanaDevice instanceof TwoDExpChannel)
			{
				TwoDExpChannel twod = (TwoDExpChannel)sardanaDevice; 
				if(twod.isAvailable())
				{
					if(twod.getState() == "ALARM")
						return IMG_POOL_TWOD_WARNING;
					else if(twod.getState() == "UNKNOWN")
						return IMG_POOL_TWOD_NA;
					else
						return IMG_POOL_TWOD;
				}
				else
					return IMG_POOL_TWOD_NA;
			}
			else
				return IMG_POOL_UNKNOWN;
		}			
		else if(sardanaDevice instanceof MeasurementGroup)
		{
			MeasurementGroup mg = (MeasurementGroup)sardanaDevice;
			if(mg.isAvailable())
			{
				if(mg.getState() == "ALARM")
					return IMG_POOL_MEASUREMENT_GROUP_WARNING;
				else if(mg.getState() == "UNKNOWN")
					return IMG_POOL_MEASUREMENT_GROUP_NA;
				else
					return IMG_POOL_MEASUREMENT_GROUP;
			}
			else
				return IMG_POOL_MEASUREMENT_GROUP_NA;				
		}
		else
			return IMG_POOL_UNKNOWN;
	}
	
	public static String getPoolTreeIcon(GenericSardanaTreeNode node)
	{
		if(node instanceof GlobalViewRootTreeNode)
		{
			return IMG_SARDANA;
		}
		if(node instanceof SardanasViewRootTreeNode)
		{
			return IMG_SARDANAS;
		}	
		if(node instanceof SardanaTreeNode)
		{
			return IMG_SARDANA;
		}
		else if(node instanceof MachineTreeNode)
		{
			return IMG_MACHINE_RUN;
		}		
		else if(node instanceof DevicePoolTreeNode)
		{
			DevicePoolTreeNode poolNode = (DevicePoolTreeNode) node;
			
			if(poolNode.getState().equals("UNKNOWN"))
				return IMG_POOL_NA;
			else if(poolNode.getState().equals("ALARM"))
				return IMG_POOL_WARNING;
			else
				return IMG_POOL;
		}
		else if(node instanceof ControllersTreeNode)
		{
			return IMG_POOL_CTRLS;
		}
		else if(node instanceof ComChannelsTreeNode)
		{
			return IMG_POOL_COM_CHANNELS;
		}
		else if(node instanceof IORegistersTreeNode)
		{
			return IMG_POOL_IOREGISTERS;
		}		
		else if(node instanceof MotorsTreeNode)
		{
			return IMG_POOL_MOTORS;
		}
		else if(node instanceof MotorGroupsTreeNode)
		{
			return IMG_POOL_MOTOR_GROUPS;
		}
		else if(node instanceof PseudoMotorsTreeNode)
		{
			return IMG_POOL_PSEUDO_MOTORS;
		}
		else if(node instanceof ExpChannelsTreeNode)
		{
			return IMG_POOL_EXP_CHANNELS;
		}
		else if(node instanceof MeasurementGroupsTreeNode)
		{
			return IMG_POOL_MEASUREMENT_GROUPS;
		}
		else 
		{
			return getNonDeviceElementIcon(node.getUserObject());
		}
	}

	public static String getDevicePoolTreeIcon(String state)
	{
		if(state.equals("UNKNOWN"))
			return IMG_POOL_NA;
		else if(state.equals("ALARM"))
			return IMG_POOL_WARNING;
		else if(state.equals("ON"))
			return IMG_POOL;
		else 
			return IMG_POOL_UNKNOWN;
	}

	public static String getDevicePoolTreeIcon()
	{
		return IMG_POOL;
	}

	public static String getMacroServerTreeIcon(String state)
	{
		if(state.equals("UNKNOWN"))
			return IMG_MACROSERVER_NA;
		else if(state.equals("ALARM"))
			return IMG_MACROSERVER_WARNING;
		else if(state.equals("ON"))
			return IMG_MACROSERVER;
		else 
			return IMG_MACROSERVER_UNKNOWN;
	}
	
	public static String getMacroServerTreeIcon()
	{
		return IMG_MACROSERVER;
	}

	public static String getDoorTreeIcon(String state)
	{
		if(state.equals("UNKNOWN"))
			return IMG_DOOR_NA;
		else if(state.equals("ALARM"))
			return IMG_DOOR_WARNING;
		else if(state.equals("ON"))
			return IMG_DOOR;
		else 
			return IMG_DOOR_UNKNOWN;
	}
	
	public static String getDoorTreeIcon()
	{
		return IMG_DOOR;
	}

	public static String getDoorsTreeIcon()
	{
		return IMG_DOORS;
	}
	
}
