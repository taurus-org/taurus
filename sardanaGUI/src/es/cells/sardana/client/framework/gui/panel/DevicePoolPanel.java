/*
 * DevicePoolPanel.java
 *
 * Created on June 7, 2006, 10:18 AM
 */

package es.cells.sardana.client.framework.gui.panel;

import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.atk.widget.CommunicationChannelListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.CommunicationChannelTableViewer;
import es.cells.sardana.client.framework.gui.atk.widget.IORegisterListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.IORegisterTableViewer;
import es.cells.sardana.client.framework.gui.atk.widget.ControllerClassListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.ControllerListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.ControllerTableViewer;
import es.cells.sardana.client.framework.gui.atk.widget.DevicePoolViewer;
import es.cells.sardana.client.framework.gui.atk.widget.ExperimentChannelListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.ExperimentChannelTableViewer;
import es.cells.sardana.client.framework.gui.atk.widget.MeasurementGroupListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.MeasurementGroupTableViewer;
import es.cells.sardana.client.framework.gui.atk.widget.MotorGroupListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.MotorGroupTableViewer;
import es.cells.sardana.client.framework.gui.atk.widget.MotorListViewer;
import es.cells.sardana.client.framework.gui.atk.widget.MotorTableViewerEx;
import es.cells.sardana.client.framework.gui.dialog.AddChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.AddComChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.AddIORegisterDialog;
import es.cells.sardana.client.framework.gui.dialog.AddControllerDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMeasurementGroupChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMeasurementGroupDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMotorDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMotorGroupDialog;
import es.cells.sardana.client.framework.gui.dialog.AddMotorGroupElementDialog;
import es.cells.sardana.client.framework.gui.dialog.RemoveMeasurementGroupChannelDialog;
import es.cells.sardana.client.framework.gui.dialog.RemoveMotorGroupElementDialog;
import es.cells.sardana.client.framework.pool.CommunicationChannel;
import es.cells.sardana.client.framework.pool.IORegister;
import es.cells.sardana.client.framework.pool.Controller;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.MeasurementGroup;
import es.cells.sardana.client.framework.pool.Motor;
import es.cells.sardana.client.framework.pool.MotorGroup;
import es.cells.sardana.client.framework.pool.PseudoMotor;
import es.cells.sardana.client.gui.swing.SwingResource;
import es.cells.tangoatk.utils.IStringFilter;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceData;

/**
 *
 * @author  tcoutinho
 */
public class DevicePoolPanel extends JPanel 
{
	public static final int CTRLS_INDEX = 0;
	public static final int MOTORS_INDEX = 1;
	public static final int MOTOR_GROUPS_INDEX = 2;
	public static final int EXP_CHANNELS_INDEX = 3;
	public static final int MEASUREMENT_GROUPS_INDEX = 4;
	public static final int COM_CHANNELS_INDEX = 5;
	public static final int CTRL_CLASSES_INDEX = 6;
	public static final int IOREGISTERS_INDEX = 7;
    
	
	protected static final String ICON_VIEW = "View as icons";
	protected static final String LIST_VIEW = "View as list";
	
	/** Model */
    private DevicePool devicePool;
    
    /** View */
    
    private DevicePoolViewer poolViewer;
    
    private ControllerTableViewer ctrlTableViewer;
    private ControllerListViewer ctrlListViewer;
    private MotorTableViewerEx motorsTableViewer;
    private MotorListViewer motorsListViewer;
    private MotorGroupTableViewer motorGroupsTableViewer;
    private MotorGroupListViewer motorGroupsListViewer;
    private ExperimentChannelTableViewer channelsTableViewer;
    private ExperimentChannelListViewer channelsListViewer;
    private MeasurementGroupTableViewer measurementGroupsTableViewer;
    private MeasurementGroupListViewer measurementGroupsListViewer;
    private CommunicationChannelTableViewer comChannelsTableViewer;
    private CommunicationChannelListViewer comChannelsListViewer;
    private IORegisterTableViewer ioRegistersTableViewer;
    private IORegisterListViewer ioRegistersListViewer;

    private ControllerClassListViewer ctrlClassListViewer;
    
    private ButtonsPanel ctrlButtonPanel;
    private ButtonsPanel motorsButtonPanel;
    private ButtonsPanel motorGroupsButtonPanel;
    private ButtonsPanel channelsButtonPanel;
    private ButtonsPanel measurementGroupsButtonPanel;
    private ButtonsPanel comChannelsButtonPanel;
    private ButtonsPanel ioRegistersButtonPanel;
    private ButtonsPanel ctrlClassButtonPanel;
    
	private JButton addCtrlButton;
	private JButton removeCtrlButton;
	private JButton cloneCtrlButton;
	private JButton initCtrlButton;
	private JButton reloadCtrlLibButton;

	private JButton addMotorButton;
	private JButton removeMotorButton;
	private JButton cloneMotorButton;
	private JButton initMotorButton;
	
	private JButton addMotorGroupButton;
	private JButton removeMotorGroupButton;
	private JButton initMotorGroupButton;
	private JButton addMotorGroupElementButton;
	private JButton removeMotorGroupElementButton;
	
	private JButton addChannelButton;
	private JButton removeChannelButton;
	private JButton cloneChannelButton;
	private JButton initChannelButton;

	private JButton addMeasurementGroupButton;
	private JButton removeMeasurementGroupButton;
	private JButton initMeasurementGroupButton;
	private JButton addMeasurementGroupChannelButton;
	private JButton removeMeasurementGroupChannelButton;

	private JButton addComChannelButton;
	private JButton removeComChannelButton;
	private JButton cloneComChannelButton;
	private JButton initComChannelButton;

	private JButton addIORegisterButton;
	private JButton removeIORegisterButton;
	private JButton cloneIORegisterButton;
	private JButton initIORegisterButton;
	
	private JButton refreshCtrlClassListButton;
	
	private JComboBox ctrlViewsCombo;
	private JComboBox motorViewsCombo;
	private JComboBox motorGroupViewsCombo;
	private JComboBox channelViewsCombo;
	private JComboBox measurementGroupViewsCombo;
	private JComboBox comChannelViewsCombo;
	private JComboBox ioRegisterViewsCombo;
    	

    private javax.swing.JTabbedPane elementsPane;
    
	protected class StartsWidthStringFilter implements IStringFilter
	{
		String prefix;
		
		public StartsWidthStringFilter(String prefix)
		{
			this.prefix = prefix;
		}
		
		public boolean isValid(String str) 
		{
			return !str.startsWith(prefix);
		}
	}
	
    /** Creates new form DevicePoolPanel */
    public DevicePoolPanel() 
    {
        initComponents();
        initATKComponents();
    }
    
    public DevicePoolPanel(DevicePool devicePool) 
    {
        this();
        setDevicePool(devicePool, CTRLS_INDEX);
    }

    public DevicePool getDevicePool()
    {
        return devicePool;
    }

    public void setDevicePool(DevicePool devicePool, int index)
    {
        this.devicePool = devicePool;
        
        if(devicePool != null)
        {
	    //    if(devicePool.isAvailable())
	    //    {	
	        	poolViewer.setModel(devicePool);
	    		ctrlTableViewer.setModel(devicePool);
	    		ctrlListViewer.setModel(devicePool);
	    		motorsTableViewer.setModel(devicePool);
	    		motorsListViewer.setModel(devicePool);
	    		motorGroupsTableViewer.setModel(devicePool);
	    		motorGroupsListViewer.setModel(devicePool);
	    		channelsTableViewer.setModel(devicePool);
	    		channelsListViewer.setModel(devicePool);
	    		comChannelsTableViewer.setModel(devicePool);
	    		comChannelsListViewer.setModel(devicePool);
	    		ioRegistersTableViewer.setModel(devicePool);
	    		ioRegistersListViewer.setModel(devicePool);
	    		measurementGroupsTableViewer.setModel(devicePool);
	    		measurementGroupsListViewer.setModel(devicePool);
	    		ctrlClassListViewer.setModel(devicePool);

	    		
	    		elementsPane.setSelectedIndex(index);
	    //    }
        }
        else
        {
        	clearModel();
        }
    }
    
