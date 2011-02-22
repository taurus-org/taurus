package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.List;

import javax.swing.AbstractCellEditor;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSpinner;
import javax.swing.JTable;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingConstants;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.table.AbstractTableModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableCellEditor;
import javax.swing.table.TableColumn;

import es.cells.sardana.client.framework.pool.CounterTimer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.IStringScalarListener;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;
import fr.esrf.tangoatk.core.StringScalarEvent;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;
import fr.esrf.tangoatk.core.attribute.NumberScalar;
import fr.esrf.tangoatk.core.attribute.StringScalar;
import fr.esrf.tangoatk.core.attribute.StringSpectrum;
import fr.esrf.tangoatk.widget.util.ATKConstant;

public class MeasurementGroupTableViewer extends JPanel
{
	protected static final ImageIcon applyIcon = new ImageIcon("res/16x16/go-jump.png");
	
	protected JScrollPane     pane;
	protected JTable          measurementGroupTable;
	protected TableModel      model;
	
	DevicePool pool;
	
	MeasurementGroupListener measurementGroupListener;
	StateListener stateListener;
	TimerListener timerListener;
	MonitorListener monitorListener;
	ITimeListener iTimeListener;
	ICountListener iCountListener;
	ChannelListListener channelListListener;
	
	public MeasurementGroupTableViewer()
	{
		super();
		initComponents();
	}
	
	private void initComponents()
	{
		model = new TableModel();
		
		//setBorder(BorderFactory.createTitledBorder("Measurement Groups"));
		
		DefaultTableColumnModel colModel = new DefaultTableColumnModel();
		
		TableColumn column = new TableColumn(0);
		column.setHeaderValue("State");
		column.setPreferredWidth(70);
		column.setMaxWidth(70);
		column.setCellRenderer(new StateCellRenderer());
		colModel.addColumn(column);
		
		column = new TableColumn(1);
		column.setHeaderValue("Name");
		column.setPreferredWidth(120);
		column.setMaxWidth(120);
		colModel.addColumn(column);
		
		column = new TableColumn(2);
		column.setHeaderValue("Device");
		colModel.addColumn(column);

		column = new TableColumn(3);
		column.setHeaderValue("Channels");
		colModel.addColumn(column);

		column = new TableColumn(4);
		column.setHeaderValue("Timer");
		column.setCellRenderer(new TimerCellRenderer());
		column.setCellEditor(new TimerCellEditor());
		colModel.addColumn(column);

		column = new TableColumn(5);
		column.setCellRenderer(new MonitorCellRenderer());
		column.setCellEditor(new MonitorCellEditor());
		column.setHeaderValue("Monitor");
		colModel.addColumn(column);
		
		column = new TableColumn(6);
		column.setHeaderValue("I. Time");
		column.setCellRenderer(new ITimeCellRenderer());
		column.setCellEditor(new ITimeCellEditor());
		column.setPreferredWidth(70);
		column.setMaxWidth(70);		
		colModel.addColumn(column);

		column = new TableColumn(7);
		column.setHeaderValue("I. Count");
		column.setCellRenderer(new ICountCellRenderer());
		column.setCellEditor(new ICountCellEditor());
		column.setPreferredWidth(70);
		column.setMaxWidth(70);
		colModel.addColumn(column);
		
		setLayout(new BorderLayout());
		pane = new JScrollPane();
		measurementGroupTable = new JTable(model, colModel);
		measurementGroupTable.setRowHeight(26);
		
		stateListener = new StateListener();
		timerListener = new TimerListener();
		monitorListener = new MonitorListener();
		iTimeListener = new ITimeListener();
		iCountListener = new ICountListener();
		channelListListener = new ChannelListListener();
		measurementGroupListener = new MeasurementGroupListener();
		
		
		pane.setViewportView(measurementGroupTable);
		
		add(pane, BorderLayout.CENTER);
	}

	public JTable getTable()
	{
		return measurementGroupTable;
	}

	public MeasurementGroup getSelectedMeasurementGroup()
	{
		int row =  measurementGroupTable.getSelectedRow();
		
		if(row < 0)
			return null;
		
		return (MeasurementGroup) measurementGroupTable.getValueAt(row, 1);
	}
	
