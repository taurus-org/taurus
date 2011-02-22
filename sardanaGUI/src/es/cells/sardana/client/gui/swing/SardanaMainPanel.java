package es.cells.sardana.client.gui.swing;

import java.awt.BorderLayout;
import java.awt.Container;

import javax.swing.JMenuBar;
import javax.swing.JPanel;
import javax.swing.JSplitPane;
import javax.swing.JTabbedPane;

import es.cells.sardana.client.framework.SardanaManager;
import fr.esrf.tangoatk.widget.util.Splash;

public class SardanaMainPanel extends JPanel 
{
	JSplitPane splitPane;
	
	Container treeView;
	Container displayView;
	Container logView;
	
	Splash splash;
	
	SardanaMainPanel(Splash splash)
	{
		super();
		
		this.splash = splash;
		
		initComponents();
	}
	
	public void progress(int v,String msg)
	{
		if(splash != null)
		{
			splash.setMessage(msg);
			splash.progress(v);
		}
	}
	
	public JMenuBar getMenuBar()
	{
		return SardanaManager.getInstance().getMenuBar();
	}
	
	void initComponents()
	{
		SardanaManager manager = SardanaManager.getInstance();
		setLayout( new BorderLayout() );
		
		// Create log panel as soon as we can so initial log messages are reported 
		progress(4,"Building viewer...");
		logView = new LogPanel( SardanaApplication.getInstance().getLogHandler() );
		progress(5,"Building information tree viewer...");
		treeView = manager.getLeftPanel();
		progress(7,"Building data panels...");
		displayView = manager.getRightPanel();
		progress(9,"Preparing display...");
		
		displayView.setName("Component");
		logView.setName("Log");
		
		JTabbedPane folderPanel = new JTabbedPane(JTabbedPane.TOP);
		
		folderPanel.add(displayView);
		folderPanel.add(logView);
		
		folderPanel.setSelectedIndex(0);
		
		splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, treeView, folderPanel);

		add(splitPane, BorderLayout.CENTER);
		progress(10,"");
	}
}
