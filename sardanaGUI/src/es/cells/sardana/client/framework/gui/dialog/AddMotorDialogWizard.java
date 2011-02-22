/*
 * AddMotorDialog.java
 *
 * Created on September 8, 2006, 9:52 AM
 */

package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.util.logging.Logger;

import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.gui.swing.SwingResource;

/**
 *
 * @author  tcoutinho
 */
public class AddMotorDialogWizard extends JDialog //implements IStringSpectrumListener 
{
	DevicePool devicePool;
	Motor motor;
	PseudoMotor pseudoMotor; 
	
	JTextField pseudoMotorNames[];
	JComboBox motorNames[];
	
	protected static final ImageIcon motorIcon = new ImageIcon("res/128x128/motor.png");
	
	private static Logger log = SardanaManager.getInstance().getLogger(AddMotorDialogWizard.class.getName());
	
	WizardPanel[] panels ;
	
	public AddMotorDialogWizard()
	{
		super();
		setTitle("Create Motor");
	}
			
	public AddMotorDialogWizard(DevicePool devicePool)
	{
		this();
		this.devicePool = devicePool;
		init();
	}
	
	public AddMotorDialogWizard(DevicePool devicePool, Motor motor)
	{
		this();
		this.devicePool = devicePool;
		this.motor = motor;
		init();
	}
	
	public AddMotorDialogWizard(DevicePool devicePool, PseudoMotor pseudoMotor) 
	{
		this();
		this.devicePool = devicePool;
		this.pseudoMotor = pseudoMotor;
		init();
	}

	private void init() 
	{
		WizardPanel firstPanel = new WizardPanel();
		
		
	}

	protected void closeAndExit()
	{
		dispose();
	}

	protected void exitPressed(ActionEvent e)
	{
		closeAndExit();
	}
	
	protected void hideAndExit()
	{
		pseudoMotor = null;
		for(Component c : getComponents())
		{
			if(c instanceof JTextField)
			{
				((JTextField)c).setText(null);
			}
			else if(c instanceof JComboBox)
			{
				((JComboBox)c).setSelectedIndex(0);
			}
		}
		setVisible(false);
	}
	
	protected class WizardPanel extends JPanel
	{
		public WizardPanel()
		{
			super( new BorderLayout() );
			
			JLabel lbl = new JLabel(motorIcon);
			
			add(lbl,BorderLayout.WEST);
		}
	}
}
