
from sardana.macroserver.macro import imacro, Type

@imacro()
def ask_number_of_points(self):
    """asks user for the number of points"""
    
    nb_points = self.input("How many points?", data_type=Type.Integer)
    

@imacro()
def ask_for_moveable(self):
    """asks user for a motor"""
    
    moveable = self.input("Which moveable?", data_type=Type.Moveable)
    self.output("You selected %s which is at %f", moveable, moveable.getPosition())

@imacro()
def ask_for_car_brand(self):
    """asks user for a car brand"""
    
    car_brands = "Mazda", "Citroen", "Renault"
    car_brand = self.input("Which car brand?", data_type=car_brands)
    self.output("You selected %s", car_brand)
    
@imacro()
def ask_for_multiple_car_brands(self):
    """asks user for several car brands"""
    
    car_brands = "Mazda", "Citroen", "Renault", "Ferrari", "Porche", "Skoda"
    car_brands = self.input("Which car brand(s)?", data_type=car_brands,
                            allow_multiple=True, title="Favorites")
    self.output("You selected %s", ", ".join(car_brands))

@imacro()
def ask_peak(self):
    """asks user for peak current of points with a custom title"""
    
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection")
    self.output("You selected a peak of %f A", peak)
    
@imacro()
def ask_peak_v2(self):
    """asks user for peak current of points with a custom title,
    default value, label and units"""
    
    label, unit = "peak", "mA"
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection", key=label, unit=unit,
                      default_value=123.4)
    self.output("You selected a %s of %f %s", label, peak, unit)
    
@imacro()
def ask_peak_v3(self):
    """asks user for peak current of points with a custom title,
    default value, label, units and ranges"""
    
    label, unit = "peak", "mA"
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection", key=label, unit=unit,
                      default_value=123.4, minimum=0.0, maximum=200.0)
    self.output("You selected a %s of %f %s", label, peak, unit)

@imacro()
def ask_peak_v4(self):
    """asks user for peak current of points with a custom title,
    default value, label, units, ranges and step size"""
    
    label, unit = "peak", "mA"
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection", key=label, unit=unit,
                      default_value=123.4, minimum=0.0, maximum=200.0,
                      step=5)
    self.output("You selected a %s of %f %s", label, peak, unit)
    
@imacro()
def ask_peak_v5(self):
    """asks user for peak current of points with a custom title,
    default value, label, units, ranges, step size and decimal places"""
    
    label, unit = "peak", "mA"
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection", key=label, unit=unit,
                      default_value=123.4, minimum=0.0, maximum=200.0,
                      step=5, decimals=2)
    self.output("You selected a %s of %f %s", label, peak, unit)
