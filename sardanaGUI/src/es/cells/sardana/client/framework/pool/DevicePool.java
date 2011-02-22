package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

import es.cells.sardana.client.framework.pool.event.PoolInternalStringSpectrumEvent;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.DeviceProperty;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IBooleanScalar;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class DevicePool extends SardanaDevice 
{
	protected List<Controller> controllers;
	protected List<CommunicationChannel> communicationChannels;
	protected List<IORegister> ioRegisters;
	protected List<Motor> motors;
	protected List<MotorGroup> motorGroups;
	protected List<PseudoMotor> pseudoMotors;
	protected List<PseudoCounter> pseudoCounters;
	protected List<ExperimentChannel> experimentChannels;
	protected List<MeasurementGroup> measurementGroups;
	
	/** 
	 *  An Hash of controller classes.
	 *  Key = Controller Type, Value = { Key = fileName, Value = Controller Class information }
	 */
	protected HashMap<ControllerType, HashMap<String, List<ControllerClass>>> controllerClasses;

	/** 
	 *  An Hash of pseudo motor classes.
	 *  Key = fileName, Value = Pseudo Motor Class information
	 */
	//protected HashMap<String, List<PseudoMotorClass>> pseudoMotorClasses;
	
	protected ControllerListListener controllerListListener;
	protected CommunicationChannelListListener communicationChannelListListener;
	protected IORegisterListListener ioRegisterListListener;
	protected MotorListListener motorListListener;
	protected MotorGroupListListener motorGroupListListener;
	protected PseudoMotorListListener pseudoMotorListListener;
	protected PseudoCounterListListener pseudoCounterListListener;
	protected ExperimentChannelListListener experimentChannelListListener;
	protected MeasurementGroupListListener measurementGroupListListener;
	
	protected List<IStringSpectrumListener> controllerClassListListeners;
	//protected List<IStringSpectrumListener> pseudoMotorClassListListeners;
	protected List<IStringSpectrumListener> controllerListListeners; 
	protected List<IStringSpectrumListener> communicationChannelListListeners; 
	protected List<IStringSpectrumListener> ioRegisterListListeners;
	protected List<IStringSpectrumListener> motorListListeners;
	protected List<IStringSpectrumListener> motorGroupListListeners;
	protected List<IStringSpectrumListener> pseudoMotorListListeners;
	protected List<IStringSpectrumListener> pseudoCounterListListeners;
	protected List<IStringSpectrumListener> experimentChannelListListeners;
	protected List<IStringSpectrumListener> measurementGroupListListeners;
	
	public DevicePool(Machine machine, String name)
	{
		super(machine, name);
		
		setPool(this);
		
		controllerClassListListeners = new ArrayList<IStringSpectrumListener>();
		communicationChannelListListeners = new ArrayList<IStringSpectrumListener>();
        ioRegisterListListeners = new ArrayList<IStringSpectrumListener>();
		//pseudoMotorClassListListeners = new ArrayList<IStringSpectrumListener>();
		controllerListListeners = new ArrayList<IStringSpectrumListener>();
		motorListListeners = new ArrayList<IStringSpectrumListener>();
		motorGroupListListeners = new ArrayList<IStringSpectrumListener>();
		pseudoMotorListListeners = new ArrayList<IStringSpectrumListener>();
		pseudoCounterListListeners = new ArrayList<IStringSpectrumListener>();
		experimentChannelListListeners = new ArrayList<IStringSpectrumListener>();
		measurementGroupListListeners = new ArrayList<IStringSpectrumListener>();
		
		controllerListListener = new ControllerListListener();
		communicationChannelListListener = new CommunicationChannelListListener(); 
		ioRegisterListListener = new IORegisterListListener(); 
		motorListListener = new MotorListListener();
		motorGroupListListener = new MotorGroupListListener();
		pseudoMotorListListener = new PseudoMotorListListener();
		pseudoCounterListListener = new PseudoCounterListListener();
		experimentChannelListListener = new ExperimentChannelListListener();
		measurementGroupListListener = new MeasurementGroupListListener();
		
		controllers = Collections.synchronizedList(new ArrayList<Controller>());
		communicationChannels = Collections.synchronizedList(new ArrayList<CommunicationChannel>());
		ioRegisters = Collections.synchronizedList(new ArrayList<IORegister>());
		motors = Collections.synchronizedList(new ArrayList<Motor>());
		motorGroups = Collections.synchronizedList(new ArrayList<MotorGroup>());
		pseudoMotors = Collections.synchronizedList(new ArrayList<PseudoMotor>());
		pseudoCounters = Collections.synchronizedList(new ArrayList<PseudoCounter>());
		experimentChannels = Collections.synchronizedList(new ArrayList<ExperimentChannel>());
		measurementGroups = Collections.synchronizedList(new ArrayList<MeasurementGroup>());
		//pseudoMotorClasses = new HashMap<String, List<PseudoMotorClass>>();
		controllerClasses = new HashMap<ControllerType,HashMap<String, List<ControllerClass>>>();
		
		for(ControllerType type : getControllerTypes())
			controllerClasses.put(type, new HashMap<String, List<ControllerClass>>());
	}

	protected void init()
	{

		// We do this before the super.init. If we did this after (because init 
		// registers for events) we may receive events while we are getting 
		// critical information.
		// For example, we may receive an event on the ControllerList and 
		// the controller classes may not have been filled before.
		if(device != null && device.isAlive() == true)
		{
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			setControllerClasses(utils.askForDevicePoolControllerClasses(this));
			setControllers(utils.askForDevicePoolControllers(this));
			setCommunicationChannels(utils.askForDevicePoolCommunicationChannels(this));
			setIORegisters(utils.askForDevicePoolIORegisters(this));
			setMotors(utils.askForDevicePoolMotors(this));
			setExperimentChannels(utils.askForDevicePoolExperimentChannels(this));
			//setPseudoMotors(utils.askForDevicePoolPseudoMotors(this));
			//setPseudoCounters(utils.askForDevicePoolPseudoCounters(this));
			setMotorGroups(utils.askForDevicePoolMotorGroups(getPool()));
			setMeasurementGroups(utils.askForDevicePoolMeasurementGroups(getPool()));
			setProperties(utils.askForDevicePoolProperties(getPool()));	
		}
		
		super.init();
	}
	
	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_CTRL_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_MOTOR_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_COM_CHANNEL_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_IOREGISTER_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_MOTOR_GROUP_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_PSEUDO_MOTOR_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_EXP_CHANNEL_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_PSEUDO_COUNTER_LIST);
		eventAttributeList.add(DevicePoolUtils.POOL_ATTR_MEASUREMENT_GROUP_LIST);
		
		for(AttributeInfoEx attr : attributeInfo)
		{
			boolean is_event_attr = false;
			for(String eventAttr : eventAttributeList)
			{
				if(eventAttr.equalsIgnoreCase(attr.name))
				{
					is_event_attr = true;
					break;
				}	
			}
			
			if(is_event_attr == true)
				continue;
			nonPolledAttributeList.add(attr.name);
		}
	}
	
	public void devStateScalarChange(DevStateScalarEvent e)
	{
		boolean old_available = available;
		
		super.devStateScalarChange(e);
		
		// Pool came back. We need to update all internal data 
		if(!old_available && available)
		{
			log.fine(getName() + " is comming back. Initializing... ");
			init();
			start();
		}

		// listeners were informed above that the pool entered an unknown state
		// so we can safely clean here
		if(old_available && !available)
		{
			log.fine(getName() + " is shutting down. Cleanup in place... ");
			unregisterFromDevice(true);
			
			synchronized (controllers) {
				controllers.clear();
				//controllers = null;
			}
			synchronized (communicationChannels) {
				for(CommunicationChannel ch: communicationChannels)
				{
					ch.cleanup(false);
				}
				communicationChannels.clear();
				//communicationChannels = null;
			}
			synchronized (ioRegisters) {
				for(IORegister ior: ioRegisters)
				{
					ior.cleanup(false);
				}
				ioRegisters.clear();
				//communicationChannels = null;
			}
			synchronized (motors) {
				for(Motor m: motors)
				{
					m.cleanup(false);
				}
				motors.clear();
				//motors = null;
			}
			synchronized (motorGroups) {
				for(MotorGroup mg: motorGroups)
				{
					mg.cleanup(false);
				}
				motorGroups.clear();
				//motorGroups = null;
			}
			synchronized (pseudoMotors) {
				for(PseudoMotor m: pseudoMotors)
				{
					m.cleanup(false);
				}
				pseudoMotors.clear();
				//pseudoMotors = null;
			}
			synchronized (experimentChannels) {
				for(ExperimentChannel ch: experimentChannels)
				{
					ch.cleanup(false);
				}
				experimentChannels.clear();
				//experimentChannels = null;
			}
			synchronized (pseudoCounters) {
				for(PseudoCounter m: pseudoCounters)
				{
					m.cleanup(false);
				}
				pseudoMotors.clear();
				//pseudoMotors = null;
			}
			synchronized (measurementGroups) {
				for(MeasurementGroup mg: measurementGroups)
				{
					mg.cleanup(false);
				}
				measurementGroups.clear();
				//measurementGroups = null;
			}
			/*
			synchronized (pseudoMotorClasses) {
				pseudoMotorClasses.clear();
				//pseudoMotorClasses = null;
			}
			*/
			synchronized (controllerClasses) {
				
				for(HashMap<String, List<ControllerClass>> ctrls_of_type : controllerClasses.values())
					ctrls_of_type.clear();
				//controllerClasses = null;
			}

			controllerClassListListeners.clear();
			communicationChannelListListeners.clear();
            ioRegisterListListeners.clear();
			//pseudoMotorClassListListeners.clear();
			controllerListListeners.clear();
			motorListListeners.clear();
			motorGroupListListeners.clear();
			pseudoMotorListListeners.clear();
			pseudoCounterListListeners.clear();
			experimentChannelListListeners.clear();
			measurementGroupListListeners.clear();

			/*
			controllerClassListListeners = null;
			communicationChannelListListeners = null;
			pseudoMotorClassListListeners = null;
			controllerListListeners = null;
			motorListListeners = null;
			motorGroupListListeners = null;
			pseudoMotorListListeners = null;
			pseudoCounterListListeners = null;
			experimentChannelListListeners = null;
			measurementGroupListListeners = null;
			
			controllerListListener = null;
			communicationChannelListListener = null;
			motorListListener = null;
			motorGroupListListener = null;
			pseudoMotorListListener = null;
			pseudoCounterListListener = null;
			experimentChannelListListener = null;
			measurementGroupListListener = null;
			*/
		}
	}
	
	public void errorChange(ErrorEvent evt)
	{
		if(available == true)
			log.warning("Received state error event");
		
		available = false;
		
		// Error change
		for(IDevStateScalarListener listener : stateListeners)
			listener.errorChange(evt);
	}
	
	public IStringSpectrum getControllerListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_CTRL_LIST);
	}

	public IStringSpectrum getCommunicationChannelListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_COM_CHANNEL_LIST);
	}

	public IStringSpectrum getIORegisterListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_IOREGISTER_LIST);
	}

	public IStringSpectrum getMotorListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_MOTOR_LIST);
	}

	public IStringSpectrum getMotorGroupListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_MOTOR_GROUP_LIST);	
	}
	
	public IStringSpectrum getPseudoMotorListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_PSEUDO_MOTOR_LIST);
	}

	public IStringSpectrum getPseudoCounterListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_PSEUDO_COUNTER_LIST);
	}
	
	public IStringSpectrum getExperimentChannelListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_EXP_CHANNEL_LIST);
	}

	public IStringSpectrum getControllerClassListAttributeModel()
	{
		String attrName = getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_CTRL_CLASS_LIST;

		IStringSpectrum ret = null;
		
		if(polledAttributes != null)
			ret = (IStringSpectrum)polledAttributes.get(attrName);
		
		if(ret == null)
		{
			if(nonPolledAttributes != null)
				ret = (IStringSpectrum) nonPolledAttributes.get(attrName);
		}
		
		return ret;
	}

	public IStringSpectrum getMeasurementGroupListAttributeModel()
	{
		if(eventAttributes == null) return null;
		return (IStringSpectrum) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_MEASUREMENT_GROUP_LIST);
	}

	public IBooleanScalar getSimulationModeAttributeModel()
	{
		if(nonPolledAttributes == null) return null;
		return (IBooleanScalar) nonPolledAttributes.get(getDeviceName() + "/" + DevicePoolUtils.POOL_ATTR_SIMULATION_MODE);
	}

	protected void initAttributes() throws ConnectionException
	{
  
		super.initAttributes();		
		getControllerListAttributeModel().addListener(controllerListListener);
		getCommunicationChannelListAttributeModel().addListener(communicationChannelListListener);
		getIORegisterListAttributeModel().addListener(ioRegisterListListener);
		getMotorListAttributeModel().addListener(motorListListener);
		getMotorGroupListAttributeModel().addListener(motorGroupListListener);
		getPseudoMotorListAttributeModel().addListener(pseudoMotorListListener);
		getExperimentChannelListAttributeModel().addListener(experimentChannelListListener);
		getPseudoCounterListAttributeModel().addListener(pseudoCounterListListener);
		getMeasurementGroupListAttributeModel().addListener(measurementGroupListListener);
		
	}
	
	@Override
	protected void unregisterFromDevice(boolean keep_beacon)
	{
		if(eventAttributes != null)
		{
			getControllerListAttributeModel().removeListener(controllerListListener);
			getCommunicationChannelListAttributeModel().removeListener(communicationChannelListListener);
			getIORegisterListAttributeModel().removeListener(ioRegisterListListener);
			getMotorListAttributeModel().removeListener(motorListListener);
			getMotorGroupListAttributeModel().removeListener(motorGroupListListener);
			getPseudoMotorListAttributeModel().removeListener(pseudoMotorListListener);
			getExperimentChannelListAttributeModel().removeListener(experimentChannelListListener);
			getPseudoCounterListAttributeModel().removeListener(pseudoCounterListListener);
			getMeasurementGroupListAttributeModel().removeListener(measurementGroupListListener);
		}
		
		super.unregisterFromDevice(keep_beacon);
	}

	@Override
	public boolean equals(Object obj) 
	{
		if(!(obj instanceof DevicePool))
			return false;
		
		return super.equals(obj);
	}
	
	public SardanaDevice getSardanaDevice(String name)
	{
		SardanaDevice ret = getMotor(name);
		if(ret != null)
			return ret;
		
		ret = getPseudoMotor(name);
		if(ret != null)
			return ret;

		ret = getMotorGroup(name);
		if(ret != null)
			return ret;

		ret = getExperimentChannel(name);
		if(ret != null)
			return ret;

		ret = getPseudoCounter(name);
		if(ret != null)
			return ret;
		
		ret = getMeasurementGroup(name);
		
		return ret;
	}

	public void initController(String ctrlName) throws DevFailed
	{
		DeviceData data = new DeviceData();
		data.insert(ctrlName);
		device.command_inout(DevicePoolUtils.POOL_CMD_INIT_CONTROLLER,data);
	}

	public void initControllers(List<String> ctrlNames) throws DevFailed
	{
		for(String ctrlName : ctrlNames)
		{
			initController(ctrlName);
		}
	}
	
	public void reloadControllerFile(String fileName) throws DevFailed
	{
		DeviceData data = new DeviceData();
		data.insert(fileName);
		device.command_inout(DevicePoolUtils.POOL_CMD_RELOAD_CONTROLLER_CODE,data);
	}

	public void reloadControllerFiles(List<String> fileNames) throws DevFailed
	{
		for(String fileName : fileNames)
		{
			reloadControllerFile(fileName);
		}
	}
	
	// Controller methods -------------------------------------------
	public void addController(Controller ctrl) 
	{
		synchronized (controllers)
		{
			controllers.add(ctrl);
		}
	}
	
	public boolean hasController(Controller ctrl) 
	{
		return controllers.contains(ctrl);
	}
	
	public Controller getController(String ctrlName) 
	{
		synchronized (controllers)
		{
			for (Controller ctrlElem : controllers)
				// TODO: remove igoneCase comparison
				if (ctrlElem.getName().equalsIgnoreCase(ctrlName))
					return ctrlElem;
			return null;
		}
	}
	
	public void setControllers(List<Controller> controllers) 
	{
		this.controllers = Collections.synchronizedList(controllers);
		
		IStringSpectrum attrModel = getControllerListAttributeModel(); 
		
		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		
		for(IStringSpectrumListener listener : controllerListListeners)
			listener.stringSpectrumChange(evt);
	}
	
	public List<Controller> getControllers()
	{
		return Collections.unmodifiableList(this.controllers);
	}
	
	public List<Controller> getMotorControllers()
	{
		List<Controller> ret = new ArrayList<Controller>();
		for(Controller ctrl : getControllers())
			if(ctrl.getType() == ControllerType.Motor)
				ret.add(ctrl);
		return ret;
	}
	
	public void clearControllers()
	{
		synchronized (controllers)
		{
			this.controllers.clear();
		}
	}
	
	/**
	 * 
	 * @param newControllers
	 * @return the deleted controllers
	 */
	public boolean updateControllers(List<Controller> newControllers) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted controllers
		//-------------------------
		ArrayList<Controller> deletedControllers = new ArrayList<Controller>();
		for(Controller oldCtrl : controllers)
			if(!newControllers.contains(oldCtrl))
				deletedControllers.add(oldCtrl);
		
		synchronized (controllers)
		{
			controllers.removeAll(deletedControllers);
		}
		
		change = deletedControllers.size() != 0;
		
		//-------------------------
		//Add the new controllers
		//-------------------------
		ArrayList<Controller> addedControllers = new ArrayList<Controller>();
		for(Controller newCtrl : newControllers)
			if(!controllers.contains(newCtrl))
				addedControllers.add(newCtrl);
		controllers.addAll(addedControllers);
		
		change |= addedControllers.size() != 0;
		
		if(!change)
			return false;
		
		//Update motors with pending controllers
	
		synchronized (motors)
		{
			for(Motor motor : motors)
				updateMotorController(motor);
		}

		updateControllerMotors();
		
		return true;
	}
	
	private void updateControllerMotors()
	{
		synchronized (controllers)
		{
			for(Controller ctrl : controllers)
				ctrl.setElements( findControllerMotors(ctrl) );
		}
	}
	
	private List<SardanaDevice> findControllerMotors(Controller ctrl)
	{
		ArrayList<SardanaDevice> ret = new ArrayList<SardanaDevice>();
		for(Motor motor : motors)
		{
			Controller motorCtrl = motor.getController();
			
			if(motorCtrl != null && ctrl.equals(motorCtrl))
				ret.add(motor);
		}	
		return ret;
	}	
	
	private void updateMotorController(Motor motor)
	{
		if(!motor.hasPendingControllerId())
			return;
	
		String[] motorData = motor.getDeviceName().split("/"); 
		Controller ctrl = getController(motorData[1]);
		motor.setController(ctrl);
	}
	
	// MotorGroup methods -------------------------------------------
	public List<MotorGroup> getMotorGroups() 
	{
		return Collections.unmodifiableList(motorGroups);
	}

	public void setMotorGroups(List<MotorGroup> motorGroups) 
	{
		this.motorGroups = motorGroups;
		
		IStringSpectrum attrModel = getMotorGroupListAttributeModel(); 
		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);


		for(IStringSpectrumListener listener : motorGroupListListeners)
			listener.stringSpectrumChange(evt);
		
	}

	public void addMotorGroup(MotorGroup motorGroup) 
	{
		synchronized(motorGroups)
		{
			motorGroups.add(motorGroup);
		}
	}
	
	public boolean hasMotorGroup(MotorGroup motorGroup) 
	{
		return motorGroups.contains(motorGroup);
	}
	
	public MotorGroup getMotorGroupByDeviceName(String motorGroupDeviceName) 
	{
		synchronized(motorGroups)
		{
			for(MotorGroup motorGroupElem : motorGroups)
				if(motorGroupElem.getDeviceName().equals(motorGroupDeviceName))
					return motorGroupElem;
		}
		return null;
	}
	
	public MotorGroup getMotorGroup(String name)
	{
		synchronized(motorGroups)
		{		
			for(MotorGroup motorGroupElem : motorGroups)
				if(motorGroupElem.getName().equals(name))
					return motorGroupElem;
		}
		return null;
	}
	
	public boolean containsMotorGroup(String name)
	{
		return getMotorGroup(name) != null;
	}
	
	public void clearMotorGroups()
	{
		synchronized(motorGroups)
		{
			motorGroups.clear();
		}
	}
	
	/**
	 * 
	 * @param newMotorGroups
	 * @return the deleted motorGroup groups
	 */
	public boolean updateMotorGroups(List<MotorGroup> newMotorGroups) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted MotorGroups
		//-------------------------
		ArrayList<MotorGroup> deletedMotorGroups = new ArrayList<MotorGroup>();
		
		synchronized (motorGroups)
		{
			for (MotorGroup oldMotorGroup : motorGroups)
				if (!newMotorGroups.contains(oldMotorGroup))
				{
					deletedMotorGroups.add(oldMotorGroup);
				}
			motorGroups.removeAll(deletedMotorGroups);
		}
		
		change = deletedMotorGroups.size() != 0;
		
		//-------------------------
		//Add the new Motors Groups
		//-------------------------
		ArrayList<MotorGroup> addedMotorGroups = new ArrayList<MotorGroup>();
		for(MotorGroup newMotorGroup : newMotorGroups)
			if(!motorGroups.contains(newMotorGroup))
				addedMotorGroups.add(newMotorGroup);
		
		synchronized(motorGroups)
		{
			motorGroups.addAll(addedMotorGroups);
		}
		
		change |= addedMotorGroups.size() != 0;
		
		return change;
	}


	// Communication channel methods -------------------------------------------
	public List<CommunicationChannel> getCommunicationChannels() 
	{
		return communicationChannels;
	}

	public void setCommunicationChannels(List<CommunicationChannel> communicationChannels) 
	{
		this.communicationChannels = Collections.synchronizedList(communicationChannels);
		
		IStringSpectrum attrModel = getCommunicationChannelListAttributeModel();

		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		for(IStringSpectrumListener listener : controllerClassListListeners)
			listener.stringSpectrumChange(evt);	
	}

	public void clearCommunicationChannels()
	{
		synchronized (communicationChannels)
		{
			communicationChannels.clear();
		}
	}
	
	public void addCommunicationChannel(CommunicationChannel communicationChannel) 
	{
		synchronized (communicationChannels)
		{
			communicationChannels.add(communicationChannel);	
		}
	}
	
	public boolean hasCommunicationChannel(CommunicationChannel communicationChannel) 
	{
		return communicationChannels.contains(communicationChannel);
	}

	public CommunicationChannel getCommunicationChannel(String communicationChannel) 
	{
		synchronized (communicationChannels)
		{
			for (CommunicationChannel communicationChannelElem : communicationChannels)
				if (communicationChannelElem.getName().equals(communicationChannel))
					return communicationChannelElem;
		}
		return null;
	}
	
	public boolean containsCommunicationChannel(String communicationChannel)
	{
		return getCommunicationChannel(communicationChannel) != null;
	}	

	public CommunicationChannel getCommunicationChannelByDeviceName(String communicationChannelDeviceName) 
	{
		synchronized (communicationChannels)
		{
			for(CommunicationChannel communicationChannelElem : communicationChannels)
				if(communicationChannelElem.getDeviceName().equals(communicationChannelDeviceName))
					return communicationChannelElem;
		}
		return null;
	}
	
	/**
	 * 
	 * @param newMotors
	 * @return the deleted motors
	 */
	public boolean updateCommunicationChannels(List<CommunicationChannel> newCommunicationChannels) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted CommunicationChannels
		//-------------------------
		ArrayList<CommunicationChannel> deletedCommunicationChannels = new ArrayList<CommunicationChannel>();
		
		synchronized (communicationChannels)
		{
			for(CommunicationChannel oldCommunicationChannel : communicationChannels)
				if(!newCommunicationChannels.contains(oldCommunicationChannel))
					deletedCommunicationChannels.add(oldCommunicationChannel);
			communicationChannels.removeAll(deletedCommunicationChannels);

		}		
		//Update information of the Controller
		for(CommunicationChannel removedCommunicationChannel : deletedCommunicationChannels)
		{
			synchronized (controllers)
			{
				for(Controller ctrl : controllers)
				{
					int pos = ctrl.getElements().indexOf(removedCommunicationChannel);
					
					if(pos >= 0)
						ctrl.getElements().remove(pos);
				}
			}
		}
		change = deletedCommunicationChannels.size() != 0;
		
		//-------------------------
		//Add the new CommunicationChannels
		//-------------------------
		ArrayList<CommunicationChannel> addedCommunicationChannels = new ArrayList<CommunicationChannel>();
		for(CommunicationChannel newCommunicationChannel : newCommunicationChannels)
			if(!communicationChannels.contains(newCommunicationChannel))
				addedCommunicationChannels.add(newCommunicationChannel);
		
		synchronized (communicationChannels)
		{
			communicationChannels.addAll(addedCommunicationChannels);	
		}
		
		//Update information of the Controller
		for(CommunicationChannel addedCommunicationChannel : addedCommunicationChannels)
		{
			Controller ctrl = addedCommunicationChannel.getController();
			if(ctrl != null)
				ctrl.addElement(addedCommunicationChannel);
			
			//In principle we don't need to do the same for the MotorGroup and PseudoMotor
			//because if a new Motor is created it initially does not belong
			//to a motorGroup group or a pseudo motor
		}
		change |= addedCommunicationChannels.size() != 0;
		
		return change;
	}
	
	

	// IORegister methods -------------------------------------------
	public List<IORegister> getIORegisters() 
	{
		return ioRegisters;
	}

	public void setIORegisters(List<IORegister> ioRegisters) 
	{
		this.ioRegisters = Collections.synchronizedList(ioRegisters);
		IStringSpectrum attrModel = getIORegisterListAttributeModel();

		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		for(IStringSpectrumListener listener : controllerClassListListeners)
			listener.stringSpectrumChange(evt);	
	}

	public void clearIORegisters()
	{
		synchronized (ioRegisters)
		{
			ioRegisters.clear();
		}
	}
	
	public void addIORegister(IORegister ioRegister) 
	{
		synchronized (ioRegisters)
		{
			ioRegisters.add(ioRegister);	
		}
	}
	
	public boolean hasIORegister(IORegister ioRegister) 
	{
		return ioRegisters.contains(ioRegister);
	}

	public IORegister getIORegister(String ioRegister) 
	{
		synchronized (ioRegisters)
		{
			for (IORegister ioRegisterElem : ioRegisters)
				if (ioRegisterElem.getName().equals(ioRegister))
					return ioRegisterElem;
		}
		return null;
	}
	
	public boolean containsIORegister(String ioRegister)
	{
		return getIORegister(ioRegister) != null;
	}	

	public IORegister getIORegisterByDeviceName(String ioRegisterDeviceName) 
	{
		synchronized (ioRegisters)
		{
			for(IORegister ioRegisterElem : ioRegisters)
				if(ioRegisterElem.getDeviceName().equals(ioRegisterDeviceName))
					return ioRegisterElem;
		}
		return null;
	}
	

	public boolean updateIORegisters(List<IORegister> newIORegisters) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted IORegisters
		//-------------------------
		ArrayList<IORegister> deletedIORegisters = new ArrayList<IORegister>();
		
		synchronized (ioRegisters)
		{
			for(IORegister oldIORegister : ioRegisters)
				if(!newIORegisters.contains(oldIORegister))
					deletedIORegisters.add(oldIORegister);
			ioRegisters.removeAll(deletedIORegisters);

		}		
		//Update information of the Controller
		for(IORegister removedIORegister : deletedIORegisters)
		{
			synchronized (controllers)
			{
				for(Controller ctrl : controllers)
				{
					int pos = ctrl.getElements().indexOf(removedIORegister);
					
					if(pos >= 0)
						ctrl.getElements().remove(pos);
				}
			}
		}
		change = deletedIORegisters.size() != 0;
		
		//-------------------------
		//Add the new IORegisters
		//-------------------------
		ArrayList<IORegister> addedIORegisters = new ArrayList<IORegister>();
		for(IORegister newIORegister : newIORegisters)
			if(!ioRegisters.contains(newIORegister))
				addedIORegisters.add(newIORegister);
		
		synchronized (ioRegisters)
		{
			ioRegisters.addAll(addedIORegisters);	
		}
		
		//Update information of the Controller
		for(IORegister addedIORegister : addedIORegisters)
		{
			Controller ctrl = addedIORegister.getController();
			if(ctrl != null)
				ctrl.addElement(addedIORegister);
			
			//In principle we don't need to do the same for the MotorGroup and PseudoMotor
			//because if a new Motor is created it initially does not belong
			//to a motorGroup group or a pseudo motor
		}
		change |= addedIORegisters.size() != 0;
		
		return change;
	}
	
	
	// Motor methods -------------------------------------------
	public List<Motor> getMotors() 
	{
		return motors;
	}

	public void setMotors(List<Motor> motors) 
	{
		this.motors = Collections.synchronizedList(motors);
		
		IStringSpectrum attrModel = getMotorListAttributeModel(); 
		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);
		
		for(IStringSpectrumListener listener : motorListListeners)
			listener.stringSpectrumChange(evt);

	}

	public void clearMotors()
	{
		synchronized (motors)
		{
			motors.clear();
		}
	}
	
	public void addMotor(Motor motor) 
	{
		synchronized (motors)
		{
			motors.add(motor);	
		}
	}
	
	public boolean hasMotor(Motor motor) 
	{
		return motors.contains(motor);
	}

	public Motor getMotor(String motor) 
	{
		synchronized (motors)
		{
			for (Motor motorElem : motors)
				if (motorElem.getName().equals(motor))
					return motorElem;
		}
		return null;
	}
	
	public boolean containsMotor(String motor)
	{
		return getMotor(motor) != null;
	}	

	public Motor getMotorByDeviceName(String motorDeviceName) 
	{
		synchronized (motors)
		{
					for(Motor motorElem : motors)
			if(motorElem.getDeviceName().equals(motorDeviceName))
				return motorElem;
		}
		return null;
	}
	
	/**
	 * 
	 * @param newMotors
	 * @return the deleted motors
	 */
	public boolean updateMotors(List<Motor> newMotors) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted Motors
		//-------------------------
		ArrayList<Motor> deletedMotors = new ArrayList<Motor>();
		
		synchronized (motors)
		{
			for(Motor oldMotor : motors)
				if(!newMotors.contains(oldMotor))
					deletedMotors.add(oldMotor);
			motors.removeAll(deletedMotors);

		}		
		//Update information of the Controller, MotorGroup and Pseudo Motors
		for(Motor removedMotor : deletedMotors)
		{
			synchronized (controllers)
			{
				for(Controller ctrl : controllers)
				{
					int pos = ctrl.getElements().indexOf(removedMotor);
					
					if(pos >= 0)
						ctrl.getElements().remove(pos);
				}
			}
			
			/*
			synchronized (controllers)
			{
				for (MotorGroup motorGroup : controllers)
				{
					int pos = motorGroup.getMotors().indexOf(removedMotor);

					if (pos >= 0)
						motorGroup.getMotors().remove(pos);
				}
			}
			*/
			
			/* TODO: Do PseudoMotor!
			for(PseudoMotor pseudoMotor : pseudoMotors)
			{
				int pos = pseudoMotor.getMotors().indexOf(removedMotor);
				
				if(pos >= 0)
					pseudoMotor.getMotors().remove(pos);
			}
			*/			
		}
		change = deletedMotors.size() != 0;
		
		//-------------------------
		//Add the new Motors
		//-------------------------
		ArrayList<Motor> addedMotors = new ArrayList<Motor>();
		for(Motor newMotor : newMotors)
			if(!motors.contains(newMotor))
				addedMotors.add(newMotor);
		
		synchronized (motors)
		{
			motors.addAll(addedMotors);	
		}
		
		//Update information of the Controller
		for(Motor addedMotor : addedMotors)
		{
			Controller ctrl = addedMotor.getController();
			if(ctrl != null)
				ctrl.addElement(addedMotor);
			
			//In principle we don't need to do the same for the MotorGroup and PseudoMotor
			//because if a new Motor is created it initially does not belong
			//to a motorGroup group or a pseudo motor
		}
		change |= addedMotors.size() != 0;
		
		return change;
	}
	
	// Pseudo Motor methods -------------------------------------------
	public List<PseudoMotor> getPseudoMotors() 
	{
		return Collections.unmodifiableList(pseudoMotors);
	}

	public void setPseudoMotors(List<PseudoMotor> pseudomotor) 
	{
		this.pseudoMotors = pseudomotor;
		
		IStringSpectrum attrModel = getPseudoMotorListAttributeModel(); 
		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		
		for(IStringSpectrumListener listener : pseudoMotorListListeners)
			listener.stringSpectrumChange(evt);

	}

	public void addPseudoMotor(PseudoMotor pseudomotor) 
	{
		synchronized(pseudoMotors)
		{
			pseudoMotors.add(pseudomotor);
		}
	}
	
	public boolean hasPseudoMotor(PseudoMotor pseudomotor) 
	{
		return pseudoMotors.contains(pseudomotor);
	}
	
	public PseudoMotor getPseudoMotorByDeviceName(String pseudoMotorDeviceName) 
	{
		synchronized(pseudoMotors)
		{		
			for(PseudoMotor pseudoMotor : pseudoMotors)
				if(pseudoMotor.getDeviceName().equals(pseudoMotorDeviceName))
					return pseudoMotor;
		}
		return null;
	}	
	
	public PseudoMotor getPseudoMotor(String name)
	{
		synchronized(pseudoMotors)
		{
			for(PseudoMotor pseudoMotor : pseudoMotors)
				if(pseudoMotor.getName().equals(name))
					return pseudoMotor;
		}
		return null;
	}
	
	public boolean updatePseudoMotors(List<PseudoMotor> newPseudoMotors) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted Pseudo Motors
		//-------------------------
		ArrayList<PseudoMotor> deletedPseudoMotors = new ArrayList<PseudoMotor>();
		synchronized(pseudoMotors)
		{
			for(PseudoMotor oldPseudoMotor : pseudoMotors)
				if(!newPseudoMotors.contains(oldPseudoMotor))
					deletedPseudoMotors.add(oldPseudoMotor);
		
			pseudoMotors.removeAll(deletedPseudoMotors);	
		}
		
		change = deletedPseudoMotors.size() != 0;
		
		//-------------------------
		//Add the new Pseudo Motors
		//-------------------------
		ArrayList<PseudoMotor> addedPseudoMotors = new ArrayList<PseudoMotor>();
		for(PseudoMotor newPseudoMotor : newPseudoMotors)
			if(!pseudoMotors.contains(newPseudoMotor))
				addedPseudoMotors.add(newPseudoMotor);
		
		synchronized(pseudoMotors)
		{
			pseudoMotors.addAll(addedPseudoMotors);
		}
		
		change |= addedPseudoMotors.size() != 0;
		
		return change;
	}	
	
	
	// Pseudo counter methods -------------------------------------------
	public List<PseudoCounter> getPseudoCounters() 
	{
		return Collections.unmodifiableList(pseudoCounters);
	}

	public void setPseudoCounters(List<PseudoCounter> pseudocounter) 
	{
		this.pseudoCounters = pseudocounter;
		
		IStringSpectrum attrModel = getPseudoCounterListAttributeModel(); 
		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		
		for(IStringSpectrumListener listener : pseudoCounterListListeners)
			listener.stringSpectrumChange(evt);

	}

	public void addPseudoCounter(PseudoCounter pseudoCounter) 
	{
		synchronized(pseudoCounters)
		{
			pseudoCounters.add(pseudoCounter);
		}
	}
	
	public boolean hasPseudoCounter(PseudoCounter pseudoCounter) 
	{
		return pseudoCounters.contains(pseudoCounter);
	}
	
	public PseudoCounter getPseudoCounterByDeviceName(String pseudoCounterDeviceName) 
	{
		synchronized(pseudoCounters)
		{		
			for(PseudoCounter pseudoCounter : pseudoCounters)
				if(pseudoCounter.getDeviceName().equals(pseudoCounterDeviceName))
					return pseudoCounter;
		}
		return null;
	}	
	
	public PseudoCounter getPseudoCounter(String name)
	{
		synchronized(pseudoCounters)
		{
			for(PseudoCounter pseudoCounter : pseudoCounters)
				if(pseudoCounter.getName().equals(name))
					return pseudoCounter;
		}
		return null;
	}
	
	public boolean updatePseudoCounters(List<PseudoCounter> newPseudoCounters) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted Pseudo Motors
		//-------------------------
		ArrayList<PseudoCounter> deletedPseudoCounters = new ArrayList<PseudoCounter>();
		synchronized(pseudoCounters)
		{
			for(PseudoCounter oldPseudoCounter : pseudoCounters)
				if(!newPseudoCounters.contains(oldPseudoCounter))
					deletedPseudoCounters.add(oldPseudoCounter);
		
			pseudoMotors.removeAll(deletedPseudoCounters);	
		}
		
		change = deletedPseudoCounters.size() != 0;
		
		//-------------------------
		//Add the new Pseudo Counters
		//-------------------------
		ArrayList<PseudoCounter> addedPseudoCounters = new ArrayList<PseudoCounter>();
		for(PseudoCounter newPseudoCounter : newPseudoCounters)
			if(!pseudoCounters.contains(newPseudoCounter))
				addedPseudoCounters.add(newPseudoCounter);
		
		synchronized(pseudoCounters)
		{
			pseudoCounters.addAll(addedPseudoCounters);
		}
		
		change |= addedPseudoCounters.size() != 0;
		
		return change;
	}	
	
	// Experiment Channel methods -------------------------------------------

	public List<CounterTimer> getCounterTimers()
	{
		ArrayList<CounterTimer> ret = new ArrayList<CounterTimer>();
		for(ExperimentChannel channel : experimentChannels)
			if(channel instanceof CounterTimer)
				ret.add((CounterTimer)channel);
		return ret;
	}

	public List<ZeroDExpChannel> getZeroDExpChannels()
	{
		ArrayList<ZeroDExpChannel> ret = new ArrayList<ZeroDExpChannel>();
		for(ExperimentChannel channel : experimentChannels)
			if(channel instanceof ZeroDExpChannel)
				ret.add((ZeroDExpChannel)channel);
		return ret;
	}

    public List<OneDExpChannel> getOneDExpChannels()
	{
		ArrayList<OneDExpChannel> ret = new ArrayList<OneDExpChannel>();
		for(ExperimentChannel channel : experimentChannels)
			if(channel instanceof OneDExpChannel)
				ret.add((OneDExpChannel)channel);
		return ret;
	}

    public List<TwoDExpChannel> getTwoDExpChannels()
	{
		ArrayList<TwoDExpChannel> ret = new ArrayList<TwoDExpChannel>();
		for(ExperimentChannel channel : experimentChannels)
			if(channel instanceof TwoDExpChannel)
				ret.add((TwoDExpChannel)channel);
		return ret;
	}

	public List<ExperimentChannel> getExperimentChannels() 
	{
		return experimentChannels;
	}

	public void setExperimentChannels(List<ExperimentChannel> channels) 
	{
		this.experimentChannels = Collections.synchronizedList(channels);
		
		IStringSpectrum attrModel = getExperimentChannelListAttributeModel(); 

		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		
		for(IStringSpectrumListener listener : experimentChannelListListeners)
			listener.stringSpectrumChange(evt);
		
	}

	public void clearExperimentChannels()
	{
		synchronized (experimentChannels)
		{
			experimentChannels.clear();
		}
	}
	
	public void addExperimentChannel(ExperimentChannel channel) 
	{
		synchronized (experimentChannels)
		{
			experimentChannels.add(channel);	
		}
	}
	
	public boolean hasExperimentChannel(ExperimentChannel channel) 
	{
		return experimentChannels.contains(channel);
	}

	public ExperimentChannel getExperimentChannel(String channel) 
	{
		synchronized (experimentChannels)
		{
			for (ExperimentChannel channelElem : experimentChannels)
				if (channelElem.getName().equals(channel))
					return channelElem;
		}
		return null;
	}
	
	public boolean containsExperimentChannel(String channel)
	{
		return getExperimentChannel(channel) != null;
	}	

	public ExperimentChannel getExperimentChannelByDeviceName(String channelDeviceName) 
	{
		synchronized (experimentChannels)
		{
					for(ExperimentChannel channelElem : experimentChannels)
			if(channelElem.getDeviceName().equals(channelDeviceName))
				return channelElem;
		}
		return null;
	}
	
	/**
	 * 
	 * @param newChannels
	 * @return the deleted channels
	 */
	public boolean updateExperimentChannels(List<ExperimentChannel> newChannels) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted ExperimentChannels
		//-------------------------
		ArrayList<ExperimentChannel> deletedExperimentChannels = new ArrayList<ExperimentChannel>();
		
		synchronized (experimentChannels)
		{
			for(ExperimentChannel oldChannel : experimentChannels)
				if(!newChannels.contains(oldChannel))
					deletedExperimentChannels.add(oldChannel);
			experimentChannels.removeAll(deletedExperimentChannels);

		}		
		//Update information of the Controller, MotorGroup and Pseudo Motors
		for(ExperimentChannel removedChannel : deletedExperimentChannels)
		{
			synchronized (controllers)
			{
				for(Controller ctrl : controllers)
				{
					int pos = ctrl.getElements().indexOf(removedChannel);
					
					if(pos >= 0)
						ctrl.getElements().remove(pos);
				}
			}
			
			/*
			synchronized (controllers)
			{
				for (MotorGroup motorGroup : controllers)
				{
					int pos = motorGroup.getMotors().indexOf(removedMotor);

					if (pos >= 0)
						motorGroup.getMotors().remove(pos);
				}
			}
			*/
			
			/* TODO: Do PseudoMotor!
			for(PseudoMotor pseudoMotor : pseudoMotors)
			{
				int pos = pseudoMotor.getMotors().indexOf(removedMotor);
				
				if(pos >= 0)
					pseudoMotor.getMotors().remove(pos);
			}
			*/			
		}
		change = deletedExperimentChannels.size() != 0;
		
		//-------------------------
		//Add the new Channels
		//-------------------------
		ArrayList<ExperimentChannel> addedChannels = new ArrayList<ExperimentChannel>();
		for(ExperimentChannel newChannel : newChannels)
			if(!experimentChannels.contains(newChannel))
				addedChannels.add(newChannel);
		
		synchronized (experimentChannels)
		{
			experimentChannels.addAll(addedChannels);	
		}
		
		//Update information of the Controller
		for(ExperimentChannel addedChannel : addedChannels)
		{
			Controller ctrl = addedChannel.getController();
			if(ctrl != null)
				ctrl.addElement(addedChannel);
			
			//In principle we don't need to do the same for the MotorGroup and PseudoMotor
			//because if a new Motor is created it initially does not belong
			//to a motorGroup group or a pseudo motor
		}
		change |= addedChannels.size() != 0;
		
		return change;
	}
	
	// MeasurementGroup methods -------------------------------------------
	public List<MeasurementGroup> getMeasurementGroups() 
	{
		return Collections.unmodifiableList(measurementGroups);
	}

	public void setMeasurementGroups(List<MeasurementGroup> measurementGroups) 
	{
		this.measurementGroups = measurementGroups;
		
		IStringSpectrum attrModel = getMeasurementGroupListAttributeModel(); 
		
		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		
		for(IStringSpectrumListener listener : measurementGroupListListeners)
			listener.stringSpectrumChange(evt);
	}

	public void addMeasurementGroup(MeasurementGroup measurementGroup) 
	{
		synchronized(measurementGroups)
		{
			measurementGroups.add(measurementGroup);
		}
	}
	
	public boolean hasMeasurementGroup(MeasurementGroup measurementGroup) 
	{
		return measurementGroups.contains(measurementGroup);
	}
	
	public MeasurementGroup getMeasurementGroupByDeviceName(String measurementGroupDeviceName) 
	{
		synchronized(measurementGroups)
		{
			for(MeasurementGroup measurementGroupElem : measurementGroups)
				if(measurementGroupElem.getDeviceName().equals(measurementGroupDeviceName))
					return measurementGroupElem;
		}
		return null;
	}
	
	public MeasurementGroup getMeasurementGroup(String name)
	{
		synchronized(measurementGroups)
		{		
			for(MeasurementGroup measurementGroupElem : measurementGroups)
				if(measurementGroupElem.getName().equals(name))
					return measurementGroupElem;
		}
		return null;
	}
	
	public boolean containsMeasurementGroup(String name)
	{
		return getMeasurementGroup(name) != null;
	}
	
	public void clearMeasurementGroups()
	{
		synchronized(measurementGroups)
		{
			measurementGroups.clear();
		}
	}
	
	/**
	 * 
	 * @param newMotorGroups
	 * @return the deleted motorGroup groups
	 */
	public boolean updateMeasurementGroups(List<MeasurementGroup> newMeasurementGroups) 
	{
		boolean change = false;
		
		//-------------------------
		//Check deleted MeasurementGroups
		//-------------------------
		ArrayList<MeasurementGroup> deletedMeasurementGroups = new ArrayList<MeasurementGroup>();
		
		synchronized (measurementGroups)
		{
			for (MeasurementGroup oldMeasurementGroup : measurementGroups)
				if (!newMeasurementGroups.contains(oldMeasurementGroup))
				{
					deletedMeasurementGroups.add(oldMeasurementGroup);
				}
			measurementGroups.removeAll(deletedMeasurementGroups);
		}
		
		//Update information of the Channel
		for(MeasurementGroup removedMeasurementGroup : deletedMeasurementGroups)
		{
			
			synchronized (experimentChannels)
			{
				for (ExperimentChannel channel : experimentChannels)
				{
					channel.removeMeasurementGroup(removedMeasurementGroup);
				}
			}	
		}
		change = deletedMeasurementGroups.size() != 0;
		
		//-------------------------
		//Add the new Measurement Groups
		//-------------------------
		ArrayList<MeasurementGroup> addedMeasurementGroups = new ArrayList<MeasurementGroup>();
		for(MeasurementGroup newMeasurementGroup : newMeasurementGroups)
			if(!measurementGroups.contains(newMeasurementGroup))
				addedMeasurementGroups.add(newMeasurementGroup);
		
		synchronized(measurementGroups)
		{
			measurementGroups.addAll(addedMeasurementGroups);
		
			//Update information in the channels that belong to these new measurementGroup
			for(MeasurementGroup measurementGroup : measurementGroups)
				for(ExperimentChannel channel : measurementGroup.getChannels())
					channel.addMeasurementGroup(measurementGroup);
		}
		
		change |= addedMeasurementGroups.size() != 0;
		
		return change;
	}

	// Controller Class methods -------------------------------------------
	
	public List<ControllerType> getControllerTypes()
	{
		ArrayList<ControllerType> ret = new ArrayList<ControllerType>();
		for(ControllerType type : ControllerType.values())
		{
			if(type != ControllerType.InvalidControllerType)
				ret.add(type);
		}
		return ret;
	}
	
	public List<String> getControllerFilesNames(ControllerType type) 
	{
		return new ArrayList<String>(controllerClasses.get(type).keySet());
	}

	public void addControllerFileName(ControllerType type, String controllerFileName) 
	{
		HashMap<String, List<ControllerClass>> typeFiles = controllerClasses.get(type);
		if(!typeFiles.containsKey(controllerFileName))
			typeFiles.put(controllerFileName, new ArrayList<ControllerClass>());
	}
	
	public boolean hasControllerFileName(ControllerType type, String controllerFileName) 
	{
		HashMap<String, List<ControllerClass>> typeFiles = controllerClasses.get(type);
		return typeFiles.containsKey(controllerFileName);
	}
	
	public HashMap<ControllerType, HashMap<String, List<ControllerClass>>> getControllerClasses()
	{
		return controllerClasses;
	}
	
	public List<ControllerClass> getControllerClassesAsList() 
	{
		List<ControllerClass> ret = new ArrayList<ControllerClass>();
		
		for(HashMap<String, List<ControllerClass>> classes_in_type : controllerClasses.values())
		{
			for(List<ControllerClass> classes_in_file : classes_in_type.values())
			{
				ret.addAll(classes_in_file);
			}
		}
		return ret;
	}
	
	public List<ControllerClass> getControllerClasses(String controllerFileName)
	{
		for(ControllerType type : controllerClasses.keySet())
		{
			List<ControllerClass> classes = getControllerClasses(type,controllerFileName);
			if(classes != null)
				return classes;
		}
		return null;
	}	
	
	public List<ControllerClass> getControllerClasses(ControllerType type, String controllerFileName)
	{
		HashMap<String, List<ControllerClass>> typeFiles = controllerClasses.get(type);
		return typeFiles.get(controllerFileName);
	}

	public void setControllerClasses(List<ControllerClass> controllerclasses) 
	{
		for(HashMap<String, List<ControllerClass>> typeCtrlsClasses : controllerClasses.values())
			typeCtrlsClasses.clear();
		
		for(ControllerClass ctrlClass : controllerclasses)
			addControllerClass(ctrlClass);

		for(Controller ctrl : controllers)
		{
			ControllerClass ctrlClass = 
				getControllerClassByName(ctrl.getType(), 
						                 ctrl.getFileName(), 
						                 ctrl.getClassName());
			
			ctrl.setCtrlClass(ctrlClass);
		}
		
		IStringSpectrum attrModel = getControllerClassListAttributeModel();

		StringSpectrumEvent evt;
		if(attrModel != null)
			evt = new StringSpectrumEvent(attrModel,attrModel.getStringSpectrumValue(),0);
		else 
			evt = new PoolInternalStringSpectrumEvent(this);

		for(IStringSpectrumListener listener : controllerClassListListeners)
			listener.stringSpectrumChange(evt);
		
	}

	/**
	 * 
	 * @param ctrlClass
	 * @return true if the class already exists or false otherwise
	 */
	public void addControllerClass(ControllerClass ctrlClass) 
	{		
		String fileName = ctrlClass.getFileName();
		HashMap<String, List<ControllerClass>> typeFiles = controllerClasses.get(ctrlClass.getType());
		List<ControllerClass> fileClasses = typeFiles.get(fileName);
		
		if(fileClasses == null)
		{
			fileClasses = new ArrayList<ControllerClass>();
			typeFiles.put(fileName,fileClasses);
		}
		
		if(!fileClasses.contains(ctrlClass))
			fileClasses.add(ctrlClass);
	}
	
	public boolean hasControllerClass(ControllerClass ctrlClass) 
	{
		HashMap<String, List<ControllerClass>> typeFiles = controllerClasses.get(ctrlClass.getType());
		List<ControllerClass> moduleClasses = typeFiles.get(ctrlClass.getFileName());
		
		if(moduleClasses == null)
			return false;
		
		return moduleClasses.contains(ctrlClass);
	}

	public ControllerClass getControllerClassByName(ControllerType type, String fileName, String className)
	{
		if(type == ControllerType.InvalidControllerType)
			return null;
		
		HashMap<String, List<ControllerClass>> typeFiles = controllerClasses.get(type);
		
		List<ControllerClass> fileClasses = typeFiles.get(fileName);
		
		if(fileClasses == null)
			return null;
	
		for(ControllerClass ctrlClass : fileClasses)
		{
			if(ctrlClass.getClassName().equals(className))
				return ctrlClass;
		}
		return null;
	}

	public ControllerClass getControllerClassByName(String fileName, String className)
	{
		for(HashMap<String, List<ControllerClass>> typeFiles : controllerClasses.values())
		{
			List<ControllerClass> fileClasses = typeFiles.get(fileName);
		
			if(fileClasses == null)
				continue;
		
			for(ControllerClass ctrlClass : fileClasses)
			{
				if(ctrlClass.getClassName().equals(className))
					return ctrlClass;
			}
		}
		return null;
	}
	
	
	
	public ControllerClass getControllerClassByName(String controllerClassName) 
	{
		String modClass[] = controllerClassName.split("\\.");
		
		if(modClass.length < 2)
			return null;
		
		// Format modulename.className
		if(modClass.length == 2)
		{
			ControllerClass ret = getControllerClassByName(modClass[0] + ".la", modClass[1]);
			
			if(ret == null)
				ret = getControllerClassByName(modClass[0] + ".py", modClass[1]);
			
			return ret;
		}
		// Format fileName.className
		else 
		{
			return getControllerClassByName(modClass[0] + "." + modClass[1], modClass[2]); 
		}
	}
		
	public boolean containsControllerClass(String controllerClassName)
	{
		return getControllerClassByName(controllerClassName) != null;
	}	

	public void addControllerClassListListener(IStringSpectrumListener listener)
	{
		if(controllerClassListListeners != null)
			controllerClassListListeners.add(listener);
	}
	
	public void removeControllerClassListListener(IStringSpectrumListener listener)
	{
		if(controllerClassListListeners != null)
			controllerClassListListeners.remove(listener);
	}
	
	public void addControllerListListener(IStringSpectrumListener listener)
	{
		if(controllerListListeners != null)
			controllerListListeners.add(listener);
	}
	
	public void removeControllerListListener(IStringSpectrumListener listener)
	{
		if(controllerListListeners != null)
			controllerListListeners.remove(listener);
	}
	
	protected class ControllerListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<Controller> newControllerList = new ArrayList<Controller>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] ctrlNames = utils.getControllerNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				Controller ctrl = getController(ctrlNames[i]);
				
				if(ctrl == null)
					ctrl = utils.getNewController(getPool(), data[i]);
				
				newControllerList.add(ctrl);
			}
			
			// if no change occured in the structure return
			if(getControllers().equals(newControllerList))
				return;
			
			boolean changed = updateControllers(newControllerList);

			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : controllerListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{
			//log.info("Quality changed for controller list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.info("Received error event for controller list");
		}
	}
	
	public void addCommunicationChannelListListener(IStringSpectrumListener listener)
	{
		if(communicationChannelListListeners != null)
			communicationChannelListListeners.add(listener);
	}
	
	public void removeCommunicationChannelListListener(IStringSpectrumListener listener)
	{
		if(communicationChannelListListeners != null)
			communicationChannelListListeners.remove(listener);
	}
	
	protected class CommunicationChannelListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<CommunicationChannel> newCommunicationChannelList = new ArrayList<CommunicationChannel>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] channelNames = utils.getCommunicationChannelNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				CommunicationChannel channel = getCommunicationChannel(channelNames[i]);
				
				if(channel == null) 
					channel = utils.getNewCommunicationChannel(getPool(), data[i]);
				
				newCommunicationChannelList.add(channel);
			}
			
			// if no change occured in the structure return
			if(getCommunicationChannels().equals(newCommunicationChannelList))
				return;
			
			boolean changed = updateCommunicationChannels(newCommunicationChannelList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : communicationChannelListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{
			//log.info("Quality changed for experiment channel list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("Received error event for communication channel list");
		}
	}	
	

	
	public void addIORegisterListListener(IStringSpectrumListener listener)
	{
		if(ioRegisterListListeners != null)
			ioRegisterListListeners.add(listener);
	}
	
	public void removeIORegisterListListener(IStringSpectrumListener listener)
	{
		if(ioRegisterListListeners != null)
			ioRegisterListListeners.remove(listener);
	}
	
	protected class IORegisterListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			ArrayList<IORegister> newIORegisterList = new ArrayList<IORegister>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] channelNames = utils.getIORegisterNames(data);
			for (int i = 0; i < data.length; i++)
			{
				IORegister channel = getIORegister(channelNames[i]);
				
				if(channel == null) 
					channel = utils.getNewIORegister(getPool(), data[i]);
				
				newIORegisterList.add(channel);
			}
			// if no change occured in the structure return
			if(getIORegisters().equals(newIORegisterList))
				return;
			
			boolean changed = updateIORegisters(newIORegisterList);
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : ioRegisterListListeners)
					listener.stringSpectrumChange(e);
			

		}

		public void stateChange(AttributeStateEvent e)
		{
			//log.info("Quality changed for experiment channel list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("Received error event for communication channel list");
		}
	}   


	public void addMotorListListener(IStringSpectrumListener listener)
	{
		if(motorListListeners != null)
			motorListListeners.add(listener);
	}
	
	public void removeMotorListListener(IStringSpectrumListener listener)
	{
		if(motorListListeners != null)
			motorListListeners.remove(listener);
	}
	
	protected class MotorListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<Motor> newMotorList = new ArrayList<Motor>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] motorNames = utils.getMotorNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				Motor motor = getMotor(motorNames[i]);
				
				if(motor == null) 
					motor = utils.getNewMotor(getPool(), data[i]);
				
				newMotorList.add(motor);
			}
			
			// if no change occured in the structure return
			if(getMotors().equals(newMotorList))
				return;
			
			boolean changed = updateMotors(newMotorList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : motorListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{ 
			//log.info("Quality changed for motor list: " + e.toString()+". New quality = "+ e.getState());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
			{
				log.finest("Received state error event for motor list");
				System.out.println(evt);
			}
		}
	}
	
	public void addMotorGroupListListener(IStringSpectrumListener listener)
	{
		if(motorGroupListListeners != null)
			motorGroupListListeners.add(listener);
	}
	
	public void removeMotorGroupListListener(IStringSpectrumListener listener)
	{
		if(motorGroupListListeners != null)
			motorGroupListListeners.remove(listener);
	}
	
	protected class MotorGroupListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<MotorGroup> newMotorGroupList = new ArrayList<MotorGroup>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] motorGroupNames = utils.getMotorGroupNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				MotorGroup motorGroup = getMotorGroup(motorGroupNames[i]);
				
				if(motorGroup == null) 
					motorGroup = utils.getNewMotorGroup(getPool(), data[i]);
				
				newMotorGroupList.add(motorGroup);
			}
			
			// if no change occured in the structure return
			if(getMotorGroups().equals(newMotorGroupList))
				return;
			
			boolean changed = updateMotorGroups(newMotorGroupList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : motorGroupListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{
			//log.info("Quality changed for motor group list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("State error event for motor group list");
		}
	}

	public void addPseudoMotorListListener(IStringSpectrumListener listener)
	{
		if(pseudoMotorListListeners != null)
			pseudoMotorListListeners.add(listener);
	}
	
	public void removePseudoMotorListListener(IStringSpectrumListener listener)
	{
		if(pseudoMotorListListeners != null)
			pseudoMotorListListeners.remove(listener);
	}
	
	protected class PseudoMotorListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{			
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<PseudoMotor> newPseudoMotorList = new ArrayList<PseudoMotor>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] pseudoMotorNames = utils.getPseudoMotorNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				PseudoMotor pseudoMotor = getPseudoMotor(pseudoMotorNames[i]);
				
				if(pseudoMotor == null) 
					pseudoMotor = utils.getNewPseudoMotor(getPool(), data[i]);
				
				newPseudoMotorList.add(pseudoMotor);
			}
			
			// if no change occured in the structure return
			if(getPseudoMotors().equals(newPseudoMotorList))
				return;
			
			boolean changed = updatePseudoMotors(newPseudoMotorList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : pseudoMotorListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{ 
			//log.info("quality changed for pseudo motor list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("Received error event event for pseudo motor list");
		}
	}
	
	
	public void addPseudoCounterListListener(IStringSpectrumListener listener)
	{
		if(pseudoCounterListListeners != null)
			pseudoCounterListListeners.add(listener);
	}
	
	public void removePseudoCounterListListener(IStringSpectrumListener listener)
	{
		if(pseudoCounterListListeners != null)
			pseudoCounterListListeners.remove(listener);
	}
	
	protected class PseudoCounterListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<PseudoCounter> newPseudoCounterList = new ArrayList<PseudoCounter>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] pseudoCounterNames = utils.getPseudoCounterNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				PseudoCounter pseudoCounter = getPseudoCounter(pseudoCounterNames[i]);
				
				if(pseudoCounter == null) 
					pseudoCounter = utils.getNewPseudoCounter(getPool(), data[i]);
				
				newPseudoCounterList.add(pseudoCounter);
			}
			
			// if no change occured in the structure return
			if(getPseudoCounters().equals(newPseudoCounterList))
				return;
			
			boolean changed = updatePseudoCounters(newPseudoCounterList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : pseudoCounterListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{ 
			//log.info("quality changed for pseudo motor list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("Received error event event for pseudo Counter list");
		}
	}
	
	public void addExperimentChannelListListener(IStringSpectrumListener listener)
	{
		if(experimentChannelListListeners != null)
			experimentChannelListListeners.add(listener);
	}
	
	public void removeExperimentChannelListListener(IStringSpectrumListener listener)
	{
		if(experimentChannelListListeners != null)
			experimentChannelListListeners.remove(listener);
	}
	
	protected class ExperimentChannelListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<ExperimentChannel> newExperimentChannelList = new ArrayList<ExperimentChannel>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] channelNames = utils.getExperimentChannelNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				ExperimentChannel channel = getExperimentChannel(channelNames[i]);
				
				if(channel == null) 
					channel = utils.getNewExperimentChannel(getPool(), data[i]);
				
				newExperimentChannelList.add(channel);
			}
			
			// if no change occurred in the structure return
			if(getExperimentChannels().equals(newExperimentChannelList))
				return;
			
			boolean changed = updateExperimentChannels(newExperimentChannelList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : experimentChannelListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{
			//log.info("Quality changed for experiment channel list: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("Received error event event for experiment channel list");
		}
	}	
	
	public void addMeasurementGroupListListener(IStringSpectrumListener listener)
	{
		if(measurementGroupListListeners != null)
			measurementGroupListListeners.add(listener);
	}
	
	public void removeMeasurementGroupListListener(IStringSpectrumListener listener)
	{
		if(measurementGroupListListeners != null)
			measurementGroupListListeners.remove(listener);
	}
	
	protected class MeasurementGroupListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			if (e.getValue() == null)
				return;
			
			String data[] = e.getValue();
			
			ArrayList<MeasurementGroup> newMeasurementGroupList = new ArrayList<MeasurementGroup>(data.length);
			
			DevicePoolUtils utils = DevicePoolUtils.getInstance();
			
			String[] measurementGroupNames = utils.getMeasurementGroupNames(data);
			
			for (int i = 0; i < data.length; i++)
			{
				MeasurementGroup measurementGroup = getMeasurementGroup(measurementGroupNames[i]);
				
				if(measurementGroup == null) 
					measurementGroup = utils.getNewMeasurementGroup(getPool(), data[i]);
				
				newMeasurementGroupList.add(measurementGroup);
			}
			
			// if no change occured in the structure return
			if(getMeasurementGroups().equals(newMeasurementGroupList))
				return;
			
			boolean changed = updateMeasurementGroups(newMeasurementGroupList);
			
			// Propagate changes to all listeners
			if(changed)
				for(IStringSpectrumListener listener : measurementGroupListListeners)
					listener.stringSpectrumChange(e);
		}

		public void stateChange(AttributeStateEvent e)
		{ 
			//log.info("Quality changed for measurement group: " + e.toString());
		}

		public void errorChange(ErrorEvent evt)
		{
			if(available)
				log.finest("Received error event for measurement group list");
		}
	}

	public int getMotorCount()
	{
		if(motors == null) return 0;
		return motors.size();
	}
	
	public int getPseudoMotorCount()
	{
		if(pseudoMotors == null) return 0;
		return pseudoMotors.size();
	}
	
	public int getMotorGroupCount()
	{
		if(motorGroups == null) return 0;
		return motorGroups.size();
	}

	public int getExperimentChannelCount()
	{
		if(experimentChannels == null) return 0;
		return experimentChannels.size();
	}
	
	public int getMeasurementGroupCount()
	{
		if(measurementGroups == null) return 0;
		return measurementGroups.size();
	}
	
	public int getCommunicationChannelCount()
	{
		if(communicationChannels == null) return 0;
		return communicationChannels.size();
	}
	
	public int getDeviceElementCount()
	{
		return getMotorCount() + getPseudoMotorCount() + getMotorGroupCount() + 
			getExperimentChannelCount() + getMeasurementGroupCount() + 
			getCommunicationChannelCount();
	}
	
	public List<SardanaDevice> getDeviceElements()
	{
		ArrayList<SardanaDevice> devs = new ArrayList<SardanaDevice>(getDeviceElementCount());
		
		devs.addAll(communicationChannels);
		devs.addAll(motors);
		devs.addAll(pseudoMotors);
		devs.addAll(motorGroups);
		devs.addAll(experimentChannels);
		devs.addAll(measurementGroups);
		
		return devs;
	}
	
	public List<Controller> getControllersInFile(String fileName)
	{
		List<Controller> ctrls = new ArrayList<Controller>();
		
		for(Controller ctrl : getControllers())
		{
			if(ctrl.getFileName().equals(fileName))
				ctrls.add(ctrl);
		}
		return ctrls;
	}

	public List<Controller> getControllersInFiles(List<String> fileNames)
	{
		List<Controller> ctrls = new ArrayList<Controller>();
		
		for(Controller ctrl : getControllers())
		{
			if(fileNames.contains(ctrl.getFileName()))
				ctrls.add(ctrl);
		}
		return ctrls;
	}

	public void setProperties(List<DeviceProperty> props) 
	{
		for(DeviceProperty prop : props)
		{
			setProperty(prop);
		}
	}
	
}
