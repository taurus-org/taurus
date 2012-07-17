
from sardana.macroserver.macro import imacro, Type

@imacro()
def ask_number_of_points(self):
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
    """asks use for peak current of points with a custom title"""
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection")
    self.output("You selected a peak of %f A", peak)
    
@imacro()
def ask_peak2(self):
    """asks use for peak current of points with a custom title"""
    unit = "mA"
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection", unit=unit)
    self.output("You selected a peak of %f %s", peak, unit)
    
@imacro()
def ask_peak3(self):
    """asks use for peak current of points with a custom title"""
    unit = "mA"
    peak = self.input("What is the peak current?", data_type=Type.Float,
                      title="Peak selection", key="Current", unit=unit,
                      default_value=123.4)
    self.output("You selected a peak of %f %s", peak, unit)
