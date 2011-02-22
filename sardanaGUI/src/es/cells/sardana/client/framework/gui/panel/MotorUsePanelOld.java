package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.Component;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.JPanel;
import javax.swing.border.TitledBorder;

import es.cells.sardana.client.framework.gui.atk.widget.LimitSwitchesViewer;
import es.cells.sardana.client.framework.gui.atk.widget.VerticalPositionViewer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.widget.attribute.BooleanScalarCheckBoxViewer;
import fr.esrf.tangoatk.widget.attribute.NumberScalarListViewer;
import fr.esrf.tangoatk.widget.properties.LabelViewer;

public class MotorUsePanelOld extends JPanel 
{
	
	protected Motor motor = null;
	protected DevicePool pool = null;
	
	VerticalPositionViewer motorPositionViewer;
	NumberScalarListViewer motorAttributesViewer;
	
	BooleanScalarCheckBoxViewer motorSimulationViewer;
	BooleanScalarCheckBoxViewer motorEncoderViewer;
	BooleanScalarCheckBoxViewer motorRoundingViewer;
	LimitSwitchesViewer motorLimitSwitchesViewer;
	
	public MotorUsePanelOld()
	{
		initComponents();
	}
	
	private void initComponents()
	{	
		setBorder(new TitledBorder("Usage"));
		setLayout(new BorderLayout());
	  
		motorPositionViewer = new VerticalPositionViewer();
		motorPositionViewer.setBorder(BorderFactory.createEtchedBorder());
		
		JPanel attributesPanel = new JPanel();
		BoxLayout l = new BoxLayout(attributesPanel, BoxLayout.Y_AXIS);
		attributesPanel.setLayout(l);
		
		motorAttributesViewer = new NumberScalarListViewer();
		motorSimulationViewer = new BooleanScalarCheckBoxViewer();
		motorEncoderViewer = new BooleanScalarCheckBoxViewer();
		motorRoundingViewer = new BooleanScalarCheckBoxViewer();
		motorLimitSwitchesViewer = new LimitSwitchesViewer();

		JPanel checkBoxPanel1 = new JPanel();
		l = new BoxLayout(checkBoxPanel1, BoxLayout.Y_AXIS);
		checkBoxPanel1.setLayout(l);
		checkBoxPanel1.add(motorSimulationViewer);
		checkBoxPanel1.add(motorEncoderViewer);
		checkBoxPanel1.add(motorRoundingViewer);
		
		JPanel checkBoxPanel2 = new JPanel();
		l = new BoxLayout(checkBoxPanel2, BoxLayout.X_AXIS);
		checkBoxPanel2.setLayout(l);
		
		checkBoxPanel2.add(checkBoxPanel1);
		checkBoxPanel2.add(motorLimitSwitchesViewer);
		
		attributesPanel.add(checkBoxPanel2);
		attributesPanel.add(motorAttributesViewer);
		
		add(attributesPanel, BorderLayout.CENTER);
		add(motorPositionViewer, BorderLayout.EAST);
	}
	
	public void setModel(Motor motor, DevicePool pool)
	{
		this.motor = motor;
		this.pool = pool;
		
		INumberScalar posModel = motor.getPositionAttributeModel();
		AttributeList motorAttrModel = motor.getNonPolledAttributes();

		posModel.refresh();
		motorAttrModel.refresh();
		
		AttributeInfoEx positionInfo = motor.getAttributeInfo("Position");
		
		motorPositionViewer.setModel(positionInfo, posModel);
		motorAttributesViewer.setModel(motorAttrModel);
		
		for(Component c : motorAttributesViewer.getComponents())
		{
			if(c instanceof LabelViewer)
			{
				((LabelViewer)c).setOpaque(false);
			}
		}
		
		//motorSimulationViewer.setAttModel(manager.getOrCreateMotorSimulationModeModel(motorDeviceName));
		//motorEncoderViewer.setAttModel(manager.getOrCreateMotorEncoderModel(motorDeviceName));
		//motorRoundingViewer.setAttModel(manager.getOrCreateMotorRoundingModel(motorDeviceName));
		//IBooleanSpectrum limSwitchModel = manager.getOrCreateMotorLimitSwitchesModel(motorDeviceName);
		//motorLimitSwitchesViewer.setAttModel(limSwitchModel);
	}
}