	public List<MeasurementGroup> getSelectedMeasurementGroups()
	{
		ArrayList<MeasurementGroup> ret = new ArrayList<MeasurementGroup>();
		int[] rows = measurementGroupTable.getSelectedRows();
		
		if(rows == null || rows.length == 0)
			return ret;
		
		for(int row : rows)
		{
			ret.add((MeasurementGroup) measurementGroupTable.getValueAt(row, 1));
		}
		
		return ret;
	}

	public void setModel(DevicePool p)
	{
		if(pool != null)
		{
			pool.removeMeasurementGroupListListener(measurementGroupListener);
			for(MeasurementGroup mg : model.measurementGroups)
			{
				mg.removeDevStateScalarListener(stateListener);
				mg.removeTimerListener(timerListener);
				mg.removeMonitorListener(monitorListener);
				mg.removeIntegrationTimeListener(iTimeListener);
				mg.removeIntegrationCountListener(iCountListener);
				mg.removeChannelsListener(channelListListener);
			}
		}
		
		pool = p;
		
		if(pool != null)
		{
			pool.addMeasurementGroupListListener(measurementGroupListener);
			model.update(pool.getMeasurementGroups());
			for(MeasurementGroup mg : model.measurementGroups)
			{
				mg.addDevStateScalarListener(stateListener);
				mg.addTimerListener(timerListener);
				mg.addMonitorListener(monitorListener);
				mg.addIntegrationTimeListener(iTimeListener);
				mg.addIntegrationCountListener(iCountListener);
				mg.addChannelsListener(channelListListener);
			}
		}
	}
	
