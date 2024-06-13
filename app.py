"""
Główny moduł aplikacji
"""

from funkcje_pomocnicze import najblizsze_stacje_pomiarowe, stworz_wykres, sformatuj_dataframe
from baza_danych import (wczytaj_stacje_bd, wczytaj_lokalizacje_bd, wczytaj_parametry_bd,
                         wczytaj_parametry_z_pomiarami_bd, wczytaj_indeksy_stacji_parametrow_bd, dodaj_do_bazy_danych)

import panel as pn
import pandas as pd
import requests
import folium
import numpy as np
import hvplot.pandas

pn.extension()


def pobierz_dane(option, index=None):
    """
    Funkcja wysyłająca zapytanie do usługi REST
    :param option: wybór url'a, do którego ma zostać wysłane zapytanie
    :param index: dodatkowy argument do zapytania (indeks stacji, czujnika, indeksu jakiści powietrza)
    :return: odpowiedź od usługi REST w postaci pliku JSON
    """
    url = ''
    # Opcje wyboru url'a
    match option:
        # Lista wszystkich stacji pomiarowych
        case 1:
            url = 'https://api.gios.gov.pl/pjp-api/rest/station/findAll'
        # Czujniki danej stacji pomiarowej
        case 2:
            url = 'https://api.gios.gov.pl/pjp-api/rest/station/sensors/'
        # Pomiary z danego czujnika
        case 3:
            url = 'https://api.gios.gov.pl/pjp-api/rest/data/getData/'
        # Indeks jakości powietrza
        case 4:
            url = 'https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/'

    request = url + str(index) if index else url
    # Obsługa błędów przy wysyłaniu zapytania w przypadku błedu wywołanie funkcji aktualizuj_alert
    try:
        req = requests.get(request)
    except requests.exceptions.HTTPError as http_error:
        http_error_message = f'[{http_error}] Błąd protokołu HTTP. Spróbuj skorzystać z bazy danych'
        aktualizuj_alert(http_error_message)
    except requests.exceptions.ConnectionError as connection_error:
        connection_error_message = (f'[{connection_error}] Brak połącznia z serwisem GIOS. Spróbuj skorzystać z bazy'
                                    f'danych')
        aktualizuj_alert(connection_error_message)
    except requests.exceptions.Timeout as timeout_error:
        timeout_error_message = f'[{timeout_error}] Błąd odpowiedz od serwera. Spróbuj skorzystać z bazy danych'
        aktualizuj_alert(timeout_error_message)
    except Exception as exp:
        exp_message = f'[{exp}] Nieoczekiwany błąd. Spróbuj lub spróbuj skorzystać z bazy danych'
        aktualizuj_alert(exp_message)
    else:
        return req.json()


def wczytaj_wszystkie_stacje():
    """
    Funkcja buduje słownik {nazwa stacji: id stacji} z odpowiedzi z funkcji pobierz_dane
    :return: słownik {nazwa stacji: id stacji}
    """
    return {stacja['stationName']: stacja['id'] for stacja in pobierz_dane(1)}


def wczytaj_wszystkie_lokalizacje():
    """
    Funkcja buduje słownik {nazwa stacji: [długość_geograficzna, szerokość_geograficzna]}
    z odpowiedzi z funkcji pobierz_dane
    :return:słownik {nazwa stacji: [długość_geograficzna, szerokość_geograficzna]}
    """
    return {stacja['stationName']: [stacja['gegrLat'], stacja['gegrLon']] for stacja in pobierz_dane(1)}


# Tworzenie słowników na stacje pomiarowe
wszystkie_stacje_pomiarowe = {}
wszystkie_lokalizacje = {}

# Inicjalizacja widgetów obsługujących wczytanie źródła danych
## Wybór źródła danych
zrodlo_danych_select = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?",
                                         name='Wybierz źródło danych',
                                         options=['Usługa REST', 'Baza danych'])
# Guzik zatwierdzający źródło danych
zrodlo_danych_button = pn.widgets.Button(name='Załaduj dane')


def przelacz_widgety(opcja):
    """
    Funkcja pomocnicza dla załaduj_dane. Włącza lub wyłącza dostępność widgetów w zależności od potrzeby
    :param opcja: True-widgety wyłączone False-widgety włączone
    """
    stacje_select_all.disabled = opcja
    miasto_input.disabled = opcja
    lokalizacja_input.disabled = opcja
    dystans_input.disabled = opcja
    miasto_input_button.disabled = opcja
    promien_szukaj_button.disabled = opcja


def zaladuj_dane(event):
    """
    Funkcja obsugujaca wszytanie danych do aplikacji w zaleznosci od wybranego ich źródła

    W zależności od wybranego źródła danych funkcja wczytuje stacje pomiarowe (id i lokalizacje),
    zmienia menu select wszystkich wyszukanych stacji oraz zmienia jego nazwę
    :param event: argument obsługujący wciśnięcie guzika zrodlo_danych_button (event)
    """
    # Wyczyszczenie ewentualnej zawartości słowników z poprzedniego użytkowania aplikacji
    global wszystkie_stacje_pomiarowe
    global wszystkie_lokalizacje
    wszystkie_lokalizacje.clear()
    wszystkie_stacje_pomiarowe.clear()

    if zrodlo_danych_select.value == 'Usługa REST':
        wszystkie_stacje_pomiarowe = wczytaj_wszystkie_stacje()
        stacje_select_all.options = [*wszystkie_stacje_pomiarowe.keys()]
        stacje_select_all.name = 'Wszystkie stacje pomiarowe z Usługi REST'
        wszystkie_lokalizacje = wczytaj_wszystkie_lokalizacje()
        # włączenie widgetów
        przelacz_widgety(False)
        aktualizuj_alert('Pobrano dane z usługi REST', typ='success')

    elif zrodlo_danych_select.value == 'Baza danych':
        wszystkie_stacje_pomiarowe = wczytaj_stacje_bd()
        if not wszystkie_stacje_pomiarowe:
            aktualizuj_alert('Baza danych jest pusta. Skorzystaj z usługi REST', typ='warning')
            przelacz_widgety(True)
        else:
            stacje_select_all.options = [*wszystkie_stacje_pomiarowe.keys()]
            stacje_select_all.name = 'Wszystkie stacje pomiarowe z bazy danych'
            wszystkie_lokalizacje = wczytaj_lokalizacje_bd()
            # włączenie widgetów
            aktualizuj_alert('Pobrano dane hz bazy danych', typ='success')
            przelacz_widgety(False)


# Metoda obsługująca kliknięcie w guzik zrodlo_danych_button
zrodlo_danych_button.on_click(zaladuj_dane)

# Widgety obsługujące wyszukiwanie przez użytkownika najbliższych stacji pomiarowych
# Pole tekstowe na szukaną lokalizację
lokalizacja_input = pn.widgets.TextInput(description='Wyszukaj stacje pomiarowe w podanym promieniu: ',
                                         name='Najbliższe stacje pomiarowe',
                                         placeholder='Wprowadź nazwę lokalizacji: ', disabled=True)
# Pole tekstowe na wpisanie promienia wyszukiwania
dystans_input = pn.widgets.TextInput(placeholder='Wprowadź promień wyszukiwania [w km]: ', disabled=True)
# Guzik wyszukujący najbliższe lokalizacje
promien_szukaj_button = pn.widgets.Button(name='Szukaj najbliższej stacji 🔍', disabled=True)


def stworz_mape_najblizsze(miejsce_wyszukiwania, promien):
    """
    Funkcja tworzy mapę ze znacznikami stacji pomiarowych oraz listę najbliższych stacji pomiarowych
    :param miejsce_wyszukiwania: podane przez użytkownika miejsce wyszukiwania
    :param promien: podany przez użytkownika promień wyszukiwania
    :return: mapa wynikowa wraz ze znacznikami, lista najbliższych stacji pomiarowych
    """

    promien = float(promien)
    centrum, wynik_lista, lokalizacje = najblizsze_stacje_pomiarowe(miejsce_wyszukiwania, promien,
                                                                    wszystkie_lokalizacje)

    # Inicjalizacja obiektu mapy
    mapa = pn.pane.plot.Folium(folium.Map(location=centrum), min_width=700, height=350, sizing_mode="stretch_width")

    # Tworzenie elementów mapy
    # Dodawanie kolejnych lokalizacji (Markerów) do mapy
    for miejsce, koordynaty in lokalizacje.items():
        folium.Marker(koordynaty, popup=f'{miejsce}').add_to(mapa.object)

    # Zakreślenie obszaru wyszukiwania
    folium.Circle(centrum, radius=promien * 1000, fill=True, fill_opacity=0.3, fill_color='yellowgreen',
                  tooltip=f'Lokalizacja stacji pomiarowych w odległości {promien} km').add_to(mapa.object)
    # Dodanie miejsca wyszukiwania na mapę
    folium.Marker(centrum, miejsce_wyszukiwania, icon=folium.Icon(color='red', )).add_to(mapa.object)

    return mapa, wynik_lista


