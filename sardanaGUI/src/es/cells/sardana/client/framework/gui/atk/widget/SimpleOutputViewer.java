package es.cells.sardana.client.framework.gui.atk.widget;
import javax.swing.JTextArea;

import es.cells.sardana.client.framework.gui.component.LengthLimitedDocument;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;


public class SimpleOutputViewer extends javax.swing.JPanel
             implements IStringSpectrumListener
{
	//Model
	IStringSpectrum                    		model;
	int 								 	textAreaLimit;					 
    private boolean                   	viewEnd = false;
    
    //View
    private javax.swing.JScrollPane    jScrollPane1;
    private javax.swing.JTextArea      strSpectText;
     
    /** Creates new form SimpleStringSpectrumViewer */

    public SimpleOutputViewer(int limit)
    {
    	 setTextAreaLimit(limit);
    	 initComponents();
    }

    private void initComponents()
    {
	jScrollPane1 = new javax.swing.JScrollPane();
	strSpectText = new javax.swing.JTextArea(new LengthLimitedDocument(getTextAreaLimit()));

	setLayout(new java.awt.BorderLayout());

//	setBorder(new javax.swing.border.TitledBorder("StringSpectrum"));
	jScrollPane1.setVerticalScrollBarPolicy(javax.swing.JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
	strSpectText.setLineWrap(false);
	strSpectText.setEditable(false);
	strSpectText.setColumns(50);
	strSpectText.setRows(10);
	strSpectText.setText("Unknown");
	strSpectText.setBackground(new java.awt.Color(204, 204, 204));
	jScrollPane1.setViewportView(strSpectText);

	add(jScrollPane1, java.awt.BorderLayout.CENTER);
     }

     public void setModel(IStringSpectrum  strSpectAtt)
     {
	if (model != null)
	{
	   model.removeListener(this);
	}
	strSpectText.setText("");
	this.model = strSpectAtt;
	
	if ( model != null )
	{
	   model.addListener(this);
	   model.refresh();
	}
     }

     /**
      * <code>getModel</code> gets the model of this SimpleStringSpectrumViewer.
      *
      * @return a <code>IStringSpectrum</code> value
      */
     public IStringSpectrum getModel()
     {
        return model;
     }


     public int getRows()
     {
       return strSpectText.getRows();
     }

     public void setRows(int rows)
     {
       strSpectText.setRows(rows);
     }

     public int getColumns()
     {
       return strSpectText.getColumns();
     }

     public void setColumns(int columns)
     {
       strSpectText.setColumns(columns);
     }

     public JTextArea getText()
     {
       return strSpectText;
     }
     
     

     /* javax.swing.JTextArea:setText(String) method has a memory
     leak on SUN Solaris JVM (seems to be OK on windows)
     The setStrTextArea method is called each time the String spectrum attribute
     is read by the refresher even if it has not changed. This will be changed in the
     future when the Tango Events will be used instead of ATK refreshers.
     For the time being a test has been added to limit the memory leak of JVM.
     */
     public void setStrTextArea(String s)
     {
	if (s.equals(strSpectText.getText()))
	  return;
	  
        strSpectText.setText(s);
        if ( isViewEnd() )
           placeTextToEnd (); 
     }

     public void stringSpectrumChange(StringSpectrumEvent evt)
     {
        int       ind_str, attr_size;
	String    str;
	
	//System.out.println("stringSpectrumChange called.\n");
	if (evt.getValue() == null)
	{
	   str = "StringSpectrumAttribute is null.\n";
	}
	else
	{
	    String[]   str_array=null;
	    
	    str_array = evt.getValue();
	    attr_size= str_array.length;
	    
	    StringBuffer strbuff = new StringBuffer(attr_size);
	    
	    for (ind_str=0; ind_str < attr_size; ind_str++)
	    {
	       strbuff.append(str_array[ind_str]);
	       strbuff.append("\n");
	    }
	    str = strbuff.toString();
	}
	setStrTextArea(str);      
     }

     public void errorChange(ErrorEvent evt)
     {

     }

     public void stateChange(AttributeStateEvent evt)
     {
	if ("VALID".equals(evt.getState()))
	{
	    strSpectText.setBackground(getBackground());
	    return;
	}
	strSpectText.setBackground(ATKConstant.getColor4Quality(evt.getState()));
     }

     /**
      * Returns whether user prefers to allways view the end of the text or not
      * @return A boolean to know whether user prefers to allways view the end of the text or not
      */
     public boolean isViewEnd ()
     {
         return viewEnd;
     }

     /**
      * Sets whether user prefers to allways view the end of the text or not.
      * @param viewEnd a boolean to set this preference
      */
     public void setViewEnd (boolean viewEnd)
     {
         this.viewEnd = viewEnd;
         if ( isViewEnd () )
             placeTextToEnd ();
     }

     private void placeTextToEnd ()
     {
         strSpectText.setCaretPosition(strSpectText.getDocument().getLength());
     }

	public int getTextAreaLimit() {
		return textAreaLimit;
	}

	public void setTextAreaLimit(int textAreaLimit) {
		this.textAreaLimit = textAreaLimit;
	}

     
     


}