package es.cells.sardana.light;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.util.ArrayList;
import java.util.HashMap;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.JPanel;

import es.cells.sardana.light.model.AquisitionElement;
import es.cells.sardana.light.model.CounterTimer;
import es.cells.sardana.light.model.MeasurementGroup;
import es.cells.sardana.light.model.ZeroDExpChannel;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.IEntity;
import fr.esrf.tangoatk.core.INumberImage;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;

public class DataAquisitionPanel extends JPanel 
{
	Device pool;
	
	HashMap<String, AquisitionElement> aqElements = new HashMap<String, AquisitionElement>();
	ArrayList<AquisitionElement> aqElementArray = new ArrayList<AquisitionElement>();
	ArrayList<CounterTimer> ctDeviceNames = new ArrayList<CounterTimer>();
	ArrayList<ZeroDExpChannel> zeroDDeviceNames = new ArrayList<ZeroDExpChannel>();
	//ArrayList<OneDExpChannel> oneDDeviceNames = new ArrayList<OneDExpChannel>();
	//ArrayList<TwoDExpChannel> twoDDeviceNames = new ArrayList<TwoDExpChannel>();
	ArrayList<MeasurementGroup> mgDeviceNames = new ArrayList<MeasurementGroup>();
	
	AttributeList stateAttributes;
	AttributeList valueAttributes;
	
	public DataAquisitionPanel(Device devicePool) 
	{
		super();
		
		this.pool = devicePool;
		
		try 
		{
			DeviceAttribute expchannel_list_attr = pool.read_attribute("ExpChannelList");
			DeviceAttribute mg_list_attr = pool.read_attribute("MeasurementGroupList");
			
			String[] expchannel_list = expchannel_list_attr.extractStringArray();
			String[] mg_list = mg_list_attr.extractStringArray();
			
			for(String full_expchannel : expchannel_list)
			{
				String[] elems = full_expchannel.split(" ");
				
				String expChannelAlias = elems[0].trim();
				String expChannelDeviceName = elems[1].trim();
				expChannelDeviceName = expChannelDeviceName.substring(1, expChannelDeviceName.indexOf(')'));
				String type = elems[2].trim();
				
				if(type.equals("Counter/Timer"))
				{
					CounterTimer ct = new CounterTimer(expChannelAlias,expChannelDeviceName);
					ctDeviceNames.add(ct);
					aqElements.put(expChannelAlias, ct);
					aqElementArray.add(ct);
				}
				else if(type.equals("Zero"))
				{
					ZeroDExpChannel zeroD = new ZeroDExpChannel(expChannelAlias,expChannelDeviceName);
					zeroDDeviceNames.add(zeroD);
					aqElements.put(expChannelAlias, zeroD);
					aqElementArray.add(zeroD);
				}
				else if(type.equals("One"))
				{
					
				}
				else if(type.equals("Two"))
				{
					
				}
				else
				{
					System.out.println("Unknown channel type: " + type);
					System.exit(-1);
				}
			}
			
			for(String full_mg : mg_list)
			{
				String[] elems = full_mg.split(" ");
				
				String mgAlias = elems[0].trim();
				String mgDeviceName = elems[1].trim();
				mgDeviceName = mgDeviceName.substring(1, mgDeviceName.indexOf(')'));

				String[] user_elems = new String[elems.length - 4];
				
				int idx = 0;
				for(int i = 4; i < elems.length; i++)
				{
					String mg_elem = elems[i].trim();
					int comma = mg_elem.indexOf(',');
					if(comma >= 0)
						mg_elem = mg_elem.substring(0,comma);
					user_elems[idx++] = mg_elem;
				}
				
				MeasurementGroup mg = new MeasurementGroup(mgAlias,mgDeviceName,user_elems);
				mg.valueAttributes = new IEntity[elems.length - 4];
				
				mgDeviceNames.add(mg);
				aqElements.put(mgAlias, mg);
				aqElementArray.add(mg);
			}
		}
		catch (DevFailed e) 
		{
			e.printStackTrace();
			System.exit(-2);
		}
		
		initComponents();
		initAttributes();		
	}

