package es.cells.sardana.client.framework;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.apache.xmlbeans.XmlOptions;
import org.apache.xmlbeans.XmlString;
import org.tango.config.AttrAlarms;
import org.tango.config.AttrArchiveEvent;
import org.tango.config.AttrChangeEvent;
import org.tango.config.AttrConfiguration;
import org.tango.config.AttrDisplay;
import org.tango.config.AttrEvents;
import org.tango.config.AttrPeriodicEvent;
import org.tango.config.AttrRange;
import org.tango.config.AttrUnits;
import org.tango.config.AttrValue;
import org.tango.config.Attribute;
import org.tango.config.Device;
import org.tango.config.Item;
import org.tango.config.Logging;
import org.tango.config.PollConfig;
import org.tango.config.Polling;
import org.tango.config.Property;

import es.cells.sardana.client.framework.IPreferences.ElementAttributeSaveLevel;
import es.cells.sardana.client.framework.IPreferences.ElementPropertySaveLevel;
import es.cells.sardana.client.framework.IPreferences.PoolPropertySaveLevel;
import es.cells.sardana.client.framework.config.ControllerRef;
import es.cells.sardana.client.framework.config.ExpChannel;
import es.cells.sardana.client.framework.config.LibElement;
import es.cells.sardana.client.framework.config.Library;
import es.cells.sardana.client.framework.config.Pool;
import es.cells.sardana.client.framework.config.PoolServer;
import es.cells.sardana.client.framework.config.ReferenceType;
import es.cells.sardana.client.framework.config.Sardana;
import es.cells.sardana.client.framework.config.SardanaDocument;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.ControllerClass;
import es.cells.sardana.client.framework.pool.ControllerType;
import es.cells.sardana.client.framework.pool.CounterTimer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyInstance;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import es.cells.sardana.client.framework.pool.ZeroDExpChannel;
import es.cells.sardana.client.framework.pool.OneDExpChannel;
import es.cells.sardana.client.framework.pool.TwoDExpChannel;
import es.cells.tangoatk.utils.IStringFilter;
import fr.esrf.Tango.AttrDataFormat;
import fr.esrf.Tango.AttrWriteType;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DbDatum;
import fr.esrf.TangoDs.TangoConst;
import fr.esrf.tangoatk.core.DeviceProperty;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IBooleanImage;
import fr.esrf.tangoatk.core.IBooleanScalar;
import fr.esrf.tangoatk.core.IBooleanSpectrum;
import fr.esrf.tangoatk.core.INumberImage;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.IStringSpectrum;

public class SardanaConfigSaver 
{
	File file;
	List<DevicePool> devicePools;
	
	IPreferences currentPreferences;
	
	String[][] currentDevicePollingInfo;
	
	public SardanaConfigSaver(File f, List<DevicePool> devicePools)
	{
		this.file = f;
		this.devicePools = devicePools;
	}
	
	public SardanaDocument build(IPreferences prefs)
	{
		currentPreferences = prefs;
		SardanaDocument xmlSardanaDoc = SardanaDocument.Factory.newInstance();
		Sardana sardana = xmlSardanaDoc.addNewSardana();

		if(devicePools.size() > 0)
		{
			String serverName = devicePools.get(0).getServerName();
			
			String[] nameInstance = serverName.split("/");
			
			if(nameInstance.length > 1)
				sardana.setName(nameInstance[1]);
		}
		
		for(DevicePool pool : devicePools)
		{
			PoolServer xmlPoolServer = sardana.addNewPoolServer();
			xmlPoolServer.setServerName(pool.getServerName());
			xmlPoolServer.setTangoHost(pool.getMachine().toString());
			
			Pool xmlPool = Pool.Factory.newInstance();
			
			String name = pool.getName();
			if(name != null && name.length() > 0 && name.indexOf("/") < 0)
				xmlPool.setAlias(pool.getName());

			xmlPool.setDeviceName(pool.getDeviceName());
			buildPoolProperties(xmlPool, pool);
			buildPollConfig(xmlPool, pool);
			buildLogging(xmlPool, pool);
			buildAttribute(xmlPool, pool, pool.getAttributeInfo("SimulationMode"));
			buildControllers(xmlPool, pool);
			buildMotors(xmlPool, pool);
			buildPseudoMotors(xmlPool, pool);
			buildMotorGroups(xmlPool, pool);
			buildCTExpChannels(xmlPool, pool);
			buildZeroDExpChannels(xmlPool, pool);
			buildOneDExpChannels(xmlPool, pool);
			buildTwoDExpChannels(xmlPool, pool);
			buildMeasurementGroups(xmlPool, pool);
			buildLibrary(xmlPool, pool);

			xmlPoolServer.setDeviceArray(new Device[] { xmlPool } );
		}
		return xmlSardanaDoc;
	}

	public void save(SardanaDocument xmlSardanaDoc) throws IOException
	{
		Map<String, String> suggestedPrefixes = new HashMap<String, String>();
		
		suggestedPrefixes.put("http://tango.org/config", "tango");
		//suggestedPrefixes.put("http://sardana.cells.es/client/framework/config", "sardana");
		
		XmlOptions options = new XmlOptions();
		options = options.setSavePrettyPrint();
		options.setSavePrettyPrintIndent(2);
		options.setSaveSuggestedPrefixes(suggestedPrefixes);
		options.setSaveAggressiveNamespaces();
		options.setUseDefaultNamespace();
		xmlSardanaDoc.save(file, options);
	}
	
