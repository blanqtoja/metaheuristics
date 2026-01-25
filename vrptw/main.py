import os
import math
import random
import copy
import matplotlib.pyplot as plt
import numpy as np

# ==========================================================
# KONFIGURACJA EKSPERYMENTU
# ==========================================================
CONFIG = {
    "instance_path": "rc101.txt",        # Ścieżka do pliku Solomon
    "save_dir": "experiment_results",   # Folder na wyniki

    # Parametry Kosztu (Kary)
    "penalty_time_window": 100.0,       # Kara za jednostkę spóźnienia
    "penalty_capacity": 1000.0,         # Kara za jednostkę przeładowania
    "penalty_vehicle": 500.0,           # Stały koszt użycia pojazdu

    # Parametry Symulowanego Wyżarzania (SA)
    "sa_T_start": 5000.0,
    "sa_alpha": 0.9995,
    "sa_T_min": 1e-4,
    "sa_log_interval": 200,

    # Prawdopodobieństwa ruchów (muszą sumować się do 1.0)
    "prob_transfer": 0.3,   # Przeniesienie klienta między trasami
    "prob_2opt": 0.3,       # Optymalizacja 2-opt wewnątrz trasy
    "prob_swap": 0.4,       # Zamiana dwóch klientów wewnątrz trasy

    # Wizualizacja
    "show_plots": True,
    "save_plots": True
}


class Customer:
    def __init__(self, idx, x, y, demand, ready, due, service):
        self.id = idx
        self.x = x
        self.y = y
        self.demand = demand
        self.ready = ready
        self.due = due
        self.service = service


