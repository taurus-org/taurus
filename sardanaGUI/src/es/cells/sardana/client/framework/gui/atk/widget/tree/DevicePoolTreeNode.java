package es.cells.sardana.client.framework.gui.atk.widget.tree;

import es.cells.sardana.client.framework.pool.DevicePool;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.attribute.BooleanScalar;

public class DevicePoolTreeNode extends GenericSardanaTreeNode
{
	protected BooleanScalar simulationMode;
	
	protected ControllersTreeNode controllersNode;
	protected ComChannelsTreeNode comChannelsNode;
    protected IORegistersTreeNode ioRegistersNode;
	protected MotorsTreeNode motorsNode;
	protected MotorGroupsTreeNode motorGroupsNode;
	protected ExpChannelsTreeNode expChannelsNode;
	protected MeasurementGroupsTreeNode measurementGroupsNode;
	
	public DevicePoolTreeNode(DevicePool userObject)
	{
		super(userObject);
	}

	public DevicePool getDevicePool()
	{
		return (DevicePool) getUserObject();
	}

	@Override
	public Object getUserObject()
	{
		return super.getUserObject();
	}

	public Device getModel()
	{
		return getDevicePool().getDevice();
	}
	
	public BooleanScalar getSimulationModeModel()
	{
		return simulationMode;
	}
	
	public void setSimulationModeModel(BooleanScalar simulationMode)
	{
		this.simulationMode = simulationMode;
	}
	
	public ControllersTreeNode getControllersNode()
	{
		return controllersNode;
	}

	public ComChannelsTreeNode getComChannelsNode()
	{
		return comChannelsNode;
	}

	public IORegistersTreeNode getIORegistersNode()
	{
		return ioRegistersNode;
	}

	public MotorGroupsTreeNode getMotorGroupsNode()
	{
		return motorGroupsNode;
	}

	public MotorsTreeNode getMotorsNode()
	{
		return motorsNode;
	}
	
	public ExpChannelsTreeNode getExpChannelsNode()
	{
		return expChannelsNode;
	}
	
	public MeasurementGroupsTreeNode getMeasurementGroupsNode()
	{
		return measurementGroupsNode;
	}

	/*
	public PseudoMotorsTreeNode getPseudoMotorsNode() 
	{
		return pseudoMotorsNode;
	}
	*/
	
	synchronized public void setControllersNode(ControllersTreeNode treeNode)
	{
		if(controllersNode != null && isNodeChild(controllersNode))
			remove(controllersNode);
		
		controllersNode = treeNode;
		
		add(controllersNode);
	}

	synchronized public void setComChannelsNode(ComChannelsTreeNode treeNode)
	{
		if(comChannelsNode != null && isNodeChild(comChannelsNode))
			remove(comChannelsNode);
		
		comChannelsNode = treeNode;
		
		add(comChannelsNode);
	}

	synchronized public void setIORegistersNode(IORegistersTreeNode treeNode)
	{
		if(ioRegistersNode != null && isNodeChild(ioRegistersNode))
			remove(ioRegistersNode);
		
		ioRegistersNode = treeNode;
		
		add(ioRegistersNode);
	}

	synchronized public void setMotorsNode(MotorsTreeNode treeNode)
	{
		if(motorsNode != null && isNodeChild(motorsNode))
			remove(motorsNode);
		
		motorsNode = treeNode;
		
		add(motorsNode);
	}
	
	synchronized public void setMotorGroupsNode(MotorGroupsTreeNode treeNode)
	{
		if(motorGroupsNode != null && isNodeChild(motorGroupsNode))
			remove(motorGroupsNode);
		
		motorGroupsNode = treeNode;
		
		add(motorGroupsNode);
	}
	
	synchronized public void setExpChannelsNode(ExpChannelsTreeNode treeNode)
	{
		if(expChannelsNode != null && isNodeChild(expChannelsNode))
			remove(expChannelsNode);
		
		expChannelsNode = treeNode;
		
		add(expChannelsNode);
	}
	
	synchronized public void setMeasurementGroupsNode(MeasurementGroupsTreeNode treeNode)
	{
		if(measurementGroupsNode != null && isNodeChild(measurementGroupsNode))
			remove(measurementGroupsNode);
		
		measurementGroupsNode = treeNode;
		
		add(measurementGroupsNode);
	}	
	/*
	synchronized public void setPseudoMotorsNode(PseudoMotorsTreeNode treeNode)
	{
		if(pseudoMotorsNode != null && isNodeChild(pseudoMotorsNode))
			remove(pseudoMotorsNode);
		
		pseudoMotorsNode = treeNode;
		
		add(pseudoMotorsNode);
	}
	*/
	
	@Override
	synchronized public void removeAllChildren()
	{
		controllersNode = null;
		motorsNode = null;
		motorGroupsNode = null;
		//pseudoMotorsNode = null;
		expChannelsNode = null;
		measurementGroupsNode = null;
		
		super.removeAllChildren();
		
	}

	public String getState()
	{
		return getDevicePool().getState();
	}
}