	protected void buildLogging(Device xmlDevice, SardanaDevice device) 
	{
		Logging xmlLogging = xmlDevice.addNewLogging();
		
		String[] currLoggingInfo = DevicePoolUtils.getCurrentLoggingInfo(device);
		
		String loggingLevel = DevicePoolUtils.getLoggingLevel(device); 
		
		if(loggingLevel != null)
			xmlLogging.setLevel(loggingLevel);
		
		if(currLoggingInfo != null && currLoggingInfo.length > 0)
			xmlLogging.setCurrentLevel(currLoggingInfo[0]);
		
		String[] targets = DevicePoolUtils.getLoggingTarget(device);
		
		if(targets != null && targets.length > 0)
			for(String target : targets)
			{
				xmlLogging.addLoggingTarget(target);
			}
		
		if(currLoggingInfo != null && currLoggingInfo.length > 1)
			for(int i = 1; i < currLoggingInfo.length; i++)
			{
				xmlLogging.addCurrentLoggingTarget(currLoggingInfo[i]);
			}
	}

	protected void buildPollConfig(Device xmlDevice, SardanaDevice device) 
	{
		try 
		{
			Database db = device.getMachine().getDataBase();
			String old_factor = null;
			String ring_depth = null;
			
			DbDatum data = db.get_device_property(device.getDeviceName(), "poll_old_factor");
			if(!data.is_empty())
				old_factor = data.extractString();
			
			data = db.get_device_property(device.getDeviceName(),"poll_ring_depth");
			if(!data.is_empty())
				ring_depth = data.extractString();
			
			if(old_factor != null || ring_depth != null)
			{
				PollConfig xmlPollConfig = xmlDevice.addNewPolling();
				
				if(old_factor != null)
					xmlPollConfig.setOldfactor(old_factor);
				if(ring_depth != null)
					xmlPollConfig.setRingdepth(ring_depth);
			}
		}
		catch(DevFailed e) 
		{
			return;
		}
	}

	protected void buildLibrary(Pool xmlPool, DevicePool pool) 
	{
		Library xmlLibrary = xmlPool.addNewLibrary();
		
		HashMap<ControllerType, HashMap<String, List<ControllerClass>>> ctrlTypes = pool.getControllerClasses();
		
		for(es.cells.sardana.client.framework.pool.ControllerType ctrlType : ctrlTypes.keySet())
		{
			HashMap<String, List<ControllerClass>> ctrlsOfType = ctrlTypes.get(ctrlType);
			for(String fileName : ctrlsOfType.keySet())
			{
				List<ControllerClass> ctrlsInFile = ctrlsOfType.get(fileName);
				for(ControllerClass ctrlClass : ctrlsInFile)
				{
					LibElement xmlLibElement = xmlLibrary.addNewLibElement();
					xmlLibElement.setType(ctrlClass.getType().toString());
					xmlLibElement.setName(ctrlClass.getFullClassName());
					xmlLibElement.setAlias(ctrlClass.getClassName());
					
					String descr = ctrlClass.getDescription();
					if(descr != null && descr.length() > 0)
						xmlLibElement.setDescription(ctrlClass.getDescription());
					
					for(PropertyInfo prop : ctrlClass.getPropertiesInfo().values())
					{
						Property xmlProp = xmlLibElement.addNewProperty();
					
						if(prop.hasDefaultValue())
						{
							Object objDftValue = prop.getDefaultValue();
							if(prop.getType().isSimpleType())
							{
								XmlString xmlStrValue = XmlString.Factory.newInstance();
								xmlStrValue.setStringValue(objDftValue.toString());
								xmlProp.set(xmlStrValue);
							}
							else
							{
								Vector<?> vecDftValue = (Vector<?>) objDftValue;
								for(Object elem : vecDftValue)
								{
									xmlProp.addItem(elem.toString());
								}
							}
						}
						
						xmlProp.setName(prop.getName());
						xmlProp.setType(prop.getType().toString());
						xmlProp.setDescription(prop.getDescription());
					}
				}
			}
		}
	}

