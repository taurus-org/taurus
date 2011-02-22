package es.cells.sardana.client.framework;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.xmlbeans.XmlException;
import org.apache.xmlbeans.XmlObject;
import org.tango.config.Device;

import es.cells.sardana.client.framework.config.ExpChannel;
import es.cells.sardana.client.framework.config.MeasurementGroup;
import es.cells.sardana.client.framework.config.Motor;
import es.cells.sardana.client.framework.config.MotorGroup;
import es.cells.sardana.client.framework.config.Pool;
import es.cells.sardana.client.framework.config.PoolServer;
import es.cells.sardana.client.framework.config.PseudoMotor;
import es.cells.sardana.client.framework.config.SardanaDocument;
import es.cells.sardana.client.framework.pool.Machine;
import fr.esrf.TangoApi.Database;
import fr.esrf.tangoatk.core.DeviceFactory;

public class SardanaConfigLoader 
{
	protected File file;
	protected Machine machine;
	
	public SardanaConfigLoader(File f, Machine m)
	{
		this.machine = m;
		this.file = f;
	}
	
	public SardanaDocument load() throws XmlException, IOException
	{
		return SardanaDocument.Factory.parse(file);
	}

	protected SardanaDocument currDoc;
	protected List<AbstractItem> currItems;
	
	public void loadToMachine(SardanaDocument doc)
	{
		currDoc = doc;
		currItems = new ArrayList<AbstractItem>();
		
		//TODO
	}
	
	public List<AbstractItem> check() 
	{
		currItems.clear();
		
		for(PoolServer xmlPoolServer : currDoc.getSardana().getPoolServerList())
		{
			assert(xmlPoolServer.sizeOfDeviceArray() == 1);
			
			Device xmlDevice = xmlPoolServer.getDeviceArray(0);
			
			assert(xmlDevice instanceof Pool);
			
			Pool xmlPool = (Pool) xmlDevice;
			
			checkDevice(xmlPool);

			for(Motor xmlMotor : xmlPool.getMotorList())
			{
				checkDevice(xmlMotor);
			}

			for(MotorGroup xmlMotorGroup : xmlPool.getMotorGroupList())
			{
				checkDevice(xmlMotorGroup);
			}
			
			for(PseudoMotor xmlPseudoMotor : xmlPool.getPseudoMotorList())
			{
				checkDevice(xmlPseudoMotor);
			}

			for(ExpChannel xmlChannel : xmlPool.getCTExpChannelList())
			{
				checkDevice(xmlChannel);
			}
			
			for(ExpChannel xmlChannel : xmlPool.getZeroDExpChannelList())
			{
				checkDevice(xmlChannel);
			}
			
			for(ExpChannel xmlChannel : xmlPool.getOneDExpChannelList())
			{
				checkDevice(xmlChannel);
			}

			for(ExpChannel xmlChannel : xmlPool.getTwoDExpChannelList())
			{
				checkDevice(xmlChannel);
			}
			
			for(MeasurementGroup xmlMeasurementGroup : xmlPool.getMeasurementGroupList())
			{
				checkDevice(xmlMeasurementGroup);
			}

		}
		
		return currItems;
	}
	
	public void checkDevice(org.tango.config.Device device)
	{
		String deviceName = device.getDeviceName();
			
		if(!isDeviceNameValid(deviceName))
		{
			currItems.add(new InvalidDeviceName(device));
		}
		else
		{	
			if(isDevice(deviceName))
			{
				currItems.add(new DeviceNameExists(device));
			}
		}
			
		String alias = device.getAlias();
		
		if(alias != null && alias.length() > 0)
		{
			if(isDevice(alias))
			{
				currItems.add(new DeviceAliasExists(device));
			}
		}
	}
	
	
	/**
	 * Check weather the given name correspond to an existing device.
	 * @param deviceName Device name.
	 * @return true if the device exists.
	 */
	public boolean isDevice(String deviceName) 
	{
		try 
		{
			DeviceFactory.getInstance().getDevice(deviceName);
		} 
		catch (Exception e) 
		{
			return false;
		}

		return true;
	}
	
	public boolean isDeviceNameValid(String deviceName)
	{
		if(deviceName == null || 
		   deviceName.length() < 1)
			return false;
		
		String[] elems = deviceName.split("/");
		
		if(elems.length != 3) return false;
		
		for(String s:elems) 
			if(s.length() < 1) 
			return false;
		
		return true;
	}
	
	public abstract class AbstractItem
	{
		public XmlObject source;
		
		public AbstractItem(XmlObject source) 
		{
			this.source = source;
		}
		
		public abstract String getDescription();
	}
	
	public class WarningItem extends AbstractItem
	{
		public WarningItem(XmlObject source) 
		{
			super(source);
		}

		@Override
		public String getDescription() 
		{
			return "Generic warning";
		}
	}
	
	public class ErrorItem extends AbstractItem
	{
		public ErrorItem(XmlObject source) 
		{
			super(source);
		}

		@Override
		public String getDescription() 
		{
			return "Generic error";
		}
		
	}
	
	public class InvalidDeviceName extends ErrorItem
	{
		public InvalidDeviceName(XmlObject source) 
		{
			super(source);
		}

		@Override
		public String getDescription() 
		{
			org.tango.config.Device d = (org.tango.config.Device) source;
			return "The name '" + d.getDeviceName() + "' is not a valid device name";
		}
	}

	public class DeviceNameExists extends ErrorItem
	{
		public DeviceNameExists(XmlObject source) 
		{
			super(source);
		}

		@Override
		public String getDescription() 
		{
			return null;
		}
	}
	
	public class DeviceAliasExists extends ErrorItem
	{
		public DeviceAliasExists(XmlObject source) 
		{
			super(source);
		}

		@Override
		public String getDescription() 
		{
			return null;
		}
	}	
}
