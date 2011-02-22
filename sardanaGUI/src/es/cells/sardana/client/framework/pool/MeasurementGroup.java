package es.cells.sardana.client.framework.pool;

import java.util.ArrayList;
import java.util.List;

import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.ICommand;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.IStringScalarListener;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.StringScalarEvent;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class MeasurementGroup extends SardanaDevice 
{
	public static CounterTimer TimerNotInitialized = new CounterTimer(null, "Not Initialized");
	public static CounterTimer MonitorNotInitialized = new CounterTimer(null, "Not Initialized");
	
	protected ArrayList<CounterTimer> cts = new ArrayList<CounterTimer>();
	protected ArrayList<ZeroDExpChannel> zerods = new ArrayList<ZeroDExpChannel>();
	protected ArrayList<OneDExpChannel> oneds = new ArrayList<OneDExpChannel>();
	protected ArrayList<TwoDExpChannel> twods = new ArrayList<TwoDExpChannel>();
	protected ArrayList<PseudoCounter> pcs = new ArrayList<PseudoCounter>();
	protected ArrayList<ExperimentChannel> channels = new ArrayList<ExperimentChannel>();
	
	
	
	protected CounterTimer timer = null;
	protected CounterTimer monitor = null;
	protected double i_time = Double.MIN_VALUE;
	protected int i_count = Integer.MIN_VALUE;
	
	protected TimerListener timerListener = new TimerListener();
	protected MonitorListener monitorListener = new MonitorListener();
	protected ITimeListener iTimeListener = new ITimeListener();
	protected ICountListener iCountListener = new ICountListener();
	protected CounterListListener counterListListener = new CounterListListener();
	protected ZeroDExpChannelListListener zerodListListener = new ZeroDExpChannelListListener();
	protected PseudoCounterListListener pcListListener = new PseudoCounterListListener();
	protected OneDExpChannelListListener onedListListener = new OneDExpChannelListListener();
	protected TwoDExpChannelListListener twodListListener = new TwoDExpChannelListListener();
	protected ChannelListListener channelsListListener = new ChannelListListener();
	
	ArrayList<IStringScalarListener> timerListeners;
	ArrayList<IStringScalarListener> monitorListeners;
	ArrayList<INumberScalarListener> iTimeListeners;
	ArrayList<INumberScalarListener> iCountListeners;
	
	protected ArrayList<IStringSpectrumListener> counterListListeners;
	protected ArrayList<IStringSpectrumListener> zerodListListeners;
	protected ArrayList<IStringSpectrumListener> pcListListeners;
	protected ArrayList<IStringSpectrumListener> onedListListeners;
	protected ArrayList<IStringSpectrumListener> twodListListeners;
	protected ArrayList<IStringSpectrumListener> channelListListeners;
	
	public MeasurementGroup(Machine machine, String name) 
	{
		super(machine, name);
		timerListeners = new ArrayList<IStringScalarListener>();
		monitorListeners = new ArrayList<IStringScalarListener>();
		iTimeListeners = new ArrayList<INumberScalarListener>();
		iCountListeners = new ArrayList<INumberScalarListener>();
		counterListListeners = new ArrayList<IStringSpectrumListener>();
		zerodListListeners = new ArrayList<IStringSpectrumListener>();
		pcListListeners = new ArrayList<IStringSpectrumListener>();
		onedListListeners = new ArrayList<IStringSpectrumListener>();
		twodListListeners = new ArrayList<IStringSpectrumListener>();
		channelListListeners = new ArrayList<IStringSpectrumListener>();
	}

	public ICommand getAbortCommandModel()
	{
		return (ICommand) commands.get(getDeviceName() + "/Abort");
	}
	
	public ICommand getStopCommandModel()
	{
		return (ICommand) commands.get(getDeviceName() + "/Stop");
	}

	public ICommand getAddExpChannelCommandModel()
	{
		return (ICommand) getCommandModel("AddExpChannel");
	}

	public ICommand getRemoveExpChannelCommandModel()
	{
		return (ICommand) getCommandModel("RemoveExpChannel");
	}

	public INumberScalar getIntegrationTimeAttributeModel()
	{
		return (INumberScalar) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_TIME);
	}

	public INumberScalar getIntegrationCountAttributeModel()
	{
		return (INumberScalar) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_COUNT);
	}

	public IStringScalar getTimerAttributeModel()
	{
		return (IStringScalar) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_TIMER);
	}

	public IStringScalar getMonitorAttributeModel()
	{
		return (IStringScalar) eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_MONITOR);
	}
	
	public IStringSpectrum getCountersAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_COUNTERS);
	}
	
	public IStringSpectrum getZeroDExpChannelsAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_ZERODEXPCHANNELS);
	}

	public IStringSpectrum getPseudoCountersAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_PSEUDOCOUNTERS);
	}

	public IStringSpectrum getOneDExpChannelsAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_ONEDEXPCHANNELS);
	}

	public IStringSpectrum getTwoDExpChannelsAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_TWODEXPCHANNELS);
	}
	
	public IStringSpectrum getChannelsAttributeModel()
	{
		return (IStringSpectrum)eventAttributes.get(getDeviceName() + "/" + DevicePoolUtils.MEASUREMENT_GROUP_ATTR_CHANNELS);
	}
	
	public void addNewExpChannel(ExperimentChannel channel) throws DevFailed
	{
		DeviceData data = new DeviceData();
		data.insert(channel.getName());
		getDevice().command_inout("AddExpChannel",data);
	}

	public void removeExpChannel(ExperimentChannel channel) throws DevFailed
	{
		DeviceData data = new DeviceData();
		data.insert(channel.getName());
		getDevice().command_inout("RemoveExpChannel",data);
	}

	public void setTimer(CounterTimer ct)
	{
		DeviceAttribute attr = new DeviceAttribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_TIMER,ct.getName());
		try 
		{
			device.write_attribute(attr);
		} 
		catch (DevFailed e) 
		{
			e.printStackTrace();
		}
	}
	
	public CounterTimer getTimer()
	{
		if(timer == null)
		{
			try 
			{
				String channel = device.read_attribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_TIMER).extractString();
				
				if(channel.equalsIgnoreCase(TimerNotInitialized.getName()))
				{
					timer = TimerNotInitialized;
				}
				else 
				{
					timer = null;
					for(ExperimentChannel ch : channels)
					{
						if(ch.getName().equalsIgnoreCase(channel))
						{
							assert(ch instanceof CounterTimer);
							timer = (CounterTimer) ch;
						}
					}
					if(timer == null)
					{
						log.warning("timer channel "+channel+" not found for "+getName()+" from list of channels:"+getChannels());
					}
				}
			} 
			catch (DevFailed e) 
			{
				log.warning("Error trying to get Timer channel from " + getName());
			}
		}
		return timer;
	}

	public void setMonitor(CounterTimer ct)
	{
		DeviceAttribute attr = new DeviceAttribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_MONITOR,ct.getName());
		
		try 
		{
			device.write_attribute(attr);
		} 
		catch (DevFailed e) 
		{
			e.printStackTrace();
		}
	}

	public CounterTimer getMonitor()
	{
		if(monitor == null)
		{
			try 
			{
				String channel = device.read_attribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_MONITOR).extractString();
				
				if(channel.equalsIgnoreCase(MonitorNotInitialized.getName()))
				{
					monitor = MonitorNotInitialized;
				}
				else
				{
					monitor = null;
					for(ExperimentChannel ch : channels)
					{
						if(ch.getName().equalsIgnoreCase(channel))
						{
							assert(ch instanceof CounterTimer);
							monitor = (CounterTimer) ch;
						}
					}
					if(monitor == null)
					{
						log.warning("monitor channel "+channel+" not found for "+getName()+" from list of channels:"+getChannels());
					}
				}
			} 
			catch (DevFailed e) 
			{
			}
		}		
		return monitor;
	}
	
	public void setIntegrationTime(double newITime) 
	{
		DeviceAttribute attr =  new DeviceAttribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_TIME,newITime);
		try 
		{
			device.write_attribute(attr);
		} 
		catch (DevFailed e) 
		{
			e.printStackTrace();
		}
	}
	
	public double getIntegrationTime()
	{
		if(i_time == Double.MIN_VALUE)
		{
			try 
			{
				i_time = device.read_attribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_TIME).extractDouble();
			} 
			catch (DevFailed e) 
			{
				i_time = -1.0;
			}
		}			
		return i_time;
	}
	
	public void setIntegrationCount(int newICount) 
	{
		DeviceAttribute attr = new DeviceAttribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_COUNT,newICount);
		try 
		{
			device.write_attribute(attr);
		} 
		catch (DevFailed e) 
		{
			e.printStackTrace();
		}
	}
	
	public int getIntegrationCount()
	{
		if(i_count == Integer.MIN_VALUE)
		{
			try 
			{
				i_count = device.read_attribute(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_COUNT).extractLong();
			} 
			catch (DevFailed e) 
			{
				i_count = -1;
			}
		}			
		return i_count;
	}

	public void addTimerListener(IStringScalarListener listener)
	{
		if(listener != null)
			timerListeners.add(listener);
	}

	public void removeTimerListener(IStringScalarListener listener)
	{
		if(listener != null)
			timerListeners.remove(listener);
	}

	public void addMonitorListener(IStringScalarListener listener)
	{
		if(listener != null)
			monitorListeners.add(listener);
	}

	public void removeMonitorListener(IStringScalarListener listener)
	{
		if(listener != null)
			monitorListeners.remove(listener);
	}

	public void addIntegrationTimeListener(INumberScalarListener listener)
	{
		if(listener != null)
			iTimeListeners.add(listener);
	}

	public void removeIntegrationTimeListener(INumberScalarListener listener)
	{
		if(listener != null)
			iTimeListeners.remove(listener);
	}	

	public void addIntegrationCountListener(INumberScalarListener listener)
	{
		if(listener != null)
			iCountListeners.add(listener);
	}

	public void removeIntegrationCountListener(INumberScalarListener listener)
	{
		if(listener != null)
			iCountListeners.remove(listener);
	}
	
	public void addCountersListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			counterListListeners.add(listener);
	}

	public void removeCountersListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			counterListListeners.remove(listener);
	}	

	public void addZeroDExpChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			zerodListListeners.add(listener);
	}

	public void removeZeroDExpChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			zerodListListeners.remove(listener);
	}	

	public void addPseudoCountersListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			pcListListeners.add(listener);
	}

	public void removePseudoCountersListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			pcListListeners.remove(listener);
	}	
	
	public void addOneDExpChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			onedListListeners.add(listener);
	}

	public void removeOneDExpChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			onedListListeners.remove(listener);
	}
	
	public void addTwoDExpChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			twodListListeners.add(listener);
	}

	public void removeTwoDExpChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			twodListListeners.remove(listener);
	}	
	
	public void addChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			channelListListeners.add(listener);
	}

	public void removeChannelsListener(IStringSpectrumListener listener)
	{
		if(listener != null)
			channelListListeners.remove(listener);
	}	

	@Override
	protected void initAttributeSemantics()
	{
		super.initAttributeSemantics();
		
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_COUNT);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_INTEGRATION_TIME);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_TIMER);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_MONITOR);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_COUNTERS);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_ZERODEXPCHANNELS);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_PSEUDOCOUNTERS);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_ONEDEXPCHANNELS);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_TWODEXPCHANNELS);
		eventAttributeList.add(DevicePoolUtils.MEASUREMENT_GROUP_ATTR_CHANNELS);
		
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
			
			/*
			if(attr.endsWith("_value"))
			{
				eventAttributeList.add(attr);
			}
			else*/
			{
				nonPolledAttributeList.add(attr.name);
			}		
		}
	}
	
	@Override
	protected void initAttributes() throws ConnectionException 
	{
		super.initAttributes();
		
		getTimerAttributeModel().addStringScalarListener(timerListener);
		getMonitorAttributeModel().addStringScalarListener(monitorListener);
		getIntegrationTimeAttributeModel().addNumberScalarListener(iTimeListener);
		getIntegrationCountAttributeModel().addNumberScalarListener(iCountListener);
		getCountersAttributeModel().addListener(counterListListener);
		getZeroDExpChannelsAttributeModel().addListener(zerodListListener);
		getPseudoCountersAttributeModel().addListener(pcListListener);
		getOneDExpChannelsAttributeModel().addListener(onedListListener);
		getTwoDExpChannelsAttributeModel().addListener(twodListListener);
		getChannelsAttributeModel().addListener(channelsListListener);
	}

	public List<CounterTimer> getCounterTimers() 
	{
		return cts;
	}
	
	public void addCounterTimer(CounterTimer ct) 
	{
		cts.add(ct);
	}

	public void addChannel(ExperimentChannel channel)
	{
		channels.add(channel);
	}

	public List<ExperimentChannel> getChannels()
	{
		return channels;
	}
	
	public void addGenericChannel(ExperimentChannel channel)
	{
		if(channel instanceof CounterTimer)
		{
			addCounterTimer((CounterTimer)channel);
		}
		else if(channel instanceof ZeroDExpChannel)
		{
			addZeroDExpChannel((ZeroDExpChannel)channel);
		}else if(channel instanceof OneDExpChannel)
		{
			addOneDExpChannel((OneDExpChannel)channel);
		}else if(channel instanceof TwoDExpChannel)
		{
			addTwoDExpChannel((TwoDExpChannel)channel);
		}
		else if(channel instanceof PseudoCounter)
		{
			addPseudoCounter((PseudoCounter)channel);
		}
		
		addChannel(channel);
	}
	
	public List<ZeroDExpChannel> getZeroDExpChannels() 
	{
		return zerods;
	}
	
	public void addZeroDExpChannel(ZeroDExpChannel zerod) 
	{
		zerods.add(zerod);
	}

	public List<OneDExpChannel> getOneDExpChannels() 
	{
		return oneds;
	}
	
	public void addOneDExpChannel(OneDExpChannel oned) 
	{
		oneds.add(oned);
	}

    public List<TwoDExpChannel> getTwoDExpChannels() 
	{
		return twods;
	}
	
	public void addTwoDExpChannel(TwoDExpChannel twod) 
	{
		twods.add(twod);
	}
	public List<PseudoCounter> getPseudoCounters() 
	{
		return pcs;
	}	
	
	public void addPseudoCounter(PseudoCounter pc) 
	{
		pcs.add(pc);
	}	

	@Override
	public boolean equals(Object obj) 
	{
		if(! (obj instanceof MeasurementGroup)) 
			return false;
		return super.equals(obj); 
	}
	
	protected abstract class DefaultStringScalarListener implements IStringScalarListener
	{
		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}	
	}

	protected abstract class DefaultNumberScalarListener implements INumberScalarListener
	{
		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}
	
	protected abstract class DefaultStringSpectrumListener implements IStringSpectrumListener
	{
		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}

	protected class TimerListener extends DefaultStringScalarListener
	{
		public void stringScalarChange(StringScalarEvent e)
		{
			String channel = e.getValue();
			if(channel.equalsIgnoreCase(TimerNotInitialized.getName()))
			{
				timer = TimerNotInitialized;
			}
			else
			{
				timer = null;
				for(CounterTimer ct :cts)
				{
					if(ct.getName().equalsIgnoreCase(channel))
						timer = ct;
				}
			}

			for(IStringScalarListener listener : timerListeners)
				listener.stringScalarChange(e);
		}	
	}
	
	protected class MonitorListener extends DefaultStringScalarListener
	{
		public void stringScalarChange(StringScalarEvent e) 
		{
			String channel = e.getValue();
			
			if(channel.equalsIgnoreCase(MonitorNotInitialized.getName()))
			{
				monitor = MonitorNotInitialized;
			}
			else
			{
				monitor = null;
				for(CounterTimer ct :cts)
				{
					if(ct.getName().equalsIgnoreCase(channel))
						monitor = ct;
				}
			}
			
			for(IStringScalarListener listener : monitorListeners)
				listener.stringScalarChange(e);
		}
	}
	
	protected class ITimeListener extends DefaultNumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent e) 
		{
			i_time = e.getValue();
			
			for(INumberScalarListener listener : iTimeListeners)
				listener.numberScalarChange(e);			
		}
	}
	
	protected class ICountListener extends DefaultNumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent e) 
		{
			i_count = (int)e.getValue();

			for(INumberScalarListener listener : iCountListeners)
				listener.numberScalarChange(e);			
		}
	}

	protected class ChannelListListener extends DefaultStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			channels.clear();
			
			String channel_names[] = e.getValue();
			
			for(String channel_name : channel_names)
			{
				channels.add(pool.getExperimentChannel(channel_name));
			}
			
			for(IStringSpectrumListener listener : channelListListeners)
				listener.stringSpectrumChange(e);
		}
	}	
	
	protected class CounterListListener extends DefaultStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			cts.clear();
			
			String channel_names[] = e.getValue();
			
			for(String channel_name : channel_names)
				cts.add((CounterTimer) pool.getExperimentChannel(channel_name));

			for(IStringSpectrumListener listener : counterListListeners)
				listener.stringSpectrumChange(e);
		}
	}
	
	protected class ZeroDExpChannelListListener extends DefaultStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			zerods.clear();
			
			String channel_names[] = e.getValue();
			
			for(String channel_name : channel_names)
				zerods.add((ZeroDExpChannel)pool.getExperimentChannel(channel_name));

			for(IStringSpectrumListener listener : zerodListListeners)
				listener.stringSpectrumChange(e);
		}
	}
	
	protected class PseudoCounterListListener extends DefaultStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			pcs.clear();
			
			String channel_names[] = e.getValue();
			
			for(String channel_name : channel_names)
				pcs.add((PseudoCounter)pool.getExperimentChannel(channel_name));

			for(IStringSpectrumListener listener : pcListListeners)
				listener.stringSpectrumChange(e);
		}
	}	
	
	protected class OneDExpChannelListListener extends DefaultStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			   
			oneds.clear();
			
			String channel_names[] = e.getValue();
			
			for(String channel_name : channel_names)
				oneds.add((OneDExpChannel)pool.getExperimentChannel(channel_name));

			for(IStringSpectrumListener listener : onedListListeners)
				listener.stringSpectrumChange(e);
		   
		}
	}
	
	protected class TwoDExpChannelListListener extends DefaultStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
		  
			
			twods.clear();
			
			String channel_names[] = e.getValue();
			
			for(String channel_name : channel_names)
				twods.add((TwoDExpChannel)pool.getExperimentChannel(channel_name));
			
			for(IStringSpectrumListener listener : twodListListeners)
				listener.stringSpectrumChange(e);
			
		}
	}
}
