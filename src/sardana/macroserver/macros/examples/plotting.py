import math
from numpy import linspace
from scipy.integrate import quad
from scipy.special import j0

from sardana.macroserver.macro import macro, Type

def j0i(x):
    """Integral form of J_0(x)"""
    def integrand(phi):
        return math.cos(x * math.sin(phi))
    return (1.0/math.pi) * quad(integrand, 0, math.pi)[0]

@macro()
def J0_plot(self):
    """Sample J0 at linspace(0, 20, 200)"""
    x = linspace(0, 20, 200)
    y = j0(x)
    x1 = x[::10]
    y1 = map(j0i, x1)
    self.pyplot.plot(x, y, label=r'$J_0(x)$') # 
    self.pyplot.plot(x1, y1, 'ro', label=r'$J_0^{integ}(x)$')
    self.pyplot.title(r'Verify $J_0(x)=\frac{1}{\pi}\int_0^{\pi}\cos(x \sin\phi)\,d\phi$')
    self.pyplot.xlabel('$x$')
    self.pyplot.legend()


from numpy import random

@macro()
def random_image(self):
    """Shows a random image 32x32"""
    img = random.random((32, 32))
    self.pyplot.matshow(img)

import numpy
    
@macro([["interactions", Type.Integer, None, ""],
        ["density", Type.Integer, None, ""]])
def mandelbrot(self, interactions, density):

    x_min, x_max = -2, 1
    y_min, y_max = -1.5, 1.5
    
    x, y = numpy.meshgrid(numpy.linspace(x_min, x_max, density),
                          numpy.linspace(y_min, y_max, density))
                         
    c = x + 1j * y
    z = c.copy()
    
    fractal = numpy.zeros(z.shape, dtype=numpy.uint8) + 255
    
    finteractions = float(interactions)
    for n in range(interactions):
        z *= z
        z += c
        mask = (fractal == 255) & (abs(z) > 10)
        fractal[mask] = 254 * n / finteractions
    self.pyplot.imshow(fractal)
