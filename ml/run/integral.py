from sympy import *
import math
t = symbols('t')
d = symbols('d')
a = symbols('a')
b = symbols('b')
l = symbols('l')

res = integrate((t**2 + a + b * t)**(-1), (t, 0, l))
print(res)

sqrt(-1/(4*a - b**2))*log(-2*a*sqrt(-1/(4*a - b**2)) + b**2*sqrt(-1/(4*a - b**2))/2 + b/2) - sqrt(-1/(4*a - b**2))*log(2*a*sqrt(-1/(4*a - b**2)) - b**2*sqrt(-1/(4*a - b**2))/2 + b/2) - sqrt(-1/(4*a - b**2))*log(-2*a*sqrt(-1/(4*a - b**2)) + b**2*sqrt(-1/(4*a - b**2))/2 + b/2 + l) + sqrt(-1/(4*a - b**2))*log(2*a*sqrt(-1/(4*a - b**2)) - b**2*sqrt(-1/(4*a - b**2))/2 + b/2 + l)

