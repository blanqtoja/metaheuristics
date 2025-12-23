import matplotlib.pyplot as plt
import numpy as np


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

best_route, best_cost = run_ACO(
                            d=d,
                            iteration=iteration,
                            n_ants=n_ants,
                            n_citys=n_citys,
                            e=e,
                            alpha=alpha,
                            beta=beta
                        )


print("Najlepsza trasa:")
print(best_route)
print("Koszt najlepszej trasy:", int(best_cost))

path = best_route.astype(int) - 1

plt.scatter(coords[:,0], coords[:,1])

for i in range(len(path)-2):
    x = [coords[path[i],0], coords[path[i+1],0]]
    y = [coords[path[i],1], coords[path[i+1],1]]
    plt.plot(x, y)

plt.title("Najkrótsza trasa zwiedzania")
plt.savefig("dsa.png")
plt.show()
