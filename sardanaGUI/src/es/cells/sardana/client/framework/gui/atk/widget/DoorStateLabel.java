package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.Icon;
import javax.swing.JLabel;
import javax.swing.Timer;

public class DoorStateLabel extends JLabel {
	
	private static final long serialVersionUID = 1L;
	
	private static final int BLINKING_RATE = 300; // in ms

	private boolean blinking;
	
	private Icon onIcon;
	private Icon offIcon;
	
	public Timer timer;
	
	public DoorStateLabel()
	{
		super();
		blinking = false;
	    timer = new Timer( BLINKING_RATE , new TimerListener(this));
	    timer.setInitialDelay(0);
	}
	
	public void setBlinking(boolean flag) 
	{
	    this.blinking = flag;
	}
	  
	public boolean isBlinking() 
	{	    
		return this.blinking;
	}
	
	public Icon getOnIcon() 
	{
		return onIcon;
	}

	public void setOnIcon(Icon onIcon) 
	{
		this.onIcon = onIcon;
	}

	public Icon getOffIcon() {
		return offIcon;
	}

	public void setOffIcon(Icon offIcon) {
		this.offIcon = offIcon;
	}

	
	  
	private class TimerListener implements ActionListener {
		  
		private DoorStateLabel bl;
		private Icon on;
		private Icon off;
		private boolean isOff = true;
		    
		public TimerListener(DoorStateLabel bl) 
		{
			this.bl = bl;
		    onIcon  = bl.getOnIcon();
		    offIcon = bl.getOffIcon();
		}
		 
		public void actionPerformed(ActionEvent e) 
		{
			if (bl.isBlinking()) 
			{
				if (isOff) 
				{
		          bl.setIcon(onIcon);
		        }
		        else 
		        {
		          bl.setIcon(offIcon);
		        }
		        isOff = !isOff;
		    }
		    else 
		    {
		    	if (isOff) 
		    	{
		    		bl.setIcon(on);
		    		isOff = false;
		    	}
		    }
		}
	}




	
}
	


