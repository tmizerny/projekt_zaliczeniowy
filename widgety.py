"""Moduł grupuje widgety użyte w aplikacji"""

import panel as pn

# Widgety sidebara aplikacji
# Wybranie źródła danych
source_menu = pn.widgets.Select(description="Z jakiego źródła aplikacja ma pobrać dane?", name='Wybierz źródło danych',
                                options=['Usługa REST', 'Baza danych'])
load_data_button = pn.widgets.Button(name='Załaduj dane')

# Najbliższe stacje pomiarowe
lokalizacja = pn.widgets.TextInput(description='Wyszukaj stacje pomiarowe w podanym promieniu: ',
                                   name='Najbliższe stacje pomiarowe',
                                   placeholder='Wprowadź nazwę lokalizacji: ', disabled=True)
distance = pn.widgets.TextInput(placeholder='Wprowadź promień wyszukiwania [w km]: ', disabled=True)
button_distance_input = pn.widgets.Button(name='Szukaj najbliższej stacji 🔍', disabled=True)

# Wszystkie stacje pomiarowe ze źródła
station_menu_all = pn.widgets.Select(name='Wszystkie stacje pomiarowe ze źródła: ', disabled=True)

# Znalezienie stacji w konkretnej miejscowości
city_input = pn.widgets.TextInput(
    name="Znajdź stację w konkretnej miejscowości: ",
    placeholder="Wprowadź nazwę miejscowości: ",
    disabled=True)
button_input = pn.widgets.Button(name='Szukaj stacji dla konkretnej miejscowości 🔍', disabled=True)

# Znalezione stacje
station_menu_city = pn.widgets.Select(name='Znalezione stacje: ', disabled=True)
button_szukaj = pn.widgets.Button(name='Wyszukaj dane dla stacji 🔍')

# Widgety panelu


number_min = pn.indicators.Number(name='Minimalne stężenie', font_size='14pt', title_size='14pt')
number_max = pn.indicators.Number(name='Maksymalne stężenie', font_size='14pt', title_size='14pt')
number_mean = pn.indicators.Number(name='Średnie stężenie', font_size='14pt', title_size='14pt')
indeks_stacji = pn.indicators.Number(name='Ogólny indeks stacji', font_size='14pt', title_size='14pt',
                                     format='{value:.0f}',
                                     colors=[(33, 'green'), (66, 'gold'), (100, 'red')])
indeks_parametru = pn.indicators.Number(name='Indeks parametru: ', font_size='14pt', title_size='14pt',
                                        format='{value:.0f}',
                                        colors=[(33, 'green'), (66, 'gold'), (100, 'red')])
