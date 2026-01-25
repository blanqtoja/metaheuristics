import os
import math
import random
import copy
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np


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


def route_cost(route, customers, capacity):
    time = 0
    load = 0
    cost = 0
    penalty = 0
    time_window_penalty = 10000
    capacity_penalty = 10000

    for i in range(len(route) - 1):
        c1 = customers[route[i]]
        c2 = customers[route[i + 1]]

        travel = dist(c1, c2)
        time += travel

        if time < c2.ready:
            time = c2.ready
        if time > c2.due:
            penalty += time_window_penalty * (time - c2.due)

        time += c2.service
        load += c2.demand
        cost += travel

    if load > capacity:
        penalty += capacity_penalty * (load - capacity)

    return cost + penalty


def solution_cost(solution, customers, capacity):
    total = 0
    vehicle_penalty = 500000  # Zmniejszone z 1000000000

    for route in solution:
        if len(route) > 2:  # tylko niepuste trasy
            total += route_cost(route, customers, capacity)
            total += vehicle_penalty  # kara za każdy użyty pojazd

    return total


def two_opt(route, customers, capacity):
    best_route = route.copy()
    best_cost = route_cost(route, customers, capacity)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if j - i == 1:
                    continue

                new_route = route[:i] + route[i:j][::-1] + route[j:]
                new_cost = route_cost(new_route, customers, capacity)

                if new_cost < best_cost:
                    best_route = new_route.copy()
                    best_cost = new_cost
                    improved = True
                    route = best_route.copy()
                    break
            if improved:
                break
        route = best_route.copy()

    return best_route


def pure_distance(solution, customers):
    total = 0
    for route in solution:
        for i in range(len(route) - 1):
            total += dist(customers[route[i]], customers[route[i + 1]])
    return total


def visualize_solution(solution, customers, title="", save_path=None, show=True):
    """Wizualizacja rozwiązania"""
    plt.figure(figsize=(12, 10))

    # Kolory dla różnych tras
    colors = plt.cm.tab20(np.linspace(0, 1, len(solution)))

    # Rysuj każdą trasę
    for idx, route in enumerate(solution):
        if len(route) <= 2:
            continue

        color = colors[idx % len(colors)]
        x_coords = [customers[i].x for i in route]
        y_coords = [customers[i].y for i in route]

        # Rysuj linię trasy
        plt.plot(x_coords, y_coords, 'o-', linewidth=2, markersize=8,
                 color=color, alpha=0.7, label=f'Pojazd {idx+1}')

        # Rysuj strzałki kierunku
        for i in range(len(route)-1):
            dx = customers[route[i+1]].x - customers[route[i]].x
            dy = customers[route[i+1]].y - customers[route[i]].y
            plt.arrow(customers[route[i]].x, customers[route[i]].y,
                      dx*0.8, dy*0.8,
                      head_width=1.0, head_length=1.5,
                      fc=color, ec=color, alpha=0.5)

    # Oznacz depot na czerwono
    depot = customers[0]
    plt.plot(depot.x, depot.y, 'rs', markersize=15,
             label='Depot', markerfacecolor='red')

    # Dodaj etykiety dla klientów
    for c in customers[1:]:
        plt.text(c.x, c.y+0.5, str(c.id), fontsize=8, ha='center')
        plt.plot(c.x, c.y, 'ko', markersize=6)

    plt.title(
        f"{title}\nPojazdy: {len([r for r in solution if len(r) > 2])}, Dystans: {pure_distance(solution, customers):.2f}")
    plt.xlabel("Współrzędna X")
    plt.ylabel("Współrzędna Y")
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
    if show:
        plt.show()
    else:
        plt.close()


