from sympy import *
import math
t = symbols('t')
d = symbols('d')
a = symbols('a')
b = symbols('b')
l = symbols('l')

res = integrate(((t**2 + d**2 - 2 * t * d * cos(a))**0.5 + b)**(-2), (t, 0, l))
print(res)

