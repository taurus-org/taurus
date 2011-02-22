package es.cells.tangoatk.widget.attribute;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.GradientPaint;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.geom.Line2D;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.BorderFactory;
import javax.swing.JComponent;
import javax.swing.border.BevelBorder;
import javax.swing.border.Border;

import com.braju.format.Format;

import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.AttributeInfoEx;
import fr.esrf.TangoDs.AttrManip;
import fr.esrf.tangoatk.core.AttributeStateEvent;
import fr.esrf.tangoatk.core.ErrorEvent;
import fr.esrf.tangoatk.core.IAttribute;
import fr.esrf.tangoatk.core.INumberSpectrum;
import fr.esrf.tangoatk.core.ISpectrumListener;
import fr.esrf.tangoatk.core.NumberSpectrumEvent;
import fr.esrf.tangoatk.widget.util.ATKConstant;
import fr.esrf.tangoatk.widget.util.ATKFormat;

public class NumberScalarBarViewer extends JComponent implements ISpectrumListener, PropertyChangeListener 
{
	protected static final int SPACING = 2;
	protected static final int H_ARROW_HEIGHT = 4;
	protected static final int V_ARROW_HEIGHT = 4;

	public enum Direction 
	{
		LeftToRight,
		RightToLeft,
		BottomToTop,
		TopToBottom
	}

	protected INumberSpectrum model;

	/** 
	 * The index in the number array for which this viewer is interested
	 */
	protected int modelIndex;

	protected AttributeInfoEx attrInfo;

	final static float dash1[] = {2.0f};
	final static BasicStroke dashed = new BasicStroke(1.0f, 
			BasicStroke.CAP_BUTT, 
			BasicStroke.JOIN_MITER, 
			10.0f, dash1, 0.0f);
	final static BasicStroke strong = new BasicStroke(3.0f);
	final static BasicStroke normal = new BasicStroke(1.0f);

	protected double
	interval,
	minValue,
	maxValue,
	minAlarm,
	maxAlarm,
	minWarning,
	maxWarning,
	value;

	/** For performance reasons the values are precalculated before rendering */
	protected String 
	minValueStr,
	maxValueStr,
	minAlarmStr,
	maxAlarmStr,
	minWarningStr,
	maxWarningStr,
	valueStr;

	protected boolean needsUpdate = true;
	protected boolean hasInvalidRange = false;

	protected boolean gradient = true;
	protected boolean drawText = true;

	protected Direction direction = Direction.LeftToRight; 

	protected Color alarmColor = Color.red;
	protected Color warningColor = ATKConstant.getColor4Quality(IAttribute.WARNING);
	protected Color validColor = ATKConstant.getColor4Quality(IAttribute.VALID);

	protected Color arrowColor = Color.black;
	protected Color valueColor = Color.black;

	protected String format = "";
	protected String userFormat = "";
	protected ATKFormat atkUserFormat;

	protected Border barBorder = null;

	protected Border needleBorder = BorderFactory.createBevelBorder(BevelBorder.RAISED);

	public NumberScalarBarViewer() 
	{
		super();
		setPreferredSize(new Dimension(180,300));
	}

	public boolean isGradient() {
		return gradient;
	}

	public void setGradient(boolean gradient) {
		this.gradient = gradient;
	}

	public Direction getDirection() {
		return direction;
	}

	public void setDirection(Direction direction) {
		this.direction = direction;
	}

	public boolean isDrawText() {
		return drawText;
	}

	public void setDrawText(boolean drawText) {
		this.drawText = drawText;
	}

	/**
	 * Overrides the format property of the attribute.
	 * @param format C like Format (ex: %5.2f) , null or "" to disable.
	 */
	public void setUserFormat(String format) 
	{
		if(format==null)
			userFormat = "";
		else
			userFormat = format;
	}

	/**
	 * Returns the user format.
	 * @return User format
	 * @see #setUserFormat
	 */
	public String getUserFormat() 
	{
		return userFormat;
	}

