Dla każdego uruchomienia zapisz:
[x] Użyte parametry eksperymentu.
[x] Najlepsza uzyskana długość trasy (koszt) i trasa (kolejność atrakcji).
[x] Najgorsza i średnia długość trasy (jeśli mierzysz populację lub różne mrówki).
[x] Wartości najlepszej trasy w każdej iteracji (do wykresu).
[x] Czas wykonania.
[x] Dla zestawu powtórzeń oblicz statystyki: średnią arytmetyczną (mean), medianę (median), odchylenie standardowe (std), najgorszy wynik (min, najlepszy wynik (max) dla najlepszych wyników.



[ ] Jaki wpływ na wyniki ma liczebność mrówek?
[ ] Jaki wpływ na działanie algorytmu na wprowadzenie prawdopodobieństwa wyboru przez mrówkę losowej atrakcji?
[ ] Jaki wpływ na wyniki ma waga feromonów na potrzeby wyboru ścieżki przez mrówki - współczynnik α?
[ ] Jaki wpływ na wyniki ma waga heurystyki na potrzeby wyboru ścieżki przez mrówkę - współczynnik β?
[ ] Jaki wpływ na wyniki ma liczba iteracji?
[ ] Jaki wpływ na wyniki współczynnik wyparowywania feromonów?
[ ] Dla każdej odpowiedzi: podaj wykresy/tabele ilustrujące obserwacje, wnioski uargumentuj statystycznie (np. porównanie średnich), jeśli występują wyjątki lub niestandardowe zachowania (np. parametry zależne od rozmiaru instancji), opisz je.


Eksperyment 1 – Wpływ liczebności mrówek m

| Konfiguracja | m   | p_random | α   | β   | T   | ρ   |
| ------------ | --- | -------- | --- | --- | --- | --- |
| E1.1         | 10  | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E1.2         | 20  | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E1.3         | 50  | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E1.4         | 100 | 0.01     | 1.0 | 5.0 | 100 | 0.3 |




Eksperyment 2 – Wpływ losowości wyboru p_random
| Konfiguracja | m  | p_random | α   | β   | T   | ρ   |
| ------------ | -- | -------- | --- | --- | --- | --- |
| E2.1         | 50 | 0.0      | 1.0 | 5.0 | 100 | 0.3 |
| E2.2         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E2.3         | 50 | 0.05     | 1.0 | 5.0 | 100 | 0.3 |
| E2.4         | 50 | 0.1      | 1.0 | 5.0 | 100 | 0.3 |


Eksperyment 3 – Wpływ współczynnika feromonów α
| Konfiguracja | m  | p_random | α   | β   | T   | ρ   |
| ------------ | -- | -------- | --- | --- | --- | --- |
| E3.1         | 50 | 0.01     | 0.5 | 5.0 | 100 | 0.3 |
| E3.2         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E3.3         | 50 | 0.01     | 2.0 | 5.0 | 100 | 0.3 |
| E3.4         | 50 | 0.01     | 5.0 | 5.0 | 100 | 0.3 |


Eksperyment 4 – Wpływ współczynnika heurystyki β
| Konfiguracja | m  | p_random | α   | β    | T   | ρ   |
| ------------ | -- | -------- | --- | ---- | --- | --- |
| E4.1         | 50 | 0.01     | 1.0 | 1.0  | 100 | 0.3 |
| E4.2         | 50 | 0.01     | 1.0 | 2.0  | 100 | 0.3 |
| E4.3         | 50 | 0.01     | 1.0 | 5.0  | 100 | 0.3 |
| E4.4         | 50 | 0.01     | 1.0 | 10.0 | 100 | 0.3 |


Eksperyment 5 – Wpływ liczby iteracji T

| Konfiguracja | m  | p_random | α   | β   | T   | ρ   |
| ------------ | -- | -------- | --- | --- | --- | --- |
| E5.1         | 50 | 0.01     | 1.0 | 5.0 | 10  | 0.3 |
| E5.2         | 50 | 0.01     | 1.0 | 5.0 | 50  | 0.3 |
| E5.3         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E5.4         | 50 | 0.01     | 1.0 | 5.0 | 500 | 0.3 |


Eksperyment 6 – Wpływ parowania feromonów ρ

| Konfiguracja | m  | p_random | α   | β   | T   | ρ   |
| ------------ | -- | -------- | --- | --- | --- | --- |
| E6.1         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.1 |
| E6.2         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.3 |
| E6.3         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.5 |
| E6.4         | 50 | 0.01     | 1.0 | 5.0 | 100 | 0.8 |


[ ] Wyniki przedstaw w tabelach oraz na wykresach (numeruj tabele i wykresy i odnoś się do nich w tekście):
[ ] Tabela wyników + podsumowanie statystyk dla każdej konfiguracji.
[ ] Wykres średniej z 5 uruchomień oraz obszar pokazujący min–max (lub ± std).
[ ] Mapa trasy: wykres dwuwymiarowy punktów (atrakcji) z narysowaną najlepszą trasą (z etykietami lub numerami).
[ ] Wykresy porównań badanych parametrów.