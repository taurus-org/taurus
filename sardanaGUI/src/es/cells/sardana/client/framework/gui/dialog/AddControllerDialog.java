package es.cells.sardana.client.framework.gui.dialog;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTabbedPane;
import javax.swing.JTextField;
import javax.swing.SwingConstants;
import javax.swing.WindowConstants;

import es.cells.sardana.client.framework.gui.IImageResource;
import es.cells.sardana.client.framework.gui.panel.ButtonsPanel;
import es.cells.sardana.client.framework.gui.panel.PropertyPanel;
import es.cells.sardana.client.framework.pool.ControllerClass;
import es.cells.sardana.client.framework.pool.ControllerType;
import es.cells.sardana.client.framework.pool.CounterTimer;
import es.cells.sardana.client.framework.pool.DevicePool;
import es.cells.sardana.client.framework.pool.DevicePoolUtils;
import es.cells.sardana.client.framework.pool.ExperimentChannel;
import es.cells.sardana.client.framework.pool.Machine;
import es.cells.sardana.client.framework.pool.PropertyInfo;
import es.cells.sardana.client.framework.pool.PropertyType;
import es.cells.sardana.client.framework.pool.PseudoCounterClass;
import es.cells.sardana.client.framework.pool.PseudoMotorClass;
import es.cells.sardana.client.framework.pool.IORegisterClass;
import es.cells.sardana.client.framework.pool.ZeroDExpChannel;
import es.cells.sardana.client.framework.pool.OneDExpChannel;
import es.cells.sardana.client.framework.pool.TwoDExpChannel;
import es.cells.sardana.client.gui.swing.SwingResource;
import fr.esrf.Tango.DevError;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.StringSpectrumEvent;

public class AddControllerDialog extends JDialog implements IStringSpectrumListener
{
	protected static final String PM_TITLE = "Pseudo Motor Roles";
	protected static final String PC_TITLE = "Pseudo Counter Roles";
    protected static final String IO_TITLE = "Predefined Values";

	DevicePool devicePool;
	ControllerClass ctrlClass;
	private JButton createButton;
	private JButton exitButton;
	private JButton refreshCtrlClassListButton;
	
	private JLabel ctrlDetailsLabel;
	
	private JLabel ctrlImg;
	private JTextField ctrlGenre;
	private JTextField ctrlModel;
	private JTextField ctrlOrganization;
	private JLabel logoImg;
	private JLabel iconImg;
	
	private JComboBox typeCombo;
	private JComboBox ctrlFileNameComboBox;
	private JComboBox ctrlClassComboBox;
	private JTextField instanceText;
	
	JTabbedPane propAndRolesPane;
	//PropertiesTableEditorPanel propertiesEditor;
	PropertyPanel propertiesEditor;
	
	JPanel pseudoMotorDataPanel;
	private JPanel pseudoMotorRolesPanel;
	private JPanel motorRolesPanel;
	private JTextField[] pseudoMotorNames;
	private JComboBox[] motorNames;
	private JScrollPane pseudoMotorRolesPane;
	private JScrollPane motorRolesPane;
	
	JPanel pseudoCounterDataPanel;
	private JPanel pseudoCounterRolesPanel;
	private JPanel counterRolesPanel;
	private JTextField[] pseudoCounterNames;
	private JComboBox[] counterNames;
	private JScrollPane pseudoCounterRolesPane;
	private JScrollPane counterRolesPane;
	
	JPanel ioRegisterDataPanel;
	private JPanel ioRegisterValuesPanel;
    private JTextField[] predefinedValues;
	private JLabel[] predefinedValuesDesc;
	private JScrollPane ioRegisterValuesPane;

	//private static Logger log = SardanaManager.getInstance().getLogger(AddControllerDialog.class.getName());

	public AddControllerDialog(DevicePool devicePool)
	{
		this(devicePool, null);
	}

	public AddControllerDialog(DevicePool devicePool, ControllerClass ctrlClass)
	{
		super();
		
		this.devicePool = devicePool;
		this.ctrlClass = ctrlClass;
		
		initComponents();
	}
	
	protected void updateFileNameCombo()
	{
		ControllerType type = (ControllerType) typeCombo.getSelectedItem();
		ctrlFileNameComboBox.removeAllItems();
		
		for(String fileName : devicePool.getControllerFilesNames(type))
			ctrlFileNameComboBox.addItem(fileName);
		
		if(ctrlFileNameComboBox.getItemCount() > 0)
			ctrlFileNameComboBox.setSelectedIndex(0);
		else
			ctrlFileNameComboBox.setSelectedIndex(-1);
	}
	
	protected void updateClassCombo()
	{
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		ctrlClassComboBox.removeAllItems();
		
		if(fileName != null)
		{
			for(ControllerClass ctrlClass : devicePool.getControllerClasses(fileName))
				ctrlClassComboBox.addItem(ctrlClass.getClassName());
		}
		
		if(ctrlClassComboBox.getItemCount() > 0)
			ctrlClassComboBox.setSelectedIndex(0);
		else
			ctrlClassComboBox.setSelectedIndex(-1);
	}
	
