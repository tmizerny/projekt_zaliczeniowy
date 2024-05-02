from pobieranie_danych import pobierz_dane
from najblizsze_stacje import najblizsze_stacje_pomiarowe
import pandas as pd
import panel as pn
import matplotlib.pyplot as plt
import folium

pn.extension()



source_menu = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?", name='Wybierz źródło danych',
                                options=['Usługa REST', 'Baza danych'])


def zaladuj_dane(event):
    if source_menu.value == 'Usługa REST':
        station_menu_all.options = [stacja['stationName'] for stacja in pobierz_dane(1)]
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

mapa = None

def zaznacz_na_mapie(miejsce, promien,
                     lista_stacji):

    promien = float(promien)
    centrum, wynik_lista, lokalizacje = najblizsze_stacje_pomiarowe(miejsce, promien, lista_stacji)
    mapa = pn.pane.plot.Folium(folium.Map(location=centrum), width=250, height=250)

    for miejsce, koordynaty in lokalizacje.items():
        folium.Marker(koordynaty, popup=f'{miejsce}').add_to(mapa.object)

    folium.Circle(centrum, radius=promien, fill=True, fill_opacity=0.3, fill_color='yellowgreen').add_to(mapa.object)




button_distance_input = pn.widgets.Button(name='Szukaj najbliższej stacji 🔍', disabled=True)
button_distance_input.on_click(zaznacz_na_mapie)



# opis = pn.pane.Markdown()

template = pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[source_menu, load_data_button, station_menu_all, pn.layout.Divider(), city_input, button_input,
             station_menu_city,
             pn.layout.Divider(), localization, distance, button_distance_input],
    main=[pn.Row(pn.Card(), pn.Card(mapa, collapsible=True, title='Lokalizacja stacji', width=300, height=300))],
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='white',
    theme_toggle=False,
    busy_indicator=None
)

template.servable()
