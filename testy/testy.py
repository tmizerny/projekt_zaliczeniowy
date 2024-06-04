
import pytest
import json
from app import wczytaj_wszystkie_stacje, wczytaj_wszystkie_lokalizacje


wszystkie_lokalizacje = wczytaj_wszystkie_lokalizacje()

def test_wczytaj_wszystkie_stacje():
    wszystkie_stacje = wczytaj_wszystkie_stacje()
    assert type(wszystkie_stacje) is dict
    for key, value in wszystkie_stacje.items():
        assert isinstance(key, str)
        assert isinstance(value,int)


def test_wczytaj_wszystkie_lokalizacje():
    assert type(wszystkie_lokalizacje) is dict
    for key, value in wszystkie_lokalizacje.items():
        assert isinstance(key, str)
        assert isinstance(value,list)
        assert len(value) == 2
        assert isinstance(value[0], str)
        assert isinstance(value[1], str)
        assert 49.0 <= float(value[0]) <= 55.0
        assert 14.0 <= float(value[1]) <= 24.5

def test_najblzsze_stacje_pomiarowe():
    ...

def zaladuj_dane_json(sciezka):
    with open(file=sciezka, mode='r') as plik:
        return json.load(plik)


def test_wczytaj_wszystkie_stacje_mp(monkeypatch):

    def pobierz_dane_z_pliku():
        return zaladuj_dane_json('testy/dane_testowe.json')

    monkeypatch.setattr('pobieranie_danych.pobierz_dane', pobierz_dane_z_pliku)

    stacje = wczytaj_wszystkie_stacje()

    stacje_json = zaladuj_dane_json('testy/dane_do_testu.json')

    assert stacje == stacje_json