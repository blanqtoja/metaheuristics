import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json

from logic import run_PSO
from functions import fun_eggholder, fun_matyas

funs_dicts = [
    {"fun": fun_eggholder,
     "name": "eggholder"}, {"fun": fun_matyas, "name": "matyas"}]
exps = [
    {
        "exp_no": 1,
        "dimensions": 2,  # wymiary - ile zmiennych w funkcji matematycznej
        "no_particles": 20,  # liczba czasteczek
        "low_lim": 0,  # dolny zakres
        "high_lim": 10,  # gorny zakres
        "inertia_weight": 0.5,  # składowa bezwladnosci
        "cognitive_coefficient": 100,  # skladowa poznawcza
        "social_coefficient": 0.3,  # skladowa spoleczna
        "iteration": 100,  # liczba iteracji
    },

]


results = []  # zbieramy wszystkie wyniki

for fun_dict in funs_dicts:
    print(fun_dict["name"])

    for ex in exps:

        for run_idx in range(5):
            (
                best_pos,
                best_cost,
                time_run,
                g_best_pos_history,
                g_best_cost_history,
                avg_pos_history,
                avg_cost_history
            ) = run_PSO(
                fun=fun_dict["fun"],
                S=ex["no_particles"],
                dimensions=ex["dimensions"],
                blo=ex["low_lim"],
                bup=ex["high_lim"],
                inertia_weight=ex["inertia_weight"],
                cognitive_coefficient=ex["cognitive_coefficient"],
                social_coefficient=ex["social_coefficient"],
                iteration=ex["iteration"]
            )

            print(
                f'Run {run_idx+1}/5, function: {fun_dict["name"]}, exp: {ex["exp_no"]}: best_cost={best_cost:.4f}, time={time_run:.2f}s')

            # zapisujemy wszystkie wyniki, lacznie z nr uruchomienia
            results.append({
                "run_idx": run_idx,
                "function_name": fun_dict["name"],
                "exp_no": ex["exp_no"],
                "dimensions": ex["dimensions"],
                "no_particles": ex["no_particles"],
                "low_lim": ex["low_lim"],
                "high_lim": ex["high_lim"],
                "inertia_weight": ex["inertia_weight"],
                "cognitive_coefficient": ex["cognitive_coefficient"],
                "social_coefficient": ex["social_coefficient"],
                "iteration": ex["iteration"],
                "time_run": time_run,
                "best_pos": best_pos.tolist(),
                "best_cost": best_cost,
                "g_best_cost_history": g_best_cost_history,
                "avg_cost_history": avg_cost_history,
                "g_best_pos_history": [pos.tolist() for pos in g_best_pos_history],
                "avg_pos_history": [pos.tolist() for pos in avg_pos_history],
            })

# zapis do pliku JSON
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nWyniki zapisane do results.json")
print(f"Łącznie uruchomień: {len(results)}")
