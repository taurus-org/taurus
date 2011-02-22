package es.cells.sardana.client.framework.gui.atk.utils;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;

import fr.esrf.TangoApi.AttributeInfoEx;

public class AttributeNameSorter extends AbstractAttributeSorter
{
	
	public AttributeNameSorter(AttributeSorter nextSorter)
	{
		super(nextSorter);
	}

	@Override
	public void setNextSorter(AttributeSorter nextSorter)
	{
		this.nextSorter = null;
	}

	public class ComparatorAttrInfoEx implements Comparator<AttributeInfoEx>
	{
		public int compare(AttributeInfoEx o1, AttributeInfoEx o2)
		{
			return o1.name.compareTo(o2.name);
		}
	}

	public ArrayList<AttributeInfoEx> sort(Collection<AttributeInfoEx> attrList)
	{
		ArrayList<AttributeInfoEx> newAttrList = new ArrayList<AttributeInfoEx>(attrList);
		
		Collections.sort(newAttrList, new ComparatorAttrInfoEx());
		
		return newAttrList;
	}

}