	protected void buildMeasurementGroups(Pool xmlPool, DevicePool pool) 
	{
		for(MeasurementGroup measurementGroup : pool.getMeasurementGroups())
		{
			es.cells.sardana.client.framework.config.MeasurementGroup xmlMeasurementGroup = xmlPool.addNewMeasurementGroup();
			xmlMeasurementGroup.setAlias(measurementGroup.getName());
			
			buildPollConfig(xmlMeasurementGroup, measurementGroup);
			buildLogging(xmlMeasurementGroup, measurementGroup);
			buildAttribute(xmlMeasurementGroup, measurementGroup, measurementGroup.getAttributeInfo("Timer"));
			buildAttribute(xmlMeasurementGroup, measurementGroup, measurementGroup.getAttributeInfo("Monitor"));
			buildAttribute(xmlMeasurementGroup, measurementGroup, measurementGroup.getAttributeInfo("Integration_time"));
			buildAttribute(xmlMeasurementGroup, measurementGroup, measurementGroup.getAttributeInfo("Integration_count"));
			
			for(SardanaDevice element : measurementGroup.getChannels())
			{
				if(element instanceof CounterTimer)
				{
					ReferenceType xmlCTExpChannelRef = xmlMeasurementGroup.addNewCTExpChannelRef();
					xmlCTExpChannelRef.setName(element.getName());
				}
				else if(element instanceof ZeroDExpChannel)
				{
					ReferenceType xmlZeroDExpChannelRef = xmlMeasurementGroup.addNewZeroDExpChannelRef();
					xmlZeroDExpChannelRef.setName(element.getName());
				}
				else if(element instanceof OneDExpChannel)
				{
					ReferenceType xmlOneDExpChannelRef = xmlMeasurementGroup.addNewOneDExpChannelRef();
					xmlOneDExpChannelRef.setName(element.getName());
				}
				else if(element instanceof TwoDExpChannel)
				{
					ReferenceType xmlTwoDExpChannelRef = xmlMeasurementGroup.addNewTwoDExpChannelRef();
					xmlTwoDExpChannelRef.setName(element.getName());
				}
			}
		}
	}

	protected void buildZeroDExpChannels(Pool xmlPool, DevicePool pool) 
	{
		AttributeFilter filter = new AttributeFilter(currentPreferences.getChannelAttributeSaveLevel());
		
		for(ZeroDExpChannel zerodExpChannel : pool.getZeroDExpChannels())
		{
			es.cells.sardana.client.framework.config.ExpChannel xmlZeroDExpChannel = xmlPool.addNewZeroDExpChannel();
		
			buildPollConfig(xmlZeroDExpChannel, zerodExpChannel);
			buildLogging(xmlZeroDExpChannel, zerodExpChannel);
			
			xmlZeroDExpChannel.setAlias(zerodExpChannel.getName());
			ControllerRef xmlCtrlRef = xmlZeroDExpChannel.addNewControllerRef();
			xmlCtrlRef.setName(zerodExpChannel.getController().getName());
			xmlCtrlRef.setIndex(zerodExpChannel.getIdInController());
			
			zerodExpChannel.getEventAttributes().refresh();
			zerodExpChannel.getPolledAttributes().refresh();
			zerodExpChannel.getNonPolledAttributes().refresh();
			
			for(AttributeInfoEx attr : zerodExpChannel.getAttributeInfo())
			{
				if(!filter.isValid(attr))
					continue;

				buildAttribute(xmlZeroDExpChannel, zerodExpChannel, attr);
			}		
		}
	}
	
	protected void buildOneDExpChannels(Pool xmlPool, DevicePool pool) 
	{
		AttributeFilter filter = new AttributeFilter(currentPreferences.getChannelAttributeSaveLevel());
		
		for(OneDExpChannel onedExpChannel : pool.getOneDExpChannels())
		{
			es.cells.sardana.client.framework.config.ExpChannel xmlOneDExpChannel = xmlPool.addNewOneDExpChannel();
		
			buildPollConfig(xmlOneDExpChannel, onedExpChannel);
			buildLogging(xmlOneDExpChannel, onedExpChannel);
			
			xmlOneDExpChannel.setAlias(onedExpChannel.getName());
			ControllerRef xmlCtrlRef = xmlOneDExpChannel.addNewControllerRef();
			xmlCtrlRef.setName(onedExpChannel.getController().getName());
			xmlCtrlRef.setIndex(onedExpChannel.getIdInController());
			
			onedExpChannel.getEventAttributes().refresh();
			onedExpChannel.getPolledAttributes().refresh();
			onedExpChannel.getNonPolledAttributes().refresh();
			
			for(AttributeInfoEx attr : onedExpChannel.getAttributeInfo())
			{
				if(!filter.isValid(attr))
					continue;

				buildAttribute(xmlOneDExpChannel, onedExpChannel, attr);
			}		
		}
	}
	
	protected void buildTwoDExpChannels(Pool xmlPool, DevicePool pool) 
	{
		AttributeFilter filter = new AttributeFilter(currentPreferences.getChannelAttributeSaveLevel());
		
		for(TwoDExpChannel twodExpChannel : pool.getTwoDExpChannels())
		{
			es.cells.sardana.client.framework.config.ExpChannel xmlTwoDExpChannel = xmlPool.addNewTwoDExpChannel();
		
			buildPollConfig(xmlTwoDExpChannel, twodExpChannel);
			buildLogging(xmlTwoDExpChannel, twodExpChannel);
			
			xmlTwoDExpChannel.setAlias(twodExpChannel.getName());
			ControllerRef xmlCtrlRef = xmlTwoDExpChannel.addNewControllerRef();
			xmlCtrlRef.setName(twodExpChannel.getController().getName());
			xmlCtrlRef.setIndex(twodExpChannel.getIdInController());
			
			twodExpChannel.getEventAttributes().refresh();
			twodExpChannel.getPolledAttributes().refresh();
			twodExpChannel.getNonPolledAttributes().refresh();
			
			for(AttributeInfoEx attr : twodExpChannel.getAttributeInfo())
			{
				if(!filter.isValid(attr))
					continue;

				buildAttribute(xmlTwoDExpChannel, twodExpChannel, attr);
			}		
		}
	}
	
