package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.Component;
import java.util.Vector;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.gui.swing.SwingResource;

public class MachineSelectDialog extends JDialog 
{
	JList machineList;
	Vector<Machine> machines;
	
	public MachineSelectDialog(Vector<Machine> machines)
	{
		this.machines = machines;
		initComponents();
	}

	private void initComponents()
	{
		setTitle("Select machine to load configuration");
		
		getContentPane().setLayout(new BorderLayout());
		
		machineList = new JList( machines );
		machineList.setCellRenderer(new MachineCellRenderer());
		machineList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		JScrollPane machineScrollPane = new JScrollPane(machineList);		
	
		getContentPane().add(machineScrollPane,BorderLayout.CENTER);
		pack();
		setVisible(true);
	}
	
	public Machine getSelectedMachine()
	{
		return (Machine) machineList.getSelectedValue();
	}
	
	protected class MachineCellRenderer extends DefaultListCellRenderer
	{
		@Override
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) 
		{
			Component c = super.getListCellRendererComponent(list, value, index, isSelected,
					cellHasFocus);
			
			Machine machine = (Machine) value;
			
			if(c instanceof JLabel)
			{
				JLabel l = (JLabel) c;
				l.setIcon(SwingResource.smallIconMap.get(IImageResource.getNonDeviceElementIcon(machine)));
			}
			
			return c;
		}
		
	}	
}
