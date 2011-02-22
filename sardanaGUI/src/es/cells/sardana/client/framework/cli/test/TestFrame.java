package es.cells.sardana.client.framework.cli.test;

/**
 * <p>Title: ExecCommander</p>
 * <p>Description: This project serves as a launchpad for development and tests of a component to make use of process execution easier</p>
 * <p>Copyright: Copyright (c) 2003</p>
 * <p>Company: N/A</p>
 * @author Doron Barak
 * @version 1.0
 */

import java.awt.AWTEvent;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.io.IOException;

import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.UIManager;
import javax.swing.border.BevelBorder;
import javax.swing.border.TitledBorder;

import es.cells.sardana.client.framework.cli.ExecHelper;
import es.cells.sardana.client.framework.cli.ExecProcessor;

public class TestFrame extends JFrame implements ExecProcessor 
{
	private JPanel contentPane;
	private JMenuBar jMenuBar1 = new JMenuBar();
	private JMenu jMenuFile = new JMenu();
	private JMenuItem jMenuFileExit = new JMenuItem();
	private JLabel statusBar = new JLabel();
	private BorderLayout borderLayout1 = new BorderLayout();
	private JTextField jTextField1 = new JTextField();
	private JMenuItem jMenuItem1 = new JMenuItem();
	private JTextArea jTextArea1 = new JTextArea();
	private JScrollPane jScrollPane1 = new JScrollPane();
	private ExecHelper exh;
	//Construct the frame
	public TestFrame() {
		enableEvents(AWTEvent.WINDOW_EVENT_MASK);
		try {
			jbInit();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	//Component initialization
	private void jbInit() throws Exception {
		contentPane = (JPanel)this.getContentPane();
		contentPane.setLayout(borderLayout1);
		this.setSize(new Dimension(400, 300));
		this.setTitle("Exec Test Frame");
		statusBar.setBorder(BorderFactory.createEtchedBorder());
		statusBar.setDebugGraphicsOptions(0);
		statusBar.setDoubleBuffered(true);
		statusBar.setOpaque(false);
		statusBar.setVerifyInputWhenFocusTarget(true);
		statusBar.setText(" Ready...");
		jMenuFile.setText("File");
		jMenuFileExit.setText("Exit");
		jMenuFileExit.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				jMenuFileExitActionPerformed(e);
			}
		});
		jTextField1.setBackground(UIManager.getColor("control"));
		jTextField1.setBorder(BorderFactory.createCompoundBorder(new TitledBorder(BorderFactory.createBevelBorder(BevelBorder.LOWERED, Color.white, Color.white, new Color(103, 101, 98), new Color(148, 145, 140)), "Input"), BorderFactory.createEmptyBorder( -2, 0, -2, 0)));
		jTextField1.setDoubleBuffered(true);
		jTextField1.setOpaque(false);
		jTextField1.setCaretColor(Color.black);
		jTextField1.setCaretPosition(0);
		jTextField1.setText("");
		jTextField1.addActionListener(new java.awt.event.ActionListener() {
			public void actionPerformed(ActionEvent e) {
				inputActionPerformed(e);
			}
		});
		contentPane.setBackground(UIManager.getColor("control"));
		contentPane.setDoubleBuffered(true);
		contentPane.setOpaque(true);
		jMenuItem1.setText("Run Command.exe");
		jMenuItem1.addActionListener(new java.awt.event.ActionListener() {
			public void actionPerformed(ActionEvent e) {
				runCommandActionPerformed(e);
			}
		});
		jTextArea1.setBackground(UIManager.getColor("control"));
		jScrollPane1.getViewport().setBackground(UIManager.getColor("control"));
		jScrollPane1.setAutoscrolls(true);
		jScrollPane1.setBorder(new TitledBorder(BorderFactory.createBevelBorder(BevelBorder.LOWERED, Color.white, Color.white, new Color(103, 101, 98), new Color(148, 145, 140)), "Output"));
		jScrollPane1.setOpaque(false);
		jTextArea1.setDoubleBuffered(true);
		jTextArea1.setOpaque(false);
		jTextArea1.setText("");
		jTextArea1.setColumns(80);
		jTextArea1.setRows(25);
		jTextArea1.setWrapStyleWord(true);
		jMenuFile.add(jMenuItem1);
		jMenuFile.add(jMenuFileExit);
		jMenuBar1.add(jMenuFile);
		setJMenuBar(jMenuBar1);
		contentPane.add(statusBar, BorderLayout.SOUTH);
		contentPane.add(jTextField1, BorderLayout.NORTH);
		contentPane.add(jScrollPane1, BorderLayout.CENTER);
		jScrollPane1.getViewport().add(jTextArea1, null);
	}

	private void updateTextArea(JTextArea textArea, String line) {
		textArea.append(line);
		textArea.setSelectionStart(textArea.getText().length());
		textArea.setSelectionEnd(textArea.getText().length());
	}

	//File | Exit action performed
	public void jMenuFileExitActionPerformed(ActionEvent e) {
		System.exit(0);
	}

	//Overridden so we can exit when window is closed
	protected void processWindowEvent(WindowEvent e) {
		super.processWindowEvent(e);
		if (e.getID() == WindowEvent.WINDOW_CLOSING) {
			jMenuFileExitActionPerformed(null);
		}
	}

	public void processNewInput(String input) {
		updateTextArea(jTextArea1, input);
	}

	public void processNewError(String error) {
		updateTextArea(jTextArea1, error);
	}

	public void processEnded(int exitValue) {
		exh = null;
		statusBar.setText("Command.exe ended..");
		JOptionPane.showMessageDialog(this, "Exit value for Command.exe was [" + exitValue + "]", "Command.exe is done!", JOptionPane.INFORMATION_MESSAGE);
		try {
			Thread.sleep(1000);
		} catch (InterruptedException ex) {
		}
		jTextArea1.setText(null);
		statusBar.setText("Ready..");
	}

	void runCommandActionPerformed(ActionEvent e) {
		if (exh == null) {
			try {
				exh = ExecHelper.exec(this, "C:\\Python24\\python.exe");
				statusBar.setText("Command.exe running..");
			} catch (IOException ex) {
				processNewError(ex.getMessage());
			}
		}
	}

	void inputActionPerformed(ActionEvent e) {
		if (exh != null) {
			exh.println(jTextField1.getText());
			jTextField1.setText(null);
		}
	}
}