from math import sin

# Matyas function


def fun_matyas(x, y):
    return 0.26 * (x*x + y*y) - 0.48 * x * y

# Eggholder function


def fun_eggholder(x, y):
    return - (y+47) * sin((abs(x/2 + (y+47)))**0.5) - x * sin((abs(x - (y+47)))**0.5)
