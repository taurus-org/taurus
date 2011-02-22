package es.cells.sardana.light.model;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingConstants;

import fr.esrf.tangoatk.core.AttributeSetException;
import fr.esrf.tangoatk.core.INumberSpectrum;

public class MotorGroup extends MovElement 
{
	public String[] user_elems;
	
	public MotorGroup(String name, String deviceName, String[] user_elems, int positionSize)
	{
		super(name, deviceName, positionSize);
		this.user_elems = user_elems;
		
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
		
		JLabel stateTextLabel = new JLabel(" State: "); 
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

		JPanel p = new JPanel(new GridBagLayout());
		
		for(int pos = 0; pos < positionSize; pos++)
		{
			gbc = new GridBagConstraints(
					0, pos, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.EAST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);	
			
			JLabel positionNameLabel = new JLabel(" pos #" + pos + ": ");
			p.add(positionNameLabel, gbc);
			
			gbc = new GridBagConstraints(
					1, pos, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.EAST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			p.add(positionLabel[pos],gbc);
			
			gbc = new GridBagConstraints(
					2, pos, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.WEST, // anchor
					GridBagConstraints.HORIZONTAL,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			p.add(positionSpinner[pos],gbc);
			
			gbc = new GridBagConstraints(
					3, pos, // grid
					1, 1, // width,height
					0.0, 0.0, // weight
					GridBagConstraints.CENTER, // anchor
					GridBagConstraints.BOTH,
					new Insets(4,2,4,2),
					0,0 // pad
					);
			p.add(copyPositionButton[pos],gbc);
		}
		
		gbc = new GridBagConstraints(
				4, 0, // grid
				1, positionSize, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.CENTER, // anchor
				GridBagConstraints.BOTH,
				new Insets(4,2,4,2),
				0,0 // pad
				);
		p.add(applyPositionButton,gbc);
		
		gbc = new GridBagConstraints(
				3, 0, // grid
				5, 1, // width,height
				0.0, 0.0, // weight
				GridBagConstraints.EAST, // anchor
				GridBagConstraints.HORIZONTAL,
				new Insets(0,0,0,0),
				0,0 // pad
				);
		elementPanel.add(p,gbc);
	
		
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
		
		JLabel eventLabel = new JLabel("pos evt #:");
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

	protected ActionListener getApplyPositionActionListener()
	{
		return new ActionListener() 
		{
			public void actionPerformed(ActionEvent e) 
			{
				INumberSpectrum s = (INumberSpectrum) positionAttribute;
				double[] values = new double[positionSize];
				for(int i=0;i<positionSize;i++)
					values[i] = (Double)positionSpinner[i].getValue();
				try 
				{
					s.setValue(values);
				} 
				catch (AttributeSetException e1) 
				{
					e1.printStackTrace();
					System.exit(-6);
				}
			}
		};
	}

}