	protected void buildCTExpChannels(Pool xmlPool, DevicePool pool) 
	{
		AttributeFilter filter = new AttributeFilter(currentPreferences.getChannelAttributeSaveLevel());
		
		for(CounterTimer ctExpChannel : pool.getCounterTimers())
		{
			ExpChannel xmlCTExpChannel = xmlPool.addNewCTExpChannel();
			xmlCTExpChannel.setAlias(ctExpChannel.getName());
			
			buildPollConfig(xmlCTExpChannel, ctExpChannel);
			buildLogging(xmlCTExpChannel, ctExpChannel);
			
			ControllerRef xmlCtrlRef = xmlCTExpChannel.addNewControllerRef();
			xmlCtrlRef.setName(ctExpChannel.getController().getName());
			xmlCtrlRef.setIndex(ctExpChannel.getIdInController());

			ctExpChannel.getEventAttributes().refresh();
			ctExpChannel.getPolledAttributes().refresh();
			ctExpChannel.getNonPolledAttributes().refresh();
			
			for(AttributeInfoEx attr : ctExpChannel.getAttributeInfo())
			{
				if(!filter.isValid(attr))
					continue;
				
				buildAttribute(xmlCTExpChannel, ctExpChannel, attr);
			}
		}
	}

	protected void buildMotorGroups(Pool xmlPool, DevicePool pool) 
	{
		for(MotorGroup motorGroup : pool.getMotorGroups())
		{
			es.cells.sardana.client.framework.config.MotorGroup xmlMotorGroup = xmlPool.addNewMotorGroup();
			xmlMotorGroup.setAlias(motorGroup.getName());
			
			buildPollConfig(xmlMotorGroup, motorGroup);
			buildLogging(xmlMotorGroup, motorGroup);
			
			for(SardanaDevice element : motorGroup.getElements())
			{
				if(element instanceof PseudoMotor)
				{
					ReferenceType xmlPseudoMotorRef = xmlMotorGroup.addNewPseudoMotorRef();
					xmlPseudoMotorRef.setName(element.getName());
				}
				else if(element instanceof Motor)
				{
					ReferenceType xmlMotorRef = xmlMotorGroup.addNewMotorRef();
					xmlMotorRef.setName(element.getName());
				}
				else if(element instanceof MotorGroup)
				{
					ReferenceType xmlMotorGroupRef = xmlMotorGroup.addNewMotorGroupRef();
					xmlMotorGroupRef.setName(element.getName());
				}
			}
		}
	}
	
	protected void buildPseudoMotors(Pool xmlPool, DevicePool pool) 
	{
		PropertyFilter filter = new PropertyFilter(currentPreferences.getPseudoMotorPropSaveLevel());
		
		for(PseudoMotor pseudoMotor : pool.getPseudoMotors())
		{
			es.cells.sardana.client.framework.config.PseudoMotor xmlPseudoMotor = xmlPool.addNewPseudoMotor();
			xmlPseudoMotor.setAlias(pseudoMotor.getName());

			ReferenceType xmlLibRef = xmlPseudoMotor.addNewLibRef();
			xmlLibRef.setName(pseudoMotor.getFullClassName());
			
			for(Motor motor : pseudoMotor.getMotors())
			{
				ReferenceType xmlMotorRef = xmlPseudoMotor.addNewMotorRef();
				xmlMotorRef.setName(motor.getName());
			}
			
			/*
			for(PropertyInstance prop : pseudoMotor.getPropertyInstances().values())
			{
				if(!filter.isValid(prop))
					continue;
				
				Property xmlProp = xmlPseudoMotor.addNewProperty();
				
				es.cells.sardana.client.framework.pool.PropertyType type = prop.getType();
								
				if(type.isSimpleType())
				{
					XmlString xmlStr = XmlString.Factory.newInstance();
					String val = DevicePoolUtils.toPropertyValueString(type, prop.getValue());
					xmlStr.setStringValue(val);
					xmlProp.set(xmlStr);
				}
				else
				{
					Vector<?> val = (Vector<?>) prop.getValue();
					for(Object o : val)
					{
						xmlProp.addItem(o.toString());
					}
				}
				
				xmlProp.setName(prop.getName());
				xmlProp.setType(type.toString());
			}*/
		}
	}

	protected void buildMotors(Pool xmlPool, DevicePool pool) 
	{
		AttributeFilter filter = new AttributeFilter(currentPreferences.getMotorAttributeSaveLevel());
		
		for(Motor motor : pool.getMotors())
		{
			es.cells.sardana.client.framework.config.Motor xmlMotor = xmlPool.addNewMotor();
			xmlMotor.setAlias(motor.getName());
			
			buildPollConfig(xmlMotor, motor);
			buildLogging(xmlMotor, motor);
			
			ControllerRef xmlCtrlRef = xmlMotor.addNewControllerRef();
			xmlCtrlRef.setName(motor.getController().getName());
			xmlCtrlRef.setIndex(motor.getIdInController());
			
			motor.getEventAttributes().refresh();
			motor.getPolledAttributes().refresh();
			motor.getNonPolledAttributes().refresh();
			
			try 
			{
				String[] rawPollingInfo = motor.getDevice().polling_status();
				
				currentDevicePollingInfo = new String[rawPollingInfo.length][];
				for(int i = 0 ; i < rawPollingInfo.length ; i++)
				{
					currentDevicePollingInfo[i] = DevicePoolUtils.extractPollingInfo(rawPollingInfo[i]);
				}
			}
			catch (DevFailed e) 
			{
				currentDevicePollingInfo = null;
			}
			for(AttributeInfoEx attr : motor.getAttributeInfo())
			{
				if(!filter.isValid(attr))
					continue;

				buildAttribute(xmlMotor, motor, attr);
			}
		}
	}
	
