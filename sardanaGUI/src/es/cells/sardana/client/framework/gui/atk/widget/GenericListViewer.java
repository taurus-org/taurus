package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.util.List;

import javax.swing.AbstractListModel;
import javax.swing.DefaultListCellRenderer;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.ListCellRenderer;
import javax.swing.SwingConstants;

import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.SardanaDevice;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.DevStateScalarEvent;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IDevStateScalarListener;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;
import fr.esrf.tangoatk.core.attribute.DevStateScalar;

public abstract class GenericListViewer  extends JPanel
{
	protected DevicePool pool;

	protected JScrollPane              pane;
	protected JList                    list;
	protected DefaultListViewerModel   model;
	
	protected StateListener stateListener;
	protected IStringSpectrumListener listener;
	
	
	public GenericListViewer()
	{
		super();
		initComponents();
	}
	
	public abstract void setModel(DevicePool p);

	protected abstract String getElementIconName(Object o);
	
	protected abstract List<?> getPoolElements();
	
	protected String getToolTip(Object o) 
	{
		return SwingResource.getToolTipForElement(o);
	}
	
	protected DefaultListViewerModel getNewListModel()
	{
		return new DefaultListViewerModel();
	}
	
	protected IStringSpectrumListener getNewListListener()
	{
		return new ElementListListener();
	}
	
	protected ListCellRenderer getNewListCellRenderer()
	{
		return new ElementCellRenderer();
	}
	
	protected StateListener getStateListener()
	{
		return stateListener;
	}
	
	protected IStringSpectrumListener getListListener()
	{
		return listener;
	}
	
	protected void initComponents()
	{
		setLayout(new BorderLayout());
		
		model = getNewListModel();
		
		list = new JList(model);
		list.setLayoutOrientation(JList.HORIZONTAL_WRAP);
		list.setVisibleRowCount(-1);
		list.setCellRenderer(getNewListCellRenderer());
		list.setFixedCellWidth(100);
		stateListener = new StateListener();
		listener = getNewListListener();
		pane = new JScrollPane(list);
		add(pane, BorderLayout.CENTER);

		MouseListener mlistener = new MouseAdapter() 
		{
		    public void mousePressed(MouseEvent e) 
		    {
		        maybeShowPopup(e);
		    }

		    public void mouseReleased(MouseEvent e) 
		    {
		        maybeShowPopup(e);
		    }

		    private void maybeShowPopup(MouseEvent e) 
		    {
		        if (e.isPopupTrigger()) 
		        {
		        	list.setSelectedIndex(list.locationToIndex(e.getPoint()));
		        	Object value = list.getSelectedValue();
		        	JPopupMenu menu = SwingResource.getPopupForElement(value);
	        		menu.show(list, e.getX(), e.getY());
		        }
		    }
		};
		list.addMouseListener(mlistener);
		
	}

	public JList getList()
	{
		return list;
	}
	
	class ElementCellRenderer extends DefaultListCellRenderer
	{
		
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) 
		{
			Component c = super.getListCellRendererComponent(
					list, value,
					index, isSelected, cellHasFocus);
			
			if(c instanceof JLabel)
			{
				JLabel l = (JLabel) c;
				l.setVerticalTextPosition(SwingConstants.BOTTOM);
				l.setHorizontalTextPosition(SwingConstants.CENTER);
				ImageIcon icon = SwingResource.bigIconMap.get(getElementIconName(value));
				//icon.setImageObserver(this);
				l.setIcon(icon);
				l.setForeground(SwingResource.getColorForElement(value));
				l.setToolTipText(getToolTip(value));
			}
			return c;
		}
	}
	
	protected class StateListener implements IDevStateScalarListener 
	{
		public void devStateScalarChange(DevStateScalarEvent e) 
		{
			Device d = ((DevStateScalar)e.getSource()).getDevice();
			model.devStateScalarChange(d);
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent e) {}

	}	

	class ElementListListener implements IStringSpectrumListener 
	{
		public void stringSpectrumChange(StringSpectrumEvent e)
		{
			model.update();
		}

		public void stateChange(AttributeStateEvent e) {}
		public void errorChange(ErrorEvent evt) {}
	}
	
	protected class DefaultListViewerModel extends AbstractListModel
	{
		List<?> elements;
		
		public void devStateScalarChange(Device d)
		{
			int motorGroupsLen = elements.size();
			
			for(int index = 0;index < motorGroupsLen; index++)
			{
				if(elements.get(index) instanceof SardanaDevice)
				{
					SardanaDevice device = (SardanaDevice) elements.get(index);
					if(d.getName().equalsIgnoreCase(device.getDeviceName()))
					{
						fireContentsChanged(this, index, index);
						return;
					}
				}
			}
		}
		
		public void update()
		{
			list.setSelectedIndex(-1);
			
			int oldCount = getSize();
			this.elements = getPoolElements();
			int newCount = getSize();
			
			fireContentsChanged(this, 0, getSize() > 0 ? getSize()-1 : 0);
			
			if(oldCount > newCount)
				fireIntervalRemoved(this, newCount, oldCount-1);
		}
		
		public Object getElementAt(int index) 
		{
			return elements.get(index);
		}
		
		public int getSize() 
		{
			return elements == null ? 0 : elements.size();
		}
	}
}
