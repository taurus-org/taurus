import math
import pprint
import numpy
import StringIO
import time
import PIL.Image
from sardana.macroserver.macro import Macro, macro, Type


@macro()
def fft_freq(self):
    signal = numpy.array([-2, 8, 6, 4, 1, 0, 3, 5],
                         dtype=float)
    fourier = numpy.fft.fft(signal)
    n = signal.size
    timestep = 0.1
    freq = numpy.fft.fftfreq(n, d=timestep)
    self.output(freq)


@macro([["message", Type.String, None, "message to print"]])
def hello_world_2(self, message):
    """This prints 'Hello, World on the screen + a
       message."""
    self.output("Hello, World!")
    self.output("Your message is: " + message)


@macro([["moveable", Type.Moveable, None, "moveable to get position"]])
def where_moveable(self, moveable):
    """This macro prints the current moveable position"""

    self.output("%s is now at %s", moveable.getName(), 
                moveable.getPosition())


@macro([["interactions", Type.Integer, None, "numb. interactions"],
        ["density",      Type.Integer, None, "density"],
        ["filename",     Type.String,  None, "filename to store image"]])
def mandelbrot(self, interactions, density, filename):
    x_min, x_max = -2, 1
    y_min, y_max = -1.5, 1.5

    x, y = numpy.meshgrid(numpy.linspace(x_min, x_max, density),
                          numpy.linspace(y_min, y_max, density))

    c = x + 1j*y # complex grid
    z = c.copy()
    
    fractal = numpy.zeros(z.shape, dtype=numpy.uint8) + 255
    
    for n in range(interactions):
        self.output("Iteration %d" % n)
        z *= z
        z += c
        mask = (fractal == 255) & (abs(z) > 10)
        fractal[mask] = 254 * n / float(interactions)
    fractal_img = PIL.Image.fromarray(fractal)
    fractal_img.save(filename)


@macro([["value",  Type.Float, None, "value (radians)"]],
       [["result", Type.Float, None, "the cosine(value)"]])
def cosine(self, value):
    """Return the cosine of value (measured in radians)."""
    return math.cos(value)


@macro([["energy", Type.Float, None, "go to energy"]])
def move_energy(self, energy):
    """This macro changes the current energy"""
    E = self.getMoveable("Energy")
    E.move(energy)
    self.output("Energy is now at %s", E.getPosition())


@macro([ ["ccd",   Type.String, None, "ccd name"],
         ["fname", Type.String, None, "filename to save"] ])
def snapshot_ccd(self, ccd, fname):
    """Saves the current ccd image to the specified file"""
    ccd_dev = self.getDevice(ccd)
    image = PIL.Image.fromarray(ccd_dev.image)
    image.save(fname)

@macro([ ["p1", Type.Float, None, "absolute position of mot01"],
         ["p2", Type.Float, None, "absolute position of mot02"] ])
def move2(self, p1, p2):
    motion = self.getMotion(["mot01", "mot02"])
    motion.move([p1, p2])

@macro([["moveable", Type.Moveable, None, "moveable to get position"]])
def where_moveable_2(self, moveable):
    """This macro prints the current moveable position"""
    
    self.wm(moveable)


@macro([ ["moveable", Type.Moveable, None, "moveable to move"],
         ["position", Type.Float, None, "absolute position"] ])
def move_moveable(self, moveable, position):
    """This macro moves a moveable to the specified position"""
    
    self.mv(moveable, position)
    self.output("%s is now at %s", moveable.getName(), moveable.getPosition())


@macro([ ["moveable", Type.Moveable, None, "scan on this moveable"],
         ["integ_time", Type.Float, 1.0, "Integration time"] ])
def fixed_ascan(self, moveable, integ_time):
    """This macro does an absolute scan on the specified motor
       between positions 0 and 85 in 10 intervals with the given
       integration time"""
    
    self.ascan(moveable, 0, 85, 10, integ_time)

@macro([["scanID", Type.Integer, -1, "scan ID"]])
def scan_info(self, scanID):
    """This macro shows information about a scan. If
    no scanID is given, -1 is assumed, meaning last scan."""
    hist = self.getEnv("ScanHistory")
    scan = None
    if scanID == -1:
        scan = hist[-1]
    else:
        for h in hist:
            if h['serialno'] == scanID:
                scan = h; break
    buff = StringIO.StringIO()
    pprint.pprint(scan, stream=buff)
    self.output(buff.getvalue())


@macro([["scanID", Type.Integer, None, "new scan ID"]])
def set_scanid(self, scanID):
    """Reset the ScanID"""
    
    self.setEnv("ScanID", scanID)