	protected void buildAttribute(Device xmlDevice, SardanaDevice device, AttributeInfoEx attr)
	{
		IAttribute attrModel = device.getAttribute(attr.name);

		attrModel.refresh();
		
		Attribute xmlAttr = xmlDevice.addNewAttribute();
		xmlAttr.setName(attr.name);
		xmlAttr.setType(attrModel.getType());

		DeviceAttributeValueFilter filter = new DeviceAttributeValueFilter(device);
		
		if(filter.isValid(attr))
		{
			buildAttributeValue(xmlAttr, attrModel, attr);
		}

		buildAttributeProperties(xmlAttr, attrModel, attr);
		buildAttributePolling(xmlAttr, attrModel, attr);
		buildAttributeEvents(xmlAttr, attrModel, attr);
		buildAttributeConfiguration(xmlAttr, attrModel, attr);
	}
	
	protected void buildAttributeConfiguration(Attribute xmlAttr, IAttribute attrModel, AttributeInfoEx attr) 
	{
		AttrConfiguration xmlAttrConfiguration = xmlAttr.addNewConfiguration();

		AttrDisplay xmlAttrDisplay = xmlAttrConfiguration.addNewDisplay();
		xmlAttrDisplay.setLabel(attr.label);
		xmlAttrDisplay.setFormat(attr.format);
		
		boolean hasDisplayUnit = !attr.display_unit.equalsIgnoreCase("No display unit");
		boolean hasUnit = !attr.unit.equalsIgnoreCase("No unit");
		boolean hasStandardUnit = !attr.standard_unit.equalsIgnoreCase("No standard unit");
		boolean hasUnits = hasDisplayUnit || hasUnit || hasStandardUnit;
		
		if(hasUnits)
		{
			AttrUnits xmlAttrUnits = xmlAttrConfiguration.addNewUnits();
			if(hasDisplayUnit)
				xmlAttrUnits.setDisplayUnit(attr.display_unit);
			if(hasUnit)
				xmlAttrUnits.setUnit(attr.unit);
			if(hasStandardUnit)
				xmlAttrUnits.setStandardUnit(attr.standard_unit);
		}
		
		boolean hasMinValue = !attr.min_value.equalsIgnoreCase("Not specified");
		boolean hasMaxValue = !attr.max_value.equalsIgnoreCase("Not specified");
		boolean hasRange = hasMinValue || hasMaxValue;
		
		if(hasRange)
		{
			AttrRange xmlAttrRange = xmlAttrConfiguration.addNewRange();
			
			if(hasMinValue)
				xmlAttrRange.setMin(attr.min_value);
			if(hasMaxValue)
				xmlAttrRange.setMax(attr.max_value);
		}
		
		boolean hasMinWarning = !attr.alarms.min_warning.equalsIgnoreCase("Not specified");
		boolean hasMaxWarning = !attr.alarms.max_warning.equalsIgnoreCase("Not specified");
		boolean hasMinAlarm = !attr.alarms.min_alarm.equalsIgnoreCase("Not specified");
		boolean hasMaxAlarm = !attr.alarms.max_alarm.equalsIgnoreCase("Not specified");
		boolean hasDeltaT = !attr.alarms.delta_t.equalsIgnoreCase("Not specified");
		boolean hasDeltaVal = !attr.alarms.delta_val.equalsIgnoreCase("Not specified");
		
		boolean hasAlarms = hasMinWarning || hasMaxWarning || hasMinAlarm || hasMaxAlarm || hasDeltaT || hasDeltaVal;
		
		if(hasAlarms)
		{
			AttrAlarms xmlAttrAlarms = xmlAttrConfiguration.addNewAlarms();
			if(hasMinWarning)
				xmlAttrAlarms.setMinWarning(attr.alarms.min_warning);
			if(hasMaxWarning)
				xmlAttrAlarms.setMaxWarning(attr.alarms.max_warning);
			if(hasMinAlarm)
				xmlAttrAlarms.setMinAlarm(attr.alarms.min_alarm);
			if(hasMaxAlarm)
				xmlAttrAlarms.setMaxAlarm(attr.alarms.max_alarm);
			if(hasDeltaT)
				xmlAttrAlarms.setDeltaT(attr.alarms.delta_t);
			if(hasDeltaVal)
				xmlAttrAlarms.setDeltaVal(attr.alarms.delta_val);
		}
		
		boolean hasDescription = !attr.description.equalsIgnoreCase("No description");
		
		if(hasDescription)
		{
			xmlAttrConfiguration.setDescription(attr.description);
		}
	}

