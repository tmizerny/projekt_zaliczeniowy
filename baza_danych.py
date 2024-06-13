"""
Moduł grupuje kod obsługujący bazę danych-tworzenie obiektów w bazie ORM, zapis danych do bazy oraz funkcje
zwracające dane z bazy danych
"""

import pandas as pd
import sqlalchemy

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Baza = declarative_base()


# Klasy obiektów do zapisu w bazie danych
class Stacja(Baza):
    """
    Klasa służąca do zapisu stacji pomiarowych w ORM
    """
    __tablename__ = 'stacje'

    # Atrybuty klasy odpowiadające kolumnom w tabeli 'stacje'
    id_stacji = Column(Integer, primary_key=True, unique=True)
    nazwa = Column(String, nullable=False)
    gegrLat = Column(Float, nullable=False)
    gegrLon = Column(Float, nullable=False)

    # Atrybuty definujące relację klasy z innymi obiektami
    parametry = relationship('Parametr', back_populates='stacja')
    indeksy = relationship('Indeks', back_populates='stacja')


class Indeks(Baza):
    """
    Klasa służąca do zapisu indeksu stacji oraz indeksu parametru w ORM
    """
    __tablename__ = 'indeksy'

    # Atrybuty klasy odpowiadające kolumnom w tabeli 'indeksy'
    id = Column(Integer, primary_key=True)
    id_stacji = Column(Integer, ForeignKey('stacje.id_stacji'), nullable=False)
    nazwa_indeksu = Column(String, nullable=False)
    value_indeksu = Column(Integer, nullable=False)
    # Atrybut definujący relację klasy z innym obiektem
    stacja = relationship('Stacja', back_populates='indeksy')


class Parametr(Baza):
    """
    Klasa służąca do zapisu danych parametrów dla stacji pomiarowych w ORM
    """
    __tablename__ = 'parametry'

    # Atrybuty klasy odpowiadające kolumnom w tabeli 'parametry'
    id = Column(Integer, primary_key=True)
    paramCode = Column(String, nullable=False)
    paramName = Column(String, nullable=False)
    id_stacji = Column(Integer, ForeignKey('stacje.id_stacji'), nullable=False)

    # Atrybuty definujące relację klasy z innymi obiektami
    stacja = relationship('Stacja', back_populates='parametry')
    pomiary = relationship('Pomiar', back_populates='parametr')


class Pomiar(Baza):
    """
    Klasa służąca do zapisu pomiarów dla parametrów w ORM
    """
    __tablename__ = 'pomiary'

    # Atrybuty klasy odpowiadające kolumnom w tabeli 'pomiary'
    id = Column(Integer, primary_key=True)
    parametr_id = Column(Integer, ForeignKey('parametry.id'), nullable=False)
    date = Column(String, nullable=False)
    value = Column(Float)
    # Atrybut definujący relację klasy z innym obiektem
    parametr = relationship('Parametr', back_populates='pomiary')


