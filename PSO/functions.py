import numpy as np
from math import sin

# Matyas function


def fun_matyas(x):
    """
    Matyas function - expects 2D array [x, y]
    """
    if isinstance(x, np.ndarray):
        x_val, y_val = x[0], x[1]
    else:
        x_val, y_val = x, y
    return 0.26 * (x_val*x_val + y_val*y_val) - 0.48 * x_val * y_val

# Eggholder function


def fun_eggholder(x):
    """
    Eggholder function - expects 2D array [x, y]
    """
    if isinstance(x, np.ndarray):
        x_val, y_val = x[0], x[1]
    else:
        x_val, y_val = x, y
    return - (y_val+47) * sin((abs(x_val/2 + (y_val+47)))**0.5) - x_val * sin((abs(x_val - (y_val+47)))**0.5)