def aktualizuj_najblizsze(event):
    """
    Funkcja obsługująca aktualizacje mapy najbliższych stacji pomiarowych oraz opisu najbliższych stacji
    :param event: argument obsługujący wciśnięcie guzika promien_szukaj_button (event)
    """
    # Wartości parametrów pobieranie z widgetów inputu tekstu
    lokalizacja = lokalizacja_input.value_input
    promien = dystans_input.value_input

    mapa, lista_lokacji = stworz_mape_najblizsze(lokalizacja, promien)

    # Tworzenie opisu dla najbliższych stacji pomiarowych
    opis = f'Najbliższe znalezione stacje pomiarowe dla {lokalizacja_input.value_input}: \n'

    for lokacja in lista_lokacji:
        nazwa, dystans = lokacja
        opis += f'* {dystans:.2f}km - {nazwa} \n'

    # Przypisywanie otrzymanych obiektów do głównego layoutu aplikacji
    main_layout[0] = mapa
    main_layout[1] = pn.pane.Markdown(opis)


# Metoda obsługująca kliknięcie w guzik promien_szukaj_button
promien_szukaj_button.on_click(aktualizuj_najblizsze)

# Menu select wszystkich wyszukanych stacji pomiarowych ze źródła danych
stacje_select_all = pn.widgets.Select(name='Wszystkie stacje pomiarowe ze źródła: ', disabled=True)

# Widgety obslugujace wyszukiwanie przez użytkownika stacji dla konkretnej miejscowości
# Pole tekstowe do podania przez użytkownika miescowości
miasto_input = pn.widgets.TextInput(
    name="Znajdź stację w konkretnej miejscowości: ",
    placeholder="Wprowadź nazwę miejscowości: ",
    disabled=True)
# Guzik do wyszukiwania miejscowości
miasto_input_button = pn.widgets.Button(name='Szukaj stacji dla konkretnej miejscowości 🔍', disabled=True)

# Widgety dotyczące wyszukania danych dla wybranej przez użytkownika miejscowości
# Menu select ze stacjami w miejscowości
stacje_w_miescie_select = pn.widgets.Select(name='Znalezione stacje: ', disabled=True)
# Guzik do wyszukania danych dla stacji w wybranej miejscowości
wyszukaj_dane_button = pn.widgets.Button(name='Wyszukaj dane dla stacji 🔍')


def zaladuj_stacje_miejscowosc(event):
    """
    Funkcja aktualizująca widget select, aby zawierał tylko stacje w wybranej przez użytkownika miejscowości
    :param event: argument obsługujący wciśnięcie guzika miesto_input_button (event)
    :return:
    """
    if miasto_input.value:
        stacje_w_miescie_select.options = [nazwa for nazwa, id in wszystkie_stacje_pomiarowe.items() if
                                           miasto_input.value in nazwa.split(',')[0]]
        stacje_w_miescie_select.disabled = False


# Metoda obsługująca wciśnięcie guzika miasto_input_button
miasto_input_button.on_click(zaladuj_stacje_miejscowosc)

# Tworzenie stringa na opis oraz słowników dla parametrów wyszukanej stacji
wszystkie_dataframy = {}
indeksy_stacji = {}
opis = ''


