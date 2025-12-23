import numpy as np

def run_ACO(d: np.array, iteration: int = 100, n_ants: int = 5, n_citys: int = 5, e: float = 0.5, alpha: float = 1, beta: float = 2):

    visibility = np.zeros_like(d)
    visibility[d > 0] = 1 / d[d > 0]

    pheromone = 0.1 * np.ones((n_citys, n_citys))

    route = np.zeros((n_ants, n_citys + 1), dtype=int)

    best_cost = np.inf
    best_route = None

    for ite in range(iteration):

        route[:, 0] = 1 # kazka mrowka odwiedza pierwsze miasto - startuje w 1 miescie

        for i in range(n_ants):  #iteracja po miastach
            visited = np.zeros(n_citys, dtype=bool)
            visited[0] = True  # city 1 visited

            for j in range(1, n_citys): #iteracja po miastach
                cur = route[i, j - 1] - 1 #wyciagamy aktualne miasto dla mrowki, odejmujemy 1 zeby dostac index 

                prob = (
                    pheromone[cur] ** alpha
                    * visibility[cur] ** beta
                ) # wyliczenie ze wzoru, dla calego wiersza macierzy - aktualne miasto

                prob[visited] = 0 # usun odwiedzone
                s = prob.sum()

                if s == 0:
                    prob[:] = 1 / n_citys
                else:
                    prob /= s #normalizacja

                next_city = np.random.choice(n_citys, p=prob) #losowanie z rozkladu prawdopodobienstwa

                route[i, j] = next_city + 1
                visited[next_city] = True

            route[i, -1] = route[i, 0] # powrot na start


        # unikamy petli, gdzie liczymy odleglosci do miast sasiadujacych na trasei
        a = route[:, :-1] - 1 #miasta startowe - bez ostatniego
        b = route[:, 1:] - 1 #miasta koncowe - bez pierwszego
        dist_cost = np.sum(d[a, b], axis=1)  
    
        idx = np.argmin(dist_cost)
        if dist_cost[idx] < best_cost:
            best_cost = dist_cost[idx]
            best_route = route[idx].copy()

        pheromone *= (1 - e) #parowanie feromonow

        delta = 1 / dist_cost

        for i in range(n_ants):
            np.add.at(
                pheromone,
                (a[i], b[i]),
                delta[i]
            )
            np.add.at(
                pheromone,
                (b[i], a[i]),
                delta[i]
            ) #dodaj delta[i] do wszystkich (a,b) z trasy mrówki

    return best_route, best_cost
