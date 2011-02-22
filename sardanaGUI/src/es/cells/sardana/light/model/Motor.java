package es.cells.sardana.light.model;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;

import javax.swing.JLabel;
import javax.swing.SwingConstants;

public class Motor extends MovElement
{

	public Motor(String name, String deviceName) 
	{
		super(name, deviceName, 1);
		
		initComponents();
	}

	private void initComponents() 
	{
		elementPanel.setLayout( new GridBagLayout() );
		
		GridBagConstraints gbc = new GridBagConstraints(
				0, 0, // grid
				1, 1, // width,height
				1.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		JLabel nameLabel = new JLabel(name); 
		nameLabel.setHorizontalAlignment(SwingConstants.RIGHT);
		elementPanel.add(nameLabel, gbc);

		gbc = new GridBagConstraints(
				1, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		JLabel stateTextLabel = new JLabel("State: "); 
		elementPanel.add(stateTextLabel, gbc);

		gbc = new GridBagConstraints(
				2, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(stateLabel,gbc);
		
		gbc = new GridBagConstraints(
				3, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);		
	
		JLabel positionNameLabel = new JLabel(" pos: ");
		positionNameLabel.setToolTipText(name);
		elementPanel.add(positionNameLabel,gbc);
		
		gbc = new GridBagConstraints(
				4, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);				

		elementPanel.add(positionLabel[0],gbc);
		
		gbc = new GridBagConstraints(
				5, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);				
		
		elementPanel.add(positionSpinner[0],gbc);

		gbc = new GridBagConstraints(
				6, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		elementPanel.add(copyPositionButton[0],gbc);
		
		gbc = new GridBagConstraints(
				7, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);				
		
		elementPanel.add(applyPositionButton,gbc);
		
		gbc = new GridBagConstraints(
				8, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		
		elementPanel.add(abortCommand,gbc);
		
		JLabel eventLabel = new JLabel("p evt #:");
		elementPanel.add(eventLabel,gbc);
		
		gbc = new GridBagConstraints(
				9, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.WEST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);				

		elementPanel.add(eventLabel,gbc);
		
		gbc = new GridBagConstraints(
				10, 0, // grid
				1, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(4,2,4,2),
				0,0 // pad
				);			
		
		elementPanel.add(positionEventCountLabel,gbc);
		
	}

	
}