	/**
	 * Sets the ATK user format of this viewer.
	 * It allows more specific formating than String format.
	 * <pre>
	 * Ex of use:
	 *   time_format = new ATKFormat() {
	 *     public String format(Number n) {
	 *       int d = n.intValue() / 60;
	 *       Object[] o = {new Integer(d / 60), new Integer(d % 60)};
	 *       return Format.sprintf("%02dh %02dmn", o);
	 *     }
	 *   };
	 *   myViewer.setUserFormat(time_format);
	 * </pre>
	 * @param format ATKFormat object or null to disable.
	 */
	public void setUserFormat(ATKFormat format) 
	{
		atkUserFormat = format;
	}

	public Border getBarBorder() {
		return barBorder;
	}

	public void setBarBorder(Border barBorder) {
		this.barBorder = barBorder;
	}
	
	public void setModel(INumberSpectrum m, AttributeInfoEx attr)
	{
		setModel(m,0,attr);
	}

	public void setModel(INumberSpectrum m, int index, AttributeInfoEx attr)
	{
		if(index < 0)
			index = 0;
		
		modelIndex = index;
		
		if(model != null)
		{
			model.removeSpectrumListener(this);

			model = null;
			attrInfo = null;
		}

		if(m == null)
		{
			return;
		}

		model = m;
		attrInfo = attr;

		model.addSpectrumListener(this);

		needsUpdate = true;

		model.refresh();
	}

	public void spectrumChange(NumberSpectrumEvent evt)
	{
		value = evt.getValue()[modelIndex];
		valueStr = getDisplayString(value);

		if(needsUpdate)
			update();

		invalidate();
		repaint();
	}

	public void stateChange(AttributeStateEvent state) 
	{
		if (state.getState().equals(IAttribute.CHANGING)) 
			valueColor = arrowColor = ATKConstant.getColor4Quality(IAttribute.CHANGING);
		else
		{
			arrowColor = Color.black;
			if (state.getState().equals(IAttribute.ALARM))
				valueColor = alarmColor;
			else
				valueColor = ATKConstant.getColor4Quality(state.getState());
		}
		invalidate();
		repaint();		
	}

	public void errorChange(ErrorEvent arg0) 
	{

	}

	public void propertyChange(PropertyChangeEvent evt) 
	{
		attrInfo = null;

		update();
		invalidate();
		repaint();
	}

	protected void update()
	{
		try
		{
			if(attrInfo == null)
				attrInfo = model.getDevice().get_attribute_info_ex("Position");

			format = attrInfo.format;

			hasInvalidRange = false;

			try
			{
				minWarning = Double.parseDouble(attrInfo.alarms.min_warning);
				maxWarning = Double.parseDouble(attrInfo.alarms.max_warning);
				minValue = Double.parseDouble(attrInfo.min_value);
				maxValue = Double.parseDouble(attrInfo.max_value);
				minAlarm = Double.parseDouble(attrInfo.min_alarm);
				maxAlarm = Double.parseDouble(attrInfo.max_alarm);

			}
			catch(NumberFormatException e)
			{
				minWarning = Double.NaN;
				maxWarning = Double.NaN;
				hasInvalidRange |= true;
			}
			
			if(!hasInvalidRange)
				interval = maxValue - minValue;

		}
		catch (DevFailed e) 
		{
			e.printStackTrace();
		}

		minValueStr = "" + minValue;
		maxValueStr = "" + maxValue;
		minWarningStr = "" + minWarning;
		maxWarningStr = "" + maxWarning;
		minAlarmStr = "" + minAlarm;
		maxAlarmStr = "" + maxAlarm;

		needsUpdate = false;
	}

