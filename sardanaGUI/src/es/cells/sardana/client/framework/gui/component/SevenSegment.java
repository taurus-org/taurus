package es.cells.sardana.client.framework.gui.component;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;

import javax.swing.JComponent;

/**
* <b>The Segments</b><br>
* <pre>
*      0    
*    ----   
*  5|    |1 
*   |  6 |  
*    ----   
*  4|    |2 
*   |    |  
*    ----   
*      3    
* </pre>
*/
public class SevenSegment extends JComponent
{
	protected int value;

	protected static boolean[][] drawElems = new boolean[][] {
		{ true, true, true, true, true, true, false }, // 0
		{ false, true, true, false, false, false, false }, // 1
		{ true, true, false, false, true, false, true }, // 2
		{ true, true, true, true, false, false, true }, // 3
		{ false, true, true, false, false, true, true }, // 4
		{ true, false, true, true, false, true, true }, // 5
		{ true, false, true, true, true, true, true }, // 6
		{ true, true, true, false, false, false, false }, // 7
		{ true, true, true, true, true, true, true }, // 8
		{ true, true, true, true, false, true, true }, // 9
		{ true, true, true, false, true, true, true }, // A
		{ true, true, true, true, true, true, true }, // B
		{ true, false, false, true, true, true, false }, // C
		{ true, true, true, true, true, true, false }, // D
		{ true, false, false, true, true, true, true }, // E
		{ true, false, false, false, true, true, true }, // F
	};

	protected int elemLength;
	protected int elemThickness;
	
	protected boolean drawShadow;
	protected Color shadowColor;
	
	public SevenSegment()
	{
		super();
	}
	
	public int getValue()
	{
		return value;
	}

	public void setValue(int value)
	{
		this.value = value;
		invalidate();
	}

	@Override
	protected void paintComponent(Graphics g) 
	{
		Graphics2D g2d = (Graphics2D) g;
		
		if (isOpaque()) { //paint background
            g.setColor(getBackground());
            g.fillRect(0, 0, getWidth(), getHeight());
		}
		
		paintShadow(g2d);
		
		int w = getWidth();
		int h = getHeight();
		
		
	}
	
	protected void paintShadow(Graphics2D g2d)
	{
		if(!drawShadow)
			return;
	}
	
	protected boolean isActive(int elem)
	{
		return drawElems[value][elem];
	}
}