	protected void buildAttributeEvents(Attribute xmlAttr, IAttribute attrModel, AttributeInfoEx attr) 
	{
		if(!attrModel.hasEvents())
			return;
		
		boolean absChangeEvent = !attr.events.ch_event.abs_change.equalsIgnoreCase("Not specified");
		boolean relChangeEvent = !attr.events.ch_event.rel_change.equalsIgnoreCase("Not specified");

		boolean anyChangeEvent = absChangeEvent || relChangeEvent;
		
		boolean absArchEvent = !attr.events.arch_event.abs_change.equalsIgnoreCase("Not specified");
		boolean relArchEvent = !attr.events.arch_event.rel_change.equalsIgnoreCase("Not specified");
		boolean perArchEvent = !attr.events.arch_event.period.equalsIgnoreCase("Not specified");
		
		boolean anyArchEvent = absArchEvent || relArchEvent || perArchEvent;
		
		boolean anyPerEvent = !attr.events.per_event.period.equalsIgnoreCase("Not specified");
		
		boolean anyEvent = anyChangeEvent || anyArchEvent || anyPerEvent;
		
		if(!anyEvent)
			return;
		
		AttrEvents xmlAttrEvents = xmlAttr.addNewEvents();
		
		if(anyChangeEvent)
		{
			AttrChangeEvent xmlAttrChangeEvent = xmlAttrEvents.addNewChangeEvent();
			if(absChangeEvent)
				xmlAttrChangeEvent.setAbsolute(attr.events.ch_event.abs_change);
			if(relChangeEvent)
			xmlAttrChangeEvent.setRelative(attr.events.ch_event.rel_change);
		}
		
		if(anyArchEvent)
		{
			AttrArchiveEvent xmlAttrArchiveEvent = xmlAttrEvents.addNewArchiveEvent();
			if(absArchEvent)
				xmlAttrArchiveEvent.setAbsolute(attr.events.arch_event.abs_change);
			if(relArchEvent)
				xmlAttrArchiveEvent.setRelative(attr.events.arch_event.rel_change);
			if(perArchEvent)
				xmlAttrArchiveEvent.setPeriod(attr.events.arch_event.period);
		}
		
		if(anyPerEvent)
		{
			AttrPeriodicEvent xmlAttrPeriodicEvent = xmlAttrEvents.addNewPeriodicEvent();
			xmlAttrPeriodicEvent.setPeriod(attr.events.per_event.period);
		}
	}

	protected void buildAttributePolling(Attribute xmlAttr, IAttribute attrModel, AttributeInfoEx attr)  
	{
		if(currentDevicePollingInfo == null || currentDevicePollingInfo.length == 0)
			return;
		
		String[] attrPollingInfo = null;
		
		for(String[] attrPI : currentDevicePollingInfo)
		{
			if(!attrPI[0].equalsIgnoreCase("attribute"))
				continue;
			
			if(!attrPI[1].equalsIgnoreCase(attr.name))
				continue;
			
			attrPollingInfo = attrPI;
			break;
		}
		
		if(attrPollingInfo != null)
		{
			Polling xmlPolling = xmlAttr.addNewPolling();
			xmlPolling.setPolled(true);
			xmlPolling.setPeriod(Integer.parseInt(attrPollingInfo[2]));
		}
	}
	
	protected void buildAttributeProperties(Attribute xmlAttr, IAttribute attrModel, AttributeInfoEx attr) 
	{
		//TODO
	}
	
