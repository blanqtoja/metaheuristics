import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from logic import run_ACO

data = np.loadtxt("A-n32-k5.txt")
coords = data[:, 1:3]
n_citys = len(coords)


d = np.zeros((n_citys, n_citys))
for i in range(n_citys):
    for j in range(n_citys):
        d[i, j] = np.linalg.norm(coords[i] - coords[j])

iteration = 100
n_ants = 5
e = 0.5
alpha = 1
beta = 2

# Lista do zbierania wyników z wielu uruchomień
runs_best_cost = []

for run_idx in range(5):
    (best_route, 
        best_cost, 
        worst_route, 
        worst_cost,
        best_route_history,
        avg_cost_history,
        best_cost_history,
        time
    ) = run_ACO(
        d=d,
        iteration=iteration,
        n_ants=n_ants,
        n_citys=n_citys,
        e=e,
        alpha=alpha,
        beta=beta
    )

    runs_best_cost.append(best_cost)
    print(f"Run {run_idx+1}/5: best_cost={int(best_cost)}, time={time:.2f}s")

# Konwersja do DataFrame i statystyki
runs_df = pd.DataFrame(runs_best_cost, columns=['best_cost'])
print("\n=== Statystyki z 5 uruchomień ===")
print(runs_df.describe())
print(f"\nMediana: {runs_df['best_cost'].median():.2f}")

# Wyniki z ostatniego uruchomienia
print("\n=== Ostatnie uruchomienie ===")
print("Najlepsza trasa:")
print(best_route)
print("Koszt najlepszej trasy:", int(best_cost))
print(f"Czas wykonania: {time:.2f}s")

path = best_route.astype(int) - 1

plt.scatter(coords[:,0], coords[:,1])

for i in range(len(path)-2):
    x = [coords[path[i],0], coords[path[i+1],0]]
    y = [coords[path[i],1], coords[path[i+1],1]]
    plt.plot(x, y)

plt.title("Najkrótsza trasa zwiedzania")
plt.savefig("Najkrótsza trasa zwiedzania.png")
plt.show()

# Wykres zbieżności (z ostatniego uruchomienia)
plt.figure()
plt.plot(avg_cost_history, label="Średni koszt w iteracji", alpha=0.7)
plt.plot(best_cost_history, label="Najlepszy koszt (best-so-far)", linewidth=2)
plt.xlabel("Iteracja")
plt.ylabel("Koszt trasy")
plt.title("Zbieżność algorytmu ACO")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("zbieznosc_ACO.png")
plt.show()