package es.cells.tangoatk.widget.property;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

import fr.esrf.tangoatk.core.DeviceProperty;

public class DevicePropertyViewer extends JPanel implements PropertyChangeListener {

	JLabel                             propertyLabel;
	JTextArea                          textAreaValue;
	JScrollPane                        scrollPane;
	
	JButton                            applyButton;
	JButton                            refreshButton;
	
	/** The model. */
    protected DeviceProperty           model;
    
	public DevicePropertyViewer() 
	{
		super();
		initComponents();
	}
	
	private void initComponents() 
	{
		setLayout(new GridBagLayout());
		
		GridBagConstraints gbc = new GridBagConstraints();
		
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;
		propertyLabel = new JLabel("No property defined");
		add(propertyLabel,gbc);
		
		gbc.gridx = 1;
		gbc.weightx = 1.0;
		gbc.weighty = 1.0;
		gbc.fill = GridBagConstraints.BOTH;
		textAreaValue = createTextAreaElement();
		scrollPane = new JScrollPane(textAreaValue);
		add(scrollPane,gbc);
		
		gbc.gridx = 2;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;
		gbc.fill = GridBagConstraints.NONE;
		gbc.anchor = GridBagConstraints.NORTH;
		applyButton = new JButton("Apply");
		add(applyButton,gbc);
		applyButton.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(model != null)
				{
					model.setValue(textAreaValue.getText());
					model.store();
				}
			}
		});		
		
		gbc.gridx = 3;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;
		gbc.fill = GridBagConstraints.NONE;
		gbc.anchor = GridBagConstraints.NORTH;
		refreshButton = new JButton("Refresh");
		add(refreshButton,gbc);
		
		refreshButton.addActionListener( new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				if(model != null)
					model.refresh();
			}
		});
	}
	
	protected JTextArea createTextAreaElement()
	{
		JTextArea ret = new JTextArea("No value defined");
		ret.setRows(3);
		ret.setEditable(model != null && model.isEditable());
		return ret;
	}
	
	public DeviceProperty getModel() 
	{
		return model;
	}

	public void setModel(DeviceProperty model) 
	{
		if(this.model != null)
			this.model.removePresentationListener(this);
		
		this.model = model;
		
		if(this.model != null)
		{
			propertyLabel.setText(this.model.getName());
			this.model.addPresentationListener(this);

			applyButton.setEnabled(model.isEditable());
			refreshButton.setEnabled(true);
			
			model.refresh();
		}
		else
		{
			propertyLabel.setText("No property defined");
			textAreaValue.setText("");
			
			applyButton.setEnabled(false);
			refreshButton.setEnabled(false);
		}
	}

	public void propertyChange(PropertyChangeEvent evt)
	{
		String newValue = ((String[]) evt.getNewValue())[0];
		textAreaValue.setText(newValue);
	}
}
