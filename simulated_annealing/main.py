import argparse
import math
import random

from simulated_annealing import simulate

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Symulowane wyżarzanie — minimalizacja funkcji jednej zmiennej."
    )

    parser.add_argument(
        "--x_min", type=float, help="Minimalna wartość x (domyślnie: -10)"
    )
    parser.add_argument(
        "--x_max", type=float, help="Maksymalna wartość x (domyślnie: 10)"
    )
    parser.add_argument(
        "--temperature", type=float, help="Początkowa temperatura (np. 100.0)"
    )
    parser.add_argument(
        "--alpha", type=float, help="Współczynnik chłodzenia (np. 0.95)"
    )
    parser.add_argument("--epochs", type=int, help="Liczba epok (np. 100)")
    parser.add_argument(
        "--steps", type=int, help="Liczba kroków w każdej epoce (np. 50)"
    )

    args = parser.parse_args()

    x_min = args.x_min if args.x_min is not None else float(input("Podaj x_min: "))
    x_max = args.x_max if args.x_max is not None else float(input("Podaj x_max: "))
    temperature = (
        args.temperature
        if args.temperature is not None
        else float(input("Podaj początkową temperaturę: "))
    )
    alpha = (
        args.alpha
        if args.alpha is not None
        else float(input("Podaj współczynnik chłodzenia (alpha): "))
    )
    epochs = (
        args.epochs if args.epochs is not None else int(input("Podaj liczbę epok: "))
    )
    steps = (
        args.steps
        if args.steps is not None
        else int(input("Podaj liczbę kroków w epoce: "))
    )

    print("\n=== Symulowane wyżarzanie ===")

    def fun(x):
        return (x - 2) ** 2 + math.sin(5 * x)

    result = simulate(
        fun,
        x_min,
        x_max,
        max_temperature=temperature,
        alpha=alpha,
        epochs=epochs,
        steps=steps,
    )

    print(f"\nNajlepsze znalezione x: {result}")
    print(f"Wartość funkcji: {fun(result)}")
