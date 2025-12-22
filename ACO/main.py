import numpy as np

d = np.array([
    [0,10,12,11,14],
    [10,0,13,15,8],
    [12,13,0,9,14],
    [11,15,9,0,16],
    [14,8,14,16,0]
], dtype=float)

iteration = 100
n_ants = 5
n_citys = 5

m = n_ants
n = n_citys
e = 0.5
alpha = 1
beta = 2

visibility = np.zeros_like(d)
visibility[d > 0] = 1 / d[d > 0]

pheromone = 0.1 * np.ones((n, n))

route = np.zeros((m, n + 1), dtype=int)

best_cost = np.inf
best_route = None

for ite in range(iteration):

    route[:, 0] = 1 # kazka mrowka odwiedza pierwsze miasto - startuje w 1 miescie

    for i in range(m):  #iteracja po miastach
        visited = np.zeros(n, dtype=bool)
        visited[0] = True  # city 1 visited

        for j in range(1, n): #iteracja po miastach
            cur = route[i, j - 1] - 1 #wyciagamy aktualne miasto dla mrowki, odejmujemy 1 zeby dostac index 

            prob = (
                pheromone[cur] ** alpha
                * visibility[cur] ** beta
            ) # wyliczenie ze wzoru, dla calego wiersza macierzy - aktualne miasto

            prob[visited] = 0 # usun odwiedzone
            s = prob.sum()

            if s == 0:
                prob[:] = 1 / n
            else:
                prob /= s #normalizacja

            next_city = np.random.choice(n, p=prob) #losowanie z rozkladu prawdopodobienstwa

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

    for i in range(m):
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

print("Najlepsza trasa:")
print(best_route)
print("Koszt najlepszej trasy:", int(best_cost))