	protected void updateDescription()
	{
		
		if(ctrlClassComboBox.getSelectedIndex() < 0)
		{
			String descr = "<html><font size='3'><i>No controller class selected</i></font>";
	    	ctrlDetailsLabel.setText(descr);
			return;
		}
		ControllerType type = (ControllerType) typeCombo.getSelectedItem();
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		String ctrlClassName = (String) ctrlClassComboBox.getSelectedItem();

		if(type!=null && fileName != null && ctrlClassName != null)
		{
			ControllerClass ctrlClass = devicePool.getControllerClassByName(type, fileName, ctrlClassName);
		
			if(ctrlClass != null)
			{
				String descr = "<html><font size='3'>" + ctrlClass.getDescription().replaceAll("\n", "<br>") + "</font>";
		    	ctrlDetailsLabel.setText(descr);
				
		    	ImageIcon ctrlImage = ctrlClass.getImageIcon();
		    	ImageIcon ctrlIcon  = ctrlClass.getIcon();
		    	
		    	if(ctrlIcon == null)
		    	{
		    		if(type == ControllerType.Motor)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_MOTOR);
		    		else if(type == ControllerType.CounterTimer)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_CT);
		    		else if(type == ControllerType.ZeroDExpChannel)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_0D);
					else if(type == ControllerType.OneDExpChannel)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_1D);
					else if(type == ControllerType.TwoDExpChannel)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_2D);
		    		else if(type == ControllerType.Communication)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_COM_CHANNEL);
		    		else if(type == ControllerType.IORegister)
		    			ctrlIcon = SwingResource.bigIconMap.get(IImageResource.IMG_POOL_CTRL_IOREGISTER);
		    	}
		    	
		    	if(ctrlImage == null)
		    	{
	    			ctrlImage = ctrlIcon;
		    	}
		    	
	    		ctrlImg.setIcon(ctrlImage);
	    		iconImg.setIcon(ctrlIcon);
	    		
		    	ImageIcon logoImage = ctrlClass.getLogo();
		    	
	    		logoImg.setIcon(logoImage);
		    	
		    	ctrlOrganization.setText(ctrlClass.getOrganization());
		    	ctrlGenre.setText(ctrlClass.getGenre());
		    	ctrlModel.setText(ctrlClass.getModel());
			}
		}
		else
		{
			String descr = "<html><font size='3'><i>No controller class selected</i></font>";
	    	ctrlDetailsLabel.setText(descr);
		}
	}

	protected void updateProperties()
	{
		if(ctrlClassComboBox.getSelectedIndex() < 0)
		{
			propertiesEditor.setModel(null, null);
			return;
		}

		ControllerType type = (ControllerType) typeCombo.getSelectedItem();
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		String ctrlClassName = (String) ctrlClassComboBox.getSelectedItem();

		if(type!=null && fileName != null && ctrlClassName != null)
		{
			ControllerClass ctrlClass = devicePool.getControllerClassByName(type, fileName, ctrlClassName);
		
			if(ctrlClass != null)
			{
		    	propertiesEditor.setModel(ctrlClass.getPropertiesInfo(), ctrlClass.getDbClassProperties());
			}
		}
		else
		{
			propertiesEditor.setModel(null, null);
		}		
	}
	
	protected void updatePseudoMotorRoles()
	{
		if(ctrlClassComboBox.getSelectedIndex() < 0)
		{
			setPseudoMotorRolesVisible(false);
			return;
		}
		
		ControllerType type = (ControllerType) typeCombo.getSelectedItem();
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		String ctrlClassName = (String) ctrlClassComboBox.getSelectedItem();
		
		if(type!=null && fileName != null && ctrlClassName != null &&
		   type == ControllerType.PseudoMotor)
		{
			PseudoMotorClass ctrlClass = (PseudoMotorClass) devicePool.getControllerClassByName(type, fileName, ctrlClassName);
			updatePseudoMotorData(ctrlClass);
			
			setPseudoMotorRolesVisible(true);
		}
		else
		{
			setPseudoMotorRolesVisible(false);
		}
	}
	
	protected void updatePseudoCounterRoles()
	{
		if(ctrlClassComboBox.getSelectedIndex() < 0)
		{
			setPseudoCounterRolesVisible(false);
			return;
		}
		
		ControllerType type = (ControllerType) typeCombo.getSelectedItem();
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		String ctrlClassName = (String) ctrlClassComboBox.getSelectedItem();
		
		if(type!=null && fileName != null && ctrlClassName != null &&
		   type == ControllerType.PseudoCounter)
		{
			PseudoCounterClass ctrlClass = (PseudoCounterClass) devicePool.getControllerClassByName(type, fileName, ctrlClassName);
			updatePseudoCounterData(ctrlClass);
			
			setPseudoCounterRolesVisible(true);
		}
		else
		{
			setPseudoCounterRolesVisible(false);
			return;
		}
		
	}

	protected void updateIORegisterValues()
	{
		if(ctrlClassComboBox.getSelectedIndex() < 0)
		{
			setIORegisterValuesVisible(false);
			return;
		}
		
		ControllerType type = (ControllerType) typeCombo.getSelectedItem();
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		String ctrlClassName = (String) ctrlClassComboBox.getSelectedItem();
		
		if(type!=null && fileName != null && ctrlClassName != null &&
		   type == ControllerType.IORegister)
		{
			IORegisterClass ctrlClass = (IORegisterClass) devicePool.getControllerClassByName(type, fileName, ctrlClassName);
			updateIORegisterData(ctrlClass);
			
			setIORegisterValuesVisible(true);
		}
		else
		{
			setIORegisterValuesVisible(false);
			return;
		}
		
	}

	protected void initComponents()
	{
		setTitle("Create Controller");
		setResizable(false);
		setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		addWindowListener( new WindowAdapter() {

			@Override
			public void windowClosing(WindowEvent e)
			{
				closeAndExit();
			}
		});
		
		JPanel mainPanel = new JPanel(new GridBagLayout());
		
		getContentPane().setLayout( new BorderLayout() );
		getContentPane().add(mainPanel, BorderLayout.CENTER);
		
		
		JLabel typeLabel = new JLabel("Type:");
		typeLabel.setHorizontalAlignment(JLabel.RIGHT);
		typeCombo = new JComboBox( devicePool.getControllerTypes().toArray() );
		
		JLabel instanceLabel = new JLabel("Name:");
		instanceLabel.setHorizontalAlignment(JLabel.RIGHT);
		instanceText = new JTextField(20);
	
		JLabel libLabel = new JLabel("Library:");
		libLabel.setHorizontalAlignment(JLabel.RIGHT);
		ctrlFileNameComboBox = new JComboBox( );

		JLabel classLabel = new JLabel("Class:");
		classLabel.setHorizontalAlignment(JLabel.RIGHT);
		ctrlClassComboBox = new JComboBox();
		
		propertiesEditor = new PropertyPanel();

		ctrlDetailsLabel = new JLabel("");
		ctrlDetailsLabel.setOpaque(false);

		ctrlImg = new JLabel();
		ctrlImg.setMinimumSize(new Dimension(256,256));
		ctrlImg.setPreferredSize(new Dimension(256,256));
		ctrlImg.setIconTextGap(0);
		ctrlImg.setHorizontalAlignment(SwingConstants.CENTER);
		ctrlImg.setVerticalAlignment(SwingConstants.CENTER);

		logoImg = new JLabel();
		logoImg.setMinimumSize(new Dimension(100,80));
		logoImg.setPreferredSize(new Dimension(100,80));
		logoImg.setIconTextGap(0);
		logoImg.setHorizontalAlignment(SwingConstants.CENTER);
		logoImg.setVerticalAlignment(SwingConstants.CENTER);

		iconImg = new JLabel();
		iconImg.setMinimumSize(new Dimension(64,64));
		iconImg.setPreferredSize(new Dimension(64,64));
		iconImg.setIconTextGap(0);
		iconImg.setHorizontalAlignment(SwingConstants.CENTER);
		iconImg.setVerticalAlignment(SwingConstants.CENTER);
		
		JLabel orgLabel = new JLabel("Organization:");
		orgLabel.setHorizontalAlignment(JLabel.RIGHT);
		ctrlOrganization = new JTextField(15);
		ctrlOrganization.setEditable(false);
		
		JLabel familyLabel = new JLabel("Family:");
		familyLabel.setHorizontalAlignment(JLabel.RIGHT);
		ctrlGenre = new JTextField(15);
		ctrlGenre.setEditable(false);
		
		JLabel modelLabel = new JLabel("Model:");
		modelLabel.setHorizontalAlignment(JLabel.RIGHT);
		ctrlModel = new JTextField(15);
		ctrlModel.setEditable(false);
		
		// Pseudo motor gui elements
        pseudoMotorDataPanel = new JPanel();
        pseudoMotorDataPanel.setLayout(new GridLayout(2, 1, 2, 2));
        
        pseudoMotorRolesPanel = new JPanel();
        pseudoMotorRolesPanel.setLayout(new GridBagLayout());
        pseudoMotorRolesPane = new JScrollPane(pseudoMotorRolesPanel);
        pseudoMotorRolesPane.setBorder(javax.swing.BorderFactory.createTitledBorder("Pseudo Motor Roles"));
        pseudoMotorRolesPane.setPreferredSize(new Dimension(220,100));
        pseudoMotorRolesPane.setMinimumSize(new Dimension(220,100));
        pseudoMotorDataPanel.add(pseudoMotorRolesPane);
        
        motorRolesPanel = new JPanel();
        motorRolesPanel.setLayout(new GridBagLayout());
        motorRolesPane = new JScrollPane(motorRolesPanel);
        motorRolesPane.setBorder(javax.swing.BorderFactory.createTitledBorder("Motor Roles"));
        motorRolesPane.setPreferredSize(new Dimension(220,100));
        motorRolesPane.setMinimumSize(new Dimension(220,100));
        pseudoMotorDataPanel.add(motorRolesPane);
        
        // pseudo counter gui elements
        pseudoCounterDataPanel = new JPanel();
        pseudoCounterDataPanel.setLayout(new GridLayout(2, 1, 2, 2));
        
        pseudoCounterRolesPanel = new JPanel();
        pseudoCounterRolesPanel.setLayout(new GridBagLayout());
        pseudoCounterRolesPane = new JScrollPane(pseudoCounterRolesPanel);
        pseudoCounterRolesPane.setBorder(javax.swing.BorderFactory.createTitledBorder("Pseudo Counter Roles"));
        pseudoCounterRolesPane.setPreferredSize(new Dimension(220,100));
        pseudoCounterRolesPane.setMinimumSize(new Dimension(220,100));
        pseudoCounterDataPanel.add(pseudoCounterRolesPane);
        
        counterRolesPanel = new JPanel();
        counterRolesPanel.setLayout(new GridBagLayout());
        counterRolesPane = new JScrollPane(counterRolesPanel);
        counterRolesPane.setBorder(javax.swing.BorderFactory.createTitledBorder("Counter Roles"));
        counterRolesPane.setPreferredSize(new Dimension(220,100));
        counterRolesPane.setMinimumSize(new Dimension(220,100));
        pseudoCounterDataPanel.add(counterRolesPane);
        
        // input/output register gui elements

        ioRegisterDataPanel = new JPanel(); 
        ioRegisterDataPanel.setLayout(new GridLayout(1, 1));

		ioRegisterValuesPanel = new JPanel();
        ioRegisterValuesPanel.setLayout(new GridBagLayout());
        ioRegisterValuesPane = new JScrollPane(ioRegisterValuesPanel);
        ioRegisterValuesPane.setPreferredSize(new Dimension(220,220));
        ioRegisterValuesPane.setMinimumSize(new Dimension(220,220));
        ioRegisterDataPanel.add(ioRegisterValuesPane);

        propAndRolesPane = new JTabbedPane();
        propAndRolesPane.addTab("Properties", new JScrollPane(propertiesEditor));
        propAndRolesPane.setSelectedIndex(0);
		
		typeCombo.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				updateFileNameCombo();
			}
		});
		
		ctrlFileNameComboBox.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				updateClassCombo();
			}
		});
		
		ctrlClassComboBox.addItemListener(new ItemListener()
		{
			public void itemStateChanged(ItemEvent e) 
			{
				if(e.getStateChange() == ItemEvent.SELECTED)
				{
					updateDescription();
					updateProperties();
					updatePseudoMotorRoles();
					updatePseudoCounterRoles();
                    updateIORegisterValues();
				}
			}
		});
		
		if(typeCombo.getItemCount() > 0)
			typeCombo.setSelectedIndex(0);		

		JPanel detailsPanel = new JPanel(new GridBagLayout());
		detailsPanel.setBorder(BorderFactory.createTitledBorder("Details"));
		
		JScrollPane detailsScrollPane = new JScrollPane(ctrlDetailsLabel);
		detailsScrollPane.setBorder(BorderFactory.createTitledBorder("Description"));
		detailsScrollPane.setOpaque(false);
		detailsScrollPane.setMinimumSize(new Dimension(280,80));
        detailsScrollPane.setPreferredSize(new Dimension(280,80));

        getContentPane().add(detailsScrollPane, BorderLayout.NORTH);
                
        GridBagConstraints gbc;
        
		gbc = new GridBagConstraints(
				0,0, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		mainPanel.add(instanceLabel, gbc);

		gbc = new GridBagConstraints(
				1,0, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		mainPanel.add(instanceText, gbc);		
        
		gbc = new GridBagConstraints(
				0,1, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(typeLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,1, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(typeCombo, gbc);

		gbc = new GridBagConstraints(
				0,2, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		mainPanel.add(libLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,2, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);		
		mainPanel.add(ctrlFileNameComboBox, gbc);

		gbc = new GridBagConstraints(
				0,3, // x,y
				1,1, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		mainPanel.add(classLabel, gbc);
		
		gbc = new GridBagConstraints(
				1,3, // x,y
				1,1, // width, height
				1.0, 0.0, //weight x,y
				GridBagConstraints.WEST, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		mainPanel.add(ctrlClassComboBox, gbc);
		
		gbc = new GridBagConstraints(
				0,4, // x,y
				2,1, // width, height
				1.0, 0.5, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.BOTH, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		//mainPanel.add(propertiesEditor, gbc);
		mainPanel.add(propAndRolesPane, gbc);
		
		gbc = new GridBagConstraints(
				2,0, // x,y
				1,5, // width, height
				1.0, 0.5, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.BOTH, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		mainPanel.add(detailsPanel,gbc);

		// FILL DetailsPanel
		
		gbc = new GridBagConstraints(
				0,0, // x,y
				3,1, // width, height
				1.0, 1.0, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.BOTH, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(ctrlImg,gbc);

		gbc = new GridBagConstraints(
				2,1, // x,y
				1,3, // width, height
				0.0, 0.0, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(logoImg,gbc);
		
		gbc = new GridBagConstraints(
				0,1, // x,y
				1,1, // width, height
				0.0, 0.33, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(orgLabel,gbc);

		gbc = new GridBagConstraints(
				1,1, // x,y
				1,1, // width, height
				0.5, 0.33, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(ctrlOrganization,gbc);

		gbc = new GridBagConstraints(
				0,2, // x,y
				1,1, // width, height
				0.0, 0.33, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(familyLabel,gbc);

		gbc = new GridBagConstraints(
				1,2, // x,y
				1,1, // width, height
				0.5, 0.33, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(ctrlGenre,gbc);

		gbc = new GridBagConstraints(
				0,3, // x,y
				1,1, // width, height
				0.0, 0.33, //weight x,y
				GridBagConstraints.EAST, //anchor
				GridBagConstraints.NONE, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(modelLabel,gbc);

		gbc = new GridBagConstraints(
				1,3, // x,y
				1,1, // width, height
				0.5, 0.33, //weight x,y
				GridBagConstraints.CENTER, //anchor
				GridBagConstraints.HORIZONTAL, // fill
				new Insets(2, 2, 2, 2), // insets
				0,0 //pad x,y
				);
		detailsPanel.add(ctrlModel,gbc);
		
		if(ctrlClass != null)
		{
			setTitle("Add new Controller");
			
			typeCombo.setEnabled(false);
			ctrlFileNameComboBox.setEnabled(false);
			ctrlClassComboBox.setEnabled(false);
			
			typeCombo.setSelectedItem(ctrlClass.getType());
			ctrlFileNameComboBox.setSelectedItem(ctrlClass.getFileName());
			ctrlClassComboBox.setSelectedItem(ctrlClass.getClassName());
		}
		
		ButtonsPanel buttonsPanel = new ButtonsPanel();
		
		refreshCtrlClassListButton = new JButton("Refresh",SwingResource.smallIconMap.get(IImageResource.IMG_REFRESH));
		createButton = new JButton("Create", SwingResource.smallIconMap.get(IImageResource.IMG_APPLY));
		exitButton = new JButton("Close", SwingResource.smallIconMap.get(IImageResource.IMG_CLOSE));
		
		refreshCtrlClassListButton.setToolTipText("Refresh the list of controller classes");
		createButton.setToolTipText("Create a new controller");
		exitButton.setToolTipText("Close window");
		
		buttonsPanel.addLeft(refreshCtrlClassListButton);
		buttonsPanel.addRight(createButton);
		buttonsPanel.addRight(exitButton);
		
		refreshCtrlClassListButton.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent e) 
			{
				refreshPressed();
			}
		});
		createButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				createPressed(e);
			}
		});
		
		exitButton.addActionListener( new ActionListener()
		{
			public void actionPerformed(ActionEvent e)
			{
				exitPressed(e);
			}
		});
		
		devicePool.addControllerClassListListener(this);
		
		getContentPane().add(buttonsPanel, BorderLayout.SOUTH);
		
		pack();
	}
	
	protected void setPseudoMotorRolesVisible(boolean b)
	{
		if(b == true)
		{
			if(propAndRolesPane.getTabCount() > 1)
			{
				if(propAndRolesPane.getTitleAt(1) != PM_TITLE)
				{
					propAndRolesPane.removeTabAt(1);
				}
			}
			propAndRolesPane.addTab(PM_TITLE, pseudoMotorDataPanel);
			propAndRolesPane.setSelectedComponent(pseudoMotorDataPanel);
		}
		else
		{
			if(propAndRolesPane.getTabCount() > 1)
			{
				if(propAndRolesPane.getTitleAt(1) == PM_TITLE)
				{
					propAndRolesPane.removeTabAt(1);
				}
			}
			propAndRolesPane.setSelectedIndex(0);
		}
	}

	protected void setPseudoCounterRolesVisible(boolean b)
	{
		if(b == true)
		{
			if(propAndRolesPane.getTabCount() > 1)
			{
				if(propAndRolesPane.getTitleAt(1) != PC_TITLE)
				{
					propAndRolesPane.removeTabAt(1);
				}
			}
			propAndRolesPane.addTab(PC_TITLE, pseudoCounterDataPanel);
			propAndRolesPane.setSelectedComponent(pseudoCounterDataPanel);
		}
		else
		{
			if(propAndRolesPane.getTabCount() > 1)
			{
				if(propAndRolesPane.getTitleAt(1) == PC_TITLE)
				{
					propAndRolesPane.removeTabAt(1);
				}
			}
			propAndRolesPane.setSelectedIndex(0);
		}
	}
	
	protected void setIORegisterValuesVisible(boolean b)
	{
		if(b == true)
		{
			if(propAndRolesPane.getTabCount() > 1)
			{
				if(propAndRolesPane.getTitleAt(1) != IO_TITLE)
				{
					propAndRolesPane.removeTabAt(1);
				}
			}
			propAndRolesPane.addTab(IO_TITLE, ioRegisterDataPanel);
			propAndRolesPane.setSelectedComponent(ioRegisterDataPanel);
		}
		else
		{
			if(propAndRolesPane.getTabCount() > 1)
			{
				if(propAndRolesPane.getTitleAt(1) == IO_TITLE)
				{
					propAndRolesPane.removeTabAt(1);
				}
			}
			propAndRolesPane.setSelectedIndex(0);
		}
	}

	protected void updatePseudoCounterData(PseudoCounterClass pcClass)
	{
		pseudoCounterRolesPanel.removeAll();
		counterRolesPanel.removeAll();
		
		if(pcClass != null)
		{
			pseudoCounterNames = new JTextField[pcClass.getPseudoCounterRoles().size()];
			counterNames = new JComboBox[pcClass.getCounterRoles().size()];
			
			GridBagConstraints gbc = new GridBagConstraints();
			gbc.insets = new Insets(2,2,2,2);
			gbc.fill = GridBagConstraints.HORIZONTAL;
			int i = 0;
			for(String pcRoles : pcClass.getPseudoCounterRoles())
			{
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 0.0;
				gbc.gridx = 0;
				gbc.gridy = i;
				JLabel pcRole = new JLabel(pcRoles);
				pcRole.setToolTipText("The role of the pseudo counter in the pseudo counter system");
				pseudoCounterRolesPanel.add(pcRole, gbc);
				
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 1.0;
				gbc.gridx = 1;
				pseudoCounterNames[i] = new JTextField();
				pseudoCounterNames[i].setToolTipText("The name of the pseudo counter which will have the corresponding role in the pseudo counter system");
				pseudoCounterRolesPanel.add(pseudoCounterNames[i], gbc);
				i++;
			}
			int j = 0;
			for(String pcRoles : pcClass.getCounterRoles())
			{
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 0.0;
				gbc.gridx = 0;
				gbc.gridy = j;
				JLabel cRole = new JLabel(pcRoles);
				cRole.setToolTipText("The role of the pseudo counter in the pseudo counter system");
				counterRolesPanel.add(cRole, gbc);
				
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 1.0;
				gbc.gridx = 1;
				
				counterNames[j] = new JComboBox();
				for(ExperimentChannel ch : devicePool.getExperimentChannels())
				{
					if(ch instanceof CounterTimer || ch instanceof ZeroDExpChannel || ch instanceof OneDExpChannel || ch instanceof TwoDExpChannel)
						counterNames[j].addItem(ch);
				}
				
				counterNames[j].setToolTipText("The name of the counter which will have the corresponding role in the pseudo counter system");
				counterRolesPanel.add(counterNames[j], gbc);
				j++;
			}			
		}
		pseudoCounterRolesPanel.revalidate();
		counterRolesPanel.revalidate();		
	}
	
	protected void updatePseudoMotorData(PseudoMotorClass pmClass) 
    {
    	pseudoMotorRolesPanel.removeAll();
    	motorRolesPanel.removeAll();
		
    	if(pmClass != null)
    	{
			pseudoMotorNames = new JTextField[pmClass.getPseudoMotorRoles().size()];
			motorNames = new JComboBox[pmClass.getMotorRoles().size()];
			
			GridBagConstraints gbc = new GridBagConstraints();
			gbc.insets = new Insets(2,2,2,2);
			gbc.fill = GridBagConstraints.HORIZONTAL;
			int i = 0;
			for(String pmRoles : pmClass.getPseudoMotorRoles())
			{
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 0.0;
				gbc.gridx = 0;
				gbc.gridy = i;
				JLabel pmRole = new JLabel(pmRoles);
				pmRole.setToolTipText("The role of the pseudo motor in the pseudo motor system");
				pseudoMotorRolesPanel.add(pmRole, gbc);
				
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 1.0;
				gbc.gridx = 1;
				pseudoMotorNames[i] = new JTextField();
				pseudoMotorNames[i].setToolTipText("The name of the pseudo motor which will have the corresponding role in the pseudo motor system");
				pseudoMotorRolesPanel.add(pseudoMotorNames[i], gbc);
				i++;
			}
			
			int j = 0;
			for(String motorRoles : pmClass.getMotorRoles())
			{
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 0.0;
				gbc.gridx = 0;
				gbc.gridy = j;
				JLabel motorRole = new JLabel(motorRoles);
				motorRole.setToolTipText("The role of the motor in the pseudo motor system");
				motorRolesPanel.add(motorRole, gbc);
				
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 1.0;
				gbc.gridx = 1;
				motorNames[j] = new JComboBox(devicePool.getMotors().toArray());
				motorNames[j].setToolTipText("The motor which will have the corresponding role in the pseudo motor system");
				motorRolesPanel.add(motorNames[j], gbc);
				
				j++;
			}
    	}
		pseudoMotorRolesPanel.revalidate();
		motorRolesPanel.revalidate();
	}
	

	protected void updateIORegisterData(IORegisterClass ioClass)
	{
		ioRegisterValuesPanel.removeAll();
		
		if(ioClass != null)
		{

            int nb_predefined_values = ioClass.getNbPredefinedValues();           
            Vector<Long> predefined_values = ioClass.getPredefinedValues();
            Vector<String> predefined_values_desc = ioClass.getPredefinedValuesDesc();

			predefinedValuesDesc = new JLabel[nb_predefined_values];
            predefinedValues     = new JTextField[nb_predefined_values];

			GridBagConstraints gbc = new GridBagConstraints();
			gbc.insets = new Insets(2,2,2,2);
			gbc.fill = GridBagConstraints.HORIZONTAL;
			
			 if(nb_predefined_values == 0){
				JLabel nbPredefinedValuesLabel = new JLabel("Not IORegister predifined values");
				nbPredefinedValuesLabel.setHorizontalAlignment(JLabel.RIGHT);
				ioRegisterValuesPanel.add(nbPredefinedValuesLabel,gbc);
			 }

            for(int i = 0; i < nb_predefined_values; i++){
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 0.0;
				gbc.gridx = 0;
				gbc.gridy = i;
                String s1 = predefined_values_desc.get(i);
                predefinedValuesDesc[i] = new JLabel(s1);
				predefinedValuesDesc[i].setToolTipText("Describes the meaning of this value for the register");
				ioRegisterValuesPanel.add(predefinedValuesDesc[i], gbc);
				
				gbc.anchor = GridBagConstraints.EAST;
				gbc.weightx = 1.0;
				gbc.gridx = 1;
                long pv = predefined_values.get(i);
				String s2 = " " + pv;
				predefinedValues[i] = new JTextField(s2);
				predefinedValues[i].setEditable(false);
				predefinedValues[i].setToolTipText("Value of the register");
				ioRegisterValuesPanel.add(predefinedValues[i], gbc);
			}
			

		}

		ioRegisterValuesPanel.revalidate();	
	}
	


	protected void refreshPressed() 
	{
		devicePool.setControllerClasses(DevicePoolUtils.getInstance().askForDevicePoolControllerClasses(devicePool));
	}

	protected void closeAndExit()
	{
		dispose();
	}
	
	protected void hideAndExit()
	{
		ctrlClass = null;
		for(Component c : getComponents())
		{
			if(c instanceof JTextField)
			{
				((JTextField)c).setText(null);
			}
			else if(c instanceof JComboBox)
			{
				((JComboBox)c).setSelectedIndex(0);
			}
		}
		devicePool.removeControllerClassListListener(this);
		setVisible(false);
	}
	
	protected void exitPressed(ActionEvent e)
	{
		closeAndExit();
	}
	
	protected void createPressed(ActionEvent e)
	{
		ControllerType ctrlType = (ControllerType) typeCombo.getSelectedItem(); 
		String ctrlTypeStr = ctrlType.toString();
		
		if(ctrlTypeStr == null)
		{
			JOptionPane.showMessageDialog(this, "Invalid Type!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}
		
		String fileName = (String) ctrlFileNameComboBox.getSelectedItem();
		
		if(fileName == null || fileName.length() == 0)
		{
			JOptionPane.showMessageDialog(this, "Invalid Library!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}
		
		String className = (String) ctrlClassComboBox.getSelectedItem();
		
		if(className == null || className.length() == 0)
		{
			JOptionPane.showMessageDialog(this, "Invalid class name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}		

		ControllerClass ctrlClass = devicePool.getControllerClassByName(fileName, className);
		
		assert(ctrlClass != null);
		
		String instance = instanceText.getText();
		
		if(instance == null || instance.length() == 0)
		{
			JOptionPane.showMessageDialog(this, "Invalid instance!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
			return;
		}		
		
		List<String> tmpPseudoMotorNames = new ArrayList<String>();
		List<String> tmpMotorNames = new ArrayList<String>();
		List<String> tmpPseudoCounterNames = new ArrayList<String>();
		List<String> tmpCounterNames = new ArrayList<String>();
		
		// Check if it is a pseudo motor controller
		if(ctrlType == ControllerType.PseudoMotor)
		{
			for(JTextField pseudoName : pseudoMotorNames)
			{
				String pmName = pseudoName.getText();
				if(pmName == null || pmName.length() == 0)
				{
					JOptionPane.showMessageDialog(null, "Invalid Pseudo motor Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
					return;
				}
				
				if(tmpPseudoMotorNames.contains(pmName))
				{
					JOptionPane.showMessageDialog(this, "The pseudo motor " + pmName + " has been assigned to more than one role", "Duplicated Pseudo Motor Names", JOptionPane.WARNING_MESSAGE);
					return;
				}
				tmpPseudoMotorNames.add(pmName);
			}

			for(JComboBox motorName: motorNames)
			{
				if(motorName.getSelectedIndex() == -1)
				{
					JOptionPane.showMessageDialog(null, "Invalid motor Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
					return;
				}
				String motorNameStr = motorName.getSelectedItem().toString();
				if(motorNameStr == null || motorNameStr.length() == 0)
				{
					JOptionPane.showMessageDialog(null, "Invalid motor Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
					return;
				}
				
				if(tmpMotorNames.contains(motorNameStr))
				{
					JOptionPane.showMessageDialog(this, "The motor " + motorNameStr + " has been assigned to more than one role", "Duplicated Motor Names", JOptionPane.WARNING_MESSAGE);
					return;
				}
				tmpMotorNames.add(motorNameStr);
			}
		}
		
		// Check if it is a pseudo counter controller
		else if(ctrlType == ControllerType.PseudoCounter)
		{
			for(JTextField pseudoName : pseudoCounterNames)
			{
				String pcName = pseudoName.getText();
				if(pcName == null || pcName.length() == 0)
				{
					JOptionPane.showMessageDialog(null, "Invalid Pseudo counter Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
					return;
				}
				
				if(tmpPseudoCounterNames.contains(pcName))
				{
					JOptionPane.showMessageDialog(this, "The pseudo counter " + pcName + " has been assigned to more than one role", "Duplicated Pseudo Counter Names", JOptionPane.WARNING_MESSAGE);
					return;
				}
				tmpPseudoCounterNames.add(pcName);
			}

			for(JComboBox counterName: counterNames)
			{
				if(counterName.getSelectedIndex() == -1)
				{
					JOptionPane.showMessageDialog(null, "Invalid counter Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
					return;
				}
				String counterNameStr = counterName.getSelectedItem().toString();
				if(counterNameStr == null || counterNameStr.length() == 0)
				{
					JOptionPane.showMessageDialog(null, "Invalid counter Name!", "Invalid Parameter", JOptionPane.WARNING_MESSAGE);
					return;
				}
				
				if(tmpCounterNames.contains(counterNameStr))
				{
					JOptionPane.showMessageDialog(this, "The counter " + counterNameStr + " has been assigned to more than one role", "Duplicated Counter Names", JOptionPane.WARNING_MESSAGE);
					return;
				}
				tmpCounterNames.add(counterNameStr);
			}
		}
		
		// Check properties
		List<PropertyInfo> propInfo = propertiesEditor.getData();
		List<Object> propNewValue = propertiesEditor.getNewValueData();
		List<Object> classPropValues = propertiesEditor.getClassPropertyValues();
		
		ArrayList<PropertyParam> propParams = new ArrayList<PropertyParam>(propNewValue.size());
		
		for(int index = 0; index < propNewValue.size(); index++)
		{
			PropertyInfo prop = propInfo.get(index);
			String propName = prop.getName();
			Object propValue = propNewValue.get(index);
			Object classPropValue = classPropValues.get(index);
			PropertyType type = prop.getType();
			
			if(!prop.hasDefaultValue())
			{
				if(classPropValue == null)
				{
					if(propValue == null)
					{
						JOptionPane.showMessageDialog(this, "The property " + propName + " must have an assigned value", "Missing Property Value", JOptionPane.WARNING_MESSAGE);
						return;
					}
				}
			}
			
			if(propNewValue.get(index) != null)
			{
				String propValueStr = DevicePoolUtils.toPropertyValueString(type, propValue);
				
				if(type.isSimpleType())
				{
					if(type == PropertyType.DevBoolean)
					{
						if(!propValueStr.equalsIgnoreCase("true") && !propValueStr.equalsIgnoreCase("false"))
						{
							JOptionPane.showMessageDialog(this, "The value of property " + propName + " is not valid. It must be 'true' or 'false'", "Property value type mismatch", JOptionPane.WARNING_MESSAGE);
							return;						
						}
					}
					else if(type == PropertyType.DevLong)
					{
						try
						{
							Integer.parseInt(propValueStr);
						}
						catch(NumberFormatException exception)
						{
							JOptionPane.showMessageDialog(this, "The value of property " + propName + " is not valid. It must be a valid integer", "Property value type mismatch", JOptionPane.WARNING_MESSAGE);
							return;						
						}
					}
					else if(type == PropertyType.DevDouble)
					{
						try
						{
							Double.parseDouble(propValueStr);
						}
						catch(NumberFormatException exception)
						{
							JOptionPane.showMessageDialog(this, "The value of property " + propName + " is not valid. It must be a valid doubles", "Property value type mismatch", JOptionPane.WARNING_MESSAGE);
							return;						
						}
					}
				}
				else 
				{
					String[] elems = propValueStr.split("\n");
					if(type == PropertyType.DevVarBooleanArray)
					{
						for(String elem : elems)
						{
							if(!elem.equalsIgnoreCase("true") && propValueStr.equalsIgnoreCase("false"))
							{
								JOptionPane.showMessageDialog(this, "The value of property " + propName + " is not valid. It must be a list of 'true' or 'false'", "Property value type mismatch", JOptionPane.WARNING_MESSAGE);
								return;						
							}
							Boolean.parseBoolean(elem);
						}
					}
					else if(type == PropertyType.DevVarLongArray)
					{
						for(String elem : elems)
						{
							try
							{
								Integer.parseInt(elem);
							}
							catch(NumberFormatException exception)
							{
								JOptionPane.showMessageDialog(this, "The value of property " + propName + " is not valid. It must be a list of integers", "Property value type mismatch", JOptionPane.WARNING_MESSAGE);
								return;						
							}
						}
					}
					else if(type == PropertyType.DevVarDoubleArray)
					{
						for(String elem : elems)
						{						
							try
							{
								Float.parseFloat(elem);
							}
							catch(NumberFormatException exception)
							{
								JOptionPane.showMessageDialog(this, "The value of property " + propName + " is not valid. It must be a list of doubles", "Property value type mismatch", JOptionPane.WARNING_MESSAGE);
								return;						
							}
						}
					}
				}
				propParams.add(new PropertyParam(propName,propValueStr));
			}
		}
		
		int paramCount = 4 + 2*propParams.size();
		
		if(ctrlType == ControllerType.PseudoMotor)
			paramCount += tmpMotorNames.size() + tmpPseudoMotorNames.size();
		else if(ctrlType == ControllerType.PseudoCounter)
			paramCount += tmpCounterNames.size() + tmpPseudoCounterNames.size();
		
		String[] params = new String [paramCount];
		
		try
		{
			params[0] = ctrlTypeStr;
			params[1] = fileName;
			params[2] = className;
			params[3] = instance;
			
			int i = 4;
			
			if(ctrlType == ControllerType.PseudoMotor)
			{
				for(String mName : tmpMotorNames)
					params[i++] = mName;
				for(String pmName : tmpPseudoMotorNames)
					params[i++] = pmName;
			}
			else if(ctrlType == ControllerType.PseudoCounter)
			{
				for(String cName : tmpCounterNames)
					params[i++] = cName;
				for(String pcName : tmpPseudoCounterNames)
					params[i++] = pcName;
			}	
			
			for(PropertyParam propParam : propParams)
			{
				params[i++] = propParam.name;
				params[i++] = propParam.value;
			}
			
			DeviceData args = new DeviceData();
			args.insert(params);
			devicePool.getDevice().executeCommand(DevicePoolUtils.POOL_CMD_CREATE_CTRL,
					args);
			
			JOptionPane.showMessageDialog(this,
					"Controller " + instance + " sucessfully created","Sucess!", JOptionPane.INFORMATION_MESSAGE);

		}
		catch (DevFailed devFailed)
		{
			StringBuffer buff = new StringBuffer("Reason:\n");
			
			for(DevError elem : devFailed.errors)
			{
				buff.append( elem.desc + "\n");
			}
			
			JOptionPane.showMessageDialog(this, 
					buff.toString(),
					"Error trying to create a new controller", 
					JOptionPane.ERROR_MESSAGE);
		}
	}

	public void stringSpectrumChange(StringSpectrumEvent e) 
	{
		updateFileNameCombo();
	}

	public void stateChange(AttributeStateEvent e) {}

	public void errorChange(ErrorEvent evt) {}
	
	public static void main(String[] args) 
	{
//		Machine m = new Machine("controls01","10000");
//		DevicePool p = new DevicePool(m, "TestPool");
//		ArrayList<ControllerClass> l = new ArrayList<ControllerClass>();
//		
//		//1
//		ControllerClass c = new ControllerClass("Type: Motor - Class: MyCtrl - File: /home/tiago/MyCtrls.py");
//		c.setDescription("Some silly motor class");
//		
//		PropertyInfo prop = new PropertyInfo("host");
//		prop.setDescription("The host name of the Icepap controller");
//		prop.setType(PropertyType.DevString);
//		prop.setDefaultValue("icepap01");
//		c.addPropertyInfo(prop);
//		
//		prop = new PropertyInfo("l1");
//		prop.setDescription("The TCP port of the Icepap controller");
//		prop.setType(PropertyType.DevLong);
//		c.addPropertyInfo(prop);
//
//		prop = new PropertyInfo("l2");
//		prop.setDescription("The TCP port of the Icepap controller");
//		prop.setType(PropertyType.DevLong);
//		prop.setDefaultValue(10);
//		c.addPropertyInfo(prop);
//		
//		prop = new PropertyInfo("b1");
//		prop.setDescription("Something");
//		prop.setType(PropertyType.DevBoolean);
//		//prop.setDefaultValue();
//		c.addPropertyInfo(prop);
//
//		prop = new PropertyInfo("b2");
//		prop.setDescription("Something 2");
//		prop.setType(PropertyType.DevBoolean);
//		prop.setDefaultValue(true);
//		c.addPropertyInfo(prop);
//
//		
//		prop = new PropertyInfo("AlternatePorts");
//		prop.setDescription("Alternate TCP connection ports for the Icepap controller");
//		prop.setType(PropertyType.DevVarStringArray);
//		//prop.setDefaultValue("2345\n3345\n4345");
//		c.addPropertyInfo(prop);
//		
//		l.add(c);
//
//		//2
//		c = new ControllerClass("Type: CounterTimer - Class: CTCtrl - File: /home/tiago/CTCtrls.py");
//		c.setDescription("Some silly Counter timer class.\n" +
//				"I am going to try to make this a very very long description but I don't know if I am capable.\n" +
//				"Well... looks like I am. Sorry to bother you!");
//		
//		prop = new PropertyInfo("AlternatePorts");
//		prop.setDescription("Silly Stuff");
//		prop.setType(PropertyType.DevVarStringArray);
//		prop.setDefaultValue("str 1\nstr 2\nstr 3");
//		c.addPropertyInfo(prop);
//
//		prop = new PropertyInfo("mode");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevLong);
//		prop.setDefaultValue(1);
//		c.addPropertyInfo(prop);
//		c.addDbClassProperty("mode",2);
//		
//
//		prop = new PropertyInfo("tf");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevBoolean);
//		prop.setDefaultValue(true);
//		c.addPropertyInfo(prop);
//
//		prop = new PropertyInfo("tf2");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevLong);
//		prop.setDefaultValue(1);
//		c.addPropertyInfo(prop);
//		
//		prop = new PropertyInfo("tf3");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevString);
//		prop.setDefaultValue("shit");
//		c.addPropertyInfo(prop);
//
//		prop = new PropertyInfo("utf4");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevBoolean);
//		c.addPropertyInfo(prop);
//		
//		l.add(c);
//		
//		//3
//		c = new PseudoMotorClass("Type: PseudoMotor - Class: Slit - File: /home/tiago/Slit.py");
//		c.setDescription("A slit pseudo motor controller\n");
//		Vector<String> pseudo_motor_roles = new Vector<String>(2);
//		pseudo_motor_roles.add("Gap");
//		pseudo_motor_roles.add("Offset");
//		((PseudoMotorClass)c).setPseudoMotorRoles(pseudo_motor_roles);
//		Vector<String> motor_roles = new Vector<String>(2);
//		motor_roles.add("sl2t");
//		motor_roles.add("sl2b");
//		((PseudoMotorClass)c).setMotorRoles(motor_roles);
//		
//		prop = new PropertyInfo("mode");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevString);
//		prop.setDefaultValue("fast");
//		c.addPropertyInfo(prop);
//		c.addDbClassProperty("mode", "ultra fast");
//		
//		l.add(c);		
//
//		//4
//		c = new PseudoMotorClass("Type: PseudoMotor - Class: TableHeight - File: /home/tiago/Slit.py");
//		c.setDescription("A table height pseudo motor controller\n");
//		pseudo_motor_roles = new Vector<String>(1);
//		pseudo_motor_roles.add("Height");
//		((PseudoMotorClass)c).setPseudoMotorRoles(pseudo_motor_roles);
//		motor_roles = new Vector<String>(3);
//		motor_roles.add("tl1");
//		motor_roles.add("tl2");
//		motor_roles.add("tl3");
//		((PseudoMotorClass)c).setMotorRoles(motor_roles);
//		
//		prop = new PropertyInfo("mode");
//		prop.setDescription("The counter timer controller mode\nMode can be slow, fast or ultra fast");
//		prop.setType(PropertyType.DevString);
//		prop.setDefaultValue("fast");
//		c.addPropertyInfo(prop);
//		c.addDbClassProperty("mode", "ultra fast");
//		
//		l.add(c);		
//		
//		// 5
//		c = new PseudoCounterClass("Type: PseudoCounter - Class: SuperCurrent - File: /home/tiago/Current.py");
//		c.setDescription("A current pseudo counter (I/I0) and (I0/I)\n");
//		Vector<String> counter_roles = new Vector<String>(2);
//		counter_roles.add("I");
//		counter_roles.add("I0");
//		Vector<String> pseudo_counter_roles = new Vector<String>(2);
//		pseudo_counter_roles.add("Normalized I");
//		pseudo_counter_roles.add("Inv. Normalized I");
//		
//		((PseudoCounterClass)c).setCounterRoles(counter_roles);
//		((PseudoCounterClass)c).setPseudoCounterRoles(pseudo_counter_roles);
//		l.add(c);			
//		
//		p.setControllerClasses(l);
//		
//		AddControllerDialog d = new AddControllerDialog(p,null);
//		d.setDefaultCloseOperation(DISPOSE_ON_CLOSE);
//		d.setVisible(true);
	}
	
	protected class PropertyParam
	{
		public PropertyParam(String name, String value)
		{
			this.name = name;
			this.value = value;
		}
		public String name;
		public String value;
	}
}
