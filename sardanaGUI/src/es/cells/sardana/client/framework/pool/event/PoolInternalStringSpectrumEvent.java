package es.cells.sardana.client.framework.pool.event;

import es.cells.sardana.client.framework.pool.DevicePool;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class PoolInternalStringSpectrumEvent extends StringSpectrumEvent 
{
	DevicePool pool;
	
	static final EmptyStringSpectrum EmptySource = new EmptyStringSpectrum();
	
	public PoolInternalStringSpectrumEvent(DevicePool source)
	{
		super(EmptySource, EmptySource.getStringSpectrumValue(), 0);
		pool = source;
	}

	public DevicePool getPool()
	{
		return pool;
	}

}
