package es.cells.sardana.tests;

import fr.esrf.tangoatk.core.AttributeList;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ConnectionException;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.INumberScalar;
import fr.esrf.tangoatk.core.INumberScalarListener;
import fr.esrf.tangoatk.core.NumberScalarEvent;

public class PseudoMotorTest {

	
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		AttributeList lst = new AttributeList();
		
		try 
		{
			INumberScalar positionAttr = (INumberScalar)lst.add("pm/pseudolib.slit/tcgap/Position");
			//INumberScalar positionAttr = (INumberScalar)lst.add("motor/dummyctrl01/1/Position");
			positionAttr.addNumberScalarListener(new INumberScalarListener() 
			{

				public void numberScalarChange(NumberScalarEvent evt) 
				{
					System.out.println("received pos changed for " + evt.getSource() + " with value " + evt.getValue());
				}

				public void stateChange(AttributeStateEvent arg0) 
				{
				
					
				}

				public void errorChange(ErrorEvent arg0) 
				{
				
					
				}
				
			});
		} 
		catch (ConnectionException e) 
		{
			e.printStackTrace();
			System.exit(-1);
		}
		
	}

}