def wczytaj_dane_dla_stacji(event):
    """
    Funkcja obsługująca wczytanie danych dla wybranej stacji w zależności od wybranego źródła danych
    :param event: argument obsługujący wciśnięcie guzika wyszukaj_dane_button (event)
    """
    # Wyczyszczenie obiektów z poprzedniej zawartości
    global opis
    global wszystkie_dataframy
    global indeksy_stacji
    wszystkie_dataframy.clear()
    indeksy_stacji.clear()
    opis = ''

    # Wyszukanie nazwy stacji, id, długości i szerokości geograficznej w słownikach dla wybranej
    # przez użytkownika stacji
    wybrana_stacja = [[nazwa, id] for nazwa, id in wszystkie_stacje_pomiarowe.items()
                      if nazwa == stacje_w_miescie_select.value][0]
    lokalizacja_wybranej_stacji = [kordynaty for nazwa, kordynaty in wszystkie_lokalizacje.items()
                                   if nazwa == stacje_w_miescie_select.value][0]

    # Aktualizacja opisu dla wybranej stacji (podstawowe informacje)
    opis = f'Podstawowe informacje dla znalezionej stacji: \n' \
           f'Nazwa stacji {wybrana_stacja[0]} \n' \
           f'Numer id stacji: {wybrana_stacja[1]} \n' \
           f'Link do trasy na Google Maps: https://www.google.com/maps/dir/?api=1&destination={lokalizacja_wybranej_stacji[0]},{lokalizacja_wybranej_stacji[1]} \n' \
           f'Lista czujników dostępnych dla stacji: \n'

    # Wyszukanie id dla wybranej stacji
    stacje = wszystkie_stacje_pomiarowe
    id_zapytania = stacje.get(stacje_w_miescie_select.value)

    if zrodlo_danych_select.value == 'Usługa REST':

        # wywołanie zapytań dla listy czujników oraz indeksów mierzonych da id szukanej stacji
        lista_czujnikow = pobierz_dane(2, id_zapytania)
        lista_indeksow = pobierz_dane(4, id_zapytania)

        # Tworzymy słownik dla wyszukanej listy czujników na stacji pomiarowej
        for czujnik in lista_czujnikow:
            # Kluczem w słowniku jest wzor parametru
            wzor_parametru = czujnik['param']['paramCode']

            # aktualizacja opisu w postaci-> wzór chemiczny/kod parametru-słowna nazwa parametru dla kolejnych czujników
            opis += f'* {czujnik['param']['paramCode']} - {czujnik['param']['paramName']}\n'

            df = pd.DataFrame((pobierz_dane(3, czujnik['id'])['values'])).fillna(0)
            df = sformatuj_dataframe(df)
            # Zapisanie danych do słownika w postaci {wzór_parametru: ramka z danymi (data i godzina, odczyt)}
            wszystkie_dataframy[wzor_parametru] = df

        # Pobranie wartości indeksu stacji oraz indeksu parametru
        for parametr, slownik in lista_indeksow.items():
            if 'IndexLevel' in parametr:
                if slownik is None:
                    continue
                else:
                    indeksy_stacji[parametr] = slownik['id']

    elif zrodlo_danych_select.value == 'Baza danych':

        # aktualizacja opisu w postaci-> wzór chemiczny/kod parametru-słowna nazwa parametru dla kolejnych czujników
        parametry = wczytaj_parametry_bd(id_zapytania)
        for slownik in parametry:
            for wzor, nazwa_parametru in slownik.items():
                opis += f'* {wzor} - {nazwa_parametru}\n'

        # Pobranie słownika ramek danych z bazy danych
        df_baza = wczytaj_parametry_z_pomiarami_bd(id_zapytania)

        # Formatowanie i przypisanie danych do zmiennej wszystkie_dataframy
        wszystkie_dataframy = {key: sformatuj_dataframe(value) for key, value in df_baza.items()}

        # Pobranie indeksów stacji z bazy danych
        indeksy_stacji = wczytaj_indeksy_stacji_parametrow_bd(id_zapytania)

    # Aktualizacja parametrów do wyświetlenia dla wybranej stacji oraz odblokowanie menu wyboru
    wybor_parametru_select.options = [*wszystkie_dataframy.keys()]
    wybor_parametru_select.disabled = False


# Metoda wczytuje dane dla stacji po kliknięciu guzika wyszukaj_dane_button
wyszukaj_dane_button.on_click(wczytaj_dane_dla_stacji)

# Menu select obsługujący wybór parametru przez użytkownika
wybor_parametru_select = pn.widgets.Select(name='Wybierz parametr do pokazania na wykresie', disabled=True)