	protected class MeasurementGroupListener implements IStringSpectrumListener 
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update(pool.getMeasurementGroups());
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}	
	
	protected class StateListener implements IDevStateScalarListener 
	{
		public void devStateScalarChange(DevStateScalarEvent e) 
		{
			Device d = ((DevStateScalar)e.getSource()).getDevice();
			model.devStateScalarChange(d);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}

	}
	
	protected class TimerListener implements IStringScalarListener
	{
		public void stringScalarChange(StringScalarEvent e)
		{
			Device d = ((StringScalar)e.getSource()).getDevice();
			model.timerChange(d);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}

	}
	
	protected class MonitorListener implements IStringScalarListener
	{
		public void stringScalarChange(StringScalarEvent e)
		{
			Device d = ((StringScalar)e.getSource()).getDevice();
			model.monitorChange(d);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}
	
	protected class ITimeListener implements INumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent e) 
		{
			Device d = ((NumberScalar)e.getSource()).getDevice();
			model.integrationTimeChange(d);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}
	
	protected class ICountListener implements INumberScalarListener
	{
		public void numberScalarChange(NumberScalarEvent e) 
		{
			Device d = ((NumberScalar)e.getSource()).getDevice();
			model.integrationCountChange(d);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}

	protected class ChannelListListener implements IStringSpectrumListener
	{
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			Device d = ((StringSpectrum)e.getSource()).getDevice();
			model.channelListChange(d);
		}
		
		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}
	}
	
	
	
	class TableModel extends AbstractTableModel
	{
		public List<MeasurementGroup> measurementGroups;

		
		@Override
		public boolean isCellEditable(int rowIndex, int columnIndex) 
		{
			return ((columnIndex >= 4) && (columnIndex <= 7)) ? true : 
				super.isCellEditable(rowIndex, columnIndex);
		}

		public int getColumnCount()
		{
			return 8;
		}

		public int getRowCount()
		{
			return measurementGroups != null ? measurementGroups.size() : 0;
		}

		@Override
		public Class<?> getColumnClass(int columnIndex) 
		{
	    	if(columnIndex == 0)
	    		return JLabel.class;
	    	else if(columnIndex == 1)
	    		return MeasurementGroup.class; 
	    	else if(columnIndex == 2)
	    		return String.class; 
	    	else if(columnIndex == 3)
	    		return ArrayList.class;
	    	else
	    		return MeasurementGroup.class;
		}

		public Object getValueAt(int rowIndex, int columnIndex)
		{
			MeasurementGroup mg = null;
		
			int measurementGroupsLen = measurementGroups.size();
			
			if(rowIndex < measurementGroupsLen)
			{
				mg = measurementGroups.get(rowIndex);
			}
			
			if(mg == null)
				return null;
			
			if(columnIndex == 0)
			{
				JLabel l = new JLabel(mg.getState());
				l.setOpaque(true);
				return l;
			}
			else if(columnIndex == 2)
				return mg.getDeviceName();
			else if(columnIndex == 3)
				return mg.getChannels();
			else 
				return mg;
		}
		
	    private void updateMeasurementGroupList(List<MeasurementGroup> newMeasurementGroups)
	    {
	    	measurementGroups = newMeasurementGroups;
	    }

	    public void update(List<MeasurementGroup> newMeasurementGroups)
	    {
	    	updateMeasurementGroupList(newMeasurementGroups);
	    	fireTableDataChanged();
	    }

		public void devStateScalarChange(Device d)
		{
			fireCellChanged(d, 0);
		}

		public void channelListChange(Device d) 
		{
			fireCellChanged(d, 3);
		}

		public void timerChange(Device d)
		{
			fireCellChanged(d, 4);
		}
		
		public void monitorChange(Device d) 
		{
			fireCellChanged(d, 5);
		}
		
		public void integrationTimeChange(Device d) 
		{
			fireCellChanged(d, 6);
		}

		public void integrationCountChange(Device d) 
		{
			fireCellChanged(d, 7);
		}
		
		protected void fireCellChanged(Device d, int column)
		{
			String devName = d.getName();
			int channelCount = measurementGroups.size();
			for(int i = 0; i < channelCount; i++)
			{
				MeasurementGroup mg = measurementGroups.get(i);
				if(mg.getDeviceName().equalsIgnoreCase(devName))
				{
					fireTableCellUpdated(i, column);
					return;
				}
			}				
		}
	}
	
	//TODO: Substance look and feel
	//class StateCellRenderer extends SubstanceDefaultTableCellRenderer
	class StateCellRenderer extends DefaultTableCellRenderer
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
	
	class TimerCellRenderer extends DefaultTableCellRenderer
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			MeasurementGroup grp = (MeasurementGroup) value;
			
			String timer_name = null;
			
			if(grp == null || grp.getTimer() == null)
				timer_name = "Not Found!";
			else
				timer_name = grp.getTimer().getName();
			
			return super.getTableCellRendererComponent(table, timer_name, isSelected, hasFocus,
					row, column);
		}
	}
	
	class TimerCellEditor extends AbstractCellEditor implements TableCellEditor, ActionListener
	{
		JComboBox combo = null;
		MeasurementGroup currentMG = null;
		
		public TimerCellEditor()
		{
			combo = new JComboBox(new Object[]{MeasurementGroup.TimerNotInitialized});
		}
		
		public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) 
		{
			currentMG = (MeasurementGroup) value;
			combo.removeActionListener(this);
			combo.removeAllItems();
			combo.addItem(MeasurementGroup.TimerNotInitialized);
			for(CounterTimer ct : currentMG.getCounterTimers())
				combo.addItem(ct);
			if(combo.getItemCount() > 0)
				combo.setSelectedItem(currentMG.getTimer());
			combo.addActionListener(this);
			return combo;
		}

		public Object getCellEditorValue() 
		{
			return currentMG;
		}

		public void actionPerformed(ActionEvent e) 
		{
			CounterTimer ct = (CounterTimer) combo.getSelectedItem();
			
			if(ct == null)
				return;
			
			if(ct != currentMG.getTimer())
			{
				currentMG.setTimer(ct);
			}
			fireEditingStopped();
		}
	}

	class MonitorCellRenderer extends DefaultTableCellRenderer
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			MeasurementGroup grp = (MeasurementGroup) value;
			return super.getTableCellRendererComponent(table, grp.getMonitor().getName(), isSelected, hasFocus,
					row, column);
		}
	}
	
	class MonitorCellEditor extends AbstractCellEditor implements TableCellEditor, ActionListener
	{
		JComboBox combo = null;
		MeasurementGroup currentMG = null;
		
		public MonitorCellEditor()
		{
			combo = new JComboBox(new Object[]{MeasurementGroup.MonitorNotInitialized});
		}
		
		public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) 
		{
			currentMG = (MeasurementGroup) value;
			combo.removeActionListener(this);
			combo.removeAllItems();
			combo.addItem(MeasurementGroup.MonitorNotInitialized);
			for(CounterTimer ct : currentMG.getCounterTimers())
				combo.addItem(ct);
			if(combo.getItemCount() > 0)
				combo.setSelectedItem(currentMG.getMonitor());
			combo.addActionListener(this);
			return combo;
		}

		public Object getCellEditorValue() 
		{
			return currentMG;
		}

		public void actionPerformed(ActionEvent e) 
		{
			CounterTimer ct = (CounterTimer) combo.getSelectedItem();
			
			if(ct == null)
				return;
			
			if(ct != currentMG.getMonitor())
			{
				currentMG.setMonitor(ct);
			}
			fireEditingStopped();
		}
	}

	class ITimeCellRenderer extends DefaultTableCellRenderer
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			MeasurementGroup grp = (MeasurementGroup) value;
			return super.getTableCellRendererComponent(table, grp.getIntegrationTime(), isSelected, hasFocus,
					row, column);
		}
	}
	
	class ITimeCellEditor extends AbstractCellEditor implements TableCellEditor, ChangeListener, ActionListener
	{
		JPanel panel;
		JSpinner spinner = null;
		JButton button = null;
		MeasurementGroup currentMG = null;
		
		public ITimeCellEditor()
		{
			panel = new JPanel(new BorderLayout(0,0));
			button = new JButton(applyIcon);
			button.setMargin(new Insets(0,0,0,0));
			spinner = new JSpinner(new SpinnerNumberModel(0.0,0.0,Double.MAX_VALUE,0.1));
			panel.add(spinner,BorderLayout.CENTER);
			panel.add(button,BorderLayout.EAST);
		}
		
		public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) 
		{
			currentMG = (MeasurementGroup) value;
			spinner.removeChangeListener(this);
			button.removeActionListener(this);
			spinner.setValue(currentMG.getIntegrationTime());
			spinner.addChangeListener(this);
			button.addActionListener(this);
			button.setEnabled(false);
			return panel;
		}

		public Object getCellEditorValue() 
		{
			return currentMG;
		}

		public void actionPerformed(ActionEvent e) 
		{
			double currITime = currentMG.getIntegrationTime();
			double newITime = (Double) spinner.getValue();
			
			if(currITime == newITime)
				return;
			
			currentMG.setIntegrationTime(newITime);
			button.setEnabled(false);
			fireEditingStopped();
		}

		public void stateChanged(ChangeEvent e) 
		{
			double currITime = currentMG.getIntegrationTime();
			double newITime = (Double) spinner.getValue();
			button.setEnabled(currITime != newITime);
		}
	}
	
	class ICountCellRenderer extends DefaultTableCellRenderer
	{
		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			MeasurementGroup grp = (MeasurementGroup) value;
			return super.getTableCellRendererComponent(table, grp.getIntegrationCount(), isSelected, hasFocus,
					row, column);
		}
	}
	
	class ICountCellEditor extends AbstractCellEditor implements TableCellEditor, ChangeListener, ActionListener
	{
		JPanel panel;
		JSpinner spinner = null;
		JButton button = null;
		MeasurementGroup currentMG = null;
		
		public ICountCellEditor()
		{
			panel = new JPanel(new BorderLayout(0,0));
			button = new JButton(applyIcon);
			button.setMargin(new Insets(0,0,0,0));
			spinner = new JSpinner(new SpinnerNumberModel(0,0,Integer.MAX_VALUE,1));
			panel.add(spinner,BorderLayout.CENTER);
			panel.add(button,BorderLayout.EAST);
		}
		
		public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected, int row, int column) 
		{
			currentMG = (MeasurementGroup) value;
			spinner.removeChangeListener(this);
			button.removeActionListener(this);
			spinner.setValue(currentMG.getIntegrationCount());
			spinner.addChangeListener(this);
			button.addActionListener(this);
			button.setEnabled(false);
			return panel;
		}

		public Object getCellEditorValue() 
		{
			return currentMG;
		}

		public void actionPerformed(ActionEvent e) 
		{
			int currICount = currentMG.getIntegrationCount();
			int newICount = (Integer) spinner.getValue();
			
			if(currICount == newICount)
				return;
			
			currentMG.setIntegrationCount(newICount);
			button.setEnabled(false);
			fireEditingStopped();
		}

		public void stateChanged(ChangeEvent e) 
		{
			int currICount = currentMG.getIntegrationCount();
			int newICount = (Integer) spinner.getValue();
			button.setEnabled(currICount != newICount);
		}
	}	
}
