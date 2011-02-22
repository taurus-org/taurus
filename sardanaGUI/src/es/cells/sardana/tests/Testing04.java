package es.cells.sardana.tests;

import java.awt.Dimension;

import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;

import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class Testing04 extends JFrame
{
	public Testing04()
	{
		setTitle("Testing 4");
		
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		Object[] elems = new Object[] {
				new ImageIcon("res/64x64/motor.png"),
				new ImageIcon("res/64x64/motor.png"),
				new ImageIcon("res/64x64/unknown.png"),
				new ImageIcon("res/64x64/motor_na.png"),
				new ImageIcon("res/64x64/motor_warning.png")
		};
		
		JList list = new JList(elems);
		list.setLayoutOrientation(JList.HORIZONTAL_WRAP);
		list.setSelectionMode(ListSelectionModel.SINGLE_INTERVAL_SELECTION);
		list.setVisibleRowCount(-1);
		JScrollPane scrollPane = new JScrollPane(list);
		scrollPane.setPreferredSize(new Dimension(250, 80));
		getContentPane().add(scrollPane);
				
		pack();
		setVisible(true);
		
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		new Testing04();
	}

	static int gid = 0;
	
	class MotorListListener implements IStringSpectrumListener
	{
		int id;
		
		public MotorListListener()
		{
			id = gid++;
		}
		
		public void stringSpectrumChange(StringSpectrumEvent e) 
		{
			System.out.print("MotorList changed (" + id + "):\n\t");
			for(String elem : e.getValue())
				System.out.print(elem + ", ");
			System.out.println();
		}

		public void stateChange(AttributeStateEvent arg0) {}
		public void errorChange(ErrorEvent arg0) {}
		
	}
}
