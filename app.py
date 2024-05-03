import datetime
from pobieranie_danych import pobierz_dane
from najblizsze_stacje import najblizsze_stacje_pomiarowe
import pandas as pd
import panel as pn
import matplotlib.pyplot as plt
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


def zaladuj_stacje_miejscowosc():
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

mapa = pn.pane.plot.Folium(folium.Map(location=[52, 20]), width=350, height=350)

wszystkie_dataframy = {}


def wczytaj_dane_dla_stacji(event):
    stacje = wczytaj_wszystkie_stacje()
    id_zapytania = stacje.get(station_menu_all.value)
    lista_czujnikow = pobierz_dane(2, id_zapytania)
    for czujnik in lista_czujnikow:
        fig_title = (pobierz_dane(3, czujnik['id'])['key'])

        wszystkie_dataframy[fig_title] = pd.DataFrame((pobierz_dane(3, czujnik['id'])['values'])).fillna(0)
        print(wszystkie_dataframy[fig_title])
    parameters_select.options = [*wszystkie_dataframy.keys()]
    parameters_select.disabled = False
    plot_button.disabled = False


button_szukaj = pn.widgets.Button(name='Wyszukaj dane dla stacji')
button_szukaj.on_click(wczytaj_dane_dla_stacji)


def zaznacz_na_mapie(miejsce, promien,lista_stacji):
    promien = float(promien)
    centrum, wynik_lista, lokalizacje = najblizsze_stacje_pomiarowe(miejsce, promien, lista_stacji)
    mapa = pn.pane.plot.Folium(folium.Map(location=centrum), width=350, height=350)

    for miejsce, koordynaty in lokalizacje.items():
        folium.Marker(koordynaty, popup=f'{miejsce}').add_to(mapa.object)

    folium.Circle(centrum, radius=promien, fill=True, fill_opacity=0.3, fill_color='yellowgreen').add_to(mapa.object)


button_distance_input = pn.widgets.Button(name='Szukaj najbliższej stacji 🔍', disabled=True)
button_distance_input.on_click(zaznacz_na_mapie)

parameters_select = pn.widgets.Select(name='Wybierz parametr do pokazania na wykresie', disabled=True)
plot_button = pn.widgets.Button(name='Aktualizuj wykres', disabled=True)

wykres = None


def aktualizuj_wykres(figsize=(4, 3)):
    dataframe = wszystkie_dataframy.get(parameters_select.value)
    x = dataframe['date']
    y = dataframe['value']
    fig, ax = plt.bar(figsize, height=50)
    ax.plot(x, y)
    ax.set(xlabel='Data', ylabel=f'{parameters_select.value}',
           title=f'Wykres stężenia {parameters_select.value} dla wybranej stacji pomiarowej')
    ax.grid()
    plt.close(fig)
    return fig


number_min = pn.indicators.Number(name='Minimalne stężenie', font_size='36pt')
number_max = pn.indicators.Number(name='Maksymalne stężenie', font_size='36pt')
number_mean = pn.indicators.Number(name='Średnie stężenie', font_size='36pt')

template = pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[source_menu, load_data_button, localization, distance, button_distance_input, pn.layout.Divider(),
             station_menu_all, city_input, button_input,
             station_menu_city, button_szukaj,
             pn.layout.Divider(), parameters_select, plot_button],
    main=[pn.Column(pn.Card(mapa, collapsible=True, title='Lokalizacja najbliższych stacji', width=500, height=500)),
          pn.Column(wykres, pn.Row(number_max, number_mean, number_min))],
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='white',
    theme_toggle=False,
    busy_indicator=None
)

template.servable()
