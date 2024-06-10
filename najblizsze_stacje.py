"""
Moduł zawieracjący funkcje szukająca najbliższe stacje pomiarowe
"""


from geopy import geocoders, distance

def najblizsze_stacje_pomiarowe(miejsce_wyszukiwania, promien_wyszukiwania, stacje_dict):
    """
    Funkcja wyszukuje najbliższe stacje pomiarowe od podanego przez użytkownika miejsca i promienia
    za pomocą paczki geopy
    :param miejsce_wyszukiwania: tekst zawierający środek miejsca wyszukiwania
    :param promien_wyszukiwania: promień wyszukiwania stacji pomiarowych
    :param stacje_dict: słownik przeszukiwanych lokalizacji
    :return: [lista długość geograficzna, szerokość geograficzna] miejsca_wyszukiwania, posortowaną
    listę krotek (odległość od centrum, nazwy znalezionych stacji) oraz
    słownik {nazwy wyszukanych stacji: [lista współrzędnych]
    """

    # Znalezienie współrzędnych podanego przez użytkownika miejsca
    geolocator = geocoders.Nominatim(user_agent="Stacje pomiarowe")
    location = geolocator.geocode(miejsce_wyszukiwania)
    centr_szerokosc, centr_dlugosc = location.latitude, location.longitude

    # Tworzenie list oraz słownika na wyniki
    stacje_lista = []
    odleglosci_lista = []
    lokalizacja_stacji = {}

    # Pętla przeszukująca podany słownik oraz zapis stacji spełniających kryterium
    for nazwa, lokalizacja in stacje_dict.items():
        odleglosc = (distance.distance((centr_szerokosc, centr_dlugosc), lokalizacja)
                     .kilometers)
        if odleglosc <= promien_wyszukiwania:
            stacje_lista.append(nazwa)
            odleglosci_lista.append(odleglosc)

            lokalizacja_stacji[nazwa] = lokalizacja

    # Sortowanie wyników
    wynik_lista = list(zip(stacje_lista, odleglosci_lista))
    wynik_lista = sorted(wynik_lista, key=lambda x: x[1])

    return [centr_szerokosc, centr_dlugosc], wynik_lista, lokalizacja_stacji




