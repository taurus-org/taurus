package es.cells.sardana.client.framework.pool;

import java.util.regex.Matcher;

import javax.swing.ImageIcon;

/**
 * 
 * @author tcoutinho
 *
 */
public class ControllerClass extends AbstractPoolClass
{
	protected ControllerType type;
	protected ControllerLanguage language;
	
	String genre;
	String model;
	String organization;
	String imgFilename;
	int imgFileSize;
	ImageIcon imageIcon;
	String logoFilename;
	int logoFileSize;
	ImageIcon logo;
	String iconFilename;
	int iconFileSize;
	ImageIcon icon;
	
	public ControllerClass(String typee, String klass, String fullPath)
	{
		super(typee,klass,fullPath);
	}

	protected void buildClassData(String type, String klass, String fullPathName)
	{
		setType(ControllerType.valueOf(type));
		setClassName(klass);
		setFullPathName(fullPathName);
		
		String[] pathElems = fullPathName.split("\\/");
		
		setFileName(pathElems[pathElems.length-1]);
		
		String[] fileElems = fileName.split("\\.");
		
		setModuleName(fileElems[0]);
		setFileExtension(fileElems[1]);
		
		language = fileExtension.equalsIgnoreCase("la") ? ControllerLanguage.CPP : 
			       (fileExtension.equalsIgnoreCase("py") ? ControllerLanguage.Python : ControllerLanguage.InvalidCtrlLanguage);		
	}	
	
	public ControllerType getType()
	{
		return type;
	}

	public void setType(ControllerType type)
	{
		this.type = type;
	}

	public ControllerLanguage getLanguage()
	{
		return language;
	}

	public void setLanguage(ControllerLanguage language)
	{
		this.language = language;
	}

	public void setGender(String genre) 
	{
		this.genre = genre;
	}

	public void setModel(String model) 
	{
		this.model = model;
	}

	public void setImageFileName(String imgFilename) 
	{
		this.imgFilename = imgFilename;
	}

	public void setImageFileSize(int imgFileSize) 
	{
		this.imgFileSize = imgFileSize;
	}

	public void setImage(ImageIcon imageIcon) 
	{
		this.imageIcon = imageIcon;
	}

	public void setLogoFileName(String logoFilename) 
	{
		this.logoFilename = logoFilename;	
	}

	public void setLogoFileSize(int logoFileSize) 
	{
		this.logoFileSize = logoFileSize;
	}

	public void setLogo(ImageIcon logo) 
	{
		this.logo = logo;
	}

	public void setIconFileName(String iconFilename) 
	{
		this.iconFilename = iconFilename;
	}
	
	public void setIconFileSize(int iconFileSize) 
	{
		this.iconFileSize = iconFileSize;
	}

	public void setIcon(ImageIcon icon) 
	{
		this.icon = icon;
	}
	
	public void setOrganization(String organization) 
	{
		this.organization = organization;
	}
	
	public String getGenre() {
		return genre;
	}

	public String getModel() {
		return model;
	}

	public String getOrganization() {
		return organization;
	}

	public ImageIcon getImageIcon() {
		return imageIcon;
	}

	public ImageIcon getLogo() {
		return logo;
	}

	public ImageIcon getIcon() {
		return icon;
	}

	@Override
	public boolean match(Object obj) 
	{
		if(!(obj instanceof ControllerClass))
			return false;

		if(!super.match(obj))
			return false;
		
		ControllerClass ctrlClass = (ControllerClass) obj; 
		
		return type.equals(ctrlClass.getType()) &&
			   language.equals(ctrlClass.getLanguage());
	}


}
