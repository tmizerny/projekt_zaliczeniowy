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
    url = ''
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
    return {stacja['stationName']: stacja['id'] for stacja in pobierz_dane(1)}


def wczytaj_wszystkie_lokalizacje():
    return {stacja['stationName']: [stacja['gegrLat'], stacja['gegrLon']] for stacja in pobierz_dane(1)}


stacje_pomiarowe = {}
wszystkie_lokalizacje = {}

source_menu = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?", name='Wybierz źródło danych',
                                options=['Usługa REST', 'Baza danych'])
load_data_button = pn.widgets.Button(name='Załaduj dane')


def zaladuj_dane(event):
    global stacje_pomiarowe
    global wszystkie_lokalizacje
    wszystkie_lokalizacje.clear()
    stacje_pomiarowe.clear()

    if source_menu.value == 'Usługa REST':
        stacje_pomiarowe = wczytaj_wszystkie_stacje()
        station_menu_all.options = [*stacje_pomiarowe.keys()]
        station_menu_all.name = 'Wszystkie stacje pomiarowe z Usługi REST'
        wszystkie_lokalizacje = wczytaj_wszystkie_lokalizacje()


    # elif source_menu.value == 'Baza danych':

        # stacje_pomiarowe = wczytaj_stacje_bd()
        # station_menu_all.options = [*stacje_pomiarowe.keys()]
        # station_menu_all.name = 'Wszystkie stacje pomiarowe z bazy danych'
        # wszystkie_lokalizacje = wczytaj_lokalizacje_bd()

    station_menu_all.disabled = False
    city_input.disabled = False
    lokalizacja.disabled = False
    distance.disabled = False
    button_input.disabled = False
    button_distance_input.disabled = False


load_data_button.on_click(zaladuj_dane)

lokalizacja = pn.widgets.TextInput(description='Wyszukaj stacje pomiarowe w podanym promieniu: ',
                                   name='Najbliższe stacje pomiarowe',
                                   placeholder='Wprowadź nazwę lokalizacji: ', disabled=True)
distance = pn.widgets.TextInput(placeholder='Wprowadź promień wyszukiwania [w km]: ', disabled=True)
button_distance_input = pn.widgets.Button(name='Szukaj najbliższej stacji 🔍', disabled=True)


def stworz_mape_najblizsze(location, promien):
    promien = float(promien)
    centrum, wynik_lista, lokalizacje = najblizsze_stacje_pomiarowe(location, promien, wszystkie_lokalizacje)

    mapa = pn.pane.plot.Folium(folium.Map(location=centrum), min_width=700, height=350, sizing_mode="stretch_width")
    for miejsce, koordynaty in lokalizacje.items():
        folium.Marker(koordynaty, popup=f'{miejsce}').add_to(mapa.object)
    folium.Circle(centrum, radius=promien * 1000, fill=True, fill_opacity=0.3, fill_color='yellowgreen',
                  tooltip=f'Lokalizacja stacji pomiarowych w odległości {promien} km').add_to(mapa.object)
    folium.Marker(centrum, location, icon=folium.Icon(color='red', )).add_to(mapa.object)

    return mapa, wynik_lista


def aktualizuj_mape(event):
    location = lokalizacja.value_input
    promien = distance.value_input

    mapa, lista_lokacji = stworz_mape_najblizsze(location, promien)
    opis = f'Najbliższe znalezione stacje pomiarowe dla {lokalizacja.value_input}: \n'

    for lokacja in lista_lokacji:
        nazwa, dystans = lokacja
        opis += f'* {dystans:.2f}km - {nazwa} \n'

    main_layout[0] = mapa
    main_layout[1] = pn.pane.Markdown(opis)


button_distance_input.on_click(aktualizuj_mape)
station_menu_all = pn.widgets.Select(name='Wszystkie stacje pomiarowe ze źródła: ', disabled=True)
city_input = pn.widgets.TextInput(
    name="Znajdź stację w konkretnej miejscowości: ",
    placeholder="Wprowadź nazwę miejscowości: ",
    disabled=True)
button_input = pn.widgets.Button(name='Szukaj stacji dla konkretnej miejscowości 🔍', disabled=True)
station_menu_city = pn.widgets.Select(name='Znalezione stacje: ', disabled=True)
button_szukaj = pn.widgets.Button(name='Wyszukaj dane dla stacji 🔍')


def zaladuj_stacje_miejscowosc(event):
    if city_input.value:
        station_menu_city.options = [nazwa for nazwa, id in stacje_pomiarowe.items() if
                                     city_input.value in nazwa.split(',')[0]]
        station_menu_city.disabled = False


button_input.on_click(zaladuj_stacje_miejscowosc)

wszystkie_dataframy = {}
indeksy_stacji = {}
opis = ''


