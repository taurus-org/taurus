package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Component;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableColumn;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MotorTableViewer extends JPanel
{
	protected JScrollPane     pane;
	protected JTable          motorTable;
	protected TableModel      model;
	
	DevicePool pool;
	
	MotorListener motorListener;
	PseudoMotorListener pseudoMotorListener;
	
	public MotorTableViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		model = new TableModel();
		
		//setBorder(BorderFactory.createTitledBorder("Motors"));
		
		DefaultTableColumnModel colModel = new DefaultTableColumnModel();
		
		TableColumn column = new TableColumn(0);
		column.setHeaderValue("State");
		column.setPreferredWidth(50);
		column.setMaxWidth(50);
		column.setCellRenderer(new MStateCellRenderer());
		colModel.addColumn(column);
		
		column = new TableColumn(1);
		column.setHeaderValue("Name");
		column.setPreferredWidth(120);
		column.setMaxWidth(120);
		colModel.addColumn(column);
		
		column = new TableColumn(2);
		column.setHeaderValue("Device");
		colModel.addColumn(column);

		setLayout(new BorderLayout());
		pane = new JScrollPane();
		motorTable = new JTable(model, colModel);
		motorListener = new MotorListener();
		pseudoMotorListener = new PseudoMotorListener();
		
		pane.setViewportView(motorTable);
		
		add(pane, BorderLayout.CENTER);
	}

	public JTable getTable()
	{
		return motorTable;
	}

	public Motor getSelectedMotor()
	{
		int row =  motorTable.getSelectedRow();
		
		if(row < 0)
			return null;
		
		return (Motor) motorTable.getValueAt(row, 1);
	}
	
	public List<Motor> getSelectedMotors()
	{
		ArrayList<Motor> ret = new ArrayList<Motor>();
		int[] rows = motorTable.getSelectedRows();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((Motor) motorTable.getValueAt(row, 1));
		}
		
		return ret;
	}
	
	/*
	public void setCustomTitle(String customTitle) 
	{
		((TitledBorder)getBorder()).setTitle(customTitle);
	}
	*/

	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeMotorListListener(motorListener);
			pool.removePseudoMotorListListener(pseudoMotorListener);
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addMotorListListener(motorListener);
			pool.addPseudoMotorListListener(pseudoMotorListener);
			model.update(pool.getMotors(), pool.getPseudoMotors());
		}
	}
	
	class PseudoMotorListener implements IStringSpectrumListener
	{

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.updatePseudoMotors(pool.getPseudoMotors());
		}

		public void stateChange(AttributeStateEvent e)
		{
			
		}

		public void errorChange(ErrorEvent evt)
		{
			
		}
		
	}
	
	class MotorListener implements IStringSpectrumListener 
	{

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.updateMotors(pool.getMotors());
		}

		public void stateChange(AttributeStateEvent e)
		{
		}

		public void errorChange(ErrorEvent evt)
		{
		}
	}
	
	class TableModel extends AbstractTableModel implements IDevStateScalarListener 
	{
		List<Motor> motors;
		List<PseudoMotor> pseudoMotors;

		public int getColumnCount()
		{
			return 3;
		}

		public int getRowCount()
		{
			int motorCount = motors != null ? motors.size() : 0;
			int pmCount = pseudoMotors != null ? pseudoMotors.size() : 0;
			return motorCount + pmCount;
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			Motor m = null;
		
			int motorsLen = motors.size();
			int pmLen = pseudoMotors.size();
			
			if(rowIndex < motorsLen)
			{
				m = motors.get(rowIndex);
			}
			else if(rowIndex < motorsLen + pmLen)
			{
				m = pseudoMotors.get(rowIndex - motorsLen);
			}
			
			if(m == null)
				return null;
			
			if(columnIndex == 0)
			{
				JLabel l = new JLabel(m.getState());
				l.setOpaque(true);
				return l;
			}
			else if(columnIndex == 1)
				return m;
			else if(columnIndex == 2)
				return m.getDeviceName();
			else 
				return null;
		}
		
	    /**
	     *  Returns <code>Object.class</code> regardless of <code>columnIndex</code>.
	     *
	     *  @param columnIndex  the column being queried
	     *  @return the Object.class
	     */
	    public Class<?> getColumnClass(int columnIndex) 
	    {
	    	if(columnIndex == 0)
	    		return JLabel.class;
	    	else if(columnIndex == 1)
	    		return Motor.class; 
	    	return Object.class;
	    }
		
	    private void updateMotorList(List<Motor> newMotors)
	    {
	    	if(motors != null)
	    	{
	    		for(Motor m : motors) m.removeDevStateScalarListener(this);
	    	}
	    	if(newMotors != null)
	    	{
	    		for(Motor m : newMotors) m.addDevStateScalarListener(this);
	    	}
	    	motors = newMotors;
	    }

	    private void updatePseudoMotorList(List<PseudoMotor> newPseudoMotors)
	    {
	    	if(pseudoMotors != null)
	    	{
	    		for(PseudoMotor m : pseudoMotors) m.removeDevStateScalarListener(this);
	    	}
	    	if(newPseudoMotors != null)
	    	{
	    		for(PseudoMotor m : newPseudoMotors) m.addDevStateScalarListener(this);
	    	}
	    	pseudoMotors = newPseudoMotors;
	    }
	    
	    public void update(List<Motor> newMotors, List<PseudoMotor> newPseudoMotors)
	    {
	    	updateMotorList(newMotors);
	    	updatePseudoMotorList(newPseudoMotors);
	    	fireTableDataChanged();
	    }
	    
	    public void updateMotors(List<Motor> newMotors)
	    {
	    	updateMotorList(newMotors);
	    	fireTableDataChanged();
	    }
	    
	    public void updatePseudoMotors(List<PseudoMotor> newPseudoMotors)
	    {
	    	updatePseudoMotorList(newPseudoMotors);
	    	fireTableDataChanged();
	    }

		public void devStateScalarChange(DevStateScalarEvent e)
		{
			Device d = ((DevStateScalar)e.getSource()).getDevice();
			
			String devName = d.getName();
			
			int motorCount = motors.size();
			for(int i = 0; i < motorCount; i++)
			{
				Motor m = motors.get(i);
				if(m.getDeviceName().equals(devName))
				{
					fireTableCellUpdated(i, 0);
					return;
				}
			}

			int pmCount = pseudoMotors.size();
			for(int i = 0; i < pmCount; i++)
			{
				PseudoMotor pm = pseudoMotors.get(i);
				if(pm.getDeviceName().equals(devName))
				{
					fireTableCellUpdated(i+motorCount, 0);
					return;
				}
			}

			
		}

		public void stateChange(AttributeStateEvent e)
		{
			// TODO Auto-generated method stub
			
		}

		public void errorChange(ErrorEvent evt)
		{
			// TODO Auto-generated method stub
			
		}
	}
	
	//TODO: Substance look and feel
	//class MStateCellRenderer extends SubstanceDefaultTableCellRenderer
	class MStateCellRenderer extends DefaultTableCellRenderer
	{

		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			if(value instanceof JLabel)
			{
				JLabel l = (JLabel)value;
				l.setHorizontalAlignment(SwingConstants.CENTER);
				if(!isSelected && !hasFocus)
				{
					l.setBackground(SwingResource.getColor4State(l.getText()));
					l.setForeground(table.getForeground());
					return l;
				}
				else
				{
					l.setBackground(table.getSelectionBackground());
					l.setForeground(SwingResource.getColor4State(l.getText()));
					return l;
				}
			}
			
			return super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
					row, column);
		}
	}
}
