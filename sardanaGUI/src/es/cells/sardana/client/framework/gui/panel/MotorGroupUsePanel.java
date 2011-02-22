package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.util.List;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JPanel;
import javax.swing.border.TitledBorder;

import es.cells.sardana.client.framework.gui.atk.widget.MultipleVerticalPositionViewer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.widget.command.VoidVoidCommandViewer;

public class MotorGroupUsePanel extends JPanel
{
	MultipleVerticalPositionViewer motorGroupPositionViewer;
	VoidVoidCommandViewer abortCmdViewer;
	
	protected static ImageIcon abortIcon = new ImageIcon("res/96x96/stop.png"); 
	
	public MotorGroupUsePanel()
	{
		initComponents();
	}
	
	private void initComponents()
	{	
		setBorder(new TitledBorder("Usage"));
		setLayout(new BorderLayout());
		
		motorGroupPositionViewer = new MultipleVerticalPositionViewer();
		motorGroupPositionViewer.setBorder(BorderFactory.createEtchedBorder());
		
		JPanel abortPanel = new JPanel(new BorderLayout());
		
		abortCmdViewer = new VoidVoidCommandViewer();
		abortCmdViewer.setExtendedParam("text", " ", false);
		abortCmdViewer.setIcon(abortIcon);
		abortPanel.add(abortCmdViewer, BorderLayout.CENTER);
		
		add(motorGroupPositionViewer, BorderLayout.CENTER);
		add(abortPanel, BorderLayout.SOUTH);
	}
	
	
	public void setModel(MotorGroup motorGroup, DevicePool pool)
	{
		INumberSpectrum posModel = motorGroup.getPositionAttributeModel();
		
		AttributeInfoEx positionGroupInfo = motorGroup.getAttributeInfo(DevicePoolUtils.MOTOR_GROUP_ATTR_POSITION);

		List<Motor> motors = motorGroup.getMotors();
		
		AttributeInfoEx[] positionsInfo = new AttributeInfoEx[motors.size()];
		
		int index = 0;
		for(Motor m : motors)
			positionsInfo[index++] = m.getAttributeInfo(DevicePoolUtils.MOTOR_GROUP_ATTR_POSITION);
		
		motorGroupPositionViewer.setModel(posModel, positionGroupInfo, positionsInfo);
		abortCmdViewer.setModel(motorGroup.getAbortCommandModel());
		
	}

}
