package es.cells.sardana.client.framework.pool.event;

import java.util.Map;

import fr.esrf.Tango.AttrDataFormat;
import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.DeviceAttribute;
import fr.esrf.tangoatk.core.AtkEventListenerList;
import fr.esrf.tangoatk.core.Device;
import fr.esrf.tangoatk.core.IAttributeStateListener;
import fr.esrf.tangoatk.core.IErrorListener;
import fr.esrf.tangoatk.core.IImageListener;
import fr.esrf.tangoatk.core.ISetErrorListener;
import fr.esrf.tangoatk.core.IStringSpectrum;
import fr.esrf.tangoatk.core.IStringSpectrumListener;
import fr.esrf.tangoatk.core.Property;

public class EmptyStringSpectrum implements IStringSpectrum {

	protected static final String[] EMPTY_VAL = new String[0];
	
	public EmptyStringSpectrum() {}
	
	public void addListener(IStringSpectrumListener l) {

	}

	public String[] getStringSpectrumValue() {
		
		return EMPTY_VAL;
	}

	public void removeListener(IStringSpectrumListener l) {
		

	}

	public void setStringSpectrumValue(String[] strSpect) {
		

	}

	public void addImageListener(IImageListener l) {
		

	}

	public void addSetErrorListener(ISetErrorListener l) {
		

	}

	public void addStateListener(IAttributeStateListener l) {
		

	}

	public void dispatch(DeviceAttribute attValue) {
		

	}

	public void dispatchError(DevFailed e) {
		

	}

	public DeviceAttribute getAttribute() {
		
		return null;
	}

	public String getDescription() {
		
		return null;
	}

	public String getDisplayUnit() {
		
		return null;
	}

	public double getDisplayUnitFactor() {
		
		return 0;
	}

	public String getFormat() {
		
		return null;
	}

	public int getHeight() {
		
		return 0;
	}

	public String getLabel() {
		
		return null;
	}

	public int getMaxXDimension() {
		
		return 0;
	}

	public int getMaxYDimension() {
		
		return 0;
	}

	public String getStandardUnit() {
		
		return null;
	}

	public double getStandardUnitFactor() {
		
		return 0;
	}

	public String getState() {
		
		return null;
	}

	public String getType() {
		
		return null;
	}

	public String getUnit() {
		
		return null;
	}

	public int getWidth() {
		
		return 0;
	}

	public int getXDimension() {
		
		return 0;
	}

	public int getYDimension() {
		
		return 0;
	}

	public boolean hasEvents() {
		
		return false;
	}

	public boolean isSkippingRefresh() {
		
		return false;
	}

	public boolean isWritable() {
		
		return false;
	}

	public void removeImageListener(IImageListener l) {
		

	}

	public void removeSetErrorListener(ISetErrorListener l) {
		

	}

	public void removeStateListener(IAttributeStateListener l) {
		

	}

	public void setDescription(String desc) {
		

	}

	public void setLabel(String label) {
		

	}

	public void setName(String s) {
		

	}

	public void setProperty(String name, Number n) {
		

	}

	public void setProperty(String name, Number n, boolean editable) {
		

	}

	public void setSkippingRefresh(boolean b) {
		

	}

	public void addErrorListener(IErrorListener listener) {
		

	}

	public String getAlias() {
		
		return null;
	}

	public Device getDevice() {
		
		return null;
	}

	public AtkEventListenerList getListenerList() {
		
		return null;
	}

	public String getName() {
		
		return null;
	}

	public String getNameSansDevice() {
		
		return null;
	}

	public Property getProperty(String name) {
		
		return null;
	}

	public Map getPropertyMap() {
		
		return null;
	}

	public boolean isExpert() {
		
		return false;
	}

	public boolean isOperator() {
		
		return false;
	}

	public void removeErrorListener(IErrorListener listener) {
		

	}

	public void setAlias(String alias) {
		

	}

	public void storeConfig() {
		

	}

	public void refresh() {
		

	}

	public AttrDataFormat getTangoDataFormat() {
		// TODO Auto-generated method stub
		return null;
	}

	public int getTangoDataType() {
		// TODO Auto-generated method stub
		return 0;
	}

}
