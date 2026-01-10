Należy napisać program umożliwiający znalezienie ekstremum (minimum lub maksimum) dwóch wybranych funkcji dwóch zmiennych f(x,y) z udostępnionej listy funkcji (tutaj).

W tym celu należy zaimplementować algorytm roju cząstek (PSO – Particle Swarm Optimization) i wykorzystać go do optymalizacji każdej z wybranych funkcji.

Opracowany program powinien umożliwiać uruchomienie algorytmu dla różnych zestawów parametrów, a jego działanie powinno być zrozumiałe dla użytkownika.

Należy przygotować sprawozdanie, w którym należy:

Omówić zasady działania algorytmu - w jaki sposób w tym rozwiązaniu działa ustalenie pozycji cząstki, prędkości cząstki, najlepszego lokalnego i globalnego rozwiązania, zachowanie cząstek w kontekście ruchu inercyjnego, tendencji do poprawiania własnego wyniku (część kognitywna), tendencji do naśladowania najlepszej cząstki w roju (część socjalna).
Opisać zasadę działania algorytmu (np. pseudokod).
Opisać wybrane miejsca implementacji rozwiązania (implementacja kluczowych miejsc w algorytmie).
Opisać zasadę działania programu (instrukcja dla użytkownika).
Zaprojektować eksperymenty i je uzasadnić (opisać). Przy projektowaniu należy uwzględnić:
listę parametrów, które będą badane,
zakresy ich wartości,
opis planu eksperymentalnego (np. „zmieniamy jeden parametr, resztę trzymamy stałą”),
informację, że każdy zestaw parametrów musi być uruchomiony co najmniej 5 razy,
sposób obliczania wyników:
najlepszy wynik,
najgorszy wynik,
średni wynik (mean),
mediana,
odchylenie standardowe (std).
Przeprowadzić eksperymenty i zaprezentować wyniki w tabelach, wykresach itp.
Przeprowadzić analizę wyników:
Jak wybrane parametry wpływają na jakość wyników?
Czy algorytm jest stabilny (analiza std)?
Czy zaobserwowano szybkie czy wolne zbieganie do rozwiązania?
Czy pojawia się ryzyko utknięcia w minimum lokalnym?
Czy trudność obu funkcji była różna?
Wnioski:
Które konfiguracje PSO okazały się najlepsze?
Jaki wpływ miały parametry algorytmu?
Czy algorytm skutecznie znalazł minimum dla obu funkcji?

---

### FAZA 1: PRZYGOTOWANIE I ZROZUMIENIE PROBLEMU
- [x]] 1. Przeanalizować opis zadania i wszystkie wymagania
- [x] 2. Wybrać 2 funkcje dwóch zmiennych f(x,y) z dostępnej listy
- [ ] 3. Zdefiniować domeny dla wybranych funkcji (zakresy x i y)
- [ ] 4. Zdefiniować czy szukamy minimum czy maksimum dla każdej funkcji
- [x] 5. Zainstalować wymagane biblioteki (numpy, matplotlib, scipy itp.)

### FAZA 2: IMPLEMENTACJA ALGORYTMU PSO
- [x] 6. Stworzyć strukturę klasy `Particle` (pozycja, prędkość, fitness, best_position)

- [x] 8. Zaimplementować inicjalizację cząstek (random position i velocity)
- [x] 9. Zaimplementować funkcję evaluate() - ocena fitness
- [x] 10. Zaimplementować update_velocity() - aktualizacja prędkości (inercja + kognitywna + socjalna część)
- [x] 11. Zaimplementować update_position() - aktualizacja pozycji
- [x] 12. Zaimplementować mechanizm tracking global best (gbest)
- [x] 13. Zaimplementować mechanizm tracking personal best (pbest)
- [x] 14. Zaimplementować główną pętlę algorytmu optimize()
- [x] 15. Dodać obsługę ograniczeń (bounds) dla pozycji i prędkości
- [ ] 16. Dodać opcję wizualizacji procesu optymalizacji (ewentualnie)

### FAZA 3: INTERFACE UŻYTKOWNIKA
- [ ] 17. Stworzyć prosty interfejs CLI do wyboru funkcji
- [ ] 18. Umożliwić użytkownikowi ustawienie parametrów PSO interaktywnie
- [ ] 19. Dodać walidację danych wejściowych
- [ ] 20. Wyświetlać postęp algorytmu (iteracja, najlepszy wynik)
- [ ] 21. Zapisywać wyniki do pliku (np. CSV)

### FAZA 4: PRZYGOTOWANIE EKSPERYMENTÓW
- [ ] 22. Zdefiniować listę parametrów do badania (w, c1, c2, num_particles, num_iterations)
- [ ] 23. Zdefiniować zakresy wartości dla każdego parametru
- [ ] 24. Opisać plan eksperymentalny (jeden parametr się zmienia, reszta stała)
- [ ] 25. Przygotować skrypt do automatycznego uruchamiania eksperymentów
- [ ] 26. Zaimplementować funkcję do uruchamiania każdego zestawu parametrów 5+ razy

### FAZA 5: ZBIERANIE DANYCH
- [ ] 27. Uruchomić wszystkie eksperymenty i zebrać wyniki
- [ ] 28. Dla każdego zestawu parametrów obliczyć:
  - [ ] najlepszy wynik (min)
  - [ ] najgorszy wynik (max)
  - [ ] średni wynik (mean)
  - [ ] mediana
  - [ ] odchylenie standardowe (std)
- [ ] 29. Zorganizować wyniki w strukturyzowany format (CSV, JSON)

### FAZA 6: ANALIZA WYNIKÓW
- [ ] 30. Stworzyć wykresy wpływu każdego parametru na jakość wyników
- [ ] 31. Przeanalizować stabilność algorytmu (wartości std)
- [ ] 32. Przeanalizować zbieganie (krok po kroku osiągane wartości)
- [ ] 33. Sprawdzić ryzyko utknięcia w minimum lokalnym
- [ ] 34. Porównać trudność obu funkcji
- [ ] 35. Stworzyć tabele podsumowujące wyniki
- [ ] 36. Stworzyć wykresy (liniowe, słupkowe, box plot)

### FAZA 7: SPRAWOZDANIE
- [ ] 37. Opisać zasady działania PSO (pozycja, prędkość, best solutions)
- [ ] 38. Wyjaśnić wpływ parametrów (w, c1, c2) - inercja, kognitywna, socjalna część
- [ ] 39. Написать pseudokod algorytmu
- [ ] 40. Wyjaśnić kluczowe fragmenty implementacji (z kodem)
- [ ] 41. Opisać instrukcję dla użytkownika (jak uruchomić program)
- [ ] 42. Dołączyć projekt eksperymentów (parametry, zakresy, plan)
- [ ] 43. Dołączyć tabele z wynikami eksperymentów
- [ ] 44. Dołączyć wykresy i wizualizacje
- [ ] 45. Przeprowadzić dyskusję na temat wyników
- [ ] 46. Wyciągnąć wnioski (najlepsze konfiguracje, wpływ parametrów, efektywność)
- [ ] 47. Zaproponować potencjalne ulepszeń (ewentualnie)

### FAZA 8: FINALIZACJA
- [ ] 48. Przegląd całego kodu - czy jest czytelny i udokumentowany
- [ ] 49. Testy końcowe - sprawdzić czy program działa bez błędów
- [ ] 50. Przegląd sprawozdania - gramatyka, formatowanie, kompletność
- [ ] 51. Ostateczny commit/backup projektu