    public void clearModel()
    {
    	poolViewer.setModel(null);
    	ctrlTableViewer.setModel(null);
    	ctrlListViewer.setModel(null);
    	motorsTableViewer.setModel(null);
    	motorsListViewer.setModel(null);
    	motorGroupsTableViewer.setModel(null);
    	motorGroupsListViewer.setModel(null);
    	channelsTableViewer.setModel(null);
    	channelsListViewer.setModel(null);
    	comChannelsTableViewer.setModel(null);
    	comChannelsListViewer.setModel(null);
    	ioRegistersTableViewer.setModel(null);
    	ioRegistersListViewer.setModel(null);
    	measurementGroupsTableViewer.setModel(null);
    	measurementGroupsListViewer.setModel(null);
    	ctrlClassListViewer.setModel(null);
    }
    
    private JPanel createStateStatusPanel()
    {
    	JPanel stateAndStatusPanel = new JPanel( new BorderLayout() );
        
    	poolViewer = new DevicePoolViewer();
    	
    	stateAndStatusPanel.add(poolViewer, BorderLayout.CENTER);
        return stateAndStatusPanel;
    }
    
    private void initATKComponents()
    {
    	JPanel stateAndStatusPanel = createStateStatusPanel();

    	ctrlTableViewer = new ControllerTableViewer();
    	ctrlTableViewer.setPreferredSize(new Dimension(375,200));
    	ctrlTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				cloneCtrlButton.setEnabled(enable);
				removeCtrlButton.setEnabled(enable);
				initCtrlButton.setEnabled(enable);
				reloadCtrlLibButton.setEnabled(enable);
			}
    	});

    	ctrlListViewer = new ControllerListViewer();
    	ctrlListViewer.setPreferredSize(new Dimension(375,200));
    	ctrlListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				cloneCtrlButton.setEnabled(enable);
				removeCtrlButton.setEnabled(enable);
				initCtrlButton.setEnabled(enable);
				reloadCtrlLibButton.setEnabled(enable);
			}
    	});

        motorsTableViewer = new MotorTableViewerEx();
        motorsTableViewer.setPreferredSize(new Dimension(375,200));
    	motorsTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() 
    	{
			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				cloneMotorButton.setEnabled(enable);
				removeMotorButton.setEnabled(enable);
				initMotorButton.setEnabled(enable);
				
				enable &= motorsTableViewer.getSelectedMotor() instanceof PseudoMotor;
			}
    	});

        motorsListViewer = new MotorListViewer();
        motorsListViewer.setPreferredSize(new Dimension(375,200));
        motorsListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() 
    	{
			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				cloneMotorButton.setEnabled(enable);
				removeMotorButton.setEnabled(enable);
				initMotorButton.setEnabled(enable);
				
				enable &= motorsListViewer.getSelectedMotor() instanceof PseudoMotor;
			}
    	});
    	
    	motorGroupsTableViewer = new MotorGroupTableViewer();
    	motorGroupsTableViewer.setPreferredSize(new Dimension(375,200));
    	motorGroupsTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeMotorGroupButton.setEnabled(enable);
				initMotorGroupButton.setEnabled(enable);
				addMotorGroupElementButton.setEnabled(enable);
				removeMotorGroupElementButton.setEnabled(enable);
			}
    	});

    	motorGroupsListViewer = new MotorGroupListViewer();
    	motorGroupsListViewer.setPreferredSize(new Dimension(375,200));
    	motorGroupsListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeMotorGroupButton.setEnabled(enable);
				initMotorGroupButton.setEnabled(enable);
				addMotorGroupElementButton.setEnabled(enable);
				removeMotorGroupElementButton.setEnabled(enable);
			}
    	});    	
    	
    	channelsTableViewer = new ExperimentChannelTableViewer();
    	channelsTableViewer.setPreferredSize(new Dimension(375,200));
    	channelsTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeChannelButton.setEnabled(enable);
				initChannelButton.setEnabled(enable);
				cloneChannelButton.setEnabled(enable);
			}
    	});

    	channelsListViewer = new ExperimentChannelListViewer();
    	channelsListViewer.setPreferredSize(new Dimension(375,200));
    	channelsListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeChannelButton.setEnabled(enable);
				initChannelButton.setEnabled(enable);
				cloneChannelButton.setEnabled(enable);
			}
    	});
    	
    	measurementGroupsTableViewer = new MeasurementGroupTableViewer();
    	measurementGroupsTableViewer.setPreferredSize(new Dimension(375,200));
    	measurementGroupsTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeMeasurementGroupButton.setEnabled(enable);
				initMeasurementGroupButton.setEnabled(enable);
				addMeasurementGroupChannelButton.setEnabled(enable);
				removeMeasurementGroupChannelButton.setEnabled(enable);
			}
    	});

    	measurementGroupsListViewer = new MeasurementGroupListViewer();
    	measurementGroupsListViewer.setPreferredSize(new Dimension(375,200));
    	measurementGroupsListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeMeasurementGroupButton.setEnabled(enable);
				initMeasurementGroupButton.setEnabled(enable);
				addMeasurementGroupChannelButton.setEnabled(enable);
				removeMeasurementGroupChannelButton.setEnabled(enable);
			}
    	});
    	
    	comChannelsTableViewer = new CommunicationChannelTableViewer();
    	comChannelsTableViewer.setPreferredSize(new Dimension(375,200));
    	comChannelsTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeComChannelButton.setEnabled(enable);
				initComChannelButton.setEnabled(enable);
				cloneComChannelButton.setEnabled(enable);
			}
    	});

    	comChannelsListViewer = new CommunicationChannelListViewer();
    	comChannelsListViewer.setPreferredSize(new Dimension(375,200));
    	comChannelsListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeComChannelButton.setEnabled(enable);
				initComChannelButton.setEnabled(enable);
				cloneComChannelButton.setEnabled(enable);
			}
    	});
    	ioRegistersTableViewer = new IORegisterTableViewer();
    	ioRegistersTableViewer.setPreferredSize(new Dimension(375,200));
    	ioRegistersTableViewer.getTable().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeIORegisterButton.setEnabled(enable);
				initIORegisterButton.setEnabled(enable);
				cloneIORegisterButton.setEnabled(enable);
			}
    	});
    	ioRegistersListViewer = new IORegisterListViewer();
    	ioRegistersListViewer.setPreferredSize(new Dimension(375,200));
    	ioRegistersListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
				removeIORegisterButton.setEnabled(enable);
				initIORegisterButton.setEnabled(enable);
				cloneIORegisterButton.setEnabled(enable);
			}
    	});	   	
    	ctrlClassListViewer = new ControllerClassListViewer();
    	ctrlClassListViewer.setPreferredSize(new Dimension(375,200));
    	ctrlClassListViewer.getList().getSelectionModel().addListSelectionListener(new ListSelectionListener() {

			public void valueChanged(ListSelectionEvent e)
			{
				boolean enable = e.getFirstIndex() >=0 && e.getFirstIndex() <= e.getLastIndex();
			}
    	});    	
    	
    	add(stateAndStatusPanel, BorderLayout.NORTH);  
        ctrlButtonPanel = new ButtonsPanel();
        ctrlButtonPanel.setMaximumSize(new Dimension(1024,24));
        motorsButtonPanel = new ButtonsPanel();
        motorsButtonPanel.setMaximumSize(new Dimension(1024,24));
        motorGroupsButtonPanel = new ButtonsPanel();
        motorGroupsButtonPanel.setMaximumSize(new Dimension(1024,24));
        channelsButtonPanel = new ButtonsPanel();
        channelsButtonPanel.setMaximumSize(new Dimension(1024,24));
        measurementGroupsButtonPanel = new ButtonsPanel();
        measurementGroupsButtonPanel.setMaximumSize(new Dimension(1024,24));
        ctrlClassButtonPanel = new ButtonsPanel();
        ctrlClassButtonPanel.setMaximumSize(new Dimension(1024,24));
        comChannelsButtonPanel = new ButtonsPanel();
        comChannelsButtonPanel.setMaximumSize(new Dimension(1024,24));
        ioRegistersButtonPanel = new ButtonsPanel();
        ioRegistersButtonPanel.setMaximumSize(new Dimension(1024,24));        

        addCtrlButton = new JButton();
        removeCtrlButton = new JButton();
        cloneCtrlButton = new JButton();
        initCtrlButton = new JButton();
        reloadCtrlLibButton = new JButton();
        ctrlViewsCombo = new JComboBox();
        
        addMotorButton = new JButton();
        removeMotorButton = new JButton();
        cloneMotorButton = new JButton();
        initMotorButton = new JButton();
        motorViewsCombo = new JComboBox();
        
        addMotorGroupButton = new JButton();
        removeMotorGroupButton = new JButton();
        initMotorGroupButton = new JButton();
        addMotorGroupElementButton = new JButton();
        removeMotorGroupElementButton = new JButton();
        motorGroupViewsCombo = new JComboBox();
        
        addChannelButton = new JButton();
        removeChannelButton = new JButton();
        cloneChannelButton = new JButton();
        initChannelButton = new JButton();
        channelViewsCombo = new JComboBox();

        addMeasurementGroupButton = new JButton();
        removeMeasurementGroupButton = new JButton();
        initMeasurementGroupButton = new JButton();
        addMeasurementGroupChannelButton = new JButton();
        removeMeasurementGroupChannelButton = new JButton();
        measurementGroupViewsCombo = new JComboBox();

        addComChannelButton = new JButton();
        removeComChannelButton = new JButton();
        cloneComChannelButton = new JButton();
        initComChannelButton = new JButton();
        comChannelViewsCombo = new JComboBox();
		
		addIORegisterButton = new JButton();
        removeIORegisterButton = new JButton();
        cloneIORegisterButton = new JButton();
        initIORegisterButton = new JButton();
        ioRegisterViewsCombo = new JComboBox();

        refreshCtrlClassListButton = new JButton();
        
        addCtrlButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addCtrlButton.setToolTipText("Add new controller");
        cloneCtrlButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_CLONE));
        cloneCtrlButton.setToolTipText("Clone controller");
        removeCtrlButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeCtrlButton.setToolTipText("Delete controller");
        initCtrlButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initCtrlButton.setToolTipText("Reinitialize the selected controller(s)");
        reloadCtrlLibButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_RELOAD));
        reloadCtrlLibButton.setToolTipText("Reload controller library");
        
        addMotorButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addMotorButton.setToolTipText("Add new motor");
        cloneMotorButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_CLONE));
        cloneMotorButton.setToolTipText("Clone motor");
        removeMotorButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeMotorButton.setToolTipText("Delete motor");
        initMotorButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initMotorButton.setToolTipText("Reinitialize the selected motor(s)");

        addMotorGroupButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addMotorGroupButton.setToolTipText("Add new motor group");
        removeMotorGroupButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeMotorGroupButton.setToolTipText("Delete motor group");
        initMotorGroupButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initMotorGroupButton.setToolTipText("Reinitialize the selected motor group(s)");
        addMotorGroupElementButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_ADD));
        addMotorGroupElementButton.setToolTipText("Add a new element to the selected motor group");
        removeMotorGroupElementButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_REMOVE));
        removeMotorGroupElementButton.setToolTipText("Remove an element from the selected motor group");

        addChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addChannelButton.setToolTipText("Add new experiment channel");
        cloneChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_CLONE));
        cloneChannelButton.setToolTipText("Clone experiment channel");
        removeChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeChannelButton.setToolTipText("Delete experiment channel");
        initChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initChannelButton.setToolTipText("Reinitialize on the selected channel(s)");
        
        addMeasurementGroupButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addMeasurementGroupButton.setToolTipText("Add new measurement group");
        removeMeasurementGroupButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeMeasurementGroupButton.setToolTipText("Delete measurement group");
        initMeasurementGroupButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initMeasurementGroupButton.setToolTipText("Reinitialize on the selected measurement group(s)");
        addMeasurementGroupChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_ADD));
        addMeasurementGroupChannelButton.setToolTipText("Add a new channel to the selected measurement group");
        removeMeasurementGroupChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_REMOVE));
        removeMeasurementGroupChannelButton.setToolTipText("Remove a channel from the selected measurement group");      

        addComChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addComChannelButton.setToolTipText("Add new communication channel");
        cloneComChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_CLONE));
        cloneComChannelButton.setToolTipText("Clone communication channel");
        removeComChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeComChannelButton.setToolTipText("Delete communication channel");
        initComChannelButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initComChannelButton.setToolTipText("Reinitialize on the selected communication channel(s)");
        addIORegisterButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_NEW));
        addIORegisterButton.setToolTipText("Add new input/output register");
        cloneIORegisterButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_CLONE));
        cloneIORegisterButton.setToolTipText("Clone input/output register");
        removeIORegisterButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_DELETE));
        removeIORegisterButton.setToolTipText("Delete input/output register");
        initIORegisterButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_INIT));
        initIORegisterButton.setToolTipText("Reinitialize on the selected input/output register(s)");

        refreshCtrlClassListButton.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_REFRESH));
        refreshCtrlClassListButton.setToolTipText("Refresh list of Controller classes");

        ctrlViewsCombo.setRenderer(new IconListComboRenderer());
        ctrlViewsCombo.addItem(ICON_VIEW);
        ctrlViewsCombo.addItem(LIST_VIEW);
        ctrlViewsCombo.setSelectedIndex(0);
        
        motorViewsCombo.setRenderer(new IconListComboRenderer());
        motorViewsCombo.addItem(ICON_VIEW);
        motorViewsCombo.addItem(LIST_VIEW);
        motorViewsCombo.setSelectedIndex(0);
        
        motorGroupViewsCombo.setRenderer(new IconListComboRenderer());
        motorGroupViewsCombo.addItem(ICON_VIEW);
        motorGroupViewsCombo.addItem(LIST_VIEW);
        motorGroupViewsCombo.setSelectedIndex(0);
        
        channelViewsCombo.setRenderer(new IconListComboRenderer());
        channelViewsCombo.addItem(ICON_VIEW);
        channelViewsCombo.addItem(LIST_VIEW);
        channelViewsCombo.setSelectedIndex(0);
        
        measurementGroupViewsCombo.setRenderer(new IconListComboRenderer());
        measurementGroupViewsCombo.addItem(ICON_VIEW);
        measurementGroupViewsCombo.addItem(LIST_VIEW);
        measurementGroupViewsCombo.setSelectedIndex(0);
        comChannelViewsCombo.setRenderer(new IconListComboRenderer());
        comChannelViewsCombo.addItem(ICON_VIEW);
        comChannelViewsCombo.addItem(LIST_VIEW);
        comChannelViewsCombo.setSelectedIndex(0);

		ioRegisterViewsCombo.setRenderer(new IconListComboRenderer());
        ioRegisterViewsCombo.addItem(ICON_VIEW);
        ioRegisterViewsCombo.addItem(LIST_VIEW);
        ioRegisterViewsCombo.setSelectedIndex(0);

        removeCtrlButton.setEnabled(false);
        cloneCtrlButton.setEnabled(false);
        initCtrlButton.setEnabled(false);
        reloadCtrlLibButton.setEnabled(false);

        removeMotorButton.setEnabled(false);
        cloneMotorButton.setEnabled(false);
        initMotorButton.setEnabled(false);
        
        removeMotorGroupButton.setEnabled(false);
        initMotorGroupButton.setEnabled(false);
        addMotorGroupElementButton.setEnabled(false);
        removeMotorGroupElementButton.setEnabled(false);
        
        removeChannelButton.setEnabled(false);
        cloneChannelButton.setEnabled(false);
        initChannelButton.setEnabled(false);
        
        removeMeasurementGroupButton.setEnabled(false);
        initMeasurementGroupButton.setEnabled(false);
        addMeasurementGroupChannelButton.setEnabled(false);
        removeMeasurementGroupChannelButton.setEnabled(false);

        removeComChannelButton.setEnabled(false);
        cloneComChannelButton.setEnabled(false);
        initComChannelButton.setEnabled(false);

        removeIORegisterButton.setEnabled(false);
        cloneIORegisterButton.setEnabled(false);
        initIORegisterButton.setEnabled(false);
      
        ctrlButtonPanel.addLeft(addCtrlButton);
        ctrlButtonPanel.addLeft(cloneCtrlButton);
        ctrlButtonPanel.addLeft(removeCtrlButton);
        ctrlButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        ctrlButtonPanel.addLeft(initCtrlButton);
        ctrlButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        ctrlButtonPanel.addLeft(reloadCtrlLibButton);
        ctrlButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        ctrlButtonPanel.addRight(ctrlViewsCombo);
        
        motorsButtonPanel.addLeft(addMotorButton);
        motorsButtonPanel.addLeft(cloneMotorButton);
        motorsButtonPanel.addLeft(removeMotorButton);
        motorsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        motorsButtonPanel.addLeft(initMotorButton);
        motorsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        motorsButtonPanel.addRight(motorViewsCombo);
        
        motorGroupsButtonPanel.addLeft(addMotorGroupButton);
        motorGroupsButtonPanel.addLeft(removeMotorGroupButton);
        motorGroupsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        motorGroupsButtonPanel.addLeft(addMotorGroupElementButton);
        motorGroupsButtonPanel.addLeft(removeMotorGroupElementButton);
        motorGroupsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        motorGroupsButtonPanel.addLeft(initMotorGroupButton);
        motorGroupsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        motorGroupsButtonPanel.addRight(motorGroupViewsCombo);
        
        channelsButtonPanel.addLeft(addChannelButton);
        channelsButtonPanel.addLeft(cloneChannelButton);
        channelsButtonPanel.addLeft(removeChannelButton);
        channelsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        channelsButtonPanel.addLeft(initChannelButton);
        channelsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        channelsButtonPanel.addRight(channelViewsCombo);

        measurementGroupsButtonPanel.addLeft(addMeasurementGroupButton);
        measurementGroupsButtonPanel.addLeft(removeMeasurementGroupButton);
        measurementGroupsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        measurementGroupsButtonPanel.addLeft(addMeasurementGroupChannelButton);
        measurementGroupsButtonPanel.addLeft(removeMeasurementGroupChannelButton);
        measurementGroupsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        measurementGroupsButtonPanel.addLeft(initMeasurementGroupButton);
        measurementGroupsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        measurementGroupsButtonPanel.addRight(measurementGroupViewsCombo);

        comChannelsButtonPanel.addLeft(addComChannelButton);
        comChannelsButtonPanel.addLeft(cloneComChannelButton);
        comChannelsButtonPanel.addLeft(removeComChannelButton);
        comChannelsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        comChannelsButtonPanel.addLeft(initComChannelButton);
        comChannelsButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        comChannelsButtonPanel.addRight(comChannelViewsCombo);
		
		ioRegistersButtonPanel.addLeft(addIORegisterButton);
        ioRegistersButtonPanel.addLeft(cloneIORegisterButton);
        ioRegistersButtonPanel.addLeft(removeIORegisterButton);
        ioRegistersButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        ioRegistersButtonPanel.addLeft(initIORegisterButton);
        ioRegistersButtonPanel.addLeft(Box.createRigidArea(new Dimension(10,10)));
        ioRegistersButtonPanel.addRight(ioRegisterViewsCombo);
        ctrlClassButtonPanel.addLeft(refreshCtrlClassListButton);
        
        JPanel ctrlPanel = new JPanel();
        ctrlPanel.setLayout(new BoxLayout(ctrlPanel,BoxLayout.Y_AXIS));
        ctrlPanel.setName("Controllers");
        final JPanel ctrlViewPanel = new JPanel(new CardLayout());
        
        JPanel motorPanel = new JPanel();
        motorPanel.setLayout(new BoxLayout(motorPanel,BoxLayout.Y_AXIS));
        motorPanel.setName("Motors");
        final JPanel motorViewPanel = new JPanel(new CardLayout());
        
        JPanel motorGroupPanel = new JPanel();
        motorGroupPanel.setLayout(new BoxLayout(motorGroupPanel,BoxLayout.Y_AXIS));
        motorGroupPanel.setName("Motor Groups");
        final JPanel motorGroupViewPanel = new JPanel(new CardLayout());
        
        JPanel expChannelPanel = new JPanel();
        expChannelPanel.setLayout(new BoxLayout(expChannelPanel,BoxLayout.Y_AXIS));
        expChannelPanel.setName("Experiment Channels");
        final JPanel channelViewPanel = new JPanel(new CardLayout());
        
        JPanel measurementGroupPanel = new JPanel();
        measurementGroupPanel.setLayout(new BoxLayout(measurementGroupPanel,BoxLayout.Y_AXIS));
        measurementGroupPanel.setName("Measurement Groups");
        final JPanel measurementGroupViewPanel = new JPanel(new CardLayout());

        JPanel comChannelPanel = new JPanel();
        comChannelPanel.setLayout(new BoxLayout(comChannelPanel,BoxLayout.Y_AXIS));
        comChannelPanel.setName("Communication Channels");
        final JPanel comChannelViewPanel = new JPanel(new CardLayout());
        JPanel ioRegisterPanel = new JPanel();
        ioRegisterPanel.setLayout(new BoxLayout(ioRegisterPanel,BoxLayout.Y_AXIS));
        ioRegisterPanel.setName("Input/Output Registers");
        final JPanel ioRegisterViewPanel = new JPanel(new CardLayout());
        
        JPanel ctrlClassPanel = new JPanel();
        ctrlClassPanel.setLayout(new BoxLayout(ctrlClassPanel,BoxLayout.Y_AXIS));
        ctrlClassPanel.setName("Controller Classes");
        final JPanel ctrlClassViewPanel = new JPanel(new CardLayout());
        
        ctrlViewPanel.add(ctrlListViewer, ICON_VIEW);
        ctrlViewPanel.add(ctrlTableViewer, LIST_VIEW);
        ctrlPanel.add(ctrlButtonPanel);
        ctrlPanel.add(ctrlViewPanel);
        
        motorViewPanel.add(motorsListViewer, ICON_VIEW);
        motorViewPanel.add(motorsTableViewer, LIST_VIEW);
        motorPanel.add(motorsButtonPanel);
        motorPanel.add(motorViewPanel);

        motorGroupViewPanel.add(motorGroupsListViewer, ICON_VIEW);
        motorGroupViewPanel.add(motorGroupsTableViewer, LIST_VIEW);
        motorGroupPanel.add(motorGroupsButtonPanel);
        motorGroupPanel.add(motorGroupViewPanel);

        channelViewPanel.add(channelsListViewer, ICON_VIEW);
        channelViewPanel.add(channelsTableViewer, LIST_VIEW);
        expChannelPanel.add(channelsButtonPanel);
        expChannelPanel.add(channelViewPanel);

        measurementGroupViewPanel.add(measurementGroupsListViewer, ICON_VIEW);
        measurementGroupViewPanel.add(measurementGroupsTableViewer, LIST_VIEW);
        measurementGroupPanel.add(measurementGroupsButtonPanel);
        measurementGroupPanel.add(measurementGroupViewPanel);

        comChannelViewPanel.add(comChannelsListViewer, ICON_VIEW);
        comChannelViewPanel.add(comChannelsTableViewer, LIST_VIEW);
        comChannelPanel.add(comChannelsButtonPanel);
        comChannelPanel.add(comChannelViewPanel);

   
        ioRegisterViewPanel.add(ioRegistersListViewer, ICON_VIEW);
		ioRegisterViewPanel.add(ioRegistersTableViewer, LIST_VIEW);
        ioRegisterPanel.add(ioRegistersButtonPanel);
        ioRegisterPanel.add(ioRegisterViewPanel);
        
        ctrlClassViewPanel.add(ctrlClassListViewer, ICON_VIEW);
		//	ctrlClassViewPanel.add(ctrlClassTableViewer, LIST_VIEW);
        ctrlClassPanel.add(ctrlClassButtonPanel);
        ctrlClassPanel.add(ctrlClassViewPanel);        

        elementsPane.add(ctrlPanel, CTRLS_INDEX);
        elementsPane.add(motorPanel, MOTORS_INDEX);
        elementsPane.add(motorGroupPanel, MOTOR_GROUPS_INDEX);
        elementsPane.add(expChannelPanel, EXP_CHANNELS_INDEX);
        elementsPane.add(measurementGroupPanel, MEASUREMENT_GROUPS_INDEX);
        elementsPane.add(comChannelPanel, COM_CHANNELS_INDEX);
        elementsPane.add(ctrlClassPanel, CTRL_CLASSES_INDEX);
        elementsPane.add(ioRegisterPanel, IOREGISTERS_INDEX);
        addCtrlButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addCtrlButtonPressed(e);
			}
        });
        
        removeCtrlButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeCtrlButtonPressed(e);
			}
        });       
        
        cloneCtrlButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				cloneCtrlButtonPressed(e);
			}
        });
        
        initCtrlButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initCtrlButtonPressed(e);
			}
    	});
        
        
        reloadCtrlLibButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				reloadCtrlLibButtonPressed(e);
			}
    	});
        
        ctrlViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(ctrlViewPanel.getLayout());
				cl.show(ctrlViewPanel, (String)e.getItem());
				ctrlListViewer.getList().setSelectedIndex(-1);
				ctrlTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });
        
        addComChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addComChannelButtonPressed(e);
			}
        });
        
        removeComChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeComChannelButtonPressed(e);
			}
        });       
        
        cloneComChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				cloneComChannelButtonPressed(e);
			}
        });
        
        initComChannelButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initComChannel(e);
			}
    	});         
        
        comChannelViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(channelViewPanel.getLayout());
				cl.show(channelViewPanel, (String)e.getItem());
				comChannelsListViewer.getList().setSelectedIndex(-1);
				comChannelsTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });        
         
        addIORegisterButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addIORegisterButtonPressed(e);
			}
        });
        
        removeIORegisterButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeIORegisterButtonPressed(e);
			}
        });       
        
        cloneIORegisterButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				cloneIORegisterButtonPressed(e);
			}
        });
        
        initIORegisterButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initIORegister(e);
			}
    	});         
        
        ioRegisterViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(ioRegisterViewPanel.getLayout());
				cl.show(ioRegisterViewPanel, (String)e.getItem());
				ioRegistersListViewer.getList().setSelectedIndex(-1);
				ioRegistersTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });        
               
        addMotorButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addMotorButtonPressed(e);
			}
        });
        
        removeMotorButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeMotorButtonPressed(e);
			}
        });       
        
        cloneMotorButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				cloneMotorButtonPressed(e);
			}
        });
        
        initMotorButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initMotor(e);
			}
    	});        
        
        motorViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(motorViewPanel.getLayout());
				cl.show(motorViewPanel, (String)e.getItem());
				motorsListViewer.getList().setSelectedIndex(-1);
				motorsTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
				
			}
        });
        
        addMotorGroupButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addMotorGroupButtonPressed(e);
			}
        });
        
        removeMotorGroupButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeMotorGroupButtonPressed(e);
			}
        });
        
        initMotorGroupButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initMotorGroup(e);
			}
    	});         
        
        addMotorGroupElementButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addMotorGroupElementButtonPressed(e);
			}
        });

        removeMotorGroupElementButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeMotorGroupElementButtonPressed(e);
			}
        });        
        
        motorGroupViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(motorGroupViewPanel.getLayout());
				cl.show(motorGroupViewPanel, (String)e.getItem());
				motorGroupsListViewer.getList().setSelectedIndex(-1);
				motorGroupsTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });
        
        addChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addChannelButtonPressed(e);
			}
        });
        
        removeChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeChannelButtonPressed(e);
			}
        });       
        
        cloneChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				cloneChannelButtonPressed(e);
			}
        });
        
        initChannelButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initChannel(e);
			}
    	});         
        
        comChannelViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(comChannelViewPanel.getLayout());
				cl.show(comChannelViewPanel, (String)e.getItem());
				comChannelsListViewer.getList().setSelectedIndex(-1);
				comChannelsTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });
               
        ioRegisterViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(ioRegisterViewPanel.getLayout());
				cl.show(ioRegisterViewPanel, (String)e.getItem());
				ioRegistersListViewer.getList().setSelectedIndex(-1);
				ioRegistersTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });

        channelViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(channelViewPanel.getLayout());
				cl.show(channelViewPanel, (String)e.getItem());
				channelsListViewer.getList().setSelectedIndex(-1);
				channelsTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
			}
        });
        
        addMeasurementGroupButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addMeasurementGroupButtonPressed(e);
			}
        });
        
        removeMeasurementGroupButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeMeasurementGroupButtonPressed(e);
			}
        });
        
        initMeasurementGroupButton.addActionListener(new ActionListener()
        {
			public void actionPerformed(ActionEvent e) 
			{
				initMeasurementGroup(e);
			}
    	});         
        
        addMeasurementGroupChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				addMeasurementGroupChannelButtonPressed(e);
			}
        });

        removeMeasurementGroupChannelButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				removeMeasurementGroupChannelButtonPressed(e);
			}
        });
        
        measurementGroupViewsCombo.addItemListener(new ItemListener()
        {
			public void itemStateChanged(ItemEvent e) 
			{
				CardLayout cl = (CardLayout)(measurementGroupViewPanel.getLayout());
				cl.show(measurementGroupViewPanel, (String)e.getItem());
				measurementGroupsListViewer.getList().setSelectedIndex(-1);
				measurementGroupsTableViewer.getTable().getSelectionModel().setSelectionInterval(-1, -1);
				
			}
        });
        
        refreshCtrlClassListButton.addActionListener(new ActionListener() 
        {
			public void actionPerformed(ActionEvent e)
			{
				refreshCtrlClassListButtonPressed(e);
			}
        });
        
    }

    protected void refreshCtrlClassListButtonPressed(ActionEvent e) 
    {
    	if(devicePool == null)
    		return;
    	
		devicePool.setControllerClasses(DevicePoolUtils.getInstance().askForDevicePoolControllerClasses(devicePool));
	}

	protected void initMotor(ActionEvent e)
    {
		List<Motor> motors = motorViewsCombo.getSelectedItem() == ICON_VIEW ?
				motorsListViewer.getSelectedMotors() :
				motorsTableViewer.getSelectedMotors();
				
		if(motors.size() < 1)
			return;
		
		int res = JOptionPane.showConfirmDialog(null, 
				"This action will perform an Init on all selected motors.\nAre you sure?", 
				"Reinitialize motor(s)", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
		
		if(res == JOptionPane.YES_OPTION)
		{
			ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
			for(Motor motor : motors)
			{
				try 
				{
					motor.Init();
				} 
				catch (DevFailed e1) 
				{
					failed.add(e1);
				}
			}
			if(failed.size() > 0)
			{
				StringBuffer buff = new StringBuffer();
				for(DevFailed e1 : failed)
				{
					buff.append(e1.getMessage() + "\n");
				}
				
				JOptionPane.showMessageDialog(null,
						buff.toString(),"Failed to reinitialize motor(s)",JOptionPane.ERROR_MESSAGE);
			}
		}
    }
    
    protected void initMotorGroup(ActionEvent e)
    {
		List<MotorGroup> motorGroups = motorGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
				motorGroupsListViewer.getSelectedMotorGroups() :
				motorGroupsTableViewer.getSelectedMotorGroups();
				
		if(motorGroups.size() < 1)
			return;
		
		int res = JOptionPane.showConfirmDialog(null, 
				"This action will perform an Init on all selected motor groups.\nAre you sure?", 
				"Reinitialize motor group(s)", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
		
		if(res == JOptionPane.YES_OPTION)
		{
			ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
			for(MotorGroup motorGroup : motorGroups)
			{
				try 
				{
					motorGroup.Init();
				} 
				catch (DevFailed e1) 
				{
					failed.add(e1);
				}
			}
			if(failed.size() > 0)
			{
				StringBuffer buff = new StringBuffer();
				for(DevFailed e1 : failed)
				{
					buff.append(e1.getMessage() + "\n");
				}
				
				JOptionPane.showMessageDialog(null,
						buff.toString(),"Failed to reinitialize motor group(s)",JOptionPane.ERROR_MESSAGE);
			}
		}    	
    }

    protected void initChannel(ActionEvent e)
    {
		List<ExperimentChannel> channels = channelViewsCombo.getSelectedItem() == ICON_VIEW ?
				channelsListViewer.getSelectedExperimentChannels() :
				channelsTableViewer.getSelectedExperimentChannels();
				
		if(channels.size() < 1)
			return;
		
		int res = JOptionPane.showConfirmDialog(null, 
				"This action will perform an Init on all selected experiment channels.\nAre you sure?", 
				"Reinitialize experiment channel(s)", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
		
		if(res == JOptionPane.YES_OPTION)
		{
			ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
			for(ExperimentChannel channel : channels)
			{
				try 
				{
					channel.Init();
				} 
				catch (DevFailed e1) 
				{
					failed.add(e1);
				}
			}
			if(failed.size() > 0)
			{
				StringBuffer buff = new StringBuffer();
				for(DevFailed e1 : failed)
				{
					buff.append(e1.getMessage() + "\n");
				}
				
				JOptionPane.showMessageDialog(null,
						buff.toString(),"Failed to reinitialize experiment channel(s)",JOptionPane.ERROR_MESSAGE);
			}
		}    	
    }

    protected void initComChannel(ActionEvent e)
    {
		List<CommunicationChannel> channels = comChannelViewsCombo.getSelectedItem() == ICON_VIEW ?
				comChannelsListViewer.getSelectedCommunicationChannels() :
				comChannelsTableViewer.getSelectedCommunicationChannels();
				
		if(channels.size() < 1)
			return;
		
		int res = JOptionPane.showConfirmDialog(null, 
				"This action will perform an Init on all selected communication channels.\nAre you sure?", 
				"Reinitialize communication channel(s)", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
		
		if(res == JOptionPane.YES_OPTION)
		{
			ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
			for(CommunicationChannel channel : channels)
			{
				try 
				{
					channel.Init();
				} 
				catch (DevFailed e1) 
				{
					failed.add(e1);
				}
			}
			if(failed.size() > 0)
			{
				StringBuffer buff = new StringBuffer();
				for(DevFailed e1 : failed)
				{
					buff.append(e1.getMessage() + "\n");
				}
				
				JOptionPane.showMessageDialog(null,
						buff.toString(),"Failed to reinitialize communication channel(s)",JOptionPane.ERROR_MESSAGE);
			}
		}    	
    }

    protected void initIORegister(ActionEvent e)
    {
		List<IORegister> ioregisters = ioRegisterViewsCombo.getSelectedItem() == ICON_VIEW ?
				ioRegistersListViewer.getSelectedIORegisters() :
				ioRegistersTableViewer.getSelectedIORegisters();
				
		if(ioregisters.size() < 1)
			return;
		
		int res = JOptionPane.showConfirmDialog(null, 
				"This action will perform an Init on all selected input/output registers.\nAre you sure?", 
				"Reinitialize input/output register(s)", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
		
		if(res == JOptionPane.YES_OPTION)
		{
			ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
			for(IORegister ioregister : ioregisters)
			{
				try 
				{
					ioregister.Init();
				} 
				catch (DevFailed e1) 
				{
					failed.add(e1);
				}
			}
			if(failed.size() > 0)
			{
				StringBuffer buff = new StringBuffer();
				for(DevFailed e1 : failed)
				{
					buff.append(e1.getMessage() + "\n");
				}
				
				JOptionPane.showMessageDialog(null,
						buff.toString(),"Failed to reinitialize input/output register(s)",JOptionPane.ERROR_MESSAGE);
			}
		}    	
    }

    protected void initMeasurementGroup(ActionEvent e)
    {
		List<MeasurementGroup> measurementGroups = measurementGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
				measurementGroupsListViewer.getSelectedMeasurementGroups() :
				measurementGroupsTableViewer.getSelectedMeasurementGroups();
				
		if(measurementGroups.size() < 1)
			return;
		
		int res = JOptionPane.showConfirmDialog(null, 
				"This action will perform an Init on all selected measurement groups.\nAre you sure?", 
				"Reinitialize measurement group(s)", JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);
		
		if(res == JOptionPane.YES_OPTION)
		{
			ArrayList<DevFailed> failed = new ArrayList<DevFailed>();
			for(MeasurementGroup measurementGroup : measurementGroups)
			{
				try 
				{
					measurementGroup.Init();
				} 
				catch (DevFailed e1) 
				{
					failed.add(e1);
				}
			}
			if(failed.size() > 0)
			{
				StringBuffer buff = new StringBuffer();
				for(DevFailed e1 : failed)
				{
					buff.append(e1.getMessage() + "\n");
				}
				
				JOptionPane.showMessageDialog(null,
						buff.toString(),"Failed to reinitialize measurement group(s)",JOptionPane.ERROR_MESSAGE);
			}
		}       	
    }

    protected void removeMotorGroupElementButtonPressed(ActionEvent e) 
    {
		MotorGroup group = motorGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
				motorGroupsListViewer.getSelectedMotorGroup() :
				motorGroupsTableViewer.getSelectedMotorGroup();
		
		if(group == null)
			return;
				
		RemoveMotorGroupElementDialog removeMGElementDialog = new RemoveMotorGroupElementDialog(devicePool, group);
		removeMGElementDialog.setLocationRelativeTo(null);
		removeMGElementDialog.setVisible(true);
	}

	protected void addMotorGroupElementButtonPressed(ActionEvent e) 
	{
		MotorGroup group = motorGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
				motorGroupsListViewer.getSelectedMotorGroup() :
				motorGroupsTableViewer.getSelectedMotorGroup();
		
		if(group == null)
			return;
				
		AddMotorGroupElementDialog addMGElementDialog = new AddMotorGroupElementDialog(devicePool, group);
		addMGElementDialog.setLocationRelativeTo(null);
		addMGElementDialog.setVisible(true);
	}
    
    protected void removeMeasurementGroupChannelButtonPressed(ActionEvent e) 
    {
		MeasurementGroup group = measurementGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
				measurementGroupsListViewer.getSelectedMeasurementGroup() :
				measurementGroupsTableViewer.getSelectedMeasurementGroup();
		
		if(group == null)
			return;
				
		RemoveMeasurementGroupChannelDialog removeMGChannelDialog = new RemoveMeasurementGroupChannelDialog(devicePool, group);
		removeMGChannelDialog.setLocationRelativeTo(null);
		removeMGChannelDialog.setVisible(true);
	}

	protected void addMeasurementGroupChannelButtonPressed(ActionEvent e) 
	{
		MeasurementGroup group = measurementGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
				measurementGroupsListViewer.getSelectedMeasurementGroup() :
				measurementGroupsTableViewer.getSelectedMeasurementGroup();
		
		if(group == null)
			return;
				
		AddMeasurementGroupChannelDialog addMGChannelDialog = new AddMeasurementGroupChannelDialog(devicePool, group);
		addMGChannelDialog.setLocationRelativeTo(null);
		addMGChannelDialog.setVisible(true);
	}

    protected void initCtrlButtonPressed(ActionEvent e) 
    {
		List<Controller> ctrls = ctrlViewsCombo.getSelectedItem() == ICON_VIEW ?
				ctrlListViewer.getSelectedControllers() :
				ctrlTableViewer.getSelectedControllers();
		
		StringBuffer msg = new StringBuffer("This action will perform an Init command on the selected controller(s)");
		msg.append("\nAre you sure you want to continue?");
    	
		int res = JOptionPane.showConfirmDialog(null, msg, "Reinitialize Controller(s)", JOptionPane.YES_NO_OPTION);
    	
		ArrayList<String> ctrl_names = new ArrayList<String>();
		
		for(Controller ctrl : ctrls)
			ctrl_names.add(ctrl.getName());
		
    	if( res == JOptionPane.YES_OPTION)
		{
    		try 
    		{
    			devicePool.initControllers(ctrl_names);
			} 
    		catch (DevFailed devFailed) 
    		{
    			StringBuffer buff = new StringBuffer("Failed to reinitialize controller(s).\nReason:");
				for(DevError elem : devFailed.errors)
					buff.append( elem.desc + "\n");
    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reinitialize controller(s)", JOptionPane.ERROR_MESSAGE);
			}
		}
	}

    protected void reloadCtrlLibButtonPressed(ActionEvent e) 
    {
		List<Controller> ctrls = ctrlViewsCombo.getSelectedItem() == ICON_VIEW ?
				ctrlListViewer.getSelectedControllers() :
				ctrlTableViewer.getSelectedControllers();

		ArrayList<String> fileNames = new ArrayList<String>();
		for(Controller ctrl : ctrls)
		{
			String fileName = ctrl.getCtrlClass().getFileName();
			if(!fileNames.contains(fileName))
				fileNames.add(fileName);
		}
		
		List<Controller> affectedCtrls = devicePool.getControllersInFiles(fileNames);
		
		StringBuffer msg = new StringBuffer("This action will affect the following controllers:");
		
		for(Controller ctrl : affectedCtrls)
			msg.append("\n" + ctrl.getName());
		
		msg.append("\nAre you sure you want to continue?");
    	
		int res = JOptionPane.showConfirmDialog(null, msg, "Reload Controller(s)", JOptionPane.YES_NO_OPTION);
    	
    	if( res == JOptionPane.YES_OPTION)
		{
    		try 
    		{
				devicePool.reloadControllerFiles(fileNames);
			} 
    		catch (DevFailed devFailed) 
    		{
    			StringBuffer buff = new StringBuffer("Failed to reload controller(s).\nReason:");
				for(DevError elem : devFailed.errors)
					buff.append( elem.desc + "\n");
    			JOptionPane.showMessageDialog(null, buff.toString(), "Failed to reload controller(s)", JOptionPane.ERROR_MESSAGE);
			}
		}
	}

	protected void clearDevicePool(ActionEvent e)
    {
    	int res = JOptionPane.showConfirmDialog(null, "Are you sure you want to clear the Device Pool configuration?", "Clear Device Pool", JOptionPane.YES_NO_OPTION);
    	
    	if( res == JOptionPane.YES_OPTION)
		{
    		DevicePoolUtils.clearDevicePool(devicePool);
		}
    }
    
	protected void removeMotorGroupButtonPressed(ActionEvent e)
	{
		List<MotorGroup> motorGroups = motorGroupViewsCombo.getSelectedItem() == ICON_VIEW ? 
			motorGroupsListViewer.getSelectedMotorGroups() :
			motorGroupsTableViewer.getSelectedMotorGroups();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove Motor Groups:\n");
		
		for(MotorGroup motorGroup : motorGroups)
			buff.append(motorGroup.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete Motor Group", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<MotorGroup, DevFailed> failedCommands = new HashMap<MotorGroup, DevFailed>();
			for(MotorGroup motorGroup : motorGroups)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(motorGroup.getName());

					devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_MOTOR_GROUP, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(motorGroup, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(MotorGroup motorGroup : failedCommands.keySet())
				{
					buff.append("Failed to delete Motor " + motorGroup.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(motorGroup);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete motorGroup groups", JOptionPane.ERROR_MESSAGE);
			}
		}				
	}

	protected void addMotorGroupButtonPressed(ActionEvent e)
	{
		AddMotorGroupDialog addMotorGroupDialog = new AddMotorGroupDialog(devicePool, null);
		addMotorGroupDialog.setLocationRelativeTo(null);
		addMotorGroupDialog.setVisible(true);
	}

	protected void cloneMotorButtonPressed(ActionEvent e)
	{
		Motor motor = motorViewsCombo.getSelectedItem() == ICON_VIEW ? 
			motorsListViewer.getSelectedMotor() :
			motorsTableViewer.getSelectedMotor();
		
		if(motor == null)
			return;
		
		AddMotorDialog addMotorDialog = new AddMotorDialog(devicePool, motor);
		addMotorDialog.setLocationRelativeTo(null);
		addMotorDialog.setVisible(true);
	}

	protected void removeMotorButtonPressed(ActionEvent e)
	{
	    List<Motor> motors = motorViewsCombo.getSelectedItem() == ICON_VIEW ? 
	    	motorsListViewer.getSelectedMotors() :
	    	motorsTableViewer.getSelectedMotors();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove Motors:\n");
		
		for(Motor motor : motors)
			buff.append(motor.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete Motors", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<Motor, DevFailed> failedCommands = new HashMap<Motor, DevFailed>();
			for(Motor motor : motors)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(motor.getName());

					if(motor instanceof PseudoMotor)
						devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_PSEUDO_MOTOR, args );
					else
						devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_MOTOR, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(motor, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(Motor motor : failedCommands.keySet())
				{
					buff.append("Failed to delete Motor " + motor.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(motor);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete motors", JOptionPane.ERROR_MESSAGE);
			}
		}		
	}

	protected void addMotorButtonPressed(ActionEvent e)
	{
		devicePool.setControllerClasses(DevicePoolUtils.getInstance().askForDevicePoolControllerClasses(devicePool));
		
		AddMotorDialog addMotorDialog = new AddMotorDialog(devicePool);
		addMotorDialog.setLocationRelativeTo(null);
		addMotorDialog.setVisible(true);
	}

	protected void cloneCtrlButtonPressed(ActionEvent e)
	{
		Controller ctrl = ctrlViewsCombo.getSelectedItem() == ICON_VIEW ?
				ctrlListViewer.getSelectedController() :
				ctrlTableViewer.getSelectedController();
		
		if(ctrl == null)
			return;
		
		AddControllerDialog addCtrlDialog = new AddControllerDialog(devicePool, ctrl.getCtrlClass());
		addCtrlDialog.setLocationRelativeTo(null);
		addCtrlDialog.setVisible(true);
	}

	protected void removeCtrlButtonPressed(ActionEvent e)
	{
		List<Controller> ctrls = ctrlViewsCombo.getSelectedItem() == ICON_VIEW ?
				ctrlListViewer.getSelectedControllers() :
				ctrlTableViewer.getSelectedControllers();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove Controllers:\n");
		
		for(Controller ctrl : ctrls)
			buff.append(ctrl.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete Controllers", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<Controller, DevFailed> failedCommands = new HashMap<Controller, DevFailed>();
			for(Controller ctrl : ctrls)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(ctrl.getName());

					devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_CTRL, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(ctrl, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(Controller ctrl : failedCommands.keySet())
				{
					buff.append("Failed to delete Controller " + ctrl.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(ctrl);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete controllers", JOptionPane.ERROR_MESSAGE);
			}
		}
	}
	
	protected void addCtrlButtonPressed(ActionEvent e)
	{
		// ControllerClassList is not event enabled so we refresh it before
		// opening the add window for controllers
		
		AddControllerDialog addCtrlDialog = new AddControllerDialog(devicePool, null);
		addCtrlDialog.setLocationRelativeTo(null);
		addCtrlDialog.setVisible(true);
	}
	
	protected void cloneChannelButtonPressed(ActionEvent e)
	{
		ExperimentChannel channel = channelViewsCombo.getSelectedItem() == ICON_VIEW ?
				channelsListViewer.getSelectedExperimentChannel() :
				channelsTableViewer.getSelectedExperimentChannel();
		
		if(channel == null)
			return;
		
		AddChannelDialog addChannelDialog = new AddChannelDialog(devicePool, channel);
		addChannelDialog.setLocationRelativeTo(null);
		addChannelDialog.setVisible(true);
	}

	protected void cloneComChannelButtonPressed(ActionEvent e)
	{
		CommunicationChannel channel = channelViewsCombo.getSelectedItem() == ICON_VIEW ?
				comChannelsListViewer.getSelectedCommunicationChannel() :
				comChannelsTableViewer.getSelectedCommunicationChannel();
		
		if(channel == null)
			return;
		
		AddComChannelDialog addComChannelDialog = new AddComChannelDialog(devicePool, channel);
		addComChannelDialog.setLocationRelativeTo(null);
		addComChannelDialog.setVisible(true);
	}

	protected void cloneIORegisterButtonPressed(ActionEvent e)
	{
		IORegister ioregister = ioRegisterViewsCombo.getSelectedItem() == ICON_VIEW ?
				ioRegistersListViewer.getSelectedIORegister() :
				ioRegistersTableViewer.getSelectedIORegister();
		
		if(ioregister == null)
			return;
		
		AddIORegisterDialog addIORegisterDialog = new AddIORegisterDialog(devicePool, ioregister);
		addIORegisterDialog.setLocationRelativeTo(null);
		addIORegisterDialog.setVisible(true);
	}

	protected void removeChannelButtonPressed(ActionEvent e)
	{
	    List<ExperimentChannel> channels = channelViewsCombo.getSelectedItem() == ICON_VIEW ?
	    		channelsListViewer.getSelectedExperimentChannels() :
	    		channelsTableViewer.getSelectedExperimentChannels();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove Channels:\n");
		
		for(ExperimentChannel channel :channels)
			buff.append(channel.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete Channels", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<ExperimentChannel, DevFailed> failedCommands = new HashMap<ExperimentChannel, DevFailed>();
			for(ExperimentChannel channel : channels)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(channel.getName());

					devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_EXP_CHANNEL, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(channel, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(ExperimentChannel channel : failedCommands.keySet())
				{
					buff.append("Failed to delete Experiment Channel " + channel.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(channel);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete experiment channels", JOptionPane.ERROR_MESSAGE);
			}
		}		
	}

	protected void removeComChannelButtonPressed(ActionEvent e)
	{
	    List<CommunicationChannel> channels = channelViewsCombo.getSelectedItem() == ICON_VIEW ?
	    		comChannelsListViewer.getSelectedCommunicationChannels() :
	    		comChannelsTableViewer.getSelectedCommunicationChannels();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove communication channels:\n");
		
		for(CommunicationChannel channel :channels)
			buff.append(channel.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete communication channels", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<CommunicationChannel, DevFailed> failedCommands = new HashMap<CommunicationChannel, DevFailed>();
			for(CommunicationChannel channel : channels)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(channel.getName());

					devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_COM_CHANNEL, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(channel, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(CommunicationChannel channel : failedCommands.keySet())
				{
					buff.append("Failed to delete Communication Channel " + channel.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(channel);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete communication channels", JOptionPane.ERROR_MESSAGE);
			}
		}		
	}

	protected void removeIORegisterButtonPressed(ActionEvent e)
	{
	    List<IORegister> ioregisters = ioRegisterViewsCombo.getSelectedItem() == ICON_VIEW ?
	    		ioRegistersListViewer.getSelectedIORegisters() :
	    		ioRegistersTableViewer.getSelectedIORegisters();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove input/output registers:\n");
		
		for(IORegister ioregister :ioregisters)
			buff.append(ioregister.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete input/output registers", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<IORegister, DevFailed> failedCommands = new HashMap<IORegister, DevFailed>();
			for(IORegister ioregister :ioregisters)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(ioregister.getName());

					devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_IOREGISTER, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(ioregister, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(IORegister ioregister : failedCommands.keySet())
				{
					buff.append("Failed to delete input/output register " + ioregister.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(ioregister);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete input/output registers", JOptionPane.ERROR_MESSAGE);
			}
		}		
	}

	protected void addChannelButtonPressed(ActionEvent e)
	{
		AddChannelDialog addChannelDialog = new AddChannelDialog(devicePool);
		addChannelDialog.setLocationRelativeTo(null);
		addChannelDialog.setVisible(true);
	}	

	protected void addComChannelButtonPressed(ActionEvent e)
	{
		AddComChannelDialog addComChannelDialog = new AddComChannelDialog(devicePool);
		addComChannelDialog.setLocationRelativeTo(null);
		addComChannelDialog.setVisible(true);
	}	

	protected void addIORegisterButtonPressed(ActionEvent e)
	{
		AddIORegisterDialog addIORegisterDialog = new AddIORegisterDialog(devicePool);
		addIORegisterDialog.setLocationRelativeTo(null);
		addIORegisterDialog.setVisible(true);
	}	
		
	protected void removeMeasurementGroupButtonPressed(ActionEvent e)
	{
		List<MeasurementGroup> measurementGroups = measurementGroupViewsCombo.getSelectedItem() == ICON_VIEW ?
			measurementGroupsListViewer.getSelectedMeasurementGroups() :	
			measurementGroupsTableViewer.getSelectedMeasurementGroups();
		
		StringBuffer buff = new StringBuffer("Are you sure you want to remove Measurement Groups:\n");
		
		for(MeasurementGroup measurementGroup : measurementGroups)
			buff.append(measurementGroup.getName() + "\n");
		
		int res = JOptionPane.showConfirmDialog(null, buff.toString(), "Delete Measurement Group", JOptionPane.YES_NO_OPTION);
		
		if( res == JOptionPane.YES_OPTION)
		{
			HashMap<MeasurementGroup, DevFailed> failedCommands = new HashMap<MeasurementGroup, DevFailed>();
			for(MeasurementGroup measurementGroup : measurementGroups)
			{
				try
				{
					DeviceData args = new DeviceData();

					args.insert(measurementGroup.getName());

					devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_DELETE_MEASUREMENT_GROUP, args );
				}	
				catch (DevFailed devFailed)
				{
					failedCommands.put(measurementGroup, devFailed);
				}
			}
			
			if(failedCommands.size() > 0)
			{
				buff = new StringBuffer();
				
				for(MeasurementGroup measurementGroup : failedCommands.keySet())
				{
					buff.append("Failed to delete measurement group " + measurementGroup.getName() + ".\nReason:");
					DevFailed devFailed = failedCommands.get(measurementGroup);
					for(DevError elem : devFailed.errors)
					{
						buff.append( elem.desc + "\n");
					}
					buff.append("-----------------\n");
				}
				JOptionPane.showMessageDialog(null, buff.toString(), "Failed to delete measurement group(s)", JOptionPane.ERROR_MESSAGE);
			}
		}				
	}

	protected void addMeasurementGroupButtonPressed(ActionEvent e)
	{
		AddMeasurementGroupDialog addMeasurementGroupDialog = new AddMeasurementGroupDialog(devicePool, null);
		addMeasurementGroupDialog.setLocationRelativeTo(null);
		addMeasurementGroupDialog.setVisible(true);
	}
	
    private void initComponents() {
        elementsPane = new javax.swing.JTabbedPane();

        setLayout(new java.awt.BorderLayout());

        add(elementsPane, java.awt.BorderLayout.CENTER);

    }
    
    protected class IconListComboRenderer extends DefaultListCellRenderer
    {
		@Override
		public Component getListCellRendererComponent(JList list, Object value, int index, boolean isSelected, boolean cellHasFocus) 
		{
			JLabel l = (JLabel) super.getListCellRendererComponent(list, value, index, isSelected,
					cellHasFocus);
			
			String type = (String) value;
			if(type == ICON_VIEW)
			{
				l.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_ICON_VIEW));
			}
			else
				l.setIcon(SwingResource.smallIconMap.get(IImageResource.IMG_LIST_VIEW));
			
			return l;
		}
    }
}
