"""
Moduł grupujący testy jednostkowe dla aplikacji
"""

import pytest
import json

import app
from app import wczytaj_wszystkie_stacje, wczytaj_wszystkie_lokalizacje

wszystkie_lokalizacje = wczytaj_wszystkie_lokalizacje()


def test_wczytaj_wszystkie_stacje():
    """
    Funkcja bezargumentowa testuje poprawność otrzymanego typu obiektu (słownik), jak i typów kluczy
    oraz wartości
    """
    wszystkie_stacje = wczytaj_wszystkie_stacje()
    assert type(wszystkie_stacje) is dict
    for key, value in wszystkie_stacje.items():
        assert isinstance(key, str)
        assert isinstance(value, int)


def test_wczytaj_wszystkie_lokalizacje():
    """
    Funkcja bezargumentowa testuje typ obiektu (słownika), dodatkowo sprawdza poprawność klucza i wartości
    długość listy, typo wartości listy, oraz czy zapisane współrzędne mieszczą się w rozciągłości geograficznej Polski
    """
    assert type(wszystkie_lokalizacje) is dict
    for key, value in wszystkie_lokalizacje.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        assert len(value) == 2
        assert isinstance(value[0], str)
        assert isinstance(value[1], str)
        assert 49.0 <= float(value[0]) <= 55.0
        assert 14.0 <= float(value[1]) <= 24.5


def zaladuj_dane_json(sciezka):
    """
    Funkcja pomocnicza dla funkcji testującej z monkeypatch

    :param sciezka: ścieżka do pliku JSON
    :return plik JSON

    """
    with open(file=sciezka, mode='r') as plik:
        return json.load(plik)


def test_wczytaj_wszystkie_stacje_mp(monkeypatch):
    """
    Funkcja testująca zgodność danych wykorzystująca monkeypatch
    :param monkeypatch: podmiana źródła danych (usługa REST) na plik JSON

    """

    def pobierz_dane_z_pliku(index=None):
        """
        Funkcja pomocnicza dla funkcji test_wczytaj_wszystkie_stacje_mp
        :param index: argument obsługujący wybór indeksu w funkcji pobierz_dane
        :return: obiekt funkcji zaladuj_dane_json
        """
        return zaladuj_dane_json('dane_testowe.json')

    monkeypatch.setattr('app.pobierz_dane', pobierz_dane_z_pliku)

    stacje = app.pobierz_dane(1)
    stacje_json = pobierz_dane_z_pliku()

    assert stacje == stacje_json
