package es.cells.tangoatk.widget.attribute;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.util.Vector;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.border.TitledBorder;

import es.cells.tangoatk.utils.IStringSplitter;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class FormStringSpectrumViewer extends JPanel implements IStringSpectrumListener
{
	protected Vector<JLabel> formLabels;
	protected Vector<JTextField> formTextFields;
	
	IStringSpectrum          model;

	IStringSplitter          splitter;
	
	String                   customTitle;
	
	/**
	 * This contructor will create a single column table view of
	 * the string spectrum.
	 */
	public FormStringSpectrumViewer()
	{
		this(new Object[]{"Value"});
	}

	/**
	 * This constructor will create a multiple column table view of the 
	 * string spectrum. 
	 * 
	 * @param columnNames Array containing the column titles
	 */
	public FormStringSpectrumViewer(Object[] rowNames)
	{
		initComponents(rowNames);
	}
	
	public String getCustomTitle() {
		return customTitle;
	}

	public void setCustomTitle(String customTitle) {
		this.customTitle = customTitle;
		((TitledBorder)getBorder()).setTitle(customTitle);
	}

	protected void initComponents(Object[] rowNames)
	{
		formLabels = new Vector<JLabel>(rowNames.length);
		formTextFields = new Vector<JTextField>(rowNames.length);
		
		setLayout( new GridBagLayout() );
		
		setBorder(new TitledBorder("StringSpectrum"));
		
		int rowCount = 0;
		for(Object rowName : rowNames)
		{
			String name = rowName.toString();
			
			JLabel label = new JLabel(name);
			JTextField text = new JTextField(30);

			formLabels.add(label);
			formTextFields.add(text);

			GridBagConstraints gbc = new GridBagConstraints();
			gbc.insets = new java.awt.Insets(2, 2, 2, 2);
			gbc.fill = GridBagConstraints.NONE;
			gbc.anchor = GridBagConstraints.EAST;
			gbc.gridx = 0;
			gbc.gridy = rowCount; 
			gbc.weightx = 0.0;
			gbc.weighty = 0.0;
			add(label, gbc);
			
			gbc = new GridBagConstraints();
			gbc.insets = new java.awt.Insets(2, 2, 2, 2);
			gbc.fill = GridBagConstraints.HORIZONTAL;
			gbc.anchor = GridBagConstraints.WEST;
			gbc.gridx = 1;
			gbc.gridy = rowCount; 
			gbc.weightx = 1.0;
			gbc.weighty = 0.0;
			add(text, gbc);
			
			rowCount++;
		}
	}
	
	public IStringSplitter getSplitter()
	{
		return splitter;
	}

	public void setSplitter(IStringSplitter splitter)
	{
		this.splitter = splitter;
	}

	public void setModel(IStringSpectrum strSpectAtt)
	{
		if (model != null)
		{
			model.removeListener(this);
		}
		
		clearRows();
		
		this.model = strSpectAtt;

		if ( model != null )
		{	
			if(customTitle == null)
				((TitledBorder)getBorder()).setTitle(model.getNameSansDevice());
			model.addListener(this);
			
			update(model.getStringSpectrumValue());
		}
	}

	private void clearRows()
	{
		for(JTextField text : formTextFields)
		{
			text.setText("");
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

	protected void update(String[] strArray)
	{
		if (strArray == null)
		{
			formTextFields.get(0).setText("no element (is null).");
		}
		else
		{
			String[] rowData = getMatchingRow(strArray);
			
			if(rowData == null)
			{
				formTextFields.get(0).setText("no match!");
				return;
			}
			
			int i = 0;
			for(String rowText : rowData)
			{
				formTextFields.get(i++).setText(rowText);
			}
		}		
	}
	
	public void stringSpectrumChange(StringSpectrumEvent evt)
	{
		update(evt.getValue());
	}
	
	protected String[] getMatchingRow(String[] strArray)
	{
		if(strArray == null)
			return null;
		
		String[] rows = null;
		
		for(String str : strArray)
		{
			rows = splitter.split(str);
			
			if(rows == null)
				continue;
			
			return rows;
		}
		
		return rows;

		/*
		String[] rows;
		
		// Search every string element for a filter match
		for(String str : strArray)
		{
			Matcher matcher = rowPattern.matcher(str);
			
			if(matcher.matches() && rowIndex < matcher.groupCount())
			{
				// If a match has been found return it
				if(indexFilter.equals(matcher.group(rowIndex)))
				{
					int len = Math.min(matcher.groupCount(), patternRowIndexes.length);
					rows = new String[len];
					for(int matchIndex = 0; matchIndex < len; matchIndex++)
						rows[matchIndex] = matcher.group(patternRowIndexes[matchIndex]);
					return rows;
				}
			}
		}
		
		return null;
		*/
	}
	
	public void stateChange(AttributeStateEvent e)
	{
	}

	public void errorChange(ErrorEvent evt)
	{
	}
	
}
