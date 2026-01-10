import numpy as np
import time
import random as r


class Particle:
    def __init__(self, position: np.ndarray, velocity: np.ndarray, cost: float):
        self.position = position
        self.velocity = velocity
        self.best_position = np.copy(position)
        self.best_cost = cost


def run_PSO(fun: callable, S: int = 20, dimensions: int = 2, blo: float = -10.0, bup: float = 10.0,
            inertia_weight: float = 0.5, cognitive_coefficient: float = 1.5,
            social_coefficient: float = 1.5, iteration: int = 100):

    time_start = time.time()
    v_range = abs(bup - blo)

    swarm = []
    for _ in range(S):
        pos = np.random.uniform(blo, bup, dimensions)
        vel = np.random.uniform(-v_range, v_range, dimensions)
        cost = fun(pos)
        swarm.append(Particle(pos, vel, cost))

    # Global best
    best_particle = min(swarm, key=lambda p: p.best_cost)
    g_best_pos = np.copy(best_particle.best_position)
    g_best_cost = best_particle.best_cost

    # Histories
    g_best_pos_history = [np.copy(g_best_pos)]
    g_best_cost_history = [g_best_cost]
    avg_pos_history = []
    avg_cost_history = []

    for _ in range(iteration):
        for p in swarm:
            rp = np.random.uniform(0, 1, dimensions)
            rg = np.random.uniform(0, 1, dimensions)

            # Update velocity
            p.velocity = (inertia_weight * p.velocity +
                          cognitive_coefficient * rp * (p.best_position - p.position) +
                          social_coefficient * rg * (g_best_pos - p.position))

            # Update position
            p.position += p.velocity

            # Clip position to limits
            p.position = np.clip(p.position, blo, bup)

            # Cost of current position
            curr_cost = fun(p.position)

            # Check if current solution is better
            if curr_cost < p.best_cost:
                p.best_cost = curr_cost
                p.best_position = np.copy(p.position)

                # Check if current solution is the best in swarm
                if curr_cost < g_best_cost:
                    g_best_cost = curr_cost
                    g_best_pos = np.copy(p.position)

        # Store histories at the end of each iteration
        g_best_pos_history.append(np.copy(g_best_pos))
        g_best_cost_history.append(g_best_cost)

        # Calculate average position and cost in swarm
        avg_pos = np.mean([p.position for p in swarm], axis=0)
        avg_pos_history.append(avg_pos)

        avg_cost = np.mean([fun(p.position) for p in swarm])
        avg_cost_history.append(avg_cost)

    time_end = time.time()
    return g_best_pos, g_best_cost, time_end - time_start, g_best_pos_history, g_best_cost_history, avg_pos_history, avg_cost_history


if __name__ == "__main__":
    def sphere_function(x): return np.sum(x**2)

    best_pos, best_val, duration, g_best_pos_hist, g_best_cost_hist, avg_pos_hist, avg_cost_hist = run_PSO(
        sphere_function)
    print(best_pos, best_val, duration)
