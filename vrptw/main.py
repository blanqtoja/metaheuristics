import os
import math
import random
import copy
import matplotlib.pyplot as plt
import numpy as np
import time
import json
import datetime

# KONFIGURACJA EKSPERYMENTU
CONFIG = {
    "instance_path": "rc101.txt",
    "save_dir": "kalibracja/op_kill_prob-0_25",

    # Kary
    "penalty_time_window": 500.0,
    "penalty_capacity": 5000.0,
    "penalty_vehicle": 10000.0,

    # Parametry SA
    "sa_T_start": 5000.0,
    "sa_alpha": 0.999,
    "sa_T_min": 0.01,
    "sa_log_interval": 2000,
    "max_iterations": 300000,

    # Prawdopobobieństwo wybrania operatora - wagi
    "w_kill": 1,
    "w_transfer": 4,
    "w_swap": 3,
    "w_2opt": 2,

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
        raise Exception(f"Brak pliku {path}")

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

                elif "CUST NO." in line:
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
        print(f"Błąd parsowania: {e}")

    return customers, capacity


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


# operatory ruchu

# transfer klienta pomiedzy trasami
def op_transfer(solution):
    non_empty = [i for i, r in enumerate(solution) if len(r) > 2]
    if not non_empty:
        return None

    r1_idx = random.choice(non_empty)  # skad zabieramy klienta- źródło
    # dokad zabieramy klienta - cel, mozna przeniesc klienta do pustej trasy
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

# wymiana klienta w tej samej lub innej trasie


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

    # zapewnione przez non_empty
    # if len(new_r1) < 3 or len(new_r2) < 3:
    #     return None

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


def op_kill_route(solution, customers, capacity):
    routes_info = []
    for i, r in enumerate(solution):
        if len(r) > 2:
            routes_info.append((i, len(r)))

    if len(routes_info) < 2:
        return None

    routes_info.sort(key=lambda x: x[1])

    # 0 - najkrotsza trasa, 0 - trasa z enumerate
    target_idx = routes_info[0][0]

    # mozliwy remis, wtedy losujemy, ktorą trasę odrzucić
    min_len = routes_info[0][1]
    candidates = [x[0] for x in routes_info if x[1] == min_len]
    target_idx = random.choice(candidates)

    # kopia tras
    new_solution_map = {i: r[:] for i, r in enumerate(solution)}

    # klienci do przeniesienia z wybranej trasy
    customers_to_move = new_solution_map[target_idx][1:-1]

    # usuwamy zawartosc trasy - depot -> depot
    new_solution_map[target_idx] = [0, 0]

    # trasy, gdzie beda mogli trafic klienci z wyzerowanej trasy
    targets = [i for i in range(len(solution)) if i !=
               target_idx and len(solution[i]) > 2]

    # musimy wstawic kazdego klienta, inaczej przerywamy op_kill
    for cust_id in customers_to_move:
        inserted = False

        # kolejnosc tras jest losowa
        random.shuffle(targets)

        for t_idx in targets:
            route = new_solution_map[t_idx]
            # best fit wewnątrz tej trasy
            best_pos = -1

            # w kazdej pozycji
            for p in range(1, len(route)):
                # tworzymy tmp route, trzeba sprawdzic, czy sie miescimy w ramach czasowych i objetosciowych
                temp_route = route[:p] + [cust_id] + route[p:]
                valid, _, _, _ = check_route_validity(
                    temp_route, customers, capacity)
                if valid:  # nie szukamy najlepszego, gdy tylko pasuje, to dopisujemy klienta
                    best_pos = p
                    break

            if best_pos != -1:
                new_solution_map[t_idx].insert(best_pos, cust_id)
                inserted = True
                break

        # jesli jakikolwiek klient nie zostal dopisany do innej trasy, to anulujemy zmiany
        if not inserted:
            return None

    changes = []
    for i in new_solution_map:
        if new_solution_map[i] != solution[i]:
            changes.append((i, new_solution_map[i]))

    return changes

# Algorytmy


def build_initial_solution(customers, capacity):
    # klienci sortowani wedlug czasu
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
                # wstawiamy najlepszą kosztowo pozycję
                route.insert(best_pos, cust_id)
                inserted = True
                break

        if not inserted:
            solution.append([0, cust_id, 0])

    return solution


def simulated_annealing(customers, capacity, params):
    start_time = time.time()

    current_sol = build_initial_solution(customers, capacity)
    current_cost = calculate_total_cost(
        current_sol, customers, capacity, params)

    best_sol = [r[:] for r in current_sol]
    best_cost = current_cost

    T = params["sa_T_start"]
    history = []

    v_start = len([r for r in current_sol if len(r) > 2])
    dist_start = sum(dist(customers[r[i]], customers[r[i+1]])
                     for r in current_sol for i in range(len(r)-1))
    history.append({
        "iter": 0,
        "cost": current_cost,
        "dist": dist_start,
        "veh": v_start,
        "temp": T
    })

    print(f"Start koszt: {current_cost:.2f} | Pojazdów: {len(current_sol)}")

    move_types = ["kill", "transfer", "swap", "2opt"]
    move_weights = [
        params["w_kill"],
        params["w_transfer"],
        params["w_swap"],
        params["w_2opt"]
    ]

    iteration = 0

    while iteration < params["max_iterations"] and T > params["sa_T_min"]:
        iteration += 1

        chosen_move = random.choices(move_types, weights=move_weights, k=1)[0]

        changes = None

        if chosen_move == "kill":
            changes = op_kill_route(current_sol, customers, capacity)
        elif chosen_move == "transfer":
            changes = op_transfer(current_sol)
        elif chosen_move == "swap":
            changes = op_swap(current_sol)
        elif chosen_move == "2opt":
            changes = op_2opt_random(current_sol)

        if not changes:
            T *= params["sa_alpha"]
            continue

        # dla zaoszczedzenia obliczen, liczymy tylko zmiany w trasach
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

        delta = new_partial_cost - old_partial_cost  # obliczanie zmiany kosztu

        # poprawa lub losowość wyboru gorszego rozw
        if delta < 0 or random.random() < math.exp(-delta / T):
            for r_idx, new_route in changes:
                current_sol[r_idx] = new_route

            current_cost += delta  # zmiana kosztu o delte

            if current_cost < best_cost:
                best_cost = current_cost
                best_sol = [r[:] for r in current_sol]

        # chłodzenie
        T *= params["sa_alpha"]

        if iteration % params["sa_log_interval"] == 0:
            v_count = len([r for r in best_sol if len(r) > 2])
            dist_val = sum(dist(customers[r[i]], customers[r[i+1]])
                           for r in best_sol for i in range(len(r)-1))
            history.append({
                "iter": iteration,
                "cost": best_cost,
                "dist": dist_val,
                "veh": v_count,
                "temp": T
            })
            print(
                f"Iter: {iteration} | T: {T:.2f} | Best Cost: {best_cost:.2f} | Dist: {dist_val:.1f} | Veh: {v_count}")

    end_time = time.time()

    return best_sol, history, end_time - start_time


def save_results_to_json(run_data, filename):
    def convert(o):
        if isinstance(o, np.int64):
            return int(o)
        if isinstance(o, np.float64):
            return float(o)
        return o

    with open(filename, 'w') as f:
        json.dump(run_data, f, indent=4, default=convert)
    print(f"Wyniki zapisane do: {filename}")


def main():
    if not os.path.exists(CONFIG["save_dir"]):
        os.makedirs(CONFIG["save_dir"])

    customers, capacity = load_solomon(CONFIG["instance_path"])
    print(f"Załadowano {len(customers)-1} klientów. Pojemność: {capacity}")

    instance_name = os.path.splitext(
        os.path.basename(CONFIG["instance_path"]))[0]
    summary_stats = []
    NUM_RUNS = 5

    for run_id in range(1, NUM_RUNS + 1):
        print(f"URUCHOMIENIE {run_id}/{NUM_RUNS}")

        best_sol, history, exec_time = simulated_annealing(
            customers, capacity, CONFIG)

        final_sol = [r for r in best_sol if len(r) > 2]
        final_dist = sum(dist(customers[r[i]], customers[r[i+1]])
                         for r in final_sol for i in range(len(r)-1))
        final_vehicles = len(final_sol)
        final_cost = history[-1]["cost"]

        # Przygotowanie danych do JSON
        run_data = {
            "meta": {
                "instance": instance_name,
                "run_id": run_id,
                "timestamp": datetime.datetime.now().isoformat()
            },
            "parameters": CONFIG,
            "results": {
                "execution_time": exec_time,
                "final_cost": final_cost,
                "final_distance": final_dist,
                "final_vehicles": final_vehicles
            },
            "history": history,  # Pełna historia zbieżności
            "routes": final_sol  # Sama struktura tras
        }

        # Zapis do pliku: np. experiment_results/rc101_run_1.json
        filename = os.path.join(
            CONFIG["save_dir"], f"{instance_name}_run_{run_id}.json")
        save_results_to_json(run_data, filename)

        # Wizualizacja (opcjonalnie tylko dla najlepszego, tu zapisujemy każdą)
        viz_path = os.path.join(
            CONFIG["save_dir"], f"{instance_name}_run_{run_id}.png")
        visualize_solution(final_sol, customers,
                           title=f"Run {run_id} | Dist: {final_dist:.2f} | Veh: {final_vehicles}",
                           save_path=viz_path, show=False)  # Show False, żeby nie blokować pętli

        summary_stats.append({
            "run": run_id,
            "dist": final_dist,
            "veh": final_vehicles,
            "time": exec_time
        })

    print(f"Podsumowanie z {NUM_RUNS} uruchomien")
    dists = [s["dist"] for s in summary_stats]
    times = [s["time"] for s in summary_stats]
    vehs = [s["veh"] for s in summary_stats]

    avg_dist = np.mean(dists)
    std_dist = np.std(dists)
    best_dist = np.min(dists)
    worst_dist = np.max(dists)

    print(
        f"Dystans: Najlepszy: {best_dist:.2f}, Najgorszy: {worst_dist:.2f}, Średni: {avg_dist:.2f}, Std: {std_dist:.2f}")
    print(f"Pojazdy (średnio): {np.mean(vehs):.1f}")
    print(f"Czas (średnio): {np.mean(times):.2f}s")

    with open(os.path.join(CONFIG["save_dir"], f"{instance_name}_summary.txt"), "w") as f:
        f.write(f"Instance: {instance_name}\n")
        f.write(f"Runs: {NUM_RUNS}\n")
        f.write(f"Best Dist: {best_dist:.2f}\n")
        f.write(f"Worst Dist: {worst_dist:.2f}\n")
        f.write(f"Avg Dist: {avg_dist:.2f}\n")
        f.write(f"Std Dev: {std_dist:.2f}\n")
        f.write(f"Avg Time: {np.mean(times):.2f}s\n")
        f.write("-" * 20 + "\n")
        for s in summary_stats:
            f.write(
                f"Run {s['run']}: Dist={s['dist']:.2f}, Veh={s['veh']}, Time={s['time']:.2f}s\n")


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
