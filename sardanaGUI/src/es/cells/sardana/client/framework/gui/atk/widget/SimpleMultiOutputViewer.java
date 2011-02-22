package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Font;
import java.util.List;

import javax.swing.JScrollPane;
import javax.swing.JTextArea;

import es.cells.sardana.client.framework.gui.component.LengthLimitedDocument;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.widget.attribute.SimpleStringSpectrumViewer;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class SimpleMultiOutputViewer 
				extends 	javax.swing.JPanel 
				implements IStringSpectrumListener 
{

	//MODEL
	List<IStringSpectrum> 	models;
	int	 				textAreaLimit;
	private boolean 		viewEnd = true;
	
	//VIEW
	private JScrollPane jScrollPane1;
	private JTextArea strSpectText;
	
	

	public SimpleMultiOutputViewer(int limit) 
	{
		setTextAreaLimit(limit);
		initComponents();
	}

	private void initComponents() 
	{
		jScrollPane1 = new JScrollPane();
		strSpectText = new JTextArea(new LengthLimitedDocument(getTextAreaLimit()));
		
		setLayout(new BorderLayout());

		jScrollPane1
			.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		strSpectText.setLineWrap(false);
		strSpectText.setEditable(false);
		strSpectText.setColumns(50);
		strSpectText.setRows(10);
		strSpectText.setBackground(new java.awt.Color(204, 204, 204));
		//strSpectText.setFont(new Font("Arial",Font.BOLD, 15));
		jScrollPane1.setViewportView(strSpectText);
		add(jScrollPane1, java.awt.BorderLayout.CENTER);
	}
	
	public void setModels(List<IStringSpectrum> strSpectAtts)
	{
		if(models != null)
		{
			for (IStringSpectrum model : models) 
				model.removeListener(this);
			strSpectText.setText("");
		}
		models = strSpectAtts;
		for (IStringSpectrum model : models)
		{	
			model.addListener(this);
			model.refresh();
		}
	}
	
	public int getRows() {
		return strSpectText.getRows();
	}

	public void setRows(int rows) {
		strSpectText.setRows(rows);
	}

	public int getColumns() {
		return strSpectText.getColumns();
	}

	public void setColumns(int columns) {
		strSpectText.setColumns(columns);
	}

	public JTextArea getText() {
		return strSpectText;
	}

	public void setStrTextArea(String s, String font) {
		if (isViewEnd())
			placeTextToEnd();
		if(font.equals("Error"))
			strSpectText.setFont(new Font("Arial",Font.BOLD, 12));
		else if(font.equals("Normal"))
			strSpectText.setFont(new Font("Arial",Font.PLAIN, 12));
			
		strSpectText.append(s);
	}

	public void stringSpectrumChange(StringSpectrumEvent evt) {
		int ind_str, attr_size;
		String str;
		String font = "Normal";
		if (evt.getValue() == null) {
			str = "StringSpectrumAttribute is null.\n";
		} else {
			String[] str_array = null;

			str_array = evt.getValue();
			attr_size = str_array.length;
			
			
			StringBuffer strbuff = new StringBuffer();
			if(((IStringSpectrum)evt.getSource()).getNameSansDevice().equals("Output"))
				strbuff.append("[Output] : ");
			if(((IStringSpectrum)evt.getSource()).getNameSansDevice().equals("Info"))
				strbuff.append("[Info] : ");
			if(((IStringSpectrum)evt.getSource()).getNameSansDevice().equals("Error"))
			{
				strbuff.append("[Error] : ");
				font = "Error";
			}
			if(((IStringSpectrum)evt.getSource()).getNameSansDevice().equals("Warning"))
				strbuff.append("[Warning] : ");
			for (ind_str = 0; ind_str < attr_size; ind_str++) 
			{
				strbuff.append(str_array[ind_str]);
				strbuff.append("\n");
			}
			str = strbuff.toString();
			if(((IStringSpectrum)evt.getSource()).getNameSansDevice().equals("Error"))
				str = str.toUpperCase();
		}
		setStrTextArea(str, font);
	}

	public void errorChange(ErrorEvent evt) {

	}

	public void stateChange(AttributeStateEvent evt) {
		if ("VALID".equals(evt.getState())) {
			strSpectText.setBackground(getBackground());
			return;
		}
		strSpectText
				.setBackground(ATKConstant.getColor4Quality(evt.getState()));
	}

	/**
	 * Returns whether user prefers to allways view the end of the text or not
	 * 
	 * @return A boolean to know whether user prefers to allways view the end of
	 *         the text or not
	 */
	public boolean isViewEnd() {
		return viewEnd;
	}

	/**
	 * Sets whether user prefers to allways view the end of the text or not.
	 * 
	 * @param viewEnd
	 *            a boolean to set this preference
	 */
	public void setViewEnd(boolean viewEnd) {
		this.viewEnd = viewEnd;
		if (isViewEnd())
			placeTextToEnd();
	}

	private void placeTextToEnd() {
		strSpectText.setCaretPosition(strSpectText.getDocument().getLength());
	}

	public int getTextAreaLimit() {
		return textAreaLimit;
	}

	public void setTextAreaLimit(int textAreaLimit) {
		this.textAreaLimit = textAreaLimit;
	}
}


