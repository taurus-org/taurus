package es.cells.tangoatk.utils;


public class DefaultStringFilter implements IStringFilter
{
	protected String filter;
	
	public DefaultStringFilter()
	{
		this(null);
	}
	
	public DefaultStringFilter(String filter)
	{
		this.filter = filter;
	}
	
	public boolean isValid(String str)
	{
		return filter == null || (str != null && filter.equals(str));
	}

	public String getFilter()
	{
		return filter;
	}

	public void setFilter(String filter)
	{
		this.filter = filter;
	}

	
}
