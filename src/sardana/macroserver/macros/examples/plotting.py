import math
from numpy import linspace
from scipy.integrate import quad
from scipy.special import j0

from sardana.macroserver.macro import macro

def j0i(x):
    """Integral form of J_0(x)"""
    def integrand(phi):
        return math.cos(x * math.sin(phi))
    return (1.0/math.pi) * quad(integrand, 0, math.pi)[0]

@macro()
def J0_plot(self):
    x = linspace(0, 20, 200)
    y = j0(x)
    x1 = x[::10]
    y1 = map(j0i, x1)
    self.pyplot.plot(x, y, label=r'$J_0(x)$') # 
    self.pyplot.plot(x1, y1, 'ro', label=r'$J_0^{integ}(x)$')
    self.pyplot.title(r'Verify $J_0(x)=\frac{1}{\pi}\int_0^{\pi}\cos(x \sin\phi)\,d\phi$')
    self.pyplot.xlabel('$x$')
    self.pyplot.legend()
