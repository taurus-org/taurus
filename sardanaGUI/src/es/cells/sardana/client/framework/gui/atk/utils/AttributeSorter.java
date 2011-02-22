package es.cells.sardana.client.framework.gui.atk.utils;

import java.util.Collection;
import java.util.List;

import fr.esrf.TangoApi.AttributeInfoEx;

public interface AttributeSorter
{	
	public void setNextSorter(AttributeSorter nextSorter);
	public List<AttributeInfoEx> sort(Collection<AttributeInfoEx> attrList);
}