	protected void buildAttributeValue(Attribute xmlAttr, IAttribute attrModel, AttributeInfoEx attr) 
	{
		AttrValue xmlValue = xmlAttr.addNewValue();
	
		if(attr.data_format == AttrDataFormat.SCALAR)
		{
			XmlString xmlStr = getXmlStringForScalarAttributeValue(attrModel, attr.data_type);
			if(xmlStr != null)
				xmlValue.set(xmlStr);
		}
		else if(attr.data_format == AttrDataFormat.SPECTRUM)
		{
			int tangoType = attr.data_type;
			
			if(tangoType == TangoConst.Tango_DEV_BOOLEAN)
			{
				IBooleanSpectrum boolModel = (IBooleanSpectrum) attrModel;
				try 
				{
					for(boolean b : boolModel.getValue())
					{
						Item xmlItem = xmlValue.addNewItem();
						String v = b ? "True" : "False";
						XmlString xmlStr = XmlString.Factory.newInstance(); 
						xmlStr.setStringValue(v);
						xmlItem.set(xmlStr);
					}
				} 
				catch (DevFailed e) 
				{
					e.printStackTrace();
				}
			}
			else if(tangoType == TangoConst.Tango_DEV_LONG ||
					tangoType == TangoConst.Tango_DEV_ULONG ||
					tangoType == TangoConst.Tango_DEV_USHORT ||
					tangoType == TangoConst.Tango_DEV_SHORT)  
			{
				INumberSpectrum longModel = (INumberSpectrum) attrModel;
				for(double d : longModel.getSpectrumValue())
				{
					Item xmlItem = xmlValue.addNewItem();
					String v = Long.toString((long)d);
					XmlString xmlStr = XmlString.Factory.newInstance(); 
					xmlStr.setStringValue(v);
					xmlItem.set(xmlStr);
				}
			}
			else if(tangoType == TangoConst.Tango_DEV_DOUBLE ||
					tangoType == TangoConst.Tango_DEV_FLOAT)
			{
				INumberSpectrum doubleModel = (INumberSpectrum) attrModel;
				for(double d : doubleModel.getSpectrumValue())
				{
					Item xmlItem = xmlValue.addNewItem();
					String v = Double.toString(d);
					XmlString xmlStr = XmlString.Factory.newInstance(); 
					xmlStr.setStringValue(v);
					xmlItem.set(xmlStr);
				}
			}
			else if(tangoType == TangoConst.Tango_DEV_STRING)
			{
				IStringSpectrum strModel = (IStringSpectrum) attrModel;
				for(String s : strModel.getStringSpectrumValue())
				{
					Item xmlItem = xmlValue.addNewItem();
					XmlString xmlStr = XmlString.Factory.newInstance(); 
					xmlStr.setStringValue(s);
					xmlItem.set(xmlStr);
				}
			}
		}
		else if(attr.data_format == AttrDataFormat.IMAGE)
		{
			int tangoType = attr.data_type;
			
			if(tangoType == TangoConst.Tango_DEV_BOOLEAN)
			{
				IBooleanImage boolModel = (IBooleanImage) attrModel;
				
				try 
				{
					for(boolean[] bArray : boolModel.getValue())
					{
						Item xmlItemArray = xmlValue.addNewItem();
						for(boolean b : bArray)
						{
							Item xmlItem = xmlItemArray.addNewItem();
							XmlString xmlStr = XmlString.Factory.newInstance(); 
							xmlStr.setStringValue(b ? "True" : "False");
							xmlItem.set(xmlStr);
						}
					}
				} 
				catch (DevFailed e) 
				{
					e.printStackTrace();
				}
			}
			else if(tangoType == TangoConst.Tango_DEV_LONG ||
					tangoType == TangoConst.Tango_DEV_ULONG ||
					tangoType == TangoConst.Tango_DEV_USHORT ||
					tangoType == TangoConst.Tango_DEV_SHORT)  
			{
				INumberImage longModel = (INumberImage) attrModel;
				try 
				{
					for(double[] dArray : longModel.getValue())
					{
						Item xmlItemArray = xmlValue.addNewItem();
						for(double d : dArray)
						{
							Item xmlItem = xmlItemArray.addNewItem();
							XmlString xmlStr = XmlString.Factory.newInstance(); 
							xmlStr.setStringValue(Long.toString((long)d));
							xmlItem.set(xmlStr);
						}
					}
				} 
				catch (DevFailed e) 
				{
					e.printStackTrace();
				}
			}
			else if(tangoType == TangoConst.Tango_DEV_DOUBLE ||
					tangoType == TangoConst.Tango_DEV_FLOAT)
			{
				INumberImage longModel = (INumberImage) attrModel;
				try 
				{
					for(double[] dArray : longModel.getValue())
					{
						Item xmlItemArray = xmlValue.addNewItem();
						for(double d : dArray)
						{
							Item xmlItem = xmlItemArray.addNewItem();
							XmlString xmlStr = XmlString.Factory.newInstance(); 
							xmlStr.setStringValue(Double.toString(d));
							xmlItem.set(xmlStr);
						}
					}
				} 
				catch (DevFailed e) 
				{
					e.printStackTrace();
				}
			}
		}
	}

	protected XmlString getXmlStringForScalarAttributeValue(IAttribute attrModel, int tangoType)
	{
		XmlString xmlStr = XmlString.Factory.newInstance();
		
		if(tangoType == TangoConst.Tango_DEV_BOOLEAN)
		{
			IBooleanScalar boolModel = (IBooleanScalar) attrModel;
			String v = boolModel.getValue() ? "True" : "False";
			xmlStr.setStringValue(v);
		}
		else if(tangoType == TangoConst.Tango_DEV_LONG ||
				tangoType == TangoConst.Tango_DEV_ULONG ||
				tangoType == TangoConst.Tango_DEV_USHORT ||
				tangoType == TangoConst.Tango_DEV_SHORT)  
		{
			INumberScalar longModel = (INumberScalar) attrModel;
			String v = Long.toString((long)longModel.getNumberScalarValue());
			xmlStr.setStringValue(v);
		}
		else if(tangoType == TangoConst.Tango_DEV_DOUBLE ||
				tangoType == TangoConst.Tango_DEV_FLOAT)
		{
			INumberScalar doubleModel = (INumberScalar) attrModel;
			String v = Double.toString(doubleModel.getNumberScalarValue());
			xmlStr.setStringValue(v);
		}
		else if(tangoType == TangoConst.Tango_DEV_STRING)
		{
			IStringScalar strModel = (IStringScalar) attrModel;
			String v = strModel.getStringValue();
			xmlStr.setStringValue(v);
		}
		else
			return null;
		return xmlStr;
	}
	
