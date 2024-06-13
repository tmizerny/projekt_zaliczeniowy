# Jakość powietrza w Polsce 


### Opis

Aplikacja służy do wyświetlania danych dla stacji pomiarowych dotyczących jakości powietrza w Polsce. Program wykorzystuje framework HoloViz Panel do stworzenia aplikacji webowej, która pobiera dane (usługa REST, baza danych), przetwarza otrzymaną odpowiedź oraz prezentuje dane w postaci dynamicznego dashboardu.

### Uruchamianie Aplikacji

Aby uruchomić aplikację należy uruchomić lokalny host wpisująć w terminalu komendę: 

panel serve app.py --autoreload

### Funkcjonalności

- Pobieranie Danych: Aplikacja pobiera dane z usługi REST prowadzonej przez GIOS - https://powietrze.gios.gov.pl/pjp/content/api
- Obsługa Wyjątków: W przypadku braku połączenia lub pustej bazy danych
- Wybór Źródła Danych: Użytkownik wybiera źródło danych (Usługa REST lub Baza danych)
- Lista Stacji: Użytkownik otrzymuje pełną listę nazw stacji w Polsce.
- Najbliższe Stacje: Użytkownik może sprawdzić listę najbliższych stacji pomiarowych w podanym promieniu. Aplikacja wyświetla mapę z naniesionymi stacjami oraz listę najbliższych stacji pomiarowych.
- Filtracja po Miejscowości: Aplikacja umożliwia wpisanie miejscowości, w której użytkownik chce znaleźć stacje pomiarowe, a następnie filtruje stacje do wybranego miasta.

### Szczegóły Wybranej Stacji

Po wybraniu stacji pomiarowej i wciśnięciu przycisku "wczytaj dane dla stacji" aplikacja **aktualizuje panel** zawierający dane dla stacji:

- mapa lokalizacyjna stacji pomiarowej
- krótki opis stacji pomiarowej zawierający najważniejsze informacje
- menu select dostępnych dla stacji parametrów pomiarowych
- wartości charakterystyczne dla danych pomiarowych (indeks stacji oraz indeksy parametrów dynamicznie zmieniają kolor czcionki w zależności od jakości powietrza)
- wykres słupkowy wraz z linią trendu dla danych pomiarowych
- suwak DateTime umożliwiający przesunięcie zakresu danch na wykresie (przesunięcie slidera **dynamicznie aktualizuje** wykres oraz wartości charakterystyczne)

### Zapis Danych

Program umożliwia zapisanie danych w bazie danych ORM. Zgrywanie pomiarów dla **wszystkich** stacji pomiarowych trwa około 15 min. Postęp można śledzić w terminalu (pokazane jest dodawanie kolejnych stacji). 
Użytkownika aplikacji webowej powiadamia alert wyświetlający informacje o zakończeniu dodawnia danych do bazy danych. 

### Struktura programu (modularyzacja)

Program jest podzielony na moduły, jednak ze względu na ograniczenia frameworku, niektóre inicjalizatory widgetów oraz funkcje obsługujące eventy i zmiany atrybutów .value widgetów muszą znajdować się w głównym module app.py. Próby modularyzacji tego kodu powodowały awarie aplikacji.

### Testy jednostkowe

Aplikacja wyposażona jest w kilka testów jednostkowych testujących zgodność modelu danych z oczekiwanym.