	private String getDisplayString(double dvalue) 
	{
		Double attDouble = new Double(dvalue);
		String dispStr;

		if (atkUserFormat != null) {
			dispStr = atkUserFormat.format(new Double(dvalue));
		} else {
			try {
				if (userFormat.length() > 0) {
					Object[] o = {attDouble};
					dispStr = Format.sprintf(userFormat, o);
				} else if (format.indexOf('%') == -1) {
					dispStr = AttrManip.format(format, dvalue);
				} else {
					Object[] o = {attDouble};
					dispStr = Format.sprintf(format, o);
				}
			} catch (Exception e) {
				return "Exception while formating";
			}
		}

		return dispStr;
	}	

	@Override
	protected void paintComponent(Graphics g) 
	{
		if (isOpaque()) { //paint background
			g.setColor(getBackground());
			g.fillRect(0, 0, getWidth(), getHeight());
		}

		//Insets insets = getInsets();
		if(hasInvalidRange)
			paintInvalidRangeComponent(g);
		else
		{
			paintValidRangeComponent(g);
		}
	}

	private void paintValidRangeComponent(Graphics g)
	{
		if(direction == Direction.LeftToRight ||
				direction == Direction.LeftToRight)
			paintValidRangeHorizontalComponent(g);
		else
			paintValidRangeVerticalComponent(g);
	}

	protected void paintBorder(Graphics g) 
	{
		Border border = getBorder();
		if (border != null) {
			border.paintBorder(this, g, 0, 0, getWidth(), getHeight());
		}
	}	

