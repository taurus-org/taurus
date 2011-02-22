package es.cells.sardana.client.framework.cli.test;

import java.awt.Dimension;
import java.awt.Toolkit;

import javax.swing.UIManager;

public class TestApplication {
	private boolean packFrame = false;
	//Construct the application
	public TestApplication() {
		TestFrame frame = new TestFrame();
		//Validate frames that have preset sizes
		//Pack frames that have useful preferred size info, e.g. from their layout
		if (packFrame) {
			frame.pack();
		} else {
			frame.validate();
		}
		//Center the window
		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		Dimension frameSize = frame.getSize();
		if (frameSize.height > screenSize.height) {
			frameSize.height = screenSize.height;
		}
		if (frameSize.width > screenSize.width) {
			frameSize.width = screenSize.width;
		}
		frame.setLocation((screenSize.width - frameSize.width) / 2, (screenSize.height - frameSize.height) / 2);
		frame.setVisible(true);
	}

	//Main method
	public static void main(String[] args) {
		try {
			UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		} catch (Exception e) {
			e.printStackTrace();
		}
		new TestApplication();
	}
}
