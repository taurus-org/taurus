package es.cells.sardana.client.framework.gui.atk.utils;


public abstract class AbstractAttributeSorter implements AttributeSorter
{

	AttributeSorter nextSorter = null;
	
	public AbstractAttributeSorter(AttributeSorter nextSorter)
	{
		setNextSorter(nextSorter);
	}
	
	public void setNextSorter(AttributeSorter nextSorter)
	{
		this.nextSorter = nextSorter;
	}

	public AttributeSorter getNextSorter()
	{
		return nextSorter;
	}
}