# Kod konfigurujący połączenie z bazą danych oraz tworzący sesję
engine = create_engine('sqlite:///baza_danych.db')
Baza.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def dodaj_do_bazy_danych(stacje, lokalizacje, funkcja):
    """
    Funkcja tworząca obiekty i dodająca je do ORM, na podstawie otrzymanych słowników oraz plików otrzymanych
    z zapytania do usługi REST
    :param stacje: słownik ze stacjami pomiarowymi {nazwa_stacji: id_stacji}
    :param lokalizacje: słownik z lokalizacjami stacji pomiarowych {nazwa stacji: [długość_geograficzna, szerokość_geograficzna]}
    :param funkcja: obiekt funkcji pobierz dane
    """
    # Pętla po stacjach pomiarowych
    for nazwa, id_stacji in stacje.items():
        print(f'Dodaję stację {nazwa}')
        gegrLat, gegrLon = lokalizacje[nazwa]
        stacja = Stacja(id_stacji=id_stacji, nazwa=nazwa, gegrLat=gegrLat, gegrLon=gegrLon)
        session.add(stacja)
        lista_czujnikow = funkcja(2, id_stacji)
        lista_indeksow = funkcja(4, id_stacji)
        # Pętla po czujnikach stacji pomiarowych
        for czujnik in lista_czujnikow:
            parametr = Parametr(id=czujnik['id'], paramCode=czujnik['param']['paramCode'],
                                paramName=czujnik['param']['paramName'], id_stacji=id_stacji)
            pomiary = funkcja(3, czujnik['id'])['values']
            # Pętla po pomiarach dla parametru
            for slownik in pomiary:
                pomiar = Pomiar(parametr_id=czujnik['id'], date=slownik['date'], value=slownik['value'])
                session.add(pomiar)
            session.add(parametr)
        # Pętla po indeksach stacji oraz parametrów
        for indeks, slownik in lista_indeksow.items():
            if 'IndexLevel' in indeks:
                if slownik is None:
                    continue
                else:
                    indeks = Indeks(id_stacji=id_stacji, nazwa_indeksu=indeks, value_indeksu=slownik['id'])
                    session.add(indeks)
    print('Dodano wszystko')
    session.commit()


def wczytaj_stacje_bd():
    """
    Bezargumentowa funkcja zwracająca słownik z query do bazy danych
    :return: słownik ze stacjami pomiarowymi {nazwa_stacji: id_stacji}
    """
    return {stacja.nazwa: stacja.id_stacji for stacja in session.query(Stacja).all()}


def wczytaj_lokalizacje_bd():
    """
    Bezargumentowa funkcja zwracająca słownik z query do bazy danych
    :return: słownik z lokalizacjami stacji pomiarowych {nazwa stacji: [długość_geograficzna, szerokość_geograficzna]}
    """
    return {stacja.nazwa: [stacja.gegrLat, stacja.gegrLon] for stacja in session.query(Stacja).all()}


def wczytaj_parametry_bd(id_stacji):
    """
    Funkcja zwracająca listę słowników z query do bazy danych przy podaniu id_stacji
    :param id_stacji: identyfikator stacji pomiarowej
    :return: lista słowników {wzór chemiczny/kod parametru: słowna nazwa parametru}
    """
    return [{parametr.paramCode: parametr.paramName} for parametr in
            session.query(Parametr).filter_by(id_stacji=id_stacji).all()]


def wczytaj_parametry_z_pomiarami_bd(id_stacji):
    """
    Funkcja zwracająca słownik z pomiarami dla stacji pomiarowej z query do bazy danych przy podaniu id_stacji oraz
    storzenie z dat i pomiarów ramki danych
    :param id_stacji: identyfikator stacji pomiarowej
    :return: słownik z pomiarami dla stacji {parametr: ramka danych (data, wartość_pomiaru)}
    """
    parametry_dict = {}
    for parametr in session.query(Parametr).filter_by(id_stacji=id_stacji).all():
        pomiary = session.query(Pomiar).filter_by(parametr_id=parametr.id).all()
        data = {pomiar.date: pomiar.value for pomiar in pomiary}
        df = pd.DataFrame(list(data.items()), columns=['date', 'value']).fillna(0)
        parametry_dict[parametr.paramCode] = df
    return parametry_dict


def wczytaj_indeksy_stacji_parametrow_bd(id_stacji):
    """
    Funkcja zwracająca słownik indeksami z query do bazy danych przy podaniu id_stacji
    :param id_stacji: identyfikator stacji pomiarowej
    :return: słownik z indeksami dla stacji {indeks: wartość_indeksu}
    """
    return {indeks.nazwa_indeksu: indeks.value_indeksu for indeks in
            session.query(Indeks).filter_by(id_stacji=id_stacji).all()}


# Zamknięcie sesji
session.close()