	protected void buildPoolProperties(Pool xmlPool, DevicePool pool)
	{
		IPreferences.PoolPropertySaveLevel saveLevel = currentPreferences.getPoolPropSaveLevel(); 
	
		if(saveLevel == IPreferences.PoolPropertySaveLevel.never)
			return;

		IStringFilter filter = new PoolPropertyStringFilter(saveLevel);
		
		for(DeviceProperty prop : pool.getProperties().values())
		{
			if(!filter.isValid(prop.getName())) continue;
			
			Property xmlProp = xmlPool.addNewProperty();

			String[] v = prop.getValue();
			if(v.length == 1)
			{
				XmlString xmlStr = XmlString.Factory.newInstance();
				xmlStr.setStringValue(v[0]);
				xmlProp.set(xmlStr);
			}
			else if(v.length > 1)
			{
				for(String s : v)
					xmlProp.addItem(s);
			}
			
			xmlProp.setName(prop.getName());
		}
	}
	
	protected void buildControllers(Pool xmlPool, DevicePool pool) 
	{
		for(Controller ctrl : pool.getControllers())
		{
			es.cells.sardana.client.framework.config.Controller xmlCtrl = xmlPool.addNewController();
			
			xmlCtrl.setName(ctrl.getName());
			xmlCtrl.setType(ctrl.getType().toString());
			
			ReferenceType xmlLibraryRef = xmlCtrl.addNewLibraryElementRef();
			
			xmlLibraryRef.setName(ctrl.getFullClassName());
			
			PropertyFilter filter = new PropertyFilter(currentPreferences.getControllerPropSaveLevel());
			
			for(PropertyInstance prop : ctrl.getPropertyInstances().values())
			{
				if(!filter.isValid(prop))
					continue;
				
				Property xmlProp = xmlCtrl.addNewProperty();
				
				es.cells.sardana.client.framework.pool.PropertyType type = prop.getType();
								
				if(type.isSimpleType())
				{
					XmlString xmlStr = XmlString.Factory.newInstance();
					String val = DevicePoolUtils.toPropertyValueString(type, prop.getValue());
					xmlStr.setStringValue(val);
					xmlProp.set(xmlStr);
				}
				else
				{
					Vector<?> val = (Vector<?>) prop.getValue();
					for(Object o : val)
					{
						xmlProp.addItem(o.toString());
					}
				}
				
				xmlProp.setName(prop.getName());
				xmlProp.setType(type.toString());
			}
		}
	}
	
	protected class PoolPropertyStringFilter implements IStringFilter 
	{
		IPreferences.PoolPropertySaveLevel saveLevel;
		
		public PoolPropertyStringFilter(PoolPropertySaveLevel saveLevel) 
		{
			super();
			this.saveLevel = saveLevel;
		}

		public boolean isValid(String str) 
		{
			if(saveLevel == IPreferences.PoolPropertySaveLevel.never)
				return false;
			else if(saveLevel == IPreferences.PoolPropertySaveLevel.essencial)
				return str.equalsIgnoreCase(DevicePoolUtils.POOL_PROP_POOL_PATH);
			else if(saveLevel == IPreferences.PoolPropertySaveLevel.exaustive)
				return !str.equalsIgnoreCase("Controller");
			else if(saveLevel == IPreferences.PoolPropertySaveLevel.all)
				return true;
			
			return true;
		}
	} 
	
	protected class PropertyFilter
	{
		IPreferences.ElementPropertySaveLevel saveLevel;

		public PropertyFilter(ElementPropertySaveLevel saveLevel) 
		{
			super();
			this.saveLevel = saveLevel;
		}
		
		public boolean isValid(PropertyInstance property)
		{
			if(saveLevel == IPreferences.ElementPropertySaveLevel.never)
				return false;
			else if(saveLevel == IPreferences.ElementPropertySaveLevel.propsWithoutDefaultValue)
				return !property.hasDefaultValue();
			else if(saveLevel == IPreferences.ElementPropertySaveLevel.propsWithOverwrittenValue)
				return (!property.hasDefaultValue()) || 
				       (!property.getDefaultValue().equals(property.getValue()));
			else if(saveLevel == IPreferences.ElementPropertySaveLevel.all)
				return true;
			
			return true;
		}
	}
	
	protected class AttributeFilter
	{
		IPreferences.ElementAttributeSaveLevel saveLevel;
		
		public AttributeFilter(ElementAttributeSaveLevel saveLevel) 
		{
			super();
			this.saveLevel = saveLevel;
		}

		public boolean isValid(AttributeInfoEx attr)
		{
			if(saveLevel == IPreferences.ElementAttributeSaveLevel.never)
				return false;
			else if(saveLevel == IPreferences.ElementAttributeSaveLevel.writable)
				return attr.writable != AttrWriteType.READ;
			else if(saveLevel == IPreferences.ElementAttributeSaveLevel.exaustive)
				return !attr.name.equalsIgnoreCase("state") && !attr.name.equalsIgnoreCase("status");
			else if(saveLevel == IPreferences.ElementAttributeSaveLevel.all)
				return true;
			
			return true;
		}
	}
	
	protected class DeviceAttributeValueFilter
	{
		protected SardanaDevice device;
		
		public DeviceAttributeValueFilter(SardanaDevice device) 
		{
			super();
			this.device = device;
		}

		public boolean isValid(AttributeInfoEx attr)
		{
			if(device instanceof Motor)
			{
				return !attr.name.equalsIgnoreCase("Position");
			}
			else 
				return true;
		}
	}
}
