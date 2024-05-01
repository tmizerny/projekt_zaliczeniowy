from pobieranie_danych import pobierz_dane
from najblizsze_stacje import najblizsze_stacje_pomiarowe
import pandas as pd
import panel as pn
import matplotlib.pyplot as plt
import folium

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 10000)

pn.extension()

# df_wszystkie_stacje = pd.DataFrame(pobierz_dane(1))
# df_wszystkie_stacje = df_wszystkie_stacje[['id','stationName']]
#
#
#
# data = pn.pane.DataFrame(df_wszystkie_stacje).servable()
#
# # wartośći najmniejsze i największe
# number_1 = pn.indicators.Number(name='Wartość najmniejsza',font_size='32pt')
# number_2 = pn.indicators.Number(name='Wartość największa',font_size='32pt')

source_menu = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?", name='Wybierz źródło danych',
                                options=['Usługa REST', 'Baza danych'])

station_menu_all = pn.widgets.Select(options=[stacja['stationName'] for stacja in pobierz_dane(1)])
city_input = pn.widgets.TextInput(
    name="Znajdź stację w konkretnej miejscowości: ",
    placeholder="Wprowadź nazwę miejscowości: ",
)
button_input = pn.widgets.Button(name='🔍')

station_menu_city = pn.widgets.Select(name='Znalezione stacje: ',
                                      options=[stacja['stationName'] for stacja in pobierz_dane(1) if
                                               city_input.value in stacja['stationName']])

localization = pn.widgets.TextInput(description='Wyszukaj stacje pomiarowe w podanym promieniu: ',
                                    name='Najbliższe stacje pomiarowe',
                                    placeholder='Wprowadź nazwę lokalizacji: ')
distance = pn.widgets.TextInput(placeholder='Wprowadź promień wyszukiwania [w km]: ')

button_distance_input = pn.widgets.Button(name='🔍')

mapa = pn.pane.plot.Folium(folium.Map(location=[52.41579805, 16.931231975777052], zoom_start=12))


def zaznacz_na_mapie(mapa, miejsce=None, promien=None, lista_stacji=pobierz_dane(1)):
    centrum, wynik_lista, lokalizacje = najblizsze_stacje_pomiarowe(miejsce, promien, lista_stacji)
    for miejsce, koordynaty in lokalizacje.items():
        folium.Marker(koordynaty, popup=f'{miejsce}').add_to(mapa)

    folium.Circle(centrum, radius=promien,fill=True, fill_opacity=0.3, fill_color='yellowgreen').add_to(mapa)

    return mapa


pn.template.FastListTemplate(
    title='Jakość powietrza w Polsce',
    sidebar=[source_menu, station_menu_all, city_input, button_input, station_menu_city,
             localization, distance, button_distance_input],
    main=mapa,
    background_color='#dcf5d0',
    header_background=' #00A170',
    accent_base_color='white',
    theme_toggle=False,
    busy_indicator=None
).servable()
