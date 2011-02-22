package es.cells.sardana.client.gui.swing;

import java.awt.BorderLayout;

import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.table.TableModel;

public class LogPanel extends JPanel {

	protected JTable logTable;
	
	protected LogHandler logHandler;
	
	public LogPanel(LogHandler logHandler) 
	{
		super( new BorderLayout() );
		
		this.logHandler = logHandler;
		
		initComponents();
	}

	private void initComponents() 
	{
		String[] cols = new String[] { "Severety", "Message", "System", "Method", "Time" };
		int[] prefW = new int [] { 60, 230, 80, 100, 80};

		TableModel tableModel = new DefaultTableModel(0, cols.length);
		
		TableColumnModel columns = new DefaultTableColumnModel();
		
		for(int i = 0; i < tableModel.getColumnCount(); i++)
		{
			TableColumn c = new TableColumn(i, prefW[i]);
			c.setHeaderValue(cols[i]);
			columns.addColumn(c);
		}
		
		logTable = new JTable( tableModel, columns );
		logTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
		
		logHandler.setTable(logTable);
		
		
		JScrollPane pane = new JScrollPane();
		pane.setViewportView(logTable);
		
		add(pane, BorderLayout.CENTER);
	}
	
	
	
	public LogHandler getLogHandler()
	{
		return logHandler;
	}
}