def visualize_improvement_history(history, save_path=None):
    """Wizualizacja historii poprawy kosztu"""
    plt.figure(figsize=(12, 6))

    iterations = [h[0] for h in history]
    costs = [h[1] for h in history]
    vehicles = [h[2] for h in history]

    # Koszt w czasie
    plt.subplot(1, 2, 1)
    plt.plot(iterations, costs, 'b-', linewidth=2)
    plt.xlabel('Iteracja')
    plt.ylabel('Koszt całkowity')
    plt.title('Zmiana kosztu w czasie')
    plt.grid(True, alpha=0.3)

    # Liczba pojazdów w czasie
    plt.subplot(1, 2, 2)
    plt.plot(iterations, vehicles, 'r-', linewidth=2)
    plt.xlabel('Iteracja')
    plt.ylabel('Liczba pojazdów')
    plt.title('Zmiana liczby pojazdów w czasie')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def simulated_annealing(init_sol, customers, capacity,
                        T=10000, alpha=0.999, T_min=1e-5,
                        log_interval=100, visualize=False, save_dir=None):

    current = copy.deepcopy(init_sol)
    best = copy.deepcopy(current)
    current_cost = solution_cost(current, customers, capacity)
    best_cost = current_cost

    iteration = 0
    improvement_history = []

    print("[1] Rozpoczęcie symulowanego wyżarzania")

    # Wizualizacja początkowa
    if visualize:
        visualize_solution(current, customers,
                           title=f"Rozwiązanie początkowe - Iteracja 0\nKoszt: {current_cost:.2f}",
                           save_path=f"{save_dir}/initial.png" if save_dir else None,
                           show=False)

    while T > T_min:
        iteration += 1
        new = copy.deepcopy(current)

        # Zapamiętaj stan przed ruchem (do wizualizacji)
        if visualize and iteration % log_interval == 0:
            old_solution = copy.deepcopy(current)

        # --- RÓŻNE TYPY RUCHÓW SĄSIEDZTWA ---
        move_type = random.random()
        move_description = ""

        # 30% - przeniesienie między trasami
        if move_type < 0.3 and len(new) > 1:
            src_idx = random.randint(0, len(new)-1)
            dest_idx = random.randint(0, len(new)-1)
            if src_idx == dest_idx or len(new[src_idx]) <= 3:
                r1 = random.choice(new)
                if len(r1) > 3:
                    i, j = random.sample(range(1, len(r1)-1), 2)
                    r1[i], r1[j] = r1[j], r1[i]
                    move_description = f"swap wewnątrz trasy {src_idx}"
            else:
                if len(new[src_idx]) > 3:
                    cust_idx = random.randint(1, len(new[src_idx])-2)
                    customer = new[src_idx].pop(cust_idx)
                    if len(new[dest_idx]) > 2:
                        pos = random.randint(1, len(new[dest_idx])-1)
                        new[dest_idx].insert(pos, customer)
                        move_description = f"przeniesienie klienta {customer} z trasy {src_idx} do {dest_idx}"
                    else:
                        new[src_idx].insert(cust_idx, customer)

        elif move_type < 0.6:  # 30% - 2-opt wewnątrz trasy
            r_idx = random.randint(0, len(new)-1)
            if len(new[r_idx]) > 4:
                new[r_idx] = two_opt(new[r_idx], customers, capacity)
                move_description = f"2-opt na trasie {r_idx}"

        else:  # 40% - swap wewnątrz trasy
            r1 = random.choice(new)
            if len(r1) > 3:
                i, j = random.sample(range(1, len(r1)-1), 2)
                r1[i], r1[j] = r1[j], r1[i]
                move_description = f"swap wewnątrz losowej trasy"

        # --- OPTYMALIZACJA LOKALNA ---
        if random.random() < 0.3:
            for k in range(len(new)):
                if len(new[k]) > 3:
                    new[k] = two_opt(new[k], customers, capacity)

        # --- OCENA ---
        new_cost = solution_cost(new, customers, capacity)
        delta = new_cost - current_cost

        if delta < 0 or random.random() < math.exp(-delta / T):
            current = new
            current_cost = new_cost

        if current_cost < best_cost:
            best = copy.deepcopy(current)
            best_cost = current_cost
            if visualize and iteration % log_interval == 0:
                print(
                    f"*** NOWE NAJLEPSZE ROZWIĄZANIE w iteracji {iteration} ***")
                print(f"Poprawa: {best_cost - current_cost:.2f}")

        # --- ZAPIS HISTORII ---
        if iteration % log_interval == 0:
            vehicles_count = len([r for r in best if len(r) > 2])
            improvement_history.append((iteration, best_cost, vehicles_count))

            print(
                f"[iter {iteration:6d}] "
                f"T={T:8.3f} | "
                f"best_cost={best_cost:10.2f} | "
                f"vehicles={vehicles_count:3d} | "
                f"distance={pure_distance(best, customers):8.2f}"
            )

            if move_description:
                print(f"    Ostatni ruch: {move_description}")

            # Wizualizacja co określoną liczbę iteracji
            if visualize and iteration % (log_interval * 10) == 0:
                visualize_solution(best, customers,
                                   title=f"Rozwiązanie - Iteracja {iteration}\nKoszt: {best_cost:.2f}, T={T:.2f}",
                                   save_path=f"{save_dir}/iteration_{iteration}.png" if save_dir else None,
                                   show=False)

        T *= alpha

    print("\n=== KONIEC SYMULOWANEGO WYŻARZANIA ===")
    print(f"Iteracje: {iteration}")
    print(f"Liczba pojazdów: {len([r for r in best if len(r) > 2])}")
    print(f"Koszt: {best_cost:.2f}")
    print(f"Dystans: {pure_distance(best, customers):.2f}")

    # Wizualizacja końcowa
    if visualize:
        visualize_solution(best, customers,
                           title=f"Rozwiązanie końcowe - Iteracja {iteration}\nKoszt: {best_cost:.2f}",
                           save_path=f"{save_dir}/final.png" if save_dir else None,
                           show=True)

        # Wizualizacja historii
        visualize_improvement_history(improvement_history,
                                      save_path=f"{save_dir}/history.png" if save_dir else None)

    return best, improvement_history


