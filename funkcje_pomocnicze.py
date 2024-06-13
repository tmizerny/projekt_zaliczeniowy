"""
Moduł zawierający kilka funkcji pomocniczych
"""
import pandas as pd
import numpy as np

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


def stworz_wykres(df):
    """
    Funkcja tworzy wykres słupkowy oraz liniowy na podstawie ramki danych
    :param df: ramka danych
    :return: kombinowany wykres słupkowy i liniowy
    """
    # Wykres słupkowy
    wykres_bar = df.hvplot.bar(x='Data i godzina odczytu', color="teal").opts(xrotation=60,
                                                                              ylabel='Stężenie parametru',
                                                                              height=600,
                                                                              width=1200,
                                                                              align='center'
                                                                              )
    # Wyliczanie linii trendu metodą najmniejszych kwadratów
    trend = np.polyfit(range(len(df)), df['value'], 1)
    trend_line = np.polyval(trend, range(len(df)))

    trend_df = pd.DataFrame({
        'Data i godzina odczytu': df['Data i godzina odczytu'],
        'Trend': trend_line
    })

    # Tworzenie linii trendu dla uzyskanych wartości
    line_plot = trend_df.hvplot.line(x='Data i godzina odczytu', y='Trend', color='red')

    # Zwracanie kombinowanego wykresu
    return wykres_bar * line_plot


def sformatuj_dataframe(df):
    """
    Funkcja pomocnicza dla funkcji wczytaj_dane_dla_stacji formatująca dane do wykresu
    :param df: ramka danych
    :return: sformatowana ramka danych
    """
    # Zamiana danych na typ datetime
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    # Dostosowanie dat i godzin do formatu 00:00 dd/mm/yyyy
    df['Data i godzina odczytu'] = df.index.strftime('%H:%M %d/%m/%Y')
    # Odwrócenie kolejności (daty najwcześniejsze będą po lewej stronie wykresu)
    df = df[::-1]
    return df
