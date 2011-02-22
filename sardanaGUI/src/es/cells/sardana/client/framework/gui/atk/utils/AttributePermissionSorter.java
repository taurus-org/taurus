package es.cells.sardana.client.framework.gui.atk.utils;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import fr.esrf.Tango.AttrWriteType;
import fr.esrf.TangoApi.AttributeInfoEx;

public class AttributePermissionSorter extends AbstractAttributeSorter
{
	public AttributePermissionSorter(AttributeSorter nextSorter)
	{
		super(nextSorter);
	}

	public List<AttributeInfoEx> sort(Collection<AttributeInfoEx> attrList)
	{
		final int splitCount = 2;
		
		ArrayList<ArrayList<AttributeInfoEx>> tmp = new ArrayList<ArrayList<AttributeInfoEx>>(splitCount);
		
		for(int i = 0; i < splitCount;i++) tmp.add(new ArrayList<AttributeInfoEx>());
		
		for(AttributeInfoEx info : attrList)
		{
			int index = -1;
			if(info.writable.value() == AttrWriteType._READ )
				index = 0;
			else
				index = 1;
			
			tmp.get(index).add(info);
		}
		
		ArrayList<AttributeInfoEx> ret = new ArrayList<AttributeInfoEx>(attrList.size());
		
		for(int i=0;i<splitCount;i++) 
		{
			List<AttributeInfoEx> nextOrder = nextSorter != null ? nextSorter.sort(tmp.get(i)) : tmp.get(i);
			ret.addAll(nextOrder);
		}
		
		return ret;
	}

}
