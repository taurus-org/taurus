package es.cells.tangoatk.widget.attribute;

import javax.swing.DefaultListModel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.border.TitledBorder;

import es.cells.tangoatk.utils.IStringFilter;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

/**
 * This viewer is intended to be used with StringSpectrum Tango Attributes.
 * The widget is a simple JList. Each string element in the String Spectrum will
 * correspond to a single entry in the JList GUI Component.
 *   
 * @author tiago coutinho (tcoutinho@cells.es)
 *
 */
public class StringSpectrumListViewer extends JPanel implements IStringSpectrumListener
{
	/** The internal scroll pane will provide an always visible vertical scrollbar. */
    private javax.swing.JScrollPane    jScrollPane1;
    
    /** The GUI List component */
    private javax.swing.JList          strSpectList;
	
    /** The model. */
	IStringSpectrum                    model;

	IStringFilter                      filter;
	
	/**
	 * The default constructor
	 *
	 */
	public StringSpectrumListViewer()
	{
		initComponents();
	}

	/**
	 * Initialization of all graphical components.
	 */
	private void initComponents()
	{
		jScrollPane1 = new JScrollPane();
		strSpectList = new JList();
		
		setLayout(new java.awt.BorderLayout());

		strSpectList.setVisibleRowCount(5);
		strSpectList.setModel( new DefaultListModel() );
		
		setBorder(new javax.swing.border.TitledBorder("StringSpectrum"));
		jScrollPane1.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		
		strSpectList.setBackground(new java.awt.Color(204, 204, 204));
		jScrollPane1.setViewportView(strSpectList);

		add(jScrollPane1, java.awt.BorderLayout.CENTER);
		
		setTitle("Unknown");
	}
	
	/**
	 * Obtains the current model attached to the JList component.
	 * 
	 * @return The model associated with the JList component.
	 */
	private DefaultListModel getListModel()
	{ 
		return (DefaultListModel) strSpectList.getModel();
	}

	public IStringFilter getFilter()
	{
		return filter;
	}

	public void setFilter(IStringFilter filter)
	{
		this.filter = filter;
	}

	/**
	 * Sets the model of the this StringSpectrumListViewer.
	 * 
	 * @param strSpectAtt the model.
	 */
	public void setModel(IStringSpectrum  strSpectAtt)
	{
		getListModel().clear();
		
		this.model = strSpectAtt;
		
		if(model == null)
		{
			setTitle("Unknown");
			return;
		}

		setTitle(model.getNameSansDevice());
		model.addListener(this);
		model.refresh();
	}

	/**
	 * <code>getModel</code> gets the model of this StringSpectrumListViewer.
	 *
	 * @return a <code>IStringSpectrum</code> value
	 */
	public IStringSpectrum getModel()
	{
		return model;
	}
	
	/**
	 * Sets the title of the titled border for this component.
	 * 
	 * @param title the new title.
	 */
	protected void setTitle(String title)
	{
		TitledBorder border = ((TitledBorder)getBorder());
		
		if(border == null)
		{
			border = new TitledBorder(title);
			setBorder(border);
		}
		else
			border.setTitle(title);
	}

	/**
	 * Gets the current number of visible rows.
	 * 
	 * @return The current number of visible rows.
	 */
	public int getRows()
	{
		return strSpectList.getVisibleRowCount();
	}

	/**
	 * Sets the number of visible rows.
	 * 
	 * @param rows the number of visible rows.
	 */
	public void setRows(int rows)
	{
		strSpectList.setVisibleRowCount(rows);
	}

	/**
	 * Gets the List GUI component of this widget.
	 * 
	 * @return The GUI List compononent
	 */
	public JList getList()
	{
		return strSpectList;
	}

	/**
	 * Invoked by the model for which this viewer has been registered when
	 * the model changes.
	 * 
	 */
	public void stringSpectrumChange(StringSpectrumEvent evt)
	{
		int       ind_str, attr_size;
		
		if (evt.getValue() == null)
		{
			getListModel().addElement("StringSpectrumAttribute is null.\n");
		}
		else
		{
			String[]   str_array=null;

			str_array = evt.getValue();
			attr_size= str_array.length;

			for (ind_str=0; ind_str < attr_size; ind_str++)
			{
				if(filter == null || filter.isValid(str_array[ind_str]))
				{
					if(!getListModel().contains(str_array[ind_str])) 
					{
						getListModel().addElement(str_array[ind_str]);
					}
				}
			}
		}
	}

	public void errorChange(ErrorEvent evt)
	{

	}

	public void stateChange(AttributeStateEvent evt)
	{

	}

}
