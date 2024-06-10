"""
Główny moduł aplikacji
"""

from najblizsze_stacje import najblizsze_stacje_pomiarowe
# from baza_danych import wczytaj_stacje_bd, wczytaj_lokalizacje_bd

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
    :param option: wybór url'a do którego ma zostać wysłane zapytanie
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
        http_error_message = f'[{http_error}] Błąd protokołu HTTP'
        aktualizuj_alert(http_error_message)
    except requests.exceptions.ConnectionError as connection_error:
        connection_error_message = f'[{connection_error}] Brak połącznia z serwisem GIOS '
        aktualizuj_alert(connection_error_message)
    except requests.exceptions.Timeout as timeout_error:
        timeout_error_message = f'[{timeout_error}] Błąd odpowiedz od serwera'
        aktualizuj_alert(timeout_error_message)
    except Exception as exp:
        exp_message = f'[{exp}] Nieoczekiwany błąd. Spróbuj później'
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
stacje_pomiarowe = {}
wszystkie_lokalizacje = {}

# Inicjalizacja widgetów obsługujących wczytanie źródła danych
## Wybór źródła danych
zrodlo_danych_select = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?",
                                         name='Wybierz źródło danych',
                                         options=['Usługa REST', 'Baza danych'])
# Guzik zatwierdzający źródło danych
zrodlo_danych_button = pn.widgets.Button(name='Załaduj dane')


def zaladuj_dane(event):
    """
    Funkcja obsugujaca wszytanie danych do aplikacji w zaleznosci od wybranego ich źródła

    W zależności od wybranego źródła danych funkcja wczytuje stacje pomiarowe (id i lokalizacje),
    zmienia menu select wszystkich wyszukanych stacji oraz zmienia jego nazwę
    :param event: argument obsługujący wciśnięcie guzika zrodlo_danych_button (event)
    """
    # Wyczyszczenie ewentualnej zawartości słowników z poprzedniego użytkowania aplikacji
    global stacje_pomiarowe
    global wszystkie_lokalizacje
    wszystkie_lokalizacje.clear()
    stacje_pomiarowe.clear()

    if zrodlo_danych_select.value == 'Usługa REST':
        stacje_pomiarowe = wczytaj_wszystkie_stacje()
        stacje_select_all.options = [*stacje_pomiarowe.keys()]
        stacje_select_all.name = 'Wszystkie stacje pomiarowe z Usługi REST'
        wszystkie_lokalizacje = wczytaj_wszystkie_lokalizacje()

    # elif source_menu.value == 'Baza danych':

    # stacje_pomiarowe = wczytaj_stacje_bd()
    # station_menu_all.options = [*stacje_pomiarowe.keys()]
    # station_menu_all.name = 'Wszystkie stacje pomiarowe z bazy danych'
    # wszystkie_lokalizacje = wczytaj_lokalizacje_bd()

    # włączenie wszystkich wyłączonych widgetów
    stacje_select_all.disabled = False
    miasto_input.disabled = False
    lokalizacja_input.disabled = False
    dystans_input.disabled = False
    miasto_input_button.disabled = False
    promien_szukaj_button.disabled = False


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
        stacje_w_miescie_select.options = [nazwa for nazwa, id in stacje_pomiarowe.items() if
                                           miasto_input.value in nazwa.split(',')[0]]
        stacje_w_miescie_select.disabled = False


# Metoda obsługująca wciśnięcie guzika miasto_input_button
miasto_input_button.on_click(zaladuj_stacje_miejscowosc)

# Tworzenie stringa na opis oraz słowników dla parametrów wyszukanej stacji
wszystkie_dataframy = {}
indeksy_stacji = {}
opis = ''


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