def wczytaj_dane_dla_stacji(event):
    global opis
    wszystkie_dataframy.clear()
    indeksy_stacji.clear()
    opis = ''

    wybrana_stacja = [[nazwa, id] for nazwa, id in stacje_pomiarowe.items() if nazwa == station_menu_city.value][0]
    lokalizacja_wybranej_stacji = \
        [kordynaty for nazwa, kordynaty in wszystkie_lokalizacje.items() if nazwa == station_menu_city.value][0]

    opis = f'Podstawowe informacje dla znalezionej stacji: \n' \
           f'Nazwa stacji {wybrana_stacja[0]} \n' \
           f'Numer id stacji: {wybrana_stacja[1]} \n' \
           f'Link do trasy na Google Maps: https://www.google.com/maps/dir/?api=1&destination={lokalizacja_wybranej_stacji[0]},{lokalizacja_wybranej_stacji[1]} \n' \
           f'Lista czujników dostępnych dla stacji: \n'
    stacje = stacje_pomiarowe
    id_zapytania = stacje.get(station_menu_city.value)

    if source_menu.value == 'Usługa REST':

        lista_czujnikow = pobierz_dane(2, id_zapytania)
        lista_indeksow = pobierz_dane(4, id_zapytania)
        for czujnik in lista_czujnikow:
            fig_title = czujnik['param']['paramCode']
            print(czujnik)
            opis += f'* {czujnik['param']['paramCode']} - {czujnik['param']['paramName']}\n'

            df = pd.DataFrame((pobierz_dane(3, czujnik['id'])['values'])).fillna(0)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df['Data i godzina odczytu'] = df.index.strftime('%H:%M %d/%m/%Y')
            df = df[::-1]
            wszystkie_dataframy[fig_title] = df

        for parametr, slownik in lista_indeksow.items():
            if 'IndexLevel' in parametr:
                if slownik is None:
                    continue
                else:
                    indeksy_stacji[parametr] = slownik

    elif source_menu.value == 'Baza danych':
        ...

    parameters_select.options = [*wszystkie_dataframy.keys()]
    parameters_select.disabled = False


parameters_select = pn.widgets.Select(name='Wybierz parametr do pokazania na wykresie', disabled=True)
button_szukaj.on_click(wczytaj_dane_dla_stacji)

number_min = pn.indicators.Number(name='Minimalne stężenie', font_size='14pt', title_size='14pt')
number_max = pn.indicators.Number(name='Maksymalne stężenie', font_size='14pt', title_size='14pt')
number_mean = pn.indicators.Number(name='Średnie stężenie', font_size='14pt', title_size='14pt')
indeks_stacji = pn.indicators.Number(name='Ogólny indeks stacji', font_size='14pt', title_size='14pt',
                                     format='{value:.0f}',
                                     colors=[(33, 'green'), (66, 'gold'), (100, 'red')])
indeks_parametru = pn.indicators.Number(name='Indeks parametru: ', font_size='14pt', title_size='14pt',
                                        format='{value:.0f}',
                                        colors=[(33, 'green'), (66, 'gold'), (100, 'red')])


def stworz_wykres(df):
    wykres_bar = df.hvplot.bar(x='Data i godzina odczytu', color="teal").opts(xrotation=60,
                                                                              ylabel='Stężenie parametru',
                                                                              height=600,
                                                                              width=1200,
                                                                              align='center'
                                                                              )
    trend = np.polyfit(range(len(df)), df['value'], 1)
    trend_line = np.polyval(trend, range(len(df)))

    trend_df = pd.DataFrame({
        'Data i godzina odczytu': df['Data i godzina odczytu'],
        'Trend': trend_line
    })

    line_plot = trend_df.hvplot.line(x='Data i godzina odczytu', y='Trend', color='red')

    return wykres_bar * line_plot


def aktualizuj_parametry(df):
    parametry = [wartosc for wartosc in df['value'] if wartosc != 0]

    number_min.value = round(min(parametry), 2)
    number_max.value = round(max(parametry), 2)
    number_mean.value = round(sum(parametry) / len(parametry), 2)

    id_parametr_ogolny = indeksy_stacji["stIndexLevel"] or None

    if id_parametr_ogolny['id'] == 0:
        indeks_stacji.value = id_parametr_ogolny['id'] + 0.1
    elif id_parametr_ogolny['id'] == -1:
        indeks_stacji.value = None
    else:
        indeks_stacji.value = id_parametr_ogolny['id']

    id_parametr_liczony_klucz = str(parameters_select.value.lower().replace(".", "")) + 'IndexLevel'
    id_parametru = indeksy_stacji.get(id_parametr_liczony_klucz, {}).get('id', None)
    id_parametru = id_parametru + 0.1 if id_parametru == 0 else id_parametru
    indeks_parametru.name = f'Indeks parametru: {parameters_select.value}'
    indeks_parametru.value = id_parametru or None


def aktualizuj_panel(event=None):
    df = wszystkie_dataframy[parameters_select.value]

    suwak = pn.widgets.DatetimeRangeSlider(
        name='Data i czas: ',
        start=df.index.min(),
        end=df.index.max(),
        value=(df.index.min(), df.index.max()),
        step=3600000
    )
    lokalizacje = wszystkie_lokalizacje
    lokalizacja_stacji = lokalizacje.get(station_menu_city.value)
    mapa = pn.pane.plot.Folium(folium.Map(location=lokalizacja_stacji), min_width=700, height=350,
                               sizing_mode="stretch_width")
    folium.Marker(lokalizacja_stacji, popup=f'Nazwa stacji: {station_menu_city.value} \n'
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


parameters_select.param.watch(aktualizuj_panel, 'value')

alert = pn.pane.Alert('Aplikacja działa poprawnie', alert_type='primary', dedent=True)


def aktualizuj_alert(wiadomosc, typ='danger'):
    alert.object = wiadomosc
    alert.alert_type = typ


main_layout = pn.Column(
    pn.Column(), pn.Row(),
    pn.Card(pn.Column(pn.Row(parameters_select),
                      pn.Row(number_max, number_mean, number_min, indeks_stacji, indeks_parametru),
                      ),
            title='Dane panelu', sizing_mode="stretch_width"),
    pn.Row(), pn.Row())

template = pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[source_menu, load_data_button, lokalizacja, distance, button_distance_input, pn.layout.Divider(),
             station_menu_all, city_input, button_input,
             station_menu_city, button_szukaj, alert
             ],
    main=[main_layout],
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='grey',
    theme_toggle=False,
    busy_indicator=None
)

template.servable()
