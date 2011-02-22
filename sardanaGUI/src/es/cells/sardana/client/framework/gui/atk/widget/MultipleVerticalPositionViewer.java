package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;

import javax.swing.BorderFactory;
import javax.swing.JPanel;
import javax.swing.border.BevelBorder;

import es.cells.tangoatk.widget.attribute.NumberScalarBarViewer;
import es.cells.tangoatk.widget.attribute.NumberScalarViewer;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.widget.properties.LabelViewer;

public class MultipleVerticalPositionViewer extends JPanel implements PropertyChangeListener
{

	LabelViewer positionLabel;
	ArrayList<NumberScalarBarViewer> positionBarArray;
	ArrayList<NumberScalarViewer> positionViewer;
	
	INumberSpectrum model;
	
	public MultipleVerticalPositionViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		refreshComponents(null,null,null);
		
	}

	private void refreshComponents(INumberSpectrum m, AttributeInfoEx positionGroupInfo, AttributeInfoEx[] positionsInfo)
	{
		setLayout(new GridBagLayout());
		
		removeAll();
		
		positionLabel = new LabelViewer();
		positionBarArray = new ArrayList<NumberScalarBarViewer>();
		positionViewer = new ArrayList<NumberScalarViewer>();
		
		if(model == null)
			return;
		
		positionLabel.setModel(m);
		positionLabel.setOpaque(false);

		GridBagConstraints gbc = new GridBagConstraints(
				0,0,
				positionsInfo.length,1,
				1.0,0.0,
				GridBagConstraints.CENTER,
				GridBagConstraints.HORIZONTAL,
				new Insets(2,2,2,2),
				0,0
			);
			add(positionLabel, gbc);
		
		for(int index = 0; index < positionsInfo.length; index++)
		{
			NumberScalarBarViewer barViewer = new NumberScalarBarViewer();
			NumberScalarViewer posViewer = new NumberScalarViewer();
			
			positionBarArray.add(barViewer);
		
			barViewer.setDirection(NumberScalarBarViewer.Direction.BottomToTop);
			barViewer.setBarBorder(BorderFactory.createBevelBorder(BevelBorder.LOWERED));
			barViewer.setModel(m, index, positionsInfo[index]);
			
			posViewer.setLabelVisible(false);
			posViewer.setApplyVisible(false);
			posViewer.setModel(m, index, positionsInfo[index]);
			
			gbc = new GridBagConstraints(
					index,1,
					1,1,
					0.0,1.0,
					GridBagConstraints.CENTER,
					GridBagConstraints.VERTICAL,
					new Insets(2,2,2,2),
					0,0
				);
			add(barViewer, gbc);
			
			gbc = new GridBagConstraints(
					index,2,
					1,1,
					0.0,0.0,
					GridBagConstraints.CENTER,
					GridBagConstraints.VERTICAL,
					new Insets(2,2,2,2),
					0,0
				);
			add(posViewer, gbc);
			
		}
		

	}

	public void setModel(INumberSpectrum m, AttributeInfoEx positionGroupInfo, AttributeInfoEx[] positionsInfo)
	{
		model = m;
	
		refreshComponents(m, positionGroupInfo, positionsInfo);
		invalidate();
		repaint();
	}
	
	public void propertyChange(PropertyChangeEvent evt) 
	{
		
	}
}