def wczytaj_dane_dla_stacji(event):
    """
    Funkcja obsługująca wczytanie danych dla wybranej stacji w zależności od wybranego źródła danych
    :param event: argument obsługujący wciśnięcie guzika wyszukaj_dane_button (event)
    """
    # Wyczyszczenie obiektów z poprzedniej zawarości
    global opis
    wszystkie_dataframy.clear()
    indeksy_stacji.clear()
    opis = ''

    # Wyszukanie nazwy stacji, id, długości i szerokości geograficznej w słownikach dla wybranej
    # przez użytkownika stacji
    wybrana_stacja = [[nazwa, id] for nazwa, id in stacje_pomiarowe.items()
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
    stacje = stacje_pomiarowe
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
                    indeksy_stacji[parametr] = slownik

    elif zrodlo_danych_select.value == 'Baza danych':
        ...

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


def aktualizuj_parametry(df):
    parametry = [wartosc for wartosc in df['value'] if wartosc != 0]

    minimum_number.value = round(min(parametry), 2)
    maximum_number.value = round(max(parametry), 2)
    srednia_number.value = round(sum(parametry) / len(parametry), 2)

    id_parametr_ogolny = indeksy_stacji["stIndexLevel"] or None

    if id_parametr_ogolny['id'] == 0:
        indeks_stacji_number.value = id_parametr_ogolny['id'] + 0.1
    elif id_parametr_ogolny['id'] == -1:
        indeks_stacji_number.value = None
    else:
        indeks_stacji_number.value = id_parametr_ogolny['id']

    id_parametr_liczony_klucz = str(wybor_parametru_select.value.lower().replace(".", "")) + 'IndexLevel'
    id_parametru = indeksy_stacji.get(id_parametr_liczony_klucz, {}).get('id', None)
    id_parametru = id_parametru + 0.1 if id_parametru == 0 else id_parametru
    indeks_parametru_number.name = f'Indeks parametru: {wybor_parametru_select.value}'
    indeks_parametru_number.value = id_parametru or None


def aktualizuj_panel(event=None):
    df = wszystkie_dataframy[wybor_parametru_select.value]

    suwak = pn.widgets.DatetimeRangeSlider(
        name='Data i czas: ',
        start=df.index.min(),
        end=df.index.max(),
        value=(df.index.min(), df.index.max()),
        step=3600000
    )
    lokalizacje = wszystkie_lokalizacje
    lokalizacja_stacji = lokalizacje.get(stacje_w_miescie_select.value)
    mapa = pn.pane.plot.Folium(folium.Map(location=lokalizacja_stacji), min_width=700, height=350,
                               sizing_mode="stretch_width")
    folium.Marker(lokalizacja_stacji, popup=f'Nazwa stacji: {stacje_w_miescie_select.value} \n'
                                            f'Lokalizacja {lokalizacja_stacji}',
                  icon=folium.Icon(color='red', )).add_to(mapa.object)
    main_layout[0] = mapa
    main_layout[1] = pn.pane.Markdown(opis)

    @pn.depends(suwak.param.value)
    def aktualizacja_wykresu(date_range):
        start_date, end_date = date_range
        filtered_df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
        aktualizuj_parametry(filtered_df)
        return stworz_wykres(filtered_df)

    main_layout[3] = pn.panel(aktualizacja_wykresu)
    main_layout[4] = suwak


wybor_parametru_select.param.watch(aktualizuj_panel, 'value')

alert = pn.pane.Alert('Aplikacja działa poprawnie', alert_type='primary', dedent=True)


def aktualizuj_alert(wiadomosc, typ='danger'):
    alert.object = wiadomosc
    alert.alert_type = typ


main_layout = pn.Column(
    pn.Column(), pn.Row(),
    pn.Card(pn.Column(pn.Row(wybor_parametru_select),
                      pn.Row(maximum_number, srednia_number, minimum_number, indeks_stacji_number, indeks_parametru_number),
                      ),
            title='Dane panelu', sizing_mode="stretch_width"),
    pn.Row(), pn.Row())

template = pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[zrodlo_danych_select, zrodlo_danych_button, lokalizacja_input, dystans_input, promien_szukaj_button,
             pn.layout.Divider(),
             stacje_select_all, miasto_input, miasto_input_button,
             stacje_w_miescie_select, wyszukaj_dane_button, alert
             ],
    main=[main_layout],
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='grey',
    theme_toggle=False,
    busy_indicator=None
)

template.servable()
