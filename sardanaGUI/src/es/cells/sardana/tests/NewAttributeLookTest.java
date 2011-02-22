package es.cells.sardana.tests;

import java.awt.BorderLayout;
import java.awt.HeadlessException;

import javax.swing.JFrame;

import es.cells.tangoatk.widget.attribute.NumberScalarViewer;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.attribute.NumberScalar;

public class NewAttributeLookTest extends JFrame
{
	public NewAttributeLookTest() throws HeadlessException
	{
		super("New Attribute Look test");
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		getContentPane().setLayout(new BorderLayout());
		
		NumberScalarViewer numberViewer = new NumberScalarViewer();
	
		getContentPane().add(numberViewer, BorderLayout.CENTER);
		
		pack();
		
		setVisible(true);
	}

	public static void main(String[] args)
	{
		new NewAttributeLookTest();
	}

	
}
