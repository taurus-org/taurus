package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;

import javax.swing.JPanel;
import javax.swing.JScrollPane;

import org.jgraph.JGraph;
import org.jgraph.graph.DefaultCellViewFactory;
import org.jgraph.graph.DefaultGraphModel;
import org.jgraph.graph.GraphLayoutCache;
import org.jgraph.graph.GraphModel;

import es.cells.sardana.client.framework.pool.DevicePool;

public class GraphPanel extends JPanel {

	/** Model */
    private DevicePool devicePool;
    
    private JGraph graph;
    private GraphModel model;
    private GraphLayoutCache view;
    
    public GraphPanel()
    {
    	model = new DefaultGraphModel();
    	view = new GraphLayoutCache(model, new DefaultCellViewFactory());
    	graph = new JGraph(model, view);
    	
    	initComponents();
    }

	private void initComponents() 
	{
		setLayout(new BorderLayout());
		
		JScrollPane pane = new JScrollPane(graph);
		add(pane, BorderLayout.CENTER);
	}

	public void setModel(DevicePool pool) 
	{
		this.devicePool = pool;
		// TODO Auto-generated method stub
		
	}
}
