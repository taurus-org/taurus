package es.cells.sardana.client.framework.macroserver;

public class MacroDescriptionModel {
	String name;
	String description;
	String advices;
	String nrOfArgs;
	String nrOfReturnValues;
	Atribute [] returnValues;
	Atribute [] atributes;
	
	public MacroDescriptionModel()
	{
		
	}
	
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public String getAdvices() {
		return advices;
	}
	public void setAdvices(String advices) {
		this.advices = advices;
	}
	public String getNrOfArgs() {
		return nrOfArgs;
	}
	public void setNrOfArgs(String nrOfArgs) {
		this.nrOfArgs = nrOfArgs;
	}
	public Atribute[] getReturnValues() {
		return returnValues;
	}
	public void setReturnValues(Atribute[] returnValues) {
		this.returnValues = returnValues;
	}
	public Atribute[] getAtributes() {
		return atributes;
	}
	public void setAtributes(Atribute[] atributes) {
		this.atributes = atributes;
	}
}
