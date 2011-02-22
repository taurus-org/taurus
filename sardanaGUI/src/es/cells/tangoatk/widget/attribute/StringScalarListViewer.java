package es.cells.tangoatk.widget.attribute;

import javax.swing.DefaultListModel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringScalar;
import fr.esrf.tangoatk.core.IStringScalarListener;
import fr.esrf.tangoatk.core.StringScalarEvent;

/**
 * This viewer is intended to be used with String Tango Attributes.
 * The widget is a simple JList. The string will be splitted according
 * to a pattern splitter into several substrings. Each substring will
 * become an entry in the JList component.
 *   
 * @author tiago coutinho (tcoutinho@cells.es)
 *
 */
public class StringScalarListViewer extends JPanel implements IStringScalarListener 
{
	/** The internal scroll pane will provide an always visible vertical scrollbar. */
    private javax.swing.JScrollPane    jScrollPane1;
    
    /** The GUI List component */
    private javax.swing.JList          strList;
	
    /** The model. */
	IStringScalar                      model;

	IStringSplitter                    splitter;
	
	/**
	 * The default constructor
	 *
	 */
	public StringScalarListViewer()
	{
		initComponents();
	}

	/**
	 * Initialization of all graphical components.
	 */
	private void initComponents()
	{
		jScrollPane1 = new JScrollPane();
		strList = new JList();
		
		setLayout(new java.awt.BorderLayout());

		strList.setVisibleRowCount(5);
		strList.setModel( new DefaultListModel() );
		
		jScrollPane1.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		
		strList.setBackground(new java.awt.Color(204, 204, 204));
		jScrollPane1.setViewportView(strList);

		add(jScrollPane1, java.awt.BorderLayout.CENTER);	
	}
	
	/**
	 * Obtains the current model attached to the JList component.
	 * 
	 * @return The model associated with the JList component.
	 */
	private DefaultListModel getListModel()
	{ 
		return (DefaultListModel) strList.getModel();
	}

	public IStringSplitter getSplitter()
	{
		return splitter;
	}

	public void setSplitter(IStringSplitter splitter)
	{
		this.splitter = splitter;
	}	
	
	/**
	 * Sets the model of the this StringSpectrumListViewer.
	 * 
	 * @param strSpectAtt the model.
	 */
	public void setModel(IStringScalar  strtAtt)
	{
		getListModel().clear();
		
		this.model = strtAtt;
		
		if(model == null)
			return;

		model.addStringScalarListener(this);
		model.refresh();
	}

	/**
	 * <code>getModel</code> gets the model of this StringSpectrumListViewer.
	 *
	 * @return a <code>IStringSpectrum</code> value
	 */
	public IStringScalar getModel()
	{
		return model;
	}
	
	/**
	 * Gets the current number of visible rows.
	 * 
	 * @return The current number of visible rows.
	 */
	public int getRows()
	{
		return strList.getVisibleRowCount();
	}

	/**
	 * Sets the number of visible rows.
	 * 
	 * @param rows the number of visible rows.
	 */
	public void setRows(int rows)
	{
		strList.setVisibleRowCount(rows);
	}

	/**
	 * Gets the List GUI component of this widget.
	 * 
	 * @return The GUI List compononent
	 */
	public JList getList()
	{
		return strList;
	}	
	
	public void stringScalarChange(StringScalarEvent evt) 
	{
		getListModel().clear();
		
		String str = evt.getValue();
		if (str == null)
		{
			getListModel().addElement("StringScalarAttribute is null.\n");
		}
		else
		{
			if(splitter == null || !splitter.isValid(str))
			{
				getListModel().addElement(str);
			}
			else
			{
				String[] str_array = splitter.split(str);
				
				for(String elem : str_array)
				{
					getListModel().addElement(elem);
				}
			}
		}		
	}

	public void stateChange(AttributeStateEvent arg0) 
	{
		
	}

	public void errorChange(ErrorEvent arg0) 
	{
		
	}

}