def load_solomon(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Nie znaleziono pliku: {path}")
    customers = []
    with open(path) as f:
        lines = f.readlines()
    capacity = int(lines[4].split()[1])
    for line in lines[9:]:
        if not line.strip():
            continue
        data = list(map(int, line.split()))
        customers.append(Customer(*data))
    return customers, capacity


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def route_cost(route, customers, capacity, params):
    time = 0
    load = 0
    cost = 0
    penalty = 0

    for i in range(len(route) - 1):
        c1 = customers[route[i]]
        c2 = customers[route[i + 1]]
        travel = dist(c1, c2)
        time += travel

        if time < c2.ready:
            time = c2.ready
        if time > c2.due:
            penalty += params["penalty_time_window"] * (time - c2.due)

        time += c2.service
        load += c2.demand
        cost += travel

    if load > capacity:
        penalty += params["penalty_capacity"] * (load - capacity)

    return cost + penalty


def solution_cost(solution, customers, capacity, params):
    total = 0
    for route in solution:
        if len(route) > 2:
            total += route_cost(route, customers, capacity, params)
            total += params["penalty_vehicle"]
    return total


def two_opt(route, customers, capacity, params):
    best_route = route.copy()
    best_cost = route_cost(route, customers, capacity, params)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                new_route = route[:i] + route[i:j][::-1] + route[j:]
                new_cost = route_cost(new_route, customers, capacity, params)
                if new_cost < best_cost:
                    best_route = new_route.copy()
                    best_cost = new_cost
                    improved = True
                    route = best_route.copy()
                    break
            if improved:
                break
    return best_route


def pure_distance(solution, customers):
    total = 0
    for route in solution:
        for i in range(len(route) - 1):
            total += dist(customers[route[i]], customers[route[i + 1]])
    return total

# --- Wizualizacja (pozostaje podobna, ale korzysta z CONFIG) ---


def visualize_solution(solution, customers, title="", save_path=None, show=True):
    plt.figure(figsize=(10, 8))
    colors = plt.cm.rainbow(np.linspace(0, 1, len(solution)))
    for idx, route in enumerate(solution):
        if len(route) <= 2:
            continue
        color = colors[idx]
        x = [customers[i].x for i in route]
        y = [customers[i].y for i in route]
        plt.plot(x, y, 'o-', color=color, alpha=0.6, label=f'R{idx+1}')

    depot = customers[0]
    plt.plot(depot.x, depot.y, 'rs', markersize=12, label='Depot')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close()

# ==========================================================
# GŁÓWNY ALGORYTM
# ==========================================================


def simulated_annealing(init_sol, customers, capacity, params):
    current = copy.deepcopy(init_sol)
    best = copy.deepcopy(current)
    current_cost = solution_cost(current, customers, capacity, params)
    best_cost = current_cost

    T = params["sa_T_start"]
    iteration = 0
    history = []

    while T > params["sa_T_min"]:
        iteration += 1
        new = copy.deepcopy(current)
        move_type = random.random()

        # Ruchy zdefiniowane w CONFIG
        p_trans = params["prob_transfer"]
        p_2opt = p_trans + params["prob_2opt"]

        if move_type < p_trans and len(new) > 1:
            # Przeniesienie między trasami
            r1, r2 = random.sample(range(len(new)), 2)
            if len(new[r1]) > 3:
                c_idx = random.randint(1, len(new[r1])-2)
                cust = new[r1].pop(c_idx)
                ins_pos = random.randint(1, len(new[r2])-1)
                new[r2].insert(ins_pos, cust)

        elif move_type < p_2opt:
            # 2-opt lokalny
            r_idx = random.randint(0, len(new)-1)
            if len(new[r_idx]) > 4:
                new[r_idx] = two_opt(new[r_idx], customers, capacity, params)

        else:
            # Swap wewnątrz trasy
            r_idx = random.randint(0, len(new)-1)
            if len(new[r_idx]) > 3:
                i, j = random.sample(range(1, len(new[r_idx])-1), 2)
                new[r_idx][i], new[r_idx][j] = new[r_idx][j], new[r_idx][i]

        new_cost = solution_cost(new, customers, capacity, params)
        delta = new_cost - current_cost

        if delta < 0 or random.random() < math.exp(-delta / T):
            current = new
            current_cost = new_cost
            if current_cost < best_cost:
                best = copy.deepcopy(current)
                best_cost = current_cost

        if iteration % params["sa_log_interval"] == 0:
            history.append((iteration, best_cost))
            print(
                f"Iter: {iteration} | T: {T:.2f} | Best Cost: {best_cost:.2f} | Dist: {pure_distance(best, customers):.2f}")

        T *= params["sa_alpha"]

    return best, history


def build_initial_solution(customers, capacity, params):
    # Prosta metoda konstrukcyjna (Sortowanie po Ready Time)
    unassigned = list(range(1, len(customers)))
    unassigned.sort(key=lambda x: customers[x].ready)
    solution = []

    for c_id in unassigned:
        inserted = False
        for route in solution:
            load = sum(customers[i].demand for i in route)
            if load + customers[c_id].demand <= capacity:
                route.insert(-1, c_id)
                inserted = True
                break
        if not inserted:
            solution.append([0, c_id, 0])
    return solution


def main():
    # 1. Przygotowanie środowiska
    if not os.path.exists(CONFIG["save_dir"]):
        os.makedirs(CONFIG["save_dir"])

    # 2. Ładowanie danych
    try:
        customers, capacity = load_solomon(CONFIG["instance_path"])
    except Exception as e:
        print(f"Błąd ładowania: {e}")
        return

    # 3. Rozwiązanie początkowe
    init_sol = build_initial_solution(customers, capacity, CONFIG)

    # 4. Eksperyment SA
    print(f"Rozpoczynam eksperyment dla: {CONFIG['instance_path']}")
    best_sol, history = simulated_annealing(
        init_sol, customers, capacity, CONFIG)

    # 5. Podsumowanie i Wizualizacja
    final_dist = pure_distance(best_sol, customers)
    num_vehicles = len([r for r in best_sol if len(r) > 2])

    print("\n=== WYNIK KOŃCOWY ===")
    print(f"Liczba pojazdów: {num_vehicles}")
    print(f"Całkowity dystans: {final_dist:.2f}")

    visualize_solution(
        best_sol, customers,
        title=f"Wynik: {CONFIG['instance_path']} | Dystans: {final_dist:.2f}",
        save_path=os.path.join(CONFIG["save_dir"], "final_route.png"),
        show=CONFIG["show_plots"]
    )


if __name__ == "__main__":
    main()
