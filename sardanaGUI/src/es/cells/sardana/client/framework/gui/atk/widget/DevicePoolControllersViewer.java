package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.Component;

import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;

import es.cells.sardana.client.framework.SardanaManager;
import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.CtrlState;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.tangoatk.widget.attribute.StringSpectrumTableViewer;
import fr.esrf.tangoatk.core.IStringSpectrum;

public class DevicePoolControllersViewer extends StringSpectrumTableViewer
{
	protected DevicePool devicePool;
	
	protected static ImageIcon ctrlOkIcon = new ImageIcon(IImageResource.IMG_CTRL_OK);
	protected static ImageIcon ctrlErrorIcon = new ImageIcon("res/24x24/important.png");
	
	public DevicePoolControllersViewer()
	{
		super();
	}

	public DevicePoolControllersViewer(Object[] columnNames, int columnIndex)
	{
		super(columnNames, columnIndex);
	}

	public DevicePoolControllersViewer(Object[] columnNames)
	{
		super(columnNames);
	}
	
	@Override
	protected void initComponents(Object[] columnNames)
	{
		
		super.initComponents(columnNames);
		
		StatusCellRenderer cellRenderer = new StatusCellRenderer();
		
		TableColumnModel colModel = strSpectTable.getColumnModel();
		
		for(int columnIndex = 0 ; columnIndex < colModel.getColumnCount(); columnIndex++)
		{
			TableColumn column = colModel.getColumn(columnIndex);
			
			column.setCellRenderer(cellRenderer);
		}
		
		/* Commented Code description: make a new column with the state of the 
		 * controller as a background color
		DefaultTableModel model = (DefaultTableModel)strSpectTable.getModel();

		TableColumn statusColumn = new TableColumn(model.getColumnCount());
		statusColumn.setHeaderValue("State");
		statusColumn.setCellRenderer(  );
		
		boolean autoCreate = strSpectTable.getAutoCreateColumnsFromModel();
		
		strSpectTable.setAutoCreateColumnsFromModel(false);
		
		strSpectTable.addColumn(statusColumn);
		model.addColumn("State");
		
		strSpectTable.setAutoCreateColumnsFromModel(autoCreate);
		*/
		
	}

	@Override
	public void setModel(IStringSpectrum strSpectAtt)
	{
		if(strSpectAtt != null)
		{
			DevicePool newDevicePool = SardanaManager.getInstance().getPoolNode(strSpectAtt.getDevice().getName()).getDevicePool(); 
			setDevicePool( newDevicePool );
		}
		super.setModel(strSpectAtt);
	}

	public DevicePool getDevicePool()
	{
		return devicePool;
	}

	public void setDevicePool(DevicePool devicePool)
	{
		this.devicePool = devicePool;
		//errorHandler.setModel(devicePool.getDevice());
	}

	/*
	public class DevicePoolErrorHandler implements IDeviceListener 
	{
		protected Device device = null;
		
		protected ArrayList<Integer> errorRows = new ArrayList<Integer>();
		
		public void setModel(Device device)
		{
			if(this.device != null)
			{
				this.device.removeListener(this);
			}
			this.device = device;
			this.errorRows.clear();
			device.addListener( this );
		}

		public void statusChange(StatusEvent evt)
		{
			String newStatus = evt.getStatus();
			
			boolean ctrlRequiresAttention = newStatus.contains(DevicePoolUtils.POOL_STATUS_CTRL_ERROR);
			
			if(ctrlRequiresAttention) 
			{
				String [] errorList = DevicePoolUtils.POOL_STATUS_CTRL_ERROR_SPLIT_PATTERN.split(newStatus);

				for(String errorMsg : errorList)
				{
					Matcher matcher = DevicePoolUtils.POOL_STATUS_CTRL_ERROR_PATTERN.matcher(errorMsg);
					
					if(matcher.matches())
					{
						String className = matcher.group( DevicePoolUtils.POOL_STATUS_CTRL_ERROR_CTRL_CLASS_INDEX);
						//String libName = matcher.group( DevicePoolUtils.POOL_STATUS_CTRL_ERROR_CTRL_LIB_INDEX);
						String ctrlInstance = matcher.group( DevicePoolUtils.POOL_STATUS_CTRL_ERROR_CTRL_INSTANCE_INDEX);
						
						int rowCount = strSpectTable.getRowCount();
						for(int i = 0; i < rowCount ; i++)
						{
							String currCtrlName = (String) strSpectTable.getValueAt(i, 1);
							String currCtrlInstance = (String) strSpectTable.getValueAt(i, 2);
							
							// TODO: remove igoneCase comparison
							if(currCtrlName.equalsIgnoreCase(className) && 
							   currCtrlInstance.equalsIgnoreCase(ctrlInstance))
								errorRows.add(i);
						}
					}
				}
			}
		}

		public boolean isRowInError(int row)
		{
			return errorRows.contains(row);
		}
		
		public void stateChange(StateEvent evt)
		{
		}

		public void errorChange(ErrorEvent evt)
		{
		}
	}
	*/
	
	class StatusCellRenderer extends DefaultTableCellRenderer
	{

		@Override
		public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column)
		{
			Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
					row, column);
			
			int columnId = table.getColumnModel().getColumn(column).getModelIndex();
			
			if(columnId == columnIndex)
			{
				String ctrlName = (String)value;
				Controller ctrl = devicePool.getController(ctrlName);
				
				if(ctrl == null)
				{
					((JLabel)c).setIcon(ctrlErrorIcon);
				}
				else
				{
					if(ctrl.getState() == CtrlState.Error)
						((JLabel)c).setIcon(ctrlErrorIcon);
					else 
						((JLabel)c).setIcon(ctrlOkIcon);
				}
			}
			else 
				((JLabel)c).setIcon(null);
				
			return c;
		}
		
	}
}