def build_initial_solution(customers, capacity):
    solution = []
    unassigned = list(range(1, len(customers)))

    unassigned.sort(key=lambda x: customers[x].ready)

    for cust_id in unassigned:
        c = customers[cust_id]
        inserted = False

        for route in solution:
            load = sum(customers[i].demand for i in route)
            if load + c.demand > capacity:
                continue

            best_pos = -1
            best_increase = float('inf')

            for pos in range(1, len(route)):
                new_route = route[:pos] + [cust_id] + route[pos:]
                increase = route_cost(new_route, customers, capacity) - \
                    route_cost(route, customers, capacity)

                if increase < best_increase:
                    best_increase = increase
                    best_pos = pos

            if best_pos != -1 and best_increase < 10000:
                route.insert(best_pos, cust_id)
                inserted = True
                break

        if not inserted:
            solution.append([0, cust_id, 0])

    # Faza konsolidacji
    improved = True
    while improved:
        improved = False
        for i in range(len(solution)):
            for j in range(i+1, len(solution)):
                if len(solution[i]) + len(solution[j]) - 4 <= 15:
                    merged = solution[i][:-1] + solution[j][1:]
                    load = sum(customers[idx].demand for idx in merged)
                    if load <= capacity and route_cost(merged, customers, capacity) < 1000000:
                        solution[i] = merged
                        solution.pop(j)
                        improved = True
                        break
            if improved:
                break

    return solution


def main():

    customers, capacity = load_solomon("rc101.txt")

    # Utwórz folder na wyniki wizualizacji
    save_dir = "visualization_results"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Utworzono folder: {save_dir}")

    # Zbuduj rozwiązanie początkowe
    print("\nBudowanie rozwiązania początkowego...")
    init_solution = build_initial_solution(customers, capacity)
    print(f"Rozwiązanie początkowe: {len(init_solution)} pojazdów")
    print(
        f"Koszt początkowy: {solution_cost(init_solution, customers, capacity):.2f}")
    print(f"Dystans początkowy: {pure_distance(init_solution, customers):.2f}")

    # Uruchom symulowane wyżarzanie z wizualizacją
    print("\nUruchamianie symulowanego wyżarzania...")
    best_solution, history = simulated_annealing(
        init_solution, customers, capacity,
        T=10000, alpha=0.9995, T_min=1e-5,
        log_interval=100,
        visualize=True,
        save_dir=save_dir
    )

    # Wyświetl szczegóły najlepszego rozwiązania
    print("\n=== SZCZEGÓŁY NAJLEPSZEGO ROZWIĄZANIA ===")
    for i, route in enumerate(best_solution):
        if len(route) > 2:
            route_load = sum(customers[idx].demand for idx in route)
            route_dist = sum(dist(customers[route[j]], customers[route[j+1]])
                             for j in range(len(route)-1))
            print(f"Pojazd {i+1}: {route}")
            print(
                f"  Klienci: {len(route)-2}, Ładunek: {route_load}/{capacity}, Dystans: {route_dist:.2f}")


if __name__ == "__main__":
    main()
