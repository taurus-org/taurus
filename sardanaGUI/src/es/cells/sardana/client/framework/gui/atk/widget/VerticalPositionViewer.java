package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.BorderFactory;
import javax.swing.JPanel;
import javax.swing.border.BevelBorder;

import es.cells.tangoatk.widget.attribute.NumberScalarBarViewer;
import es.cells.tangoatk.widget.attribute.NumberScalarViewer;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.widget.properties.LabelViewer;

public class VerticalPositionViewer extends JPanel implements PropertyChangeListener
{	
	LabelViewer positionLabel;
	NumberScalarBarViewer positionBarViewer;
	//NumberScalarWheelEditor positionEditor;
	NumberScalarViewer positionViewer;
	
	INumberScalar model;
	
	public VerticalPositionViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents() 
	{
		setLayout(new GridBagLayout());
		
		positionLabel = new LabelViewer();
		positionBarViewer = new NumberScalarBarViewer();
		positionViewer = new NumberScalarViewer();
		
		positionLabel.setOpaque(false);
		
		positionBarViewer.setDirection(NumberScalarBarViewer.Direction.BottomToTop);
		positionBarViewer.setBarBorder(BorderFactory.createBevelBorder(BevelBorder.LOWERED));
		
		positionViewer.setLabelVisible(false);
		
		GridBagConstraints gbc = new GridBagConstraints();
		
		gbc.fill = GridBagConstraints.NONE;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 0;
		gbc.gridy = 0;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;
		add(positionLabel, gbc);

		
		gbc = new GridBagConstraints();
		gbc.fill = GridBagConstraints.BOTH;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 0;
		gbc.gridy = 1;
		gbc.weightx = 0.0;
		gbc.weighty = 1.0;
		add(positionBarViewer, gbc);
		
		gbc = new GridBagConstraints();
		gbc.fill = GridBagConstraints.NONE;
		gbc.insets = new Insets(2,2,2,2);
		gbc.gridx = 0;
		gbc.gridy = 2;
		gbc.weightx = 0.0;
		gbc.weighty = 0.0;
		//add(positionEditor, gbc);		
		add(positionViewer, gbc);

	}

	public void setLabelVisible(boolean v)
	{
		positionLabel.setVisible(v);
		
	}
	
	public void setModel(AttributeInfoEx positionInfo, INumberScalar m)
	{
		model = m;
		
		positionLabel.setModel(model);
		positionBarViewer.setModel(model, positionInfo);
		//positionEditor.setModel(model);
		positionViewer.setModel(model);
	}
	
	public void propertyChange(PropertyChangeEvent evt) 
	{
		
	}
	
}
