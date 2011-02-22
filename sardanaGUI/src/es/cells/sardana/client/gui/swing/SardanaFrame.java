package es.cells.sardana.client.gui.swing;

import javax.swing.JFrame;

import es.cells.sardana.client.framework.gui.IImageResource;
import fr.esrf.tangoatk.widget.util.Splash;

@SuppressWarnings("serial")
public class SardanaFrame extends JFrame 
{
	protected SardanaMainPanel mainPanel;

	
	public SardanaFrame(Splash splash)
	{
		super("Sardana");
		initComponents(splash);
	}
	
	protected void initComponents(Splash splash)
	{
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		setIconImage(SwingResource.smallIconMap.get(IImageResource.IMG_SARDANA).getImage());
		
		try
		{
			mainPanel = new SardanaMainPanel(splash);
			getContentPane().add(mainPanel);
			setJMenuBar(mainPanel.getMenuBar());
			this.pack();
			this.setVisible(true);
			
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
	}
}
