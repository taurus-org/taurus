package es.cells.sardana.client.framework.cli;

import java.awt.BorderLayout;
import java.io.IOException;
import java.io.InputStream;

import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.SwingUtilities;

public class IPythonCLI extends JFrame
{
	JTextArea area;

	public IPythonCLI()
	{
		super("IPythonCLI");
		
		initComponents();
	}
	
	protected void initComponents()
	{
		setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
		
		getContentPane().setLayout( new BorderLayout() );
		
		area = new JTextArea(25, 80);
		
		JScrollPane pane = new JScrollPane(area);
		
		getContentPane().add(pane, BorderLayout.CENTER);
		
		Runtime rt = Runtime.getRuntime();
		try
		{
			Process proc = rt.exec( new String [] {"C:\\Python24\\python.exe", "-h"});
		
			final InputStream inputStream = proc.getInputStream();
			
			
			
			SwingUtilities.invokeLater( new Runnable() {

				public void run()
				{
					byte[] readBuffer = new byte[256];
					try
					{
						while(inputStream.read(readBuffer) != -1)
						{
							
						}
					}
					catch (IOException e)
					{
						e.printStackTrace();
					}
				}
				
			});
		}
		catch (IOException e)
		{
			e.printStackTrace();
		}
		
		pack();
		setVisible(true);
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args)
	{
		new IPythonCLI();
	}

}