	private void paintValidRangeVerticalComponent(Graphics g)
	{
		Graphics2D g2d = (Graphics2D) g.create();

		g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

		Font valueFont = g2d.getFont().deriveFont(Font.BOLD,14);
		FontMetrics fontMetrics = g2d.getFontMetrics();
		FontMetrics valueFontMetrics = g2d.getFontMetrics(valueFont);

		String tmp = getDisplayString(-99999.99);
		int maxValueFontWidth = valueFontMetrics.stringWidth(tmp);
		int maxNormalFontWidth = fontMetrics.stringWidth(tmp);
		int normalFontHeight = fontMetrics.getHeight();

		final int w = getWidth();
		final int h = getHeight();

		final int hRectStart = maxValueFontWidth + SPACING + V_ARROW_HEIGHT;
		final int hRectEnd = w - maxNormalFontWidth + SPACING;
		final int vRectStart = normalFontHeight + SPACING;
		final int vRectEnd = h;

		final int rectWidth = hRectEnd - hRectStart;
		final int rectHeight = vRectEnd - vRectStart;

		final int minAlarmHeight = (int) Math.round(rectHeight*(minAlarm - minValue)/interval);
		final int minWarningHeight = (int) Math.round(rectHeight*(minWarning - minAlarm)/interval);
		final int safeHeight = (int) Math.round(rectHeight*(maxWarning - minWarning)/interval);
		final int halfSafeHeight = (int) Math.round(rectHeight*0.5*(maxWarning - minWarning)/interval);
		final int maxWarningHeight = (int) Math.round(rectHeight*(maxAlarm - maxWarning)/interval);
		final int maxAlarmHeight = (int) Math.round(rectHeight*(maxValue - maxAlarm)/interval);

		final int maxAlarmY = vRectStart + maxAlarmHeight;
		final int maxWarningY = maxAlarmY + maxWarningHeight;
		final int safeY = maxWarningY + safeHeight; 
		final int minWarningY = safeY + minWarningHeight;
		final int minAlarmY = minWarningY + minAlarmHeight;

		//top to bottom
		//final int minAlarmY = vRectStart + minAlarmHeight;
		//final int minWarningY = minAlarmY + minWarningHeight;
		//final int safeY = minWarningY + safeHeight;
		//final int maxWarningY = safeY + maxWarningHeight;
		//final int maxAlarmY = maxWarningY + maxAlarmHeight;

		//Draw rectangle
		if(gradient)
		{
			g2d.setPaint(new GradientPaint(hRectStart,vRectStart,alarmColor,hRectStart,maxAlarmY,alarmColor));
			g2d.fillRect(hRectStart, vRectStart, rectWidth, maxAlarmHeight);

			g2d.setPaint(new GradientPaint(hRectStart,maxAlarmY,alarmColor,hRectStart,maxWarningY,warningColor));
			g2d.fillRect(hRectStart, maxAlarmY, rectWidth, maxWarningHeight);

			g2d.setPaint(new GradientPaint(hRectStart,maxWarningY,warningColor,hRectStart,maxWarningY+halfSafeHeight,validColor));
			g2d.fillRect(hRectStart, maxWarningY, rectWidth, halfSafeHeight);

			g2d.setPaint(new GradientPaint(hRectStart,maxWarningY+safeHeight/2,validColor,hRectStart,safeY,warningColor));
			g2d.fillRect(hRectStart, maxWarningY+halfSafeHeight, rectWidth, halfSafeHeight);

			g2d.setPaint(new GradientPaint(hRectStart,safeY,warningColor,hRectStart,minWarningY,alarmColor));
			g2d.fillRect(hRectStart, safeY, rectWidth, minWarningHeight);

			g2d.setPaint(new GradientPaint(hRectStart,minWarningY,alarmColor,hRectStart,minAlarmY,alarmColor));
			g2d.fillRect(hRectStart, minWarningY, rectWidth, minAlarmHeight);
		}
		else
		{
			g2d.setPaint(alarmColor);
			g2d.fillRect(hRectStart, vRectStart, rectWidth, maxAlarmHeight);
			g2d.setPaint(warningColor);
			g2d.fillRect(hRectStart, maxAlarmY, rectWidth, maxWarningHeight);
			g2d.setPaint(validColor);
			g2d.fillRect(hRectStart, maxWarningY, rectWidth, safeHeight);
			g2d.setPaint(warningColor);
			g2d.fillRect(hRectStart, safeY, rectWidth, minWarningHeight);
			g2d.setPaint(alarmColor);
			g2d.fillRect(hRectStart, minWarningY, rectWidth, minAlarmHeight);
		}

		if(drawText)
		{
			//Draw Text
			g2d.setPaint(Color.black);
			g2d.drawString(maxValueStr, w - fontMetrics.stringWidth(maxValueStr) - 2, vRectStart-2);
			g2d.drawString(maxAlarmStr, w - fontMetrics.stringWidth(maxAlarmStr) - 2, maxAlarmY-2);
			g2d.drawString(maxWarningStr, w - fontMetrics.stringWidth(maxWarningStr) - 2, maxWarningY-2);
			g2d.drawString(minWarningStr, w - fontMetrics.stringWidth(minWarningStr) - 2, safeY-2);
			g2d.drawString(minAlarmStr, w - fontMetrics.stringWidth(minAlarmStr) - 2, minWarningY-2);
			g2d.drawString(minValueStr, w - fontMetrics.stringWidth(minValueStr) - 2, minAlarmY-2);

			//Draw Lines
			g2d.setPaint(Color.gray);
			g2d.setStroke(dashed);
			g2d.draw(new Line2D.Double(hRectStart, vRectStart, w, vRectStart));
			g2d.draw(new Line2D.Double(hRectStart, maxAlarmY, w, maxAlarmY));
			g2d.draw(new Line2D.Double(hRectStart, maxWarningY, w, maxWarningY));
			g2d.draw(new Line2D.Double(hRectStart, safeY, w, safeY));
			g2d.draw(new Line2D.Double(hRectStart, minWarningY, w, minWarningY));
			g2d.draw(new Line2D.Double(hRectStart, minAlarmY, w, minAlarmY));
		}

		if (barBorder != null)
			barBorder.paintBorder(this, g, hRectStart, vRectStart, rectWidth, rectHeight);

		//Draw Value pointer
		int valueCoord = vRectEnd - (int) Math.round(rectHeight*(value - minValue)/interval) ;
		/*
		g2d.setPaint(arrowColor);
		g2d.setStroke(normal);
		g2d.draw(new Line2D.Double(hRectStart, valueCoord, hRectEnd-1, valueCoord));

		g2d.draw(new Line2D.Double(hRectStart-4, valueCoord-4, hRectStart-4, valueCoord+4));
		g2d.draw(new Line2D.Double(hRectStart-3, valueCoord-3, hRectStart-3, valueCoord+3));
		g2d.draw(new Line2D.Double(hRectStart-2, valueCoord-3, hRectStart-2, valueCoord+2));
		g2d.draw(new Line2D.Double(hRectStart-1, valueCoord-1, hRectStart-1, valueCoord+1));
		 */
		g2d.setFont(valueFont);
		g2d.setPaint(valueColor);

		int valueY = Math.max(valueCoord+V_ARROW_HEIGHT/2, vRectStart+valueFontMetrics.getHeight());
		valueY = Math.min(valueY, vRectEnd);

		g2d.drawString(valueStr, hRectStart - H_ARROW_HEIGHT - SPACING - valueFontMetrics.stringWidth(valueStr), valueY);

		if(needleBorder != null)
			needleBorder.paintBorder(this, g, hRectStart, valueCoord-2, rectWidth, 4);

		g2d.dispose();
	}

