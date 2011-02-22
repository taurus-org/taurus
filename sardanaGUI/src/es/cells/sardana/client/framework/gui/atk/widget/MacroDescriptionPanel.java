package es.cells.sardana.client.framework.gui.atk.widget;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;

import javax.swing.JTextArea;

import es.cells.sardana.client.framework.macroserver.Atribute;
import es.cells.sardana.client.framework.macroserver.AtributeRepeat;
import es.cells.sardana.client.framework.macroserver.MacroDescriptionModel;

public class MacroDescriptionPanel extends JTextArea{
	
	public static final String name = "Name: ";
	public static final String description = "Description: ";
	public static final String advice = "Advice: ";
	public static final String noOfArgs = "Number of arguments: ";
	public static final String noOfReturns = "Number of returns: ";
	public static final String args = "Arguments: ";
	public static final String argName = "name: ";
	public static final String argType = "type: ";
	public static final String argDescription = "description: ";
	public static final String argDefVal = "default value: ";
	
	MacroDescriptionModel model;
	
	public MacroDescriptionPanel()
	{
		super(100,40);
	}
	
	public void paintComponent(Graphics g)
	{
		super.paintComponent(g);
		
		if(model != null)
		{
			Font nameFont = new Font("Arial",Font.BOLD,12);
			Font valueFont = new Font("Arial",Font.PLAIN,12);
			Font argNameFont = new Font ("Arial", Font.BOLD,11);
			Font argValueFont = new Font ("Arial", Font.PLAIN,11);
			
			FontMetrics nameFontMetric = g.getFontMetrics(nameFont);
			FontMetrics valueFontMetric = g.getFontMetrics(valueFont);
			FontMetrics argNameFontMetric = g.getFontMetrics(argNameFont);
			FontMetrics argValueFontMetric = g.getFontMetrics(argValueFont);
			
			final int nameWidth = nameFontMetric.stringWidth(name);
			final int descriptionWidth = nameFontMetric.stringWidth(description);
			final int adviceWidth = nameFontMetric.stringWidth(advice);
			final int noOfArgsWidth = nameFontMetric.stringWidth(noOfArgs);
			final int argsWidth = nameFontMetric.stringWidth(args);
			final int argNameWidth = argNameFontMetric.stringWidth(argName);
			final int argTypeWidth = argNameFontMetric.stringWidth(argType);
			final int argDescriptionWidth = argNameFontMetric.stringWidth(argDescription);
			final int argDefValWidth = argNameFontMetric.stringWidth(argDefVal);
			
			final int nameHight = nameFontMetric.getAscent();
			final int argsHight = argNameFontMetric.getAscent();
			
			Dimension d = getSize();
			int xPos = 10;
			int yPos = 10;
		
			g.setFont(nameFont);
			g.drawString(name, xPos, yPos);                    	xPos += nameWidth; 
			g.setFont(valueFont);
			g.drawString(model.getName(), xPos, yPos);			xPos = 10;					yPos += nameHight;
			g.setFont(nameFont);
			g.drawString(description, xPos, yPos);              xPos += descriptionWidth;
			g.setFont(valueFont);
			String descriptionText = model.getDescription();
			int descriptionTextWidth = valueFontMetric.stringWidth(descriptionText); 
			int maxRowWidth = d.width - descriptionWidth - 15; 
			if( descriptionText.contains(new String("\n")))
			{
				String [] lines = descriptionText.split(new String("\n"));
				
				for (String string : lines) 
				{
					g.drawString(string, xPos, yPos);										yPos += nameHight;
				}
																xPos = 10;
			}
			else
			{
				g.drawString(descriptionText, xPos, yPos);		xPos = 10;					yPos += nameHight;
			}
			g.setFont(nameFont);
			g.drawString(advice, xPos, yPos);					xPos += adviceWidth;
			g.setFont(valueFont);
			g.drawString(model.getAdvices(), xPos, yPos);		xPos = 10;					yPos += nameHight;
			g.setFont(nameFont);
			g.drawString(noOfArgs, xPos, yPos);              	xPos += noOfArgsWidth;
			g.setFont(valueFont);
			g.drawString(model.getNrOfArgs(), xPos, yPos);		xPos = 10;					yPos += nameHight;
			g.setFont(nameFont);
			g.drawString(args, xPos, yPos);						xPos = 40;					yPos += (nameHight + argsHight);
			
			if(model.getAtributes() != null)
				for (Atribute atribute : model.getAtributes()) {
					g.setFont(argNameFont);									xPos = 40;
					g.drawString(argName, xPos, yPos);						xPos += argNameWidth;
					g.setFont(argValueFont);
					g.drawString(atribute.getName(), xPos, yPos);			xPos = 40;				yPos += argsHight;
					g.setFont(argNameFont);
					g.drawString(argType, xPos, yPos);						xPos += argTypeWidth;
					g.setFont(argValueFont);
					g.drawString(atribute.getType(), xPos, yPos);			xPos = 40;				yPos += argsHight;
					g.setFont(argNameFont);
					g.drawString(argDescription, xPos, yPos);				xPos += argDescriptionWidth;
					g.setFont(argValueFont);
					g.drawString(atribute.getDescription(), xPos, yPos);	xPos = 40;				yPos += argsHight;
					g.setFont(argNameFont);
					g.drawString(argDefVal, xPos, yPos);					xPos += argDefValWidth;
					g.setFont(argValueFont);
					g.drawString(atribute.getDefaultValue(), xPos, yPos);	xPos = 40;				yPos += argsHight;
					if(atribute instanceof AtributeRepeat)
					{
						for (Atribute atributeRepeat : ((AtributeRepeat)atribute).getAtributes()) {
							g.setFont(argNameFont);										xPos = 60;
							g.drawString(argName, xPos, yPos);							xPos += argNameWidth;
							g.setFont(argValueFont);
							g.drawString(atributeRepeat.getName(), xPos, yPos);			xPos = 60;				yPos += argsHight;
							g.setFont(argNameFont);
							g.drawString(argType, xPos, yPos);							xPos += argTypeWidth;
							g.setFont(argValueFont);
							g.drawString(atributeRepeat.getType(), xPos, yPos);			xPos = 60;				yPos += argsHight;
							g.setFont(argNameFont);
							g.drawString(argDescription, xPos, yPos);					xPos += argDescriptionWidth;
							g.setFont(argValueFont);
							g.drawString(atributeRepeat.getDescription(), xPos, yPos);	xPos = 60;				yPos += argsHight;
							g.setFont(argNameFont);
							g.drawString(argDefVal, xPos, yPos);						xPos += argDefValWidth;
							g.setFont(argValueFont);
							g.drawString(atributeRepeat.getDefaultValue(), xPos, yPos);	xPos = 60;				yPos += argsHight;
						}
					}
					yPos+=argsHight;
				}
		}	
	}

	public MacroDescriptionModel getModel() {
		return model;
	}

	public void setModel(MacroDescriptionModel model) {
		this.model = model;
		repaint();
	}

}

