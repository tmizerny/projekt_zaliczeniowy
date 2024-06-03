from geopy import geocoders, distance

def najblizsze_stacje_pomiarowe(miejsce_wyszukiwania, promien_wyszukiwania, stacje_dict):
    geolocator = geocoders.Nominatim(user_agent="Stacje pomiarowe")
    location = geolocator.geocode(miejsce_wyszukiwania)
    centr_szerokosc, centr_dlugosc = location.latitude, location.longitude

    stacje_lista = []
    odleglosci_lista = []
    lokalizacja_stacji = {}

    for nazwa, lokalizacja in stacje_dict.items():
        odleglosc = (distance.distance((centr_szerokosc, centr_dlugosc), lokalizacja)
                     .kilometers)
        if odleglosc <= promien_wyszukiwania:
            stacje_lista.append(nazwa)
            odleglosci_lista.append(odleglosc)

            lokalizacja_stacji[nazwa] = lokalizacja

    wynik_lista = list(zip(stacje_lista, odleglosci_lista))
    wynik_lista = sorted(wynik_lista, key=lambda x: x[1])

    return [centr_szerokosc, centr_dlugosc], wynik_lista, lokalizacja_stacji




