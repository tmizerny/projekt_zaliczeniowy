import requests


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
    except requests.exceptions.ConnectionError as connection_error:
        connection_error_message = f'Brak połącznia z serwisem GIOS '

    except requests.exceptions.Timeout as timeout_error:
        timeout_error_message = f'[{timeout_error}] Błąd odpowiedz od serwera '
    else:
        return req.json()


