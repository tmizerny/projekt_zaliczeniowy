import sqlite3
from pobieranie_danych import pobierz_dane

stacje_dict = {stacja['stationName']: stacja['id'] for stacja in pobierz_dane(1)}
lokalizacje = {stacja['stationName']: [stacja['gegrLat'], stacja['gegrLon']] for stacja in pobierz_dane(1)}


sql_select_all = '''
SELECT nazwa, id_stacji, gegrLat, gegrLon FROM stacje'''
sql_select_stacje = '''
SELECT nazwa, id_stacji FROM stacje'''
sql_select_stacje_lokalizacja = '''SELECT nazwa, gegrLat, gegrLon FROM stacje'''


sql_select_parametry = '''SELECT * FROM parametry'''


def rob_tabele_stacji(cur: sqlite3.Cursor):
    sql_drop = 'DROP TABLE IF EXISTS stacje'
    cur.execute(sql_drop)
    sql1 = '''
    CREATE TABLE IF NOT EXISTS stacje (
                    id_stacji INTEGER PRIMARY KEY,
                    nazwa TEXT,
                    gegrLat REAL,
                    gegrLon REAL
                 )'''
    cur.execute(sql1)

def rob_tabele_parametry(cur: sqlite3.Cursor):
    sql_drop = 'DROP TABLE IF EXISTS parametry'
    cur.execute(sql_drop)
    sql_create = f'''
    CREATE TABLE parametry (
                    id INTEGER PRIMARY KEY,
                    id_stacji INTEGER,
                    paramCode TEXT,
                    paramName TEXT,
                    FOREIGN KEY (id_stacji) REFERENCES stacje(id_stacji)
                 )'''
    cur.execute(sql_create)
def dodaj_stacje(cur: sqlite3.Cursor, nazwa: str, id_stacji: int, gegrLat: float, gegrLon: float):
    sql = """
        INSERT INTO stacje (nazwa, id_stacji, gegrLat, gegrLon)
        VALUES (?, ?, ?, ?);
        """
    cur.execute(sql, (nazwa, id_stacji, gegrLat, gegrLon))

def dodaj_parametr(cur: sqlite3.Cursor, id_stacji: int, paramCode: str, paramName: str):
    sql_insert = """
        INSERT INTO parametry (id_stacji, paramCode, paramName)
        VALUES (?, ?, ?);
        """
    cur.execute(sql_insert, (id_stacji, paramCode, paramName))

with sqlite3.connect('baza_danych.db') as conn:
    cur = conn.cursor()
    rob_tabele_stacji(cur)
    rob_tabele_parametry(cur)
    for nazwa, id_stacji in stacje_dict.items():
        szerokosc, dlugosc = lokalizacje[nazwa]
        dodaj_stacje(cur, nazwa, id_stacji, szerokosc, dlugosc)
        lista_czujnikow = pobierz_dane(2, id_stacji)

        for parametr in lista_czujnikow:
            paramCode = parametr['param']['paramCode']
            paramName = parametr['param']['paramName']
            dodaj_parametr(cur, id_stacji, paramCode, paramName)

    conn.commit()

def pobierz_wszystkie_stacje():
    with sqlite3.connect('baza_danych.db') as conn:
        cur = conn.cursor()
        cur.execute(sql_select_stacje)
        return cur.fetchall()

def pobierz_wszystkie_stacje_lokalizacja():
    with sqlite3.connect('baza_danych.db') as conn:
        cur = conn.cursor()
        cur.execute(sql_select_stacje_lokalizacja)
        stacje_lok = cur.fetchall()
        return {stacja[0]:[stacja[1],stacja[2]] for stacja in stacje_lok}


def pobierz_wszystkie_parametry():
    with sqlite3.connect('baza_danych.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM parametry")
        return cur.fetchall()


# print(pobierz_wszystkie_parametry())