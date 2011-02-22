package es.cells.sardana.client.framework.gui.atk.utils;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoDs.TangoConst;

public class AttributeTypeSorter extends AbstractAttributeSorter
{
	public AttributeTypeSorter(AttributeSorter nextSorter)
	{
		super(nextSorter);
	}

	public List<AttributeInfoEx> sort(Collection<AttributeInfoEx> attrList)
	{
		final int splitCount = 5;
		
		ArrayList<ArrayList<AttributeInfoEx>> tmp = new ArrayList<ArrayList<AttributeInfoEx>>(splitCount);
		
		for(int i = 0; i < splitCount;i++) tmp.add(new ArrayList<AttributeInfoEx>());
		
		for(AttributeInfoEx info : attrList)
		{
			int index = -1;
			if(info.data_type == TangoConst.Tango_DEV_BOOLEAN ||
			   info.data_type == 19) // DEVVAR_BOOLEANARRAY
				index = 0;
			else if(info.data_type == TangoConst.Tango_DEV_LONG ||
					info.data_type == TangoConst.Tango_DEVVAR_LONGARRAY)
				index = 1;
			else if(info.data_type == TangoConst.Tango_DEV_DOUBLE ||
					info.data_type == TangoConst.Tango_DEVVAR_DOUBLEARRAY)
				index = 2;
			else if(info.data_type == TangoConst.Tango_DEV_STRING ||
					info.data_type == TangoConst.Tango_DEVVAR_STRINGARRAY)
				index = 3;
			else
				index = 4;
			
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
