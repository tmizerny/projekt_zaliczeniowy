


class Commune:
    """
    Klasa reprezentująca gminę
    """

    __instances = {}

    def __new__(cls, provinceName, districtName, communeName):
        key = (provinceName, districtName, communeName)
        if key not in cls.__instances:
            instance = super(Commune, cls).__new__(cls)
            instance.provinceName = provinceName
            instance.districtName = districtName
            instance.communeName = communeName
            cls.__instances[key] = instance
        return cls.__instances[key]

    def __init__(self, provinceName, districtName, communeName):
        self.__communeName = communeName
        self.__districtName = districtName
        self.__provinceName = provinceName

    # Properties parametrów
    @property
    def commune_name(self):
        return self.__communeName

    @property
    def district_name(self):
        return self.__districtName

    @property
    def province_name(self):
        return self.__provinceName

    # Settery parametrów

    @commune_name.setter
    def commune_name(self, communeName):
        self.__communeName = communeName

    @district_name.setter
    def district_name(self, districtName):
        self.__districtName = districtName

    @province_name.setter
    def province_name(self, provinceName):
        self.__provinceName = provinceName

    def __str__(self):
        return (f"Stacja znajduje się w wojewdztwie: {self.province_name}, "
                f"powiecie {self.districtName}, gminie {self.commune_name}")




class City:
    """
    Klasa reprezentująca miejscowość
    """

    __instances = {}

    def __new__(cls, id, name, commune):
        key = (id, name, commune['communeName'])
        if key not in cls.__instances:
            instance = super(City, cls).__new__(cls)
            instance.id = id
            instance.name = name
            instance.commune = commune
            cls.__instances[key] = instance
        return cls.__instances[key]

    def __init__(self, id, name,commune):
        self.__cityId = id
        self.__cityName = name
        self.__commune = Commune(**commune)

    @property
    def city_id(self):
        return self.__cityId

    @property
    def city_name(self):
        return self.__cityName

    @property
    def commune(self):
        return self.__commune

    @city_id.setter
    def city_id(self, cityId):
        self.__cityId = cityId

    @city_name.setter
    def city_name(self, cityName):
        self.__cityId = cityName

    @commune.setter
    def commune(self, commune):
        self.__commune = commune

    def __str__(self):
        return f"Stacja jest w mieście {self.city_name} o numerze ID={self.city_id}"


class Station:
    """
    Klasa reprezentująca stację pomiarową
    """

    def __init__(self, id, stationName, gegrLat, gegrLon, city, addressStreet):
        self.__stationId = id
        self.__stationName = stationName
        self.__gegrLat = gegrLat
        self.__gegrLon = gegrLon
        self.__addressStreet = addressStreet
        self.city = City(**city)

    @property
    def station_id(self):
        return self.__stationId

    @property
    def station_name(self):
        return self.__stationName

    @property
    def gegr_lat(self):
        return self.__gegrLat

    @property
    def gegr_lon(self):
        return self.__gegrLon

    @property
    def address(self):
        return self.__addressStreet

    @station_id.setter
    def station_id(self, stationId):
        self.__stationId = stationId

    @station_name.setter
    def station_name(self, stationName):
        self.__stationName = stationName

    @gegr_lat.setter
    def gegr_lat(self, gegrLat):
        self.__gegrLat = gegrLat

    @gegr_lon.setter
    def gegr_lon(self, gegrLon):
        self.__gegrLon = gegrLon

    @address.setter
    def address(self, addressStreet):
        self.__addressStreet = addressStreet

    def __str__(self):
        return (f'Stacja o Id={self.station_id}, o nazwie {self.station_name}, znajduje się na koordynatach '
                f'{self.gegr_lat}{self.gegr_lon} przy ulicy {self.address}')


class Sensor:
    """
    Klasa reprezentująca stanowisko pomiarowe
    """

    def __init__(self, id, stationId, param):
        self.__id = id
        self.__stationId = stationId
        self.param = Param(**param)

    @property
    def id(self):
        return self.__id

    @property
    def station_id(self):
        return self.__stationId

    @id.setter
    def id(self, _id):
        self.__id = _id

    @station_id.setter
    def station_id(self, stationId):
        self.__stationId = stationId

    def __str__(self):
        return f'Stacja o Id/Station Id {self.id}/{self.station_id}'


class Param:
    """
    Klasa reprezentująca parametr pomiarowy
    """

    def __init__(self, paramName, paramFormula, paramCode, idParam):
        self.__paramName = paramName
        self.__paramFormula = paramFormula
        self.__paramCode = paramCode
        self.__idParam = idParam

    @property
    def param_name(self):
        return self.__paramName

    @property
    def param_formula(self):
        return self.__paramFormula

    @property
    def param_code(self):
        return self.__paramCode

    @property
    def id_param(self):
        return self.__idParam

    @param_name.setter
    def param_name(self, paramName):
        self.__paramName = paramName

    @param_formula.setter
    def param_formula(self, paramFormula):
        self.__paramFormula = paramFormula

    @param_code.setter
    def param_code(self, paramCode):
        self.__paramCode = paramCode

    @id_param.setter
    def id_param(self, idParam):
        self.__idParam = idParam

    def __str__(self):
        return (f'Parametry badane przez stacje: \n'
                f'Id parametru: {self.id_param} \n'
                f'Nazwa parametru: {self.param_name} \n'
                f'Wzór parametru: {self.param_formula}\n')


class Value:
    """
    Klasa reprezentująca pojedynczy pomiar
    """

    def __init__(self, date, value):
        self.date = _Data(date) #
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):

        self.__value = 'Brak pomiaru' if value is None else value

    def __str__(self):
        return f"Wartość pomiaru wynosiła {self.value}"
class _Data:
    """
    Klasa reprezentująca zestaw danych pomiarowych
    """

    def __init__(self, date):
        self.__date, self.__time = date.split()


    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        self.__date = date

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, date):
        self.__time = date

    def __str__(self):
        return f'Pomiar zanotowano w dniu {self.date} o godzinie {self.time}'