	private void paintValidRangeHorizontalComponent(Graphics g)
	{
		Graphics2D g2d = (Graphics2D) g.create();

		g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

		FontMetrics fontMetrics = g2d.getFontMetrics();

		final int fontHeight = drawText ? fontMetrics.getHeight() : 0;

		final int vUpTextStart1 = drawText ? fontHeight : 0;
		final int vUpTextStart2 = drawText ? 2*vUpTextStart1 + SPACING : 0;
		final int vTopArrow = drawText ? vUpTextStart2 + SPACING : 0;
		final int vRectStart = vTopArrow + H_ARROW_HEIGHT;

		final int w = getWidth();
		final int h = getHeight();

		final int vDownTextStart = h;
		final int vArrowEnd = drawText ? vDownTextStart - fontHeight - SPACING : h;
		final int vRectEnd = vArrowEnd - H_ARROW_HEIGHT;

		final int minAlarmWidth = (int) Math.round(w*(minAlarm - minValue)/interval);
		final int minWarningWidth = (int) Math.round(w*(minWarning - minAlarm)/interval);
		final int safeWidth = (int) Math.round(w*(maxWarning - minWarning)/interval);
		final int halfSafeWidth = (int) Math.round(w*0.5*(maxWarning - minWarning)/interval);
		final int maxWarningWidth = (int) Math.round(w*(maxAlarm - maxWarning)/interval);
		final int maxAlarmWidth = (int) Math.round(w*(maxValue - maxAlarm)/interval);

		final int minAlarmX = minAlarmWidth;
		final int minWarningX = minAlarmX + minWarningWidth;
		final int safeX = minWarningX + safeWidth;
		final int maxWarningX = safeX + maxWarningWidth;
		final int maxAlarmX = maxWarningX + maxAlarmWidth;

		final int rectHeight = vRectEnd - vRectStart;

		//Draw rectangle
		if(gradient)
		{
			g2d.setPaint(new GradientPaint(0,vRectStart,alarmColor, minAlarmX,vRectStart,alarmColor));
			g2d.fillRect(0, vRectStart, minAlarmWidth, rectHeight);

			g2d.setPaint(new GradientPaint(minAlarmX,vRectStart,alarmColor,minWarningX,vRectStart,warningColor));
			g2d.fillRect(minAlarmX, vRectStart, minWarningWidth, rectHeight);

			g2d.setPaint(new GradientPaint(minWarningX,vRectStart,warningColor,minWarningX+halfSafeWidth,vRectStart,validColor));
			g2d.fillRect(minWarningX, vRectStart, halfSafeWidth, rectHeight);

			g2d.setPaint(new GradientPaint(minWarningX+halfSafeWidth,vRectStart,validColor,safeX,vRectStart,warningColor));
			g2d.fillRect(minWarningX+halfSafeWidth, vRectStart, halfSafeWidth, rectHeight);

			g2d.setPaint(new GradientPaint(safeX,vRectStart,warningColor,maxWarningX,vRectStart,alarmColor));
			g2d.fillRect(safeX, vRectStart, maxWarningWidth, rectHeight);

			g2d.setPaint(new GradientPaint(maxWarningX,vRectStart,alarmColor,maxAlarmX,vRectStart,alarmColor));
			g2d.fillRect(maxWarningX, vRectStart, maxAlarmWidth, rectHeight);
		}
		else
		{
			g2d.setPaint(alarmColor);
			g2d.fillRect(0, vRectStart, minAlarmWidth, rectHeight);
			g2d.setPaint(warningColor);
			g2d.fillRect(minAlarmX, vRectStart, minWarningWidth, rectHeight);
			g2d.setPaint(validColor);
			g2d.fillRect(minWarningX, vRectStart, safeWidth, rectHeight);
			g2d.setPaint(warningColor);
			g2d.fillRect(safeX, vRectStart, maxWarningWidth, rectHeight);
			g2d.setPaint(alarmColor);
			g2d.fillRect(maxWarningX, vRectStart, maxAlarmWidth, rectHeight);
		}

		if(drawText)
		{
			//Draw Text
			g2d.setPaint(Color.black);
			g2d.drawString(minValueStr, 2, vDownTextStart);
			g2d.drawString(minAlarmStr, minAlarmX-fontMetrics.stringWidth(minAlarmStr)/2, vUpTextStart2);
			g2d.drawString(minWarningStr, minWarningX-fontMetrics.stringWidth(minWarningStr)/2, vUpTextStart1);
			g2d.drawString(maxWarningStr, safeX-fontMetrics.stringWidth(maxWarningStr)/2, vUpTextStart2);
			g2d.drawString(maxAlarmStr, maxWarningX-fontMetrics.stringWidth(maxAlarmStr)/2, vUpTextStart1);
			g2d.drawString(maxValueStr, maxAlarmX-2-fontMetrics.stringWidth(maxValueStr), vDownTextStart);

			//Draw Lines
			g2d.setPaint(Color.gray);
			g2d.setStroke(dashed);
			g2d.draw(new Line2D.Double(0, vRectStart, 0, vDownTextStart));
			g2d.draw(new Line2D.Double(minAlarmX, vUpTextStart2+2, minAlarmX, vRectEnd));
			g2d.draw(new Line2D.Double(minWarningX, vUpTextStart1+2, minWarningX, vRectEnd));
			g2d.draw(new Line2D.Double(safeX, vUpTextStart2+2, safeX, vRectEnd));
			g2d.draw(new Line2D.Double(maxWarningX, vUpTextStart1+2, maxWarningX, vRectEnd));
			g2d.draw(new Line2D.Double(maxAlarmX-1, vRectStart, maxAlarmX-1, vDownTextStart));
		}

		if (barBorder != null)
			barBorder.paintBorder(this, g, 0, vRectStart, w, rectHeight);

		//Draw Value pointer
		int valueCoord = (int) Math.round(w*(value - minValue)/interval) ;
		/*
		g2d.setPaint(arrowColor);
		g2d.setStroke(normal);
		g2d.draw(new Line2D.Double(valueCoord, vRectStart, valueCoord, vRectEnd));

		g2d.setStroke(normal);
		g2d.draw(new Line2D.Double(valueCoord-4, vRectStart-4, valueCoord+4, vRectStart-4));
		g2d.draw(new Line2D.Double(valueCoord-3, vRectStart-3, valueCoord+3, vRectStart-3));
		g2d.draw(new Line2D.Double(valueCoord-2, vRectStart-2, valueCoord+2, vRectStart-2));
		g2d.draw(new Line2D.Double(valueCoord-1, vRectStart-1, valueCoord+1, vRectStart-1));

		g2d.draw(new Line2D.Double(valueCoord-4, vArrowEnd-2, valueCoord+4, vArrowEnd-2));
		g2d.draw(new Line2D.Double(valueCoord-3, vArrowEnd-3, valueCoord+3, vArrowEnd-3));
		g2d.draw(new Line2D.Double(valueCoord-2, vArrowEnd-4, valueCoord+2, vArrowEnd-4));
		g2d.draw(new Line2D.Double(valueCoord-1, vArrowEnd-5, valueCoord+1, vArrowEnd-5));
		 */
		if(needleBorder != null)
			needleBorder.paintBorder(this, g, valueCoord-2, vRectStart, 4, rectHeight);

		//Draw value text
		g2d.setFont(getFont().deriveFont(Font.BOLD,14));
		fontMetrics = g2d.getFontMetrics();

		int valueWidth = fontMetrics.stringWidth(valueStr);
		int valueX = Math.max(0, valueCoord - valueWidth/2);
		valueX = Math.min(w - valueWidth, valueX);
		int valueY = vRectEnd - 4;

		g2d.drawString(valueStr, valueX, valueY);

		g2d.dispose();
	}

