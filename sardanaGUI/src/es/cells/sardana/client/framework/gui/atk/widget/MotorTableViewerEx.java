package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.util.ArrayList;
import java.util.List;

import javax.swing.DefaultCellEditor;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.JTextField;
import javax.swing.UIManager;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;

import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.AttrWriteType;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MotorTableViewerEx extends JPanel 
{
	public static final Color veryLightGrey = new Color(0.95f,0.95f,0.95f);
	
	protected JScrollPane      pane;
	protected JTable           motorTable;
	protected MotorsTableModel model;
	
	DevicePool pool;
	
	MotorListener motorListener;
	PseudoMotorListener pseudoMotorListener;
	
	public MotorTableViewerEx()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		model = new MotorsTableModel();
		
		setLayout(new BorderLayout());
		pane = new JScrollPane();
		motorTable = new JTable(model);
		motorListener = new MotorListener();
		pseudoMotorListener = new PseudoMotorListener();
		pane.setViewportView(motorTable);
		motorTable.setDefaultRenderer(String.class, new ParamNameCellRenderer());
		motorTable.setDefaultRenderer(Motor.class, new MotorCellRenderer());
		motorTable.setDefaultEditor(Motor.class, new MotorCellEditor(new JTextField(10)));
		motorTable.setCellSelectionEnabled(true);
		motorTable.setRowMargin(0);
		motorTable.setRowHeight(18);
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
			model.update();
		}
	}
	
	class MotorCellEditor extends DefaultCellEditor
	{
		public MotorCellEditor(JTextField textField) {
			super(textField);
		}
		
		public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) 
		{
			JTextField textField = (JTextField) super.getTableCellEditorComponent(table, value, isSelected, row, column);
			/*
			JLabel l = (JLabel) table.getCellRenderer(row, column);
			*/
			textField.setText("");
			return textField;
		}
	}
	
	
	class MotorCellRenderer extends JLabel implements TableCellRenderer
	{
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) 
		{
			Motor m = (Motor) value;
			setOpaque(true);
			
			if(isSelected)
			{
				setBackground(Color.blue);
				setForeground(Color.white);
			}
			else
			{
				
				if(table.getModel().isCellEditable(row, column))
				{
					setBackground(Color.white);
					setForeground(Color.black);
				}
				else
				{
					setBackground(veryLightGrey);
					setForeground(Color.black);
				}
			}
			
			switch(row)
			{
			case STATE:
			{
				String state = m.getState();
				setText(state);
				if(!isSelected && !hasFocus)
				{
					setBackground(SwingResource.getColor4State(state));
					setForeground(table.getForeground());
				}
				else
				{
					setBackground(table.getSelectionBackground());
					setForeground(SwingResource.getColor4State(state));
				}
			}
			break;
			case DEV_NAME:
			{
				setText(m.getDeviceName());
			}
			break;
			case CONTROLLER:
			{
				if(m instanceof PseudoMotor)
				{
					setText("----");
				}
				else
				{
					Controller c = m.getController();
					setText(c != null ? c.getName() : "unknown!");
				}
			}
			break;
			case INDEX:
			{
				setText(""+m.getIdInController());
			}
			break;
			default:
			{
				String paramName = ((MotorsTableModel)table.getModel()).getParamName(row);
				AttributeInfoEx info = m.getAttributeInfo(paramName);

				String s = null;
				if(info == null)
				{
					s = "----";
				}
				else
				{
					IAttribute entity = m.getAttribute(paramName);
					Object v = SwingResource.getEntityValue(entity, info);
					
					if(v == null)
					{
						s = "null value";
					}
					else
					{
						if(v instanceof boolean[])
						{
							s = "";
							for(boolean b : (boolean[])v)
							{
								s += "<" + (b ? "T" : "F") + ">";
							}
						}
						else
							s = v.toString();
					}
				}
				setText(s);
			}
			break;
			}
			return this;
		}
		
	}
	
	class ParamNameCellRenderer extends JLabel implements TableCellRenderer
	{
        public ParamNameCellRenderer() 
        {
			super();
		}

		public Component getTableCellRendererComponent(JTable table, Object value,
                boolean isSelected, boolean hasFocus, int rowIndex, int vColIndex) {

			JTableHeader header = table.getTableHeader();
			
            if (header != null) 
            {
            	setOpaque(true);
                setForeground(header.getForeground());
                setBackground(header.getBackground());
                setFont(header.getFont());
            }
            
            setBorder(UIManager.getBorder("TableHeader.cellBorder"));			
			
        	// Configure the component with the specified value
            setText(value.toString());
    
            // Set tool tip if desired
            setToolTipText((String)value);
    
            // Since the renderer is a component, return itself
            return this;
        }
    
        // The following methods override the defaults for performance reasons
        public void validate() {}
        public void revalidate() {}
        protected void firePropertyChange(String propertyName, Object oldValue, Object newValue) {}
        public void firePropertyChange(String propertyName, boolean oldValue, boolean newValue) {}
		
	}
	
	protected static final String[] PARAM_NAMES = new String[] { 
		"State",
		"Status",
		"Device name",
		"Controller",
		"Index",
		"SimulationMode",
		"Position",
		"DialPosition",
		"Offset",
		"Step_per_unit",
		"Backlash",
		"Base_rate",
		"Acceleration",
		"Deceleration",
		"Velocity"
	};
	
	protected static final int
		STATE      = 0,
		STATUS     = 1,
		DEV_NAME   = 2,
		CONTROLLER = 3,
		INDEX      = 4,
		
		SIMMODE    = 5,
		POSITION   = 6,
		DPOS       = 7,
		OFFSET     = 8,
		SPUNIT     = 9,
		BACKLASH   = 10,
		BASERATE   = 11,
		ACCEL      = 12,
		DECEL      = 13,
		VELOCITY   = 14;
		
	class MotorsTableModel extends AbstractTableModel
	{
		List<Motor> motors = new ArrayList<Motor>();
		List<PseudoMotor> pseudoMotors = new ArrayList<PseudoMotor>();
		List<String> extraParamRowNames = new ArrayList<String>();
		List<String> labelRowNames = new ArrayList<String>();
		
		AttributeList attrList = new AttributeList();
		
		public MotorsTableModel()
		{
		}
		
		public String getParamName(int row)
		{
			if (row < PARAM_NAMES.length)
				return PARAM_NAMES[row];
			return extraParamRowNames.get(row - PARAM_NAMES.length);
		}
		
		public Class<?> getColumnClass(int columnIndex)
		{
			switch(columnIndex) 
			{
				case 0: return String.class;
				default: return Motor.class;
			}
		}

		public int getColumnCount() 
		{
			return motors.size() + pseudoMotors.size() + 1;
		}

		public String getColumnName(int columnIndex) 
		{
			if(columnIndex == 0)
				return " ";
			
			columnIndex--;
			
			if(columnIndex < motors.size())
				return motors.get(columnIndex).getName();
			
			columnIndex -= motors.size();
			
			return pseudoMotors.get(columnIndex).getName();
		}

		public int getRowCount() 
		{
			return labelRowNames.size();
		}

		public Object getValueAt(int rowIndex, int columnIndex) 
		{
			if(columnIndex == 0) 
			{
				return labelRowNames.get(rowIndex);
			}
			columnIndex--;
			
			if(columnIndex < motors.size())
				return motors.get(columnIndex);
			
			columnIndex -= motors.size();
			
			return pseudoMotors.get(columnIndex);
			
		}

		public boolean isCellEditable(int rowIndex, int columnIndex) 
		{
			if(columnIndex == 0 || rowIndex < 5)
				return false;
			
			Motor m = (Motor)getValueAt(rowIndex,columnIndex);
			
			if(m instanceof PseudoMotor)
			{
				if(rowIndex == POSITION)
					return true;
				return false;
			}
			
			String paramName = getParamName(rowIndex);
			
			AttributeInfoEx info = m.getAttributeInfo(paramName);
			
			if(info == null)
				return false;
			
			return !(info.writable == AttrWriteType.READ);
		}

		public void setValueAt(Object aValue, int rowIndex, int columnIndex) 
		{
			Motor m = (Motor)getValueAt(rowIndex,columnIndex);
			
			String paramName = getParamName(rowIndex);
			
			IAttribute entity = m.getAttribute(paramName);
			
			AttributeInfoEx info = m.getAttributeInfo(paramName);
			
			String res = SwingResource.setScalarEntityValue(entity, info, (String) aValue);
			
			if(res != null)
			{
				JOptionPane.showMessageDialog(null, 
						res, "Error", JOptionPane.ERROR_MESSAGE);
			}
		}

		public void update()
		{
			motors = pool.getMotors();
			pseudoMotors = pool.getPseudoMotors();
			
			updateParams();
			
			for(Motor m : motors)
			{
				//m.getEventAttributes().add
			}
			
			fireTableStructureChanged();
		}
		
		protected void updateParams()
		{
			extraParamRowNames.clear();
			labelRowNames.clear();
			
			if(motors.size() == 0)
			{
				for(String paramName : PARAM_NAMES)
				{
					labelRowNames.add(paramName);
				}
				return;
			}
			
			Motor m = motors.get(0);
			
			for(String paramName : PARAM_NAMES)
			{
				AttributeInfoEx info = m.getAttributeInfo(paramName);
				String label = buildParamLabel(paramName, info);
				labelRowNames.add(label);
			}
			
			// Handle extra attributes
			for(Motor motor : motors)
			{
				for(AttributeInfoEx info : motor.getAttributeInfo())
				{
					boolean contains = false;
					for(String paramName : PARAM_NAMES)
					{
						if(paramName.equalsIgnoreCase(info.name))
						{
							contains = true;
							break;
						}
					}
					
					if(contains == false && !extraParamRowNames.contains(info.name))
					{
						String label = buildParamLabel(info.name, info);
						extraParamRowNames.add(info.name);
						labelRowNames.add(label);
					}
				}
			}
		}
		
		protected String buildParamLabel(String paramName, AttributeInfoEx info)
		{
			String lbl = "";
			
			if(info == null)
				lbl = paramName;
			else 
			{
				lbl = info.label;
				
				if(info.label != null && info.label.length() > 0)
					lbl = info.label;
				else
					lbl = paramName;
				
				if(info.unit != null && info.unit.length() > 0 && !info.unit.equalsIgnoreCase("No Unit"))
					lbl += "(" + info.unit + ")";
			}
			return lbl;
				
		}
	}
	
	class PseudoMotorListener implements IStringSpectrumListener
	{

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update();
		}

		public void stateChange(AttributeStateEvent e){}
		public void errorChange(ErrorEvent evt){}
	}
	
	class MotorListener implements IStringSpectrumListener 
	{

		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update();
		}

		public void stateChange(AttributeStateEvent e){}
		public void errorChange(ErrorEvent evt){}
	}	
}