# Gruba widgetów number obsługujących wyświetlanie wartości charakterystycznych dla danych (min, max, srednia)
minimum_number = pn.indicators.Number(name='Minimalne stężenie', font_size='14pt', title_size='14pt')
maximum_number = pn.indicators.Number(name='Maksymalne stężenie', font_size='14pt', title_size='14pt')
srednia_number = pn.indicators.Number(name='Średnie stężenie', font_size='14pt', title_size='14pt')

# Widgety wyświetlają wartości indeksów dla stacji oraz indeksów parametrów
# Dodatkowo widgety zmieniają kolor w zależności od wartości parametru (0,1 - zielony, 2,3 - zółty, 4,5 - czerwony)
indeks_stacji_number = pn.indicators.Number(name='Ogólny indeks stacji', font_size='14pt', title_size='14pt',
                                            format='{value:.0f}',
                                            colors=[(33, 'green'), (66, 'gold'), (100, 'red')])
indeks_parametru_number = pn.indicators.Number(name='Indeks parametru: ', font_size='14pt', title_size='14pt',
                                               format='{value:.0f}',
                                               colors=[(33, 'green'), (66, 'gold'), (100, 'red')])


def aktualizuj_parametry(df):
    """
    Funkcja aktualizuje wartości widgetów Number z wartościami charakterystycznymi na podstawie ramki danych
    :param df: ramka danych
    """

    # Wykluczenie wartości zerowych z danych
    parametry = [wartosc for wartosc in df['value'] if wartosc != 0]

    # Aktualizacja wartości widgetów o wartości charakterystyczne
    minimum_number.value = round(min(parametry), 2)
    maximum_number.value = round(max(parametry), 2)
    srednia_number.value = round(sum(parametry) / len(parametry), 2)

    # Zmiana wartości widgetu odpowiadającego za ogólny indeks stacji
    id_parametr_ogolny = indeksy_stacji["stIndexLevel"] or None

    # W przypadku wartości indeksu 0 zmiana jego wartości (widget potraktowałby 0 jako None)
    if id_parametr_ogolny == 0:
        indeks_stacji_number.value = id_parametr_ogolny + 0.1
    elif id_parametr_ogolny == -1:
        indeks_stacji_number.value = None
    else:
        indeks_stacji_number.value = id_parametr_ogolny

    # # Zmiana wartości widgetu odpowiadająca za indeks danego parametru
    id_parametr_liczony_klucz = str(wybor_parametru_select.value.lower().replace(".", "")) + 'IndexLevel'
    id_parametru = indeksy_stacji.get(id_parametr_liczony_klucz, None)
    id_parametru = id_parametru + 0.1 if id_parametru == 0 else id_parametru

    # Aktualizacja widgetu
    indeks_parametru_number.name = f'Indeks parametru: {wybor_parametru_select.value}'
    indeks_parametru_number.value = id_parametru or None


def utworz_slider(df):
    """
    Funkcja pomocnicza funkcji aktualizuj panel tworzy widget slider wyboru daty i czasu pomaru na podstawie ramki danych
    :param df: ramka danych
    :return: widget DatetimeRangeSlider
    """
    return pn.widgets.DatetimeRangeSlider(
        name='Data i czas: ',
        start=df.index.min(),
        end=df.index.max(),
        value=(df.index.min(), df.index.max()),
        step=3600000
    )


def aktualizuj_mape_panel(lokalizacje):
    """
    Funkcja pomocnicza funkcji aktualizuj_panel
    tworzy obiekt mapy na podstawie wybranej przez użytkownika stacji pomiarowej
    :param lokalizacje: słownik wszystkich dostępnych lokalizacji
    :return: obiekt mapy
    """
    lokalizacja_stacji = lokalizacje.get(stacje_w_miescie_select.value)
    mapa = pn.pane.plot.Folium(folium.Map(location=lokalizacja_stacji), min_width=700, height=350,
                               sizing_mode="stretch_width")
    folium.Marker(lokalizacja_stacji, popup=f'Nazwa stacji: {stacje_w_miescie_select.value} \n'
                                            f'Lokalizacja {lokalizacja_stacji}',
                  icon=folium.Icon(color='red', )).add_to(mapa.object)
    return mapa


