import os
import math
import random
import copy
import matplotlib.pyplot as plt
import numpy as np
import time

# ==========================================================
# KONFIGURACJA EKSPERYMENTU
# ==========================================================
CONFIG = {
    "instance_path": "rc101.txt",
    "save_dir": "experiment_results",

    # Kary (Hard Constraints)
    "penalty_time_window": 500.0,
    "penalty_capacity": 5000.0,
    # Zwiększamy karę za pojazd, aby algorytm desperacko chciał je usuwać
    "penalty_vehicle": 10000.0,

    # Parametry SA (Dłuższe, wolniejsze chłodzenie)
    "sa_T_start": 5000.0,
    "sa_alpha": 0.9999,      # Bardzo wolne chłodzenie - pozwoli na 100k+ iteracji
    "sa_T_min": 0.01,
    "sa_log_interval": 2000,
    "max_iterations": 300000,  # Zwiększony limit iteracji

    # Wagi ruchów (Suma nie musi być 1, algorytm używa if/elif)
    # Dodajemy logikę dla kill_route w kodzie
    "show_plots": True
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
        print(f"Brak pliku {path}. Generuję losowe dane testowe...")
        return generate_dummy_data()

    customers = []
    capacity = 0

    try:
        with open(path, 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        iterator = iter(lines)
        while True:
            try:
                line = next(iterator)
                if "CAPACITY" in line:
                    cap_line = next(iterator)
                    parts = cap_line.split()
                    if len(parts) >= 1:
                        capacity = int(parts[-1])
                    else:
                        capacity = 200

                elif "DATA SECTION" in line or "CUST NO." in line:
                    break
            except StopIteration:
                break

        while True:
            try:
                line = next(iterator)
                parts = line.split()
                if not parts or not parts[0].isdigit():
                    continue
                data = list(map(int, parts))
                if len(data) >= 7:
                    customers.append(
                        Customer(data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
            except StopIteration:
                break

    except Exception as e:
        print(f"Krytyczny błąd parsowania: {e}")
        return generate_dummy_data()

    return customers, capacity


def generate_dummy_data():
    custs = [Customer(0, 50, 50, 0, 0, 1000, 0)]
    for i in range(1, 21):
        custs.append(Customer(
            i, random.randint(0, 100), random.randint(0, 100),
            random.randint(5, 20),
            random.randint(0, 800), random.randint(850, 1000), 10
        ))
    return custs, 200


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def check_route_validity(route, customers, capacity):
    time = 0
    load = 0
    dist_cost = 0
    t_pen = 0

    prev = customers[0]

    for c_idx in route[1:-1]:
        curr = customers[c_idx]
        d = dist(prev, curr)
        dist_cost += d
        time += d

        if time < curr.ready:
            time = curr.ready
        if time > curr.due:
            t_pen += (time - curr.due)

        time += curr.service
        load += curr.demand
        prev = curr

    last = customers[0]
    d = dist(prev, last)
    dist_cost += d
    time += d
    if time > last.due:
        t_pen += (time - last.due)

    c_pen = 0
    if load > capacity:
        c_pen = (load - capacity)

    is_valid = (t_pen == 0 and c_pen == 0)
    return is_valid, dist_cost, t_pen, c_pen


def get_route_cost_with_penalties(route, customers, capacity, params):
    _, d_cost, t_pen, c_pen = check_route_validity(route, customers, capacity)
    total = d_cost
    total += t_pen * params["penalty_time_window"]
    total += c_pen * params["penalty_capacity"]
    return total


def calculate_total_cost(solution, customers, capacity, params):
    total = 0
    for route in solution:
        if len(route) > 2:
            total += get_route_cost_with_penalties(
                route, customers, capacity, params)
            total += params["penalty_vehicle"]
    return total

# ==========================================================
# OPERATORY RUCHÓW
# ==========================================================


def op_transfer(solution):
    non_empty = [i for i, r in enumerate(solution) if len(r) > 2]
    if not non_empty:
        return None

    r1_idx = random.choice(non_empty)
    r2_idx = random.randint(0, len(solution) - 1)

    if r1_idx == r2_idx:
        return None

    new_r1 = solution[r1_idx][:]
    new_r2 = solution[r2_idx][:]

    cust_idx = random.randint(1, len(new_r1) - 2)
    customer = new_r1.pop(cust_idx)

    insert_idx = random.randint(1, len(new_r2) - 1)
    new_r2.insert(insert_idx, customer)

    return [(r1_idx, new_r1), (r2_idx, new_r2)]


def op_swap(solution):
    non_empty = [i for i, r in enumerate(solution) if len(r) > 2]
    if len(non_empty) < 1:
        return None

    r1_idx = random.choice(non_empty)
    r2_idx = random.choice(non_empty)

    new_r1 = solution[r1_idx][:]
    if r1_idx == r2_idx:
        new_r2 = new_r1
    else:
        new_r2 = solution[r2_idx][:]

    if len(new_r1) < 3 or len(new_r2) < 3:
        return None

    c1_idx = random.randint(1, len(new_r1) - 2)
    c2_idx = random.randint(1, len(new_r2) - 2)

    new_r1[c1_idx], new_r2[c2_idx] = new_r2[c2_idx], new_r1[c1_idx]

    if r1_idx == r2_idx:
        return [(r1_idx, new_r1)]
    else:
        return [(r1_idx, new_r1), (r2_idx, new_r2)]


def op_2opt_random(solution):
    non_empty = [i for i, r in enumerate(solution) if len(r) > 3]
    if not non_empty:
        return None

    r_idx = random.choice(non_empty)
    new_r = solution[r_idx][:]

    i, j = sorted(random.sample(range(1, len(new_r) - 1), 2))
    new_r[i:j] = reversed(new_r[i:j])

    return [(r_idx, new_r)]

# --- NOWY AGRESYWNY OPERATOR ---


def op_kill_route(solution, customers, capacity):
    """Próbuje usunąć najkrótszą trasę i rozparcelować jej klientów"""
    # 1. Znajdź najkrótsze trasy
    routes_info = []
    for i, r in enumerate(solution):
        if len(r) > 2:
            routes_info.append((i, len(r)))

    if len(routes_info) < 2:
        return None

    # Sortuj od najkrótszej
    routes_info.sort(key=lambda x: x[1])

    # Weź najkrótszą (lub jedną z najkrótszych, żeby nie utknąć)
    target_idx = routes_info[0][0]

    # Jeśli mamy kilka o tej samej minimalnej długości, wylosuj jedną z nich
    min_len = routes_info[0][1]
    candidates = [x[0] for x in routes_info if x[1] == min_len]
    target_idx = random.choice(candidates)

    # Kopia tras
    new_solution_map = {i: r[:] for i, r in enumerate(solution)}

    # Klienci do przeniesienia
    customers_to_move = new_solution_map[target_idx][1:-1]

    # "Czyścimy" trasę docelową
    new_solution_map[target_idx] = [0, 0]

    # Potencjalne cele (inne niepuste trasy)
    targets = [i for i in range(len(solution)) if i !=
               target_idx and len(solution[i]) > 2]

    # Próba wstawienia każdego klienta
    for cust_id in customers_to_move:
        inserted = False
        # Mieszamy kolejność sprawdzania tras docelowych
        random.shuffle(targets)

        for t_idx in targets:
            route = new_solution_map[t_idx]
            # Best fit wewnątrz tej trasy
            best_pos = -1

            # Sprawdzamy każdą pozycję
            for p in range(1, len(route)):
                temp_route = route[:p] + [cust_id] + route[p:]
                valid, _, _, _ = check_route_validity(
                    temp_route, customers, capacity)
                if valid:
                    best_pos = p
                    break  # First valid fit (szybsze niż best fit)

            if best_pos != -1:
                new_solution_map[t_idx].insert(best_pos, cust_id)
                inserted = True
                break

        if not inserted:
            # Porażka - nie da się upchnąć klientów
            return None

    # Zbieramy zmiany
    changes = []
    for i in new_solution_map:
        if new_solution_map[i] != solution[i]:
            changes.append((i, new_solution_map[i]))

    return changes

# ==========================================================
# ALGORYTMY
# ==========================================================


def build_initial_solution(customers, capacity):
    unassigned = sorted(list(range(1, len(customers))),
                        key=lambda x: customers[x].ready)
    solution = []

    while unassigned:
        cust_id = unassigned.pop(0)
        inserted = False

        for route in solution:
            best_pos = -1
            min_cost_increase = float('inf')

            for i in range(1, len(route)):
                temp_route = route[:i] + [cust_id] + route[i:]
                valid, cost, _, _ = check_route_validity(
                    temp_route, customers, capacity)

                if valid:
                    if cost < min_cost_increase:
                        min_cost_increase = cost
                        best_pos = i

            if best_pos != -1:
                route.insert(best_pos, cust_id)
                inserted = True
                break

        if not inserted:
            solution.append([0, cust_id, 0])

    return solution


def simulated_annealing(customers, capacity, params):
    current_sol = build_initial_solution(customers, capacity)
    current_cost = calculate_total_cost(
        current_sol, customers, capacity, params)

    best_sol = [r[:] for r in current_sol]
    best_cost = current_cost

    T = params["sa_T_start"]
    history = []

    print(f"Start koszt: {current_cost:.2f} | Pojazdów: {len(current_sol)}")

    iteration = 0

    while iteration < params["max_iterations"] and T > params["sa_T_min"]:
        iteration += 1

        r = random.random()
        changes = None

        # Prawdopodobieństwa ruchów
        # 10% na agresywną redukcję trasy
        # 40% na transfer (dobre do poprawiania)
        # 30% na swap
        # 20% na 2-opt

        if r < 0.1:
            changes = op_kill_route(current_sol, customers, capacity)
        elif r < 0.5:
            changes = op_transfer(current_sol)
        elif r < 0.8:
            changes = op_swap(current_sol)
        else:
            changes = op_2opt_random(current_sol)

        if not changes:
            continue

        old_partial_cost = 0
        new_partial_cost = 0

        for r_idx, new_route in changes:
            old_partial_cost += get_route_cost_with_penalties(
                current_sol[r_idx], customers, capacity, params)
            if len(current_sol[r_idx]) > 2:
                old_partial_cost += params["penalty_vehicle"]

            new_partial_cost += get_route_cost_with_penalties(
                new_route, customers, capacity, params)
            if len(new_route) > 2:
                new_partial_cost += params["penalty_vehicle"]

        delta = new_partial_cost - old_partial_cost

        if delta < 0 or random.random() < math.exp(-delta / T):
            for r_idx, new_route in changes:
                current_sol[r_idx] = new_route

            current_cost += delta

            if current_cost < best_cost:
                best_cost = current_cost
                best_sol = [r[:] for r in current_sol]
                # Logujemy od razu, jeśli znaleźliśmy coś super (mniej pojazdów)
                # v_count = len([r for r in best_sol if len(r) > 2])
                # print(f"*** New Best: {best_cost:.1f} (Veh: {v_count}) ***")

        T *= params["sa_alpha"]

        if iteration % params["sa_log_interval"] == 0:
            v_count = len([r for r in best_sol if len(r) > 2])
            dist_val = sum(dist(customers[r[i]], customers[r[i+1]])
                           for r in best_sol for i in range(len(r)-1))
            history.append(best_cost)
            print(
                f"Iter: {iteration} | T: {T:.2f} | Best Cost: {best_cost:.2f} | Dist: {dist_val:.1f} | Veh: {v_count}")

    return best_sol, history


def main():
    if not os.path.exists(CONFIG["save_dir"]):
        os.makedirs(CONFIG["save_dir"])

    customers, capacity = load_solomon(CONFIG["instance_path"])
    print(f"Załadowano {len(customers)-1} klientów. Pojemność: {capacity}")

    best_sol, history = simulated_annealing(customers, capacity, CONFIG)

    final_sol = [r for r in best_sol if len(r) > 2]
    final_dist = sum(dist(customers[r[i]], customers[r[i+1]])
                     for r in final_sol for i in range(len(r)-1))

    print("\n=== WYNIK KOŃCOWY ===")
    print(f"Liczba pojazdów: {len(final_sol)}")
    print(f"Całkowity dystans: {final_dist:.2f}")

    visualize_solution(
        final_sol, customers,
        title=f"VRPTW Result | Veh: {len(final_sol)} | Dist: {final_dist:.1f}",
        save_path=os.path.join(CONFIG["save_dir"], "optimized_result.png"),
        show=CONFIG["show_plots"]
    )

    plt.figure()
    plt.plot(history)
    plt.title("Zbieżność funkcji kosztu")
    plt.xlabel("Iteracja / Log Interval")
    plt.ylabel("Koszt")
    if CONFIG["show_plots"]:
        plt.show()


def visualize_solution(solution, customers, title="", save_path=None, show=True):
    plt.figure(figsize=(10, 8))
    colors = plt.cm.nipy_spectral(np.linspace(0, 1, len(solution)))

    depot = customers[0]
    plt.plot(depot.x, depot.y, 'ks', markersize=15, label='Depot')

    for idx, route in enumerate(solution):
        color = colors[idx]
        x_coords = [customers[i].x for i in route]
        y_coords = [customers[i].y for i in route]

        plt.plot(x_coords, y_coords, '-', color=color,
                 alpha=0.7, linewidth=1.5)
        plt.plot(x_coords[1:-1], y_coords[1:-1],
                 'o', color=color, markersize=5)

    plt.title(title)
    plt.grid(True, alpha=0.3)
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()


if __name__ == "__main__":
    main()
