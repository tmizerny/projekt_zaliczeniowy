from geopy import geocoders, distance


def najblizsze_stacje_pomiarowe(miejsce_wyszukiwania, promien_wyszukiwania, lista_stacji):
    geolocator = geocoders.Nominatim(user_agent="Stacje pomiarowe")
    location = geolocator.geocode(miejsce_wyszukiwania)
    centr_szerokosc, centr_dlugosc = location.latitude, location.longitude

    stacje_lista = []
    odleglosci_lista = []

    for stacja in lista_stacji:
        odleglosc = (distance.distance((centr_szerokosc, centr_dlugosc), (stacja['gegrLat'], stacja['gegrLon']))
                     .kilometers)
        if odleglosc <= promien_wyszukiwania:
            stacje_lista.append(stacja['stationName'])
            odleglosci_lista.append(odleglosc)

    wynik_lista = list(zip(stacje_lista, odleglosci_lista))
    wynik_lista = sorted(wynik_lista, key=lambda x: x[1])
    return wynik_lista


