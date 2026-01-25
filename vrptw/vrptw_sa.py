# vrptw_sa.py
import math
import random
import copy


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


# Poprawiona funkcja route_cost z bardziej agresywnymi karami:
def route_cost(route, customers, capacity):
    time = 0
    load = 0
    cost = 0
    penalty = 0
    time_window_penalty = 10000  # ZWIĘKSZONE (było 1000)
    capacity_penalty = 10000     # ZWIĘKSZONE (było 1000)

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
    vehicle_penalty = 1000000000  # ZWIĘKSZONE! (było 10000)

    for route in solution:
        if len(route) > 2:  # tylko niepuste trasy
            total += route_cost(route, customers, capacity)
            total += vehicle_penalty  # kara za każdy użyty pojazd

    # Dodatkowo: kara za puste trasy (jeśli takie są)
    for route in solution:
        if len(route) <= 2:
            total += vehicle_penalty * 0.5

    return total


def two_opt(route, customers, capacity):
    """Two-opt z faktycznym sprawdzaniem poprawy kosztu"""
    best_route = route.copy()
    best_cost = route_cost(route, customers, capacity)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                # Pomijamy jeśli sąsiadują
                if j - i == 1:
                    continue

                new_route = route[:i] + route[i:j][::-1] + route[j:]
                new_cost = route_cost(new_route, customers, capacity)

                if new_cost < best_cost:
                    best_route = new_route.copy()
                    best_cost = new_cost
                    improved = True
                    route = best_route.copy()
                    break  # zacznij od nowa po znalezieniu poprawy
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


def simulated_annealing(init_sol, customers, capacity,
                        T=10000, alpha=0.999, T_min=1e-5,
                        log_interval=100):

    current = copy.deepcopy(init_sol)
    best = copy.deepcopy(current)
    current_cost = solution_cost(current, customers, capacity)
    best_cost = current_cost

    iteration = 0
    print("[1] Rozpoczęcie symulowanego wyżarzania")

    while T > T_min:
        iteration += 1
        new = copy.deepcopy(current)

        # --- RÓŻNE TYPY RUCHÓW SĄSIEDZTWA ---
        move_type = random.random()

        # 30% - przeniesienie między trasami
        if move_type < 0.3 and len(new) > 1:
            # Wybierz trasę źródłową i docelową
            src_idx = random.randint(0, len(new)-1)
            dest_idx = random.randint(0, len(new)-1)
            if src_idx == dest_idx or len(new[src_idx]) <= 3:
                # Fallback do swap wewnętrznego
                r1 = random.choice(new)
                if len(r1) > 3:
                    i, j = random.sample(range(1, len(r1)-1), 2)
                    r1[i], r1[j] = r1[j], r1[i]
            else:
                # Przenieś losowego klienta (nie depot)
                if len(new[src_idx]) > 3:
                    cust_idx = random.randint(1, len(new[src_idx])-2)
                    customer = new[src_idx].pop(cust_idx)
                    # Wstaw w losowe miejsce w trasie docelowej
                    if len(new[dest_idx]) > 2:
                        pos = random.randint(1, len(new[dest_idx])-1)
                        new[dest_idx].insert(pos, customer)
                    else:
                        new[src_idx].insert(cust_idx, customer)  # przywróć

        elif move_type < 0.6:  # 30% - 2-opt wewnątrz trasy
            r_idx = random.randint(0, len(new)-1)
            if len(new[r_idx]) > 4:
                new[r_idx] = two_opt(new[r_idx], customers, capacity)

        else:  # 40% - swap wewnątrz trasy (oryginalny ruch)
            r1 = random.choice(new)
            if len(r1) > 3:
                i, j = random.sample(range(1, len(r1)-1), 2)
                r1[i], r1[j] = r1[j], r1[i]

        # --- OPTYMALIZACJA LOKALNA (nie zawsze) ---
        if random.random() < 0.3:  # 30% szans na lokalne poprawienie
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

        # --- LOGOWANIE ---
        if iteration % log_interval == 0:
            # tylko trasy z klientami
            vehicles = len([r for r in best if len(r) > 2])
            print(
                f"[iter {iteration:6d}] "
                f"T={T:8.3f} | "
                f"best_cost={best_cost:10.2f} | "
                f"vehicles={vehicles:3d} | "
                f"distance={pure_distance(best, customers):8.2f}"
            )

        T *= alpha

    return best


# Poprawiona funkcja inicjalizacji z próbą konsolidacji:
def build_initial_solution(customers, capacity):
    solution = []
    unassigned = list(range(1, len(customers)))

    # Posortuj klientów według czasu ready (najwcześniejsi pierwsi)
    unassigned.sort(key=lambda x: customers[x].ready)

    for cust_id in unassigned:
        c = customers[cust_id]
        inserted = False

        # Spróbuj wstawić do istniejących tras
        for route in solution:
            load = sum(customers[i].demand for i in route)
            if load + c.demand > capacity:
                continue

            # Sprawdź wszystkie możliwe pozycje
            best_pos = -1
            best_increase = float('inf')

            for pos in range(1, len(route)):
                new_route = route[:pos] + [cust_id] + route[pos:]
                increase = route_cost(new_route, customers, capacity) - \
                    route_cost(route, customers, capacity)

                if increase < best_increase:
                    best_increase = increase
                    best_pos = pos

            if best_pos != -1 and best_increase < 10000:  # Akceptowalny wzrost
                route.insert(best_pos, cust_id)
                inserted = True
                break

        if not inserted:
            solution.append([0, cust_id, 0])

    # Faza konsolidacji: spróbuj połączyć krótkie trasy
    improved = True
    while improved:
        improved = False
        for i in range(len(solution)):
            for j in range(i+1, len(solution)):
                if len(solution[i]) + len(solution[j]) - 4 <= 15:  # -4 bo dwa depoty
                    merged = solution[i][:-1] + solution[j][1:]  # połącz trasy
                    load = sum(customers[idx].demand for idx in merged)
                    if load <= capacity and route_cost(merged, customers, capacity) < 1000000:
                        solution[i] = merged
                        solution.pop(j)
                        improved = True
                        break
            if improved:
                break

    return solution
