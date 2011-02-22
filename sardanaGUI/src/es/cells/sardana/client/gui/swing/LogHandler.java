/**
 * 
 */
package es.cells.sardana.client.gui.swing;

import java.util.ArrayList;
import java.util.Date;
import java.util.logging.Handler;
import java.util.logging.LogRecord;

import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;

class LogHandler extends Handler
{
	JTable output;
	
	protected ArrayList<LogRecord> pendingRecords = new ArrayList<LogRecord>();
	
	public LogHandler(JTable output)
	{
		this.output = output;
	}
	
	@Override
	public void close() throws SecurityException
	{
		
	}

	@Override
	public void flush()
	{
		for(LogRecord logRecord: pendingRecords)
		{
			publish(logRecord);
		}
		pendingRecords.clear();
	}

	public void setTable(JTable output)
	{
		this.output = output;
		flush();
	}
	
	@Override
	public void publish(LogRecord record)
	{
		if(output != null)
		{
			String method = "-";
			
			if(record.getSourceClassName() != null &&
			   record.getSourceMethodName() != null)
			{
				method = record.getSourceClassName()+ "::" + record.getSourceMethodName();
				Object[] params = record.getParameters();
				if(params != null && params.length > 0)
				{
					int count = params.length;
					method += "(";
					for(int i = 0; i < count; i++)
					{
						method += params[i];
						method += (i < count -1 ) ? ", " : ")";
					}
				}
			}
			
			((DefaultTableModel)output.getModel()).addRow(new String[] 
			{
				record.getLevel().toString(),
				record.getMessage(),
				record.getLoggerName(),
				method,
				new Date(record.getMillis()).toString()
			}	
			);
		}
		else
			pendingRecords.add(record);
	}
}