import datetime
from pobieranie_danych import pobierz_dane
from najblizsze_stacje import najblizsze_stacje_pomiarowe
import pandas as pd
import panel as pn
import hvplot.pandas
import folium

pn.extension()

source_menu = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?", name='Wybierz źródło danych',
                                options=['Usługa REST', 'Baza danych'])


def wczytaj_wszystkie_stacje():
    return {stacja['stationName']: stacja['id'] for stacja in pobierz_dane(1)}


def zaladuj_dane(event):
    if source_menu.value == 'Usługa REST':
        stacje_pomiarowe = wczytaj_wszystkie_stacje()
        station_menu_all.options = [*stacje_pomiarowe.keys()]
        station_menu_all.disabled = False
        city_input.disabled = False
        localization.disabled = False
        distance.disabled = False
        button_input.disabled = False
        button_distance_input.disabled = False
    else:
        ...
    # Załadowanie danych z bazy danych


load_data_button = pn.widgets.Button(name='Załaduj dane')
load_data_button.on_click(zaladuj_dane)

station_menu_all = pn.widgets.Select(name='Wszystkie stacje pomiarowe ze źródła: ', disabled=True)

city_input = pn.widgets.TextInput(
    name="Znajdź stację w konkretnej miejscowości: ",
    placeholder="Wprowadź nazwę miejscowości: ",
    disabled=True)


def zaladuj_stacje_miejscowosc(event):
    if city_input.value:
        station_menu_city.options = [stacja['stationName'] for stacja in pobierz_dane(1) if
                                     city_input.value in stacja['stationName'].split(',')[0]]
        station_menu_city.disabled = False


button_input = pn.widgets.Button(name='Szukaj stacji dla konkretnej miejscowości 🔍', disabled=True)
button_input.on_click(zaladuj_stacje_miejscowosc)

station_menu_city = pn.widgets.Select(name='Znalezione stacje: ', disabled=True)

localization = pn.widgets.TextInput(description='Wyszukaj stacje pomiarowe w podanym promieniu: ',
                                    name='Najbliższe stacje pomiarowe',
                                    placeholder='Wprowadź nazwę lokalizacji: ', disabled=True)
distance = pn.widgets.TextInput(placeholder='Wprowadź promień wyszukiwania [w km]: ', disabled=True)

wszystkie_dataframy = {}


def wczytaj_dane_dla_stacji(event):
    stacje = wczytaj_wszystkie_stacje()
    id_zapytania = stacje.get(station_menu_all.value)
    lista_czujnikow = pobierz_dane(2, id_zapytania)
    for czujnik in lista_czujnikow:
        fig_title = (pobierz_dane(3, czujnik['id'])['key'])

        df = pd.DataFrame((pobierz_dane(3, czujnik['id'])['values'])).fillna(0)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df['Data i godzina odczytu'] = df.index.strftime('%H:%M %d/%m/%Y')
        df = df[::-1]

        wszystkie_dataframy[fig_title] = df

    parameters_select.options = [*wszystkie_dataframy.keys()]
    parameters_select.disabled = False
    button_wykres.disabled = False

parameters_select = pn.widgets.Select(name='Wybierz parametr do pokazania na wykresie', disabled=True)

def stworz_wykres(df):
    return df.hvplot.bar(x='Data i godzina odczytu').opts(xrotation=60)

def aktualizuj_wykres(event):
    df = wszystkie_dataframy[parameters_select.value]
    wykres = stworz_wykres(df)
    suwak = pn.widgets.DateRangeSlider(name='Data', start=df.index.min().date(),
                                                end=df.index.max().date(), value=(df.index.min().date(),
                                                                                  df.index.max().date()))
    main_layout[2] = wykres
    main_layout[3] = suwak

    @pn.depends(suwak.param.value)
    def aktualizuj_wykres(date_range):
        start_date, end_date = date_range
        filtered_df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
        return aktualizuj_wykres(filtered_df)

button_szukaj = pn.widgets.Button(name='Wyszukaj dane dla stacji')
button_szukaj.on_click(wczytaj_dane_dla_stacji)


def stworz_mape(location, promien):
    promien = float(promien)
    centrum, wynik_lista, lokalizacje = najblizsze_stacje_pomiarowe(location, promien, pobierz_dane(1))

    mapa = pn.pane.plot.Folium(folium.Map(location=centrum), width=700, height=350)
    for miejsce, koordynaty in lokalizacje.items():
        folium.Marker(koordynaty, popup=f'{miejsce}').add_to(mapa.object)
    folium.Circle(centrum, radius=promien * 1000, fill=True, fill_opacity=0.3, fill_color='yellowgreen',
                  tooltip='Lokalizacja najbliższych stacji pomiarowych').add_to(
        mapa.object)

    return mapa


def aktualizuj_mape(event):
    location = localization.value_input
    promien = distance.value_input

    mapa = stworz_mape(location, promien)
    main_layout[0] = mapa


button_distance_input = pn.widgets.Button(name='Szukaj najbliższej stacji 🔍', disabled=True)
button_distance_input.on_click(aktualizuj_mape)

button_wykres = pn.widgets.Button(name='Aktualizuj wykres',disabled=True)
button_wykres.on_click(aktualizuj_wykres)

number_min = pn.indicators.Number(name='Minimalne stężenie', font_size='14pt')
number_max = pn.indicators.Number(name='Maksymalne stężenie', font_size='14pt')
number_mean = pn.indicators.Number(name='Średnie stężenie', font_size='14pt')





main_layout = pn.Column(
    pn.Column(),
    pn.Card(pn.Column(pn.Row(parameters_select,button_wykres),pn.Row(number_max,number_mean,number_min),

),title='Dane stacji'),pn.Row(),pn.Row())

template = pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[source_menu, load_data_button, localization, distance, button_distance_input, pn.layout.Divider(),
             station_menu_all, city_input, button_input,
             station_menu_city, button_szukaj,
             ],
    main=[main_layout],
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='white',
    theme_toggle=False,
    busy_indicator=None
)

template.servable()
