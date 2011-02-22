package es.cells.tangoatk.utils;

import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class DefaultStringSplitter implements IStringSplitter
{
	protected Pattern pattern;
	protected int[] patternGroups;
	
	protected IStringFilter filter;
	protected int columnIndex;
	
	public IStringFilter getFilter()
	{
		return filter;
	}

	public void setFilter(IStringFilter filter)
	{
		this.filter = filter;
	}
	
	/**
	 * 
	 * @param pattern the pattern which will decide how the string will be split
	 * @param patternGroups The element indexes of the split which will be returned after a split operation. 
	 *                      If null is given then all elements found will be returned.
	 */
	public DefaultStringSplitter(Pattern pattern, int[] patternGroups)
	{
		this(pattern, patternGroups, null, -1);
	}
	
	public DefaultStringSplitter(Pattern pattern, int[] patternGroups, IStringFilter filter, int columnIndex)
	{
		this.pattern = pattern;
		this.patternGroups = patternGroups;
		this.filter = filter;
		this.columnIndex = columnIndex;
	}
	
	public String[] split(String str)
	{
		if(pattern == null)
			return new String[] { str };

		String[] elems = rawSplit(str);
		
		if(elems == null)
			return null;

		int col = columnIndex < 0 ? 0 : columnIndex; 
		
		if(!isValid(elems[col]))
			return null;
		
		if(patternGroups != null && patternGroups.length <= 1)
			return new String[] { str };
		
		return elems;
	}

	protected String[] rawSplit(String str)
	{
		if(patternGroups != null)
		{
			Matcher matcher = pattern.matcher(str);
			
			if(!matcher.matches())
				return null;

			int len = Math.min(matcher.groupCount(), patternGroups.length);
			String[] columns = new String[len];
		
			for(int matchIndex = 0; matchIndex < len; matchIndex++)
				columns[matchIndex] = matcher.group(patternGroups[matchIndex]);
			
			return columns;
		}
		else
		{
			return pattern.split(str);
		}
	}
	
	public boolean isValid(String str)
	{
		if(filter == null || columnIndex < 0)
			return true;
		
		return filter.isValid(str);
	}
}
