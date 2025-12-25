import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from logic import run_ACO

# obsluga wielu plikow
files = ["A-n80-k10.txt" , "A-n32-k5.txt"]
datasets = []
for fname in files:

    data = np.loadtxt(fname)
    coords = data[:, 1:3]
    n_citys = len(coords)


    d = np.zeros((n_citys, n_citys))
    for i in range(n_citys):
        for j in range(n_citys):
            d[i, j] = np.linalg.norm(coords[i] - coords[j])

    datasets.append(
        {   
            "dataset": fname,
            "coords": coords.copy(),
            "n_citys": n_citys,
            "distances": d.copy(),
        }
    )

exps = [
    # Eksperyment 1 - Wpływ liczebności mrówek m
    {
        "exp_no": 1,
        "m": 10,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 1,
        "m": 20,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 1,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 1,
        "m": 100,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },

    # Eksperyment 2 - Wpływ losowości wyboru p_random
    {
        "exp_no": 2,
        "m": 50,  # mrowki
        "p_random": 0.0, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 2,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 2,
        "m": 50,  # mrowki
        "p_random": 0.05, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 2,
        "m": 50,  # mrowki
        "p_random": 0.1, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },

    # Eksperyment 3 - Wpływ współczynnika feromonów alfa

    {
        "exp_no": 3,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 0.5, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 3,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 3,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 2, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 3,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 5, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },

    # Eksperyment 4 - Wpływ współczynnika heurystyki beta

    {
        "exp_no": 4,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 1, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 4,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 2, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 4,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 4,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 10, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },

    # Eksperyment 5 - Wpływ liczby iteracji T

    {
        "exp_no": 5,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 10, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 5,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 50, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 5,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 5,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 500, # iteracje
        "p": 0.3, # parowanie feromonow
    },

    # Eksperyment 6 - Wpływ parowania feromonów pho

    {
        "exp_no": 6,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.1, # parowanie feromonow
    },
    {
        "exp_no": 6,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.3, # parowanie feromonow
    },
    {
        "exp_no": 6,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.5, # parowanie feromonow
    },
    {
        "exp_no": 6,
        "m": 50,  # mrowki
        "p_random": 0.01, # wybor losowego miasta
        "alpha": 1, # wplyw feromonow
        "beta": 5, # wplyw dystansu
        "T": 100, # iteracje
        "p": 0.8, # parowanie feromonow
    },
]



results = []  # zbieramy wszystkie wyniki

for dataset in datasets:
    print(dataset["dataset"])
    coords = dataset["coords"]
    n_citys = dataset["n_citys"]
    distances = dataset["distances"]

    for ex in exps:
        runs_best_cost = []
        all_best_history = []
        times = []

        for run_idx in range(5):
            (best_route, 
             best_cost, 
             worst_route, 
             worst_cost,
             best_route_history,
             avg_cost_history,
             best_cost_history,
             time_run
            ) = run_ACO(
                d=distances,
                iteration=ex["T"],
                n_ants=ex["m"],
                n_citys=n_citys,
                e=ex["p"],
                alpha=ex["alpha"],
                beta=ex["beta"],
            )

            runs_best_cost.append(best_cost)
            all_best_history.append(avg_cost_history)
            times.append(time_run)

            print(f"Run {run_idx+1}/5, dataset: {dataset["dataset"]}, exp: {ex["exp_no"]}: best_cost={int(best_cost)}, time={time_run:.2f}s")

        mean_best = np.mean(runs_best_cost)
        std_best = np.std(runs_best_cost)
        mean_time = np.mean(times)

        # zapisujemy średnie wyniki wraz z parametrami do listy
        results.append({
            "dataset": dataset["dataset"],
            "exp_no": ex["exp_no"],
            "m": ex["m"],
            "p_random": ex["p_random"],
            "alpha": ex["alpha"],
            "beta": ex["beta"],
            "T": ex["T"],
            "p": ex["p"],
            "time_run": time_run,
            "mean_best_cost": mean_best,
            "std_best_cost": std_best,
            "mean_time": mean_time,
            "best_route": best_route,
            "best_cost": best_cost,
            "worst_route": worst_route,
            "worst_cost": worst_cost,
            "avg_cost_history": avg_cost_history,  #średnia długość trasy
            "best_cost_history": best_cost_history,

        })

