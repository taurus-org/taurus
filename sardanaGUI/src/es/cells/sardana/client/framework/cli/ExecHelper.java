package es.cells.sardana.client.framework.cli;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;

public class ExecHelper implements Runnable {
	// Allocate 1K buffers for Input and Error Streams..
	private byte[] inBuffer = new byte[1024];
	private byte[] errBuffer = new byte[1024];
	// Declare internal variables we will need..
	private Process process;
	private InputStream pErrorStream;
	private InputStream pInputStream;
	private OutputStream pOutputStream;
	private PrintWriter outputWriter;
	private Thread processThread;
	private Thread inReadThread;
	private Thread errReadThread;
	private ExecProcessor handler;
	// Private constructor so that no one can create a new ExecHelper directly..
	private ExecHelper(ExecProcessor ep, Process p) {
		// Save variables..
		handler = ep;
		process = p;
		// Get the streams..
		pErrorStream = process.getErrorStream();
		pInputStream = process.getInputStream();
		pOutputStream = process.getOutputStream();
		// Create a PrintWriter on top of the output stream..
		outputWriter = new PrintWriter(pOutputStream, true);
		// Create the threads and start them..
		processThread = new Thread(this);
		inReadThread = new Thread(this);
		errReadThread = new Thread(this);
		// Start Threads..
		processThread.start();
		inReadThread.start();
		errReadThread.start();
	}

	private void processEnded(int exitValue) {
		// Handle process end..
		handler.processEnded(exitValue);
	}

	private void processNewInput(String input) {
		// Handle process new input..
		handler.processNewInput(input);
	}

	private void processNewError(String error) {
		// Handle process new error..
		handler.processNewError(error);
	}

	// Run the command and return the ExecHelper wrapper object..
	public static ExecHelper exec(ExecProcessor handler, String command) throws IOException {
		return new ExecHelper(handler, Runtime.getRuntime().exec(command));
	}

	// Print the output string through the print writer..
	public void print(String output) {
		outputWriter.print(output);
	}

	// Print the output string (and a CRLF pair) through the print writer..
	public void println(String output) {
		outputWriter.println(output);
	}

	public void run() {
		// Are we on the process Thread?
		if (processThread == Thread.currentThread()) {
			try {
				// This Thread just waits for the process to end and notifies the handler..
				processEnded(process.waitFor());
			} catch (InterruptedException ex) {
				ex.printStackTrace();
			}
			// Are we on the InputRead Thread?
		} else if (inReadThread == Thread.currentThread()) {
			try {
				// Read the InputStream in a loop until we find no more bytes to read..
				for (int i = 0; i > -1; i = pInputStream.read(inBuffer)) {
					// We have a new segment of input, so process it as a String..
					processNewInput(new String(inBuffer, 0, i));
				}
			} catch (IOException ex) {
				ex.printStackTrace();
			}
			// Are we on the ErrorRead Thread?
		} else if (errReadThread == Thread.currentThread()) {
			try {
				// Read the ErrorStream in a loop until we find no more bytes to read..
				for (int i = 0; i > -1; i = pErrorStream.read(errBuffer)) {
					// We have a new segment of error, so process it as a String..
					processNewError(new String(errBuffer, 0, i));
				}
			} catch (IOException ex) {
				ex.printStackTrace();
			}
		}
	}
}
