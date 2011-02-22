package es.cells.tangoatk.widget.attribute;

import java.awt.BorderLayout;
import java.awt.Component;

import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumnModel;
import javax.swing.table.TableModel;

import es.cells.sardana.client.framework.SardanaManager;
import fr.esrf.Tango.DevFailed;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.IDevStateScalar;
import fr.esrf.tangoatk.widget.attribute.StateViewer;

/**
 * A Specific String Spectrum viewer that interprets each string item of
 * the string spectrum as a Device.
 * The user of this class must specify which index of the regular expression
 * contains the Device Name (in the usual device format: xxx/xxx/xxx). 
 * 
 * @author tcoutinho
 *
 */
public class StringSpectrumDeviceTableViewer extends StringSpectrumTableViewer
{

	protected int deviceColumnIndex;
	
	/**
	 * This constructor will create a multiple column table view of the 
	 * string spectrum. 
	 * 
	 * @param columnNames Array containing the column titles
	 * @param columnIndex The column that will represent the primary key/indentifier of the
	 *                    table. If set to -1 the complete string will be used as the identifier.
	 * @param deviceColumnIndex The column index that contains the device name.
	 */
	public StringSpectrumDeviceTableViewer(Object[] columnNames, int columnIndex, int deviceColumnIndex)
	{
		super(columnNames, columnIndex);
		this.deviceColumnIndex = deviceColumnIndex; 
	}

	@Override
	protected TableColumnModel createColumnModel(Object[] columnNames)
	{
		Object[] cols = new Object[columnNames.length + 1];
		System.arraycopy(columnNames, 0, cols, 0, columnNames.length);
		cols[columnNames.length] = "State";
		TableColumnModel model = super.createColumnModel(cols);
		model.getColumn(columnNames.length).setCellRenderer(new DeviceStateCellRenderer());
		return model;
	}

	@Override
	protected TableModel createTableModel(int columnCount)
	{
		return super.createTableModel(columnCount + 1);
	}
	
	@Override
	protected Object[] getCells(String row)
	{
		Object[] cells = super.getCells(row);
		
		if(cells == null)
			return null;

		Object[] ret = new Object[cells.length + 1];
		
		System.arraycopy(cells, 0, ret, 0, cells.length);
		
		String devName = (String)cells[deviceColumnIndex];
		
		IDevStateScalar state = SardanaManager.getInstance().
										getSardanaDevice(devName).getStateAttributeModel();
		
		if(state == null)
		{
			ret[ret.length-1] = "Device not found: " + devName;
		}
		else 
		{
			MyStateViewer devState = new MyStateViewer();
			
			// force not to show any text
			Component value = devState.getComponent(1);
			devState.removeAll();
			devState.setLayout( new BorderLayout() );
			devState.add(value, BorderLayout.CENTER);
			if(state != null)
			{
				if(state.getValue() != null)
				{
					devState.setModel( state );
					ret[ret.length-1] = devState;
				}
			}
		}
		return ret;
	}

	public void clearTable()
	{
		DefaultTableModel model = getTableModel();
		
		int rowCount = model.getRowCount();
		int lastColumnIndex = model.getColumnCount() - 1;
		
		for(int i = 0; i < rowCount; i++)
		{
			Object stateCell = model.getValueAt(0, lastColumnIndex);
			if(stateCell instanceof StateViewer)
			{
				((MyStateViewer)stateCell).getModel().
							removeDevStateScalarListener((MyStateViewer)stateCell);
			}
			model.removeRow(0);
		}
	}
	
	class DeviceStateCellRenderer implements TableCellRenderer
	{
		public Component getTableCellRendererComponent(JTable table, 
														Object value, 
														boolean isSelected, 
														boolean hasFocus, 
														int row, 
														int column)
		{
			if(value instanceof String)
				return new JLabel((String)value);
			
			MyStateViewer viewer = (MyStateViewer) value;
			return viewer;
		}
	}
	
	class MyStateViewer extends StateViewer
	{
		@Override
		public void devStateScalarChange(DevStateScalarEvent evt)
		{
			super.devStateScalarChange(evt);
			//TODO: performance improvement: update only the cell wich has been changed
			getTableModel().fireTableRowsUpdated(0, getTableModel().getRowCount());
		}
		
		
	}
}
