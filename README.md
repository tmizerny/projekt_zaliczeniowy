# Jakość powietrza w Polsce 

## Aplikacja webowa służaca do wyświetlania danych pomiarowych dotyczących jakości powietrza w Polsce

### Opis

Program wykorzystuje framework Holovitz Panel do stworzenia aplikacji webowej, która pobiera dane z usługi REST, przetwarza otrzymaną odpowiedź oraz prezentuje dane w postaci dynamicznego dashboardu.

### Uruchamianie aplikacji

Aby uruchomić aplikację należy uruchomić lokalny host wpisująć w terminalu komendę: 
**panel serve app.py --autoreload**

Aplikacja **pobiera dane** z usługi REST prowadzonej prze GIOS. W przypadku braku połączenia z usługą program **obsługuje wyjątki** przy braku dostępności usługi czy braku łączności. Za wyświetlanie wiadomości error handlera odpowiedzialny jest widget z alertami.
Użytkownik jest napierw poproszony o wybranie źródła danych. 
Następnie użytkownik otrzymuje **pełną listę** nazw stacji w Polsce. 
Użytkownik może **sprawdzić listę najbliższych stacji pomiarowych** w podanym przez siebie promieniu. Aplikacja **wyświetla mapę** z naniesionymi stacjami oraz **listę** najbliższych stacji pomiarowych.
Aplikacja umożliwia wpisanie miejscowości w której użytkownik chce znaleźć stacje pomiarowe., a następnie **filtruje** stacje pomiarowe do tych w wybranym mieście.

Po wybraniu stacji pomiarowej i wciśnięciu przycisku wczytaj dane dla stacji aplikacja **aktualizuje panel** zawierający dane dla stacji, do których należą:

- mapa lokalizacyjna stacji pomiarowej
- krótki opis stacji pomiarowej zawierający najważniejsze informacje
- menu select dostępnych dla stacji parametrów pomiarowych
- wartości charakterystyczne dla danych pomiarowych (indeks stacji oraz indeksy parametrów dynamicznie zmieniają kolor czcionki w zależności od jakości powietrza)
- wykres słupkowy wraz z linią trendu dla danych pomiarowych
- suwak DateTime umożliwiający przesunięcie zakresu danch na wykresie (przesunięcie slidera **dynamicznie aktualizuje** wykres oraz wartości charakterystyczne)

Program umożliwia zapisanie danych w bazie danych ORM. Zgrywanie pomiarów dla **wszystkich** stacji pomiarowych trwa około 15 min. Postęp można śledzić w terminalu (pokazane jest dodawanie kolejnych stacji). 
Użytkownika aplikacji webowej powiadamia alert wyświetlający informacje o zakończeniu dodawnia danych do bazy danych. 

Program podzielony jest w miarę możliwości na moduły. Większa objętość głownego modułu programu app.py spowodowana jest brakiem możliwości modularyzacji inicjalizatorów widgetów oraz funkcji odwołujących się do funkcjonalności widgetów (obsługa eventów oraz zmiania atrybutów .value widgetów). Próba modularyzacji takiego kodu crashowała aplikacje. 

Aplikacja wyposażona jest w kilka testów jednostkowych testujących zgodność modelu danych z oczekiwanym.