	private void paintInvalidRangeComponent(Graphics g) 
	{
		Graphics2D g2d = (Graphics2D) g.create();

		int w = getWidth();
		int h = getHeight();

		final int vArrowEnd = h;
		final int vRectStart = H_ARROW_HEIGHT;
		final int vRectEnd = h - H_ARROW_HEIGHT;

		if(gradient)
		{
			if(direction == Direction.LeftToRight)
				g2d.setPaint(new GradientPaint(0,0,validColor,w,h,Color.gray));
			else if(direction == Direction.RightToLeft)
				g2d.setPaint(new GradientPaint(0,0,Color.gray,w,h,validColor));
			else if(direction == Direction.BottomToTop)
				g2d.setPaint(new GradientPaint(0,h,validColor,w,0,Color.gray));
			else if(direction == Direction.TopToBottom)
				g2d.setPaint(new GradientPaint(0,h,Color.gray,w,0,validColor));
		}
		else
			g2d.setPaint(validColor);

		g2d.fillRect(0, vRectStart, w, vRectEnd-vRectStart);


		//Draw Value pointer
		int valueCoord = (int) Math.round(w*(value - minValue)/interval) ;
		g2d.setPaint(arrowColor);
		g2d.setStroke(strong);
		g2d.draw(new Line2D.Double(valueCoord, vRectStart, valueCoord, vRectEnd));

		g2d.setStroke(normal);
		g2d.draw(new Line2D.Double(valueCoord-4, vRectStart-4, valueCoord+4, vRectStart-4));
		g2d.draw(new Line2D.Double(valueCoord-3, vRectStart-3, valueCoord+3, vRectStart-3));
		g2d.draw(new Line2D.Double(valueCoord-2, vRectStart-2, valueCoord+2, vRectStart-2));
		g2d.draw(new Line2D.Double(valueCoord-1, vRectStart-1, valueCoord+1, vRectStart-1));

		g2d.draw(new Line2D.Double(valueCoord-4, vArrowEnd-2, valueCoord+4, vArrowEnd-2));
		g2d.draw(new Line2D.Double(valueCoord-3, vArrowEnd-3, valueCoord+3, vArrowEnd-3));
		g2d.draw(new Line2D.Double(valueCoord-2, vArrowEnd-4, valueCoord+2, vArrowEnd-4));
		g2d.draw(new Line2D.Double(valueCoord-1, vArrowEnd-5, valueCoord+1, vArrowEnd-5));

		g2d.dispose();
	}



}