def aktualizuj_panel(event=None):
    """
    Funkcja aktualizująca główną zawartość panelu
    :param event: argument obsługujący zmianę wartości parametru menu select wybor_parametru_select (event)
    """
    # Wczytanie opowiedniej ramki danych
    df = wszystkie_dataframy[wybor_parametru_select.value]

    # Tworzenie suwaka wyboru daty i czasu dla ramki danych oraz utworzenie mapy dla wybranej lokalizacji
    suwak = utworz_slider(df)
    lokalizacje = wszystkie_lokalizacje

    # Aktualizacja panelu
    main_layout[0] = aktualizuj_mape_panel(lokalizacje)
    main_layout[1] = pn.pane.Markdown(opis)

    @pn.depends(suwak.param.value)
    def aktualizacja_wykresu(zakres_dat):
        """
        Funkcja pomocnicza funkcji aktualizuj panel. Funkcja wykorzystuje dekorator depends aby dynamicznie akutalzować
        wykres w zależności od wybranego zakresu dat. Dadatkowo funkcja wywołuje zmianę wartości widgetów Number
        :param zakres_dat: przedział dat i czasu z suwaka
        :return: wykres na podstawie zaktualizowanego zakresu dat i czasu
        """
        data_start, data_end = zakres_dat
        filtered_df = df[(df.index >= pd.Timestamp(data_start)) & (df.index <= pd.Timestamp(data_end))]
        aktualizuj_parametry(filtered_df)
        return stworz_wykres(filtered_df)

    # Aktualizacja panelu
    main_layout[3] = pn.panel(aktualizacja_wykresu)
    main_layout[4] = suwak


# Metoda siedząca zmianę wartości parametry w menu select i wywołująca funkcję przy jej zmianie
wybor_parametru_select.param.watch(aktualizuj_panel, 'value')
# Widget obsługujący ostrzerzenia
alert = pn.pane.Alert('Aplikacja działa poprawnie', alert_type='primary', dedent=True)


def aktualizuj_alert(wiadomosc, typ='danger'):
    """
    Funkcja aktualizuje widget odpowiedzialny za ostrzeżenia o nową treść i typ alertu
    :param wiadomosc: wiadomość wyświetlana w alercie
    :param typ: typ alertu
    """
    alert.object = wiadomosc
    alert.alert_type = typ


def zapisz_dane_bd(event=None):
    """
    Funkcja obsługująca zapis danych z usługi REST do bazy danych. Dodatkowo zmienia wiadomość i typ alertu
    :param event: argument obsługujący kliknięcie w guzik baza_danych_button (event)
    :return:
    """
    aktualizuj_alert('Zapisuje dane do bazy danych', typ='warning')
    dodaj_do_bazy_danych(wszystkie_stacje_pomiarowe, wszystkie_lokalizacje, pobierz_dane)
    aktualizuj_alert('Wczytano dane do bazy', 'primary')
    baza_danych_button.disabled = True


# Guzik obsługujący zapis danych do bazy danych
baza_danych_button = pn.widgets.Button(name='Zapisz dane do bazy danych')
# Metoda wywołująca funkcję odpowiedzialną za zapis do bazy danych po kliknięciu widgetu baza_danych_button
baza_danych_button.on_click(zapisz_dane_bd)

# Głowny layout panelu. Puste rzędy zostają zaktualizowane w toku działania aplikacji
main_layout = pn.Column(
    pn.Column(), pn.Row(),
    pn.Card(pn.Column(pn.Row(wybor_parametru_select),
                      pn.Row(maximum_number, srednia_number, minimum_number, indeks_stacji_number,
                             indeks_parametru_number),
                      ),
            title='Dane panelu', sizing_mode="stretch_width"),
    pn.Row(), pn.Row())

# Głowna templatka aplikacji
template = pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[zrodlo_danych_select, zrodlo_danych_button, lokalizacja_input, dystans_input, promien_szukaj_button,
             pn.layout.Divider(),
             stacje_select_all, miasto_input, miasto_input_button,
             stacje_w_miescie_select, wyszukaj_dane_button, alert, baza_danych_button
             ],
    main=[main_layout],
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='grey',
    theme_toggle=False,
    busy_indicator=None
)

template.servable()
