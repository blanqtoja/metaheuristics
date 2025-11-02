import random
import math


def calc_temper(temper, alfa):
    return temper * alfa


def neighbour_fun(x, temper, x_min, x_max):
    low = x - 2 * temper
    high = x + 2 * temper

    final_low = max(low, x_min)
    final_high = min(high, x_max)

    if final_low > final_high:
        final_low = final_high

    return final_low, final_high


def probab_accept(fun, x, xprim, temper):
    return math.exp(-(fun(xprim) - fun(x)) / temper)


# fun - function
# max_temperature - temperature at the beginning
# alpha - temperature multiplication factor
# epochs - number of epochs
# steps - number of steps in each epoch
# neighbour_fun - function returns range for new neighbour
# eplison - accuracy, stop condition
# max_no_improvement - number of epochs without improvement grather than epsilon
def simulate(
    fun,
    x_min,
    x_max,
    max_temperature,
    alpha,
    epochs,
    steps,
    neighbour_fun=neighbour_fun,
    epsilon=0.001,
    max_no_improvement=10,
    min_temper=0.001,
):
    x = random.uniform(x_min, x_max)

    x_best = x
    f_best = fun(x_best)

    temper = max_temperature  # start with max temp
    f_best_prev = f_best
    no_improvement_cnt = 0

    for _ in range(0, epochs):

        for _ in range(0, steps):

            low, high = neighbour_fun(
                x_best, temper, x_min, x_max
            )  # number from range of x-2temper, x+2temper

            xprim = random.uniform(low, high)

            if fun(xprim) <= fun(x):
                x = xprim
            else:
                if probab_accept(fun, x, xprim, temper) > random.random():
                    x = xprim

            if fun(x) < f_best:
                f_best = fun(x)
                x_best = x

        temper = calc_temper(temper, alpha)

        if temper < min_temper:
            return x_best

        if abs(f_best_prev - f_best) < epsilon:
            no_improvement_cnt += 1
        else:
            no_improvement_cnt = 0

        f_best_prev = f_best

        if no_improvement_cnt >= max_no_improvement:
            return x_best
    return x_best