# konwersja do DataFrame
df_results = pd.DataFrame(results)
df_results.to_csv("results_ACO.csv", index=False)
print(df_results.head())



# for dataset in datasets:
#     # dataset dla danego pliku
#     coords = dataset["coords"]
#     n_citys = dataset["n_citys"]
#     distances = dataset["distances"]

#     #parametry dla danego eksperymentu
#     for ex in exps:

#         # Lista do zbierania wyników z wielu uruchomień
#         runs_best_cost = []
#         all_best_history = []

#         for run_idx in range(5):
#             (best_route, 
#                 best_cost, 
#                 worst_route, 
#                 worst_cost,
#                 best_route_history,
#                 avg_cost_history,
#                 best_cost_history,
#                 time
#             ) = run_ACO(
#                 d=distances,
#                 iteration=ex["T"],
#                 n_ants=ex["m"],
#                 n_citys=n_citys,
#                 e=ex["p"],
#                 alpha=ex["alpha"],
#                 beta=ex["beta"],
#             )

#             runs_best_cost.append(best_cost)
#             all_best_history.append(avg_cost_history)
#             print(f"Run {run_idx+1}/5: best_cost={int(best_cost)}, time={time:.2f}s")


#         mean = np.mean(all_best_history, axis=0)
#         std = np.std(all_best_history, axis=0)
#         x = np.arange(len(mean))

#         plt.plot(mean)
#         plt.fill_between(x, mean-std, mean+std, alpha=0.3)
#         plt.title("Średnia najlepszych wyników z 5 uruchomień")
#         plt.savefig("Średnia najlepszych wyników.png")
#         plt.show()
#         plt.clf()

#         # Konwersja do DataFrame i statystyki
#         runs_df = pd.DataFrame(runs_best_cost, columns=['best_cost'])
#         print("\n=== Statystyki z 5 uruchomień ===")
#         print(runs_df.describe())
#         print(f"\nMediana: {runs_df['best_cost'].median():.2f}")

#         # Wyniki z ostatniego uruchomienia
#         #todo: dodac subploty zeby byly widoczne wszystkie uruchomienia
#         print("\n=== Ostatnie uruchomienie ===")
#         print("Najlepsza trasa:")
#         print(best_route)
#         print("Koszt najlepszej trasy:", int(best_cost))
#         print(f"Czas wykonania: {time:.2f}s")

#         path = best_route.astype(int) - 1

#         plt.scatter(coords[:,0], coords[:,1])

#         for i in range(len(path)-2):
#             x = [coords[path[i],0], coords[path[i+1],0]]
#             y = [coords[path[i],1], coords[path[i+1],1]]
#             plt.plot(x, y)

#         for i, (x,y) in enumerate(coords):
#             plt.text(x, y, str(i+1))

#         plt.title("Najkrótsza trasa zwiedzania")
#         plt.savefig("Najkrótsza trasa zwiedzania.png")
#         plt.show()

#         # Wykres zbieżności (z ostatniego uruchomienia)
#         plt.figure()
#         plt.plot(avg_cost_history, label="Średni koszt w iteracji", alpha=0.7)
#         plt.plot(best_cost_history, label="Najlepszy koszt (best-so-far)", linewidth=2)
#         plt.xlabel("Iteracja")
#         plt.ylabel("Koszt trasy")
#         plt.title("Zbieżność algorytmu ACO")
#         plt.legend()
#         plt.grid(True, alpha=0.3)
#         plt.savefig("zbieznosc_ACO.png")
#         plt.show()