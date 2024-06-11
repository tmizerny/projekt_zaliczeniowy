import pandas as pd
import sqlalchemy
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


Baza = declarative_base()


class Stacja(Baza):
    __tablename__ = 'stacje'

    id_stacji = Column(Integer, primary_key=True, unique=True)
    nazwa = Column(String, nullable=False)
    gegrLat = Column(Float, nullable=False)
    gegrLon = Column(Float, nullable=False)
    parametry = relationship('Parametr', back_populates='stacja')
    indeksy = relationship('Indeks', back_populates='stacja')


class Indeks(Baza):
    __tablename__ = 'indeksy'

    id = Column(Integer, primary_key=True)
    id_stacji = Column(Integer, ForeignKey('stacje.id_stacji'), nullable=False)
    nazwa_indeksu = Column(String, nullable=False)
    value_indeksu = Column(Integer, nullable=False)
    stacja = relationship('Stacja', back_populates='indeksy')


class Parametr(Baza):
    __tablename__ = 'parametry'

    id = Column(Integer, primary_key=True)
    paramCode = Column(String, nullable=False)
    paramName = Column(String, nullable=False)
    id_stacji = Column(Integer, ForeignKey('stacje.id_stacji'), nullable=False)
    stacja = relationship('Stacja', back_populates='parametry')
    pomiary = relationship('Pomiar', back_populates='parametr')


class Pomiar(Baza):
    __tablename__ = 'pomiary'

    id = Column(Integer, primary_key=True)
    parametr_id = Column(Integer, ForeignKey('parametry.id'), nullable=False)
    date = Column(String, nullable=False)
    value = Column(Float)
    parametr = relationship('Parametr', back_populates='pomiary')


engine = create_engine('sqlite:///baza_danych.db')
Baza.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def dodaj_do_bazy_danych(stacje, lokalizacje, funkcja):

    for nazwa, id_stacji in stacje.items():
        print(f'Dodaję stację {nazwa}')
        gegrLat, gegrLon = lokalizacje[nazwa]
        stacja = Stacja(id_stacji=id_stacji, nazwa=nazwa, gegrLat=gegrLat, gegrLon=gegrLon)
        session.add(stacja)
        lista_czujnikow = funkcja(2, id_stacji)
        lista_indeksow = funkcja(4, id_stacji)
        for czujnik in lista_czujnikow:
            parametr = Parametr(id=czujnik['id'], paramCode=czujnik['param']['paramCode'],
                                paramName=czujnik['param']['paramName'], id_stacji=id_stacji)
            pomiary = funkcja(3, czujnik['id'])['values']
            for slownik in pomiary:
                pomiar = Pomiar(parametr_id=czujnik['id'], date=slownik['date'], value=slownik['value'])

                session.add(pomiar)
            session.add(parametr)
        for indeks, slownik in lista_indeksow.items():
            if 'IndexLevel' in indeks:
                if slownik is None:
                    continue
                else:
                    indeks = Indeks(id_stacji=id_stacji, nazwa_indeksu=indeks, value_indeksu=slownik['id'])
                    session.add(indeks)
    print('Dodano wszystko')
    session.commit()



# dodaj_do_bazy_danych(stacje_dict, lokalizacje)


def wczytaj_stacje_bd():
    return {stacja.nazwa: stacja.id_stacji for stacja in session.query(Stacja).all()}


#
# print(wczytaj_stacje_bd())

def wczytaj_lokalizacje_bd():
    return {stacja.nazwa: [stacja.gegrLat, stacja.gegrLon] for stacja in session.query(Stacja).all()}
#

#
def wczytaj_parametry_bd(id_stacji):
    return [{parametr.paramCode: parametr.paramName} for parametr in session.query(Parametr).filter_by(id_stacji=id_stacji).all()]




def wczytaj_parametry_z_pomiarami_bd(id_stacji):
    parametry_dict = {}
    for parametr in session.query(Parametr).filter_by(id_stacji=id_stacji).all():
        pomiary = session.query(Pomiar).filter_by(parametr_id=parametr.id).all()
        data = {pomiar.date: pomiar.value for pomiar in pomiary}
        df = pd.DataFrame(list(data.items()), columns=['date', 'value']).fillna(0)
        parametry_dict[parametr.paramCode] = df
    return parametry_dict

def wczytaj_indeksy_stacji_parametrow_bd(id_stacji):
    return {indeks.nazwa_indeksu : indeks.value_indeksu for indeks in session.query(Indeks).filter_by(id_stacji=id_stacji).all()}



session.close()