	private void initAttributes() 
	{
		stateAttributes = new AttributeList();
		valueAttributes = new AttributeList();

		for(int i = 0; i < aqElementArray.size(); i++)
		{
			AquisitionElement m = aqElementArray.get(i);
			
			try
			{   
				DevStateScalar state = (DevStateScalar) stateAttributes.add(m.deviceName + "/state");
				state.addDevStateScalarListener(m.stateListener);
			}
			catch (Exception e)
			{
				System.out.println("Error creating state attribute for " + m.deviceName);
				System.exit(-3);
			}
		}
		
		for(int i = 0; i < ctDeviceNames.size(); i++)
		{
			CounterTimer m = ctDeviceNames.get(i);
			try
			{
				IEntity entity = valueAttributes.add(m.deviceName + "/value");
				
				INumberScalar valueAttr = (INumberScalar)entity;
				valueAttr.addNumberScalarListener(m.valueListener);
				m.valueAttribute = entity;
			}
			catch (Exception e)
			{
				System.out.println("Error creating value attribute. Exiting...");
				System.exit(-4);
			}
		}
		
		for(int i = 0; i < mgDeviceNames.size(); i++)
		{
			MeasurementGroup mg = mgDeviceNames.get(i);
			
			try
			{
				INumberScalar itime = (INumberScalar) valueAttributes.add(mg.deviceName + "/Integration_time");
				INumberScalar icount = (INumberScalar) valueAttributes.add(mg.deviceName + "/Integration_count");
				IStringScalar timer = (IStringScalar) valueAttributes.add(mg.deviceName + "/Timer");
				IStringScalar monitor = (IStringScalar) valueAttributes.add(mg.deviceName + "/Monitor");
				
				mg.integrationTime = itime;
				mg.integrationCount = icount;
				mg.timer = timer;
				mg.monitor = monitor;
				
				itime.addNumberScalarListener(mg.integrationTimeListener);
				icount.addNumberScalarListener(mg.integrationCountListener);
				timer.addStringScalarListener(mg.timertListener);
				monitor.addStringScalarListener(mg.monitortListener);
			}
			catch (Exception e)
			{
				System.out.println("Error creating measurement group attribute. Exiting...");
				System.exit(-4);
			}			
			
			int zeroD_index = 0;
			for(int j = 0; j < mg.user_elems.length; j++)
			{
				try
				{
					IEntity entity = valueAttributes.add(mg.deviceName + "/" + mg.user_elems[j] + "_value");
					
					if(entity instanceof INumberScalar)
					{
						INumberScalar valueAttr = (INumberScalar)entity;
						valueAttr.addNumberScalarListener(mg.valueListeners[zeroD_index]);
						zeroD_index++;
					}
					else if(entity instanceof INumberSpectrum)
					{
						INumberSpectrum valueAttr = (INumberSpectrum)entity;
						valueAttr.addSpectrumListener(mg.valueArrayListener);
					}
					else if(entity instanceof INumberImage)
					{
						INumberImage valueAttr = (INumberImage)entity;
						//valueAttr.addImageListener(null);
					}
					
					mg.valueAttributes[j] = entity;
					
					if(j == 0)
						mg.valueAttribute = entity;
				}
				catch (Exception e)
				{
					System.out.println("Error creating value attribute. Exiting...");
					System.exit(-4);
				}
			}
		}
	}

	private void initComponents() 
	{
		setLayout(new GridBagLayout());
		
		GridBagConstraints gbc = new GridBagConstraints(
				0, 0, // grid
				1, 1, // width,height
				1.0, 0.20, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.BOTH, // fill
				new Insets(0,0,0,0),
				0,0 // pad
				);		
		
		JPanel ctPanel = new JPanel();
		ctPanel.setLayout(new BoxLayout(ctPanel,BoxLayout.Y_AXIS));
		ctPanel.setBorder(BorderFactory.createTitledBorder("Counter/Timers"));
		add(ctPanel, gbc);

		gbc = new GridBagConstraints(
				0, 1, // grid
				1, 1, // width,height
				1.0, 0.20, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.BOTH, // fill
				new Insets(0,0,0,0),
				0,0 // pad
				);		
		
		JPanel zeroDPanel = new JPanel();
		zeroDPanel.setLayout(new BoxLayout(zeroDPanel,BoxLayout.Y_AXIS));
		zeroDPanel.setBorder(BorderFactory.createTitledBorder("0D Experiment Channels"));
		add(zeroDPanel, gbc);

		gbc = new GridBagConstraints(
				0, 2, // grid
				1, 1, // width,height
				1.0, 0.20, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.BOTH, // fill
				new Insets(0,0,0,0),
				0,0 // pad
				);
		
		JPanel oneDPanel = new JPanel();
		oneDPanel.setLayout(new BoxLayout(oneDPanel,BoxLayout.Y_AXIS));
		oneDPanel.setBorder(BorderFactory.createTitledBorder("1D Experiment Channels"));
		add(oneDPanel, gbc);
		
		gbc = new GridBagConstraints(
				0, 3, // grid
				1, 1, // width,height
				1.0, 0.20, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.BOTH, // fill
				new Insets(0,0,0,0),
				0,0 // pad
				);
		
		JPanel twoDPanel = new JPanel();
		twoDPanel.setLayout(new BoxLayout(twoDPanel,BoxLayout.Y_AXIS));
		twoDPanel.setBorder(BorderFactory.createTitledBorder("2D Experiment Channels"));
		add(twoDPanel, gbc);
		
		gbc = new GridBagConstraints(
				0, 4, // grid
				1, 1, // width,height
				1.0, 0.20, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.BOTH, // fill
				new Insets(0,0,0,0),
				0,0 // pad
				);
		
		JPanel mgPanel = new JPanel();
		mgPanel.setLayout(new BoxLayout(mgPanel,BoxLayout.Y_AXIS));
		mgPanel.setBorder(BorderFactory.createTitledBorder("Measurement Groups"));
		add(mgPanel, gbc);
		
		for(CounterTimer ct : ctDeviceNames)
			ctPanel.add(ct.elementPanel);

		for(ZeroDExpChannel zeroD : zeroDDeviceNames)
			zeroDPanel.add(zeroD.elementPanel);

		for(MeasurementGroup mg : mgDeviceNames)
			mgPanel.add(mg.elementPanel);
		
		/*
		for(OneDExpChannel oneD : oneDDeviceNames)
			oneDPanel.add(oneD.elementPanel);

		for(TwoDExpChannel twoD : twoDDeviceNames)
			twoDPanel.add(twoD.elementPanel);
		*/
	}
}
