package es.cells.sardana.tests;

import javax.swing.JFrame;

import es.cells.sardana.client.framework.gui.component.SevenSegment;

public class SevenSegmentTest extends JFrame
{

	public SevenSegmentTest() 
	{	
		super("Seven Segment display");
		
		SevenSegment s = new SevenSegment();
		
		getContentPane().add(s);
		
		pack();
		setVisible(true);
	}

	public static void main(String[] args)
	{
		new SevenSegmentTest();
	}
}
