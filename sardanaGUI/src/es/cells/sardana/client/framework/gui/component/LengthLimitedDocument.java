package es.cells.sardana.client.framework.gui.component;

import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.PlainDocument;

public class LengthLimitedDocument extends PlainDocument {
	
    int limit;

    public LengthLimitedDocument(int limit) 
    {
        this.limit = limit;
    }

    public void insertString(int offs, String str, AttributeSet a)
     throws BadLocationException 
     {
        if (str == null)
            return;
        super.insertString(offs, str, a);
        int length = getLength();
        if (length > limit)
        {
        	remove(0,length-limit);
        	//this is to start text from the first line
            String  parts[] = getText( 0 , limit).split("\n");
            remove(0,(parts[0].length()+1));
        }
        
    }
}

