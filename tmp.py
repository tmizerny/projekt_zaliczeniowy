import requests
import pprint as pp
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

    req = requests.get(request)


    return req.json()


lista_czujnikow = pobierz_dane(2,944)


for czujnik in lista_czujnikow:
    pomiary = pobierz_dane(3, czujnik['id'])['values']
    for slownik in pomiary:
        print(slownik['date'])