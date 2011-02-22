package es.cells.sardana.client.framework.pool;

public enum ControllerType 
{
	InvalidControllerType,
	Motor,
	CounterTimer,
	ZeroDExpChannel,
	OneDExpChannel,
	TwoDExpChannel,
	Communication,
	PseudoMotor,
	PseudoCounter,
    IORegister;

	@Override
	public String toString()
	{
		return super.toString();
	}
	
	
}
