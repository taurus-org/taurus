package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.BorderFactory;
import javax.swing.JPanel;
import javax.swing.border.BevelBorder;

import es.cells.sardana.client.framework.pool.Motor;
import es.cells.tangoatk.widget.attribute.NumberScalarBarViewer;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.widget.attribute.NumberScalarWheelEditor;
import fr.esrf.tangoatk.widget.attribute.SimpleScalarViewer;
import fr.esrf.tangoatk.widget.properties.LabelViewer;

public class PositionViewer extends JPanel implements PropertyChangeListener
{	
	LabelViewer attrLabel;
	NumberScalarBarViewer barPanel;
	SimpleScalarViewer posViewer;
	NumberScalarWheelEditor posEditor;
	
	INumberScalar model;
	
	public PositionViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents() 
	{
		setLayout(new GridBagLayout());
		
		attrLabel = new LabelViewer();
		posViewer = new SimpleScalarViewer();
		posEditor = new NumberScalarWheelEditor();
		barPanel = new NumberScalarBarViewer();

		attrLabel.setOpaque(false);
		posViewer.setSizingBehavior(SimpleScalarViewer.MATRIX_BEHAVIOR);
		barPanel.setBarBorder(BorderFactory.createBevelBorder(BevelBorder.LOWERED));
		
		GridBagConstraints gbc = new GridBagConstraints();
		gbc.fill = GridBagConstraints.VERTICAL;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.weightx = 0.0;
		gbc.weighty = 1.0;
		gbc.ipady = 100;
		add(attrLabel, gbc);

		gbc = new GridBagConstraints();
		gbc.fill = GridBagConstraints.BOTH;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 1;
		gbc.gridy = 0;
		gbc.weightx = 0.7;
		gbc.weighty = 1.0;
		add(barPanel, gbc);

		gbc = new GridBagConstraints();
		gbc.fill = GridBagConstraints.HORIZONTAL;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 2;
		gbc.gridy = 0;
		gbc.weightx = 0.15;
		gbc.weighty = 0.2;
		add(posViewer, gbc);

		gbc = new GridBagConstraints();
		gbc.fill = GridBagConstraints.HORIZONTAL;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 3;
		gbc.gridy = 0;
		gbc.weightx = 0.15;
		gbc.weighty = 0.2;
		add(posEditor, gbc);
	}

	public void setModel(Motor motor, INumberScalar m)
	{
		model = m;
		
		attrLabel.setText(model.getLabel());
		
		posViewer.setModel(model);
		posEditor.setModel(model);
		attrLabel.setModel(model);
		barPanel.setModel(model, motor.getAttributeInfo("Position"));
	}
	
	public void propertyChange(PropertyChangeEvent evt) 
	{
		
	}
	
}
