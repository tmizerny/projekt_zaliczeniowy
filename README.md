# Jakość powietrza w Polsce 

### Aplikacja webowa służaca do wyświetlania danych pomiarowych dotyczących jakości powietrza w Polsce


Aby uruchomić aplikację należy uruchomić lokalny host wpisująć w terminalu komendę: **panel serve app.py --autoreload**

Aplikacja **pobiera dane** z usługi REST prowadzonej prze GIOS. W przypadku braku połączenia z usługą program **obsługuje wyjątki** przy braku dostępności usługi czy braku łączności. Za wyświetlanie wiadomości error handlera odpowiedzialny jest widget z alertami.
Użytkownik jest napierw poproszony o wybranie źródła danych. 
Następnie użytkownik otrzymuje **pełną listę** nazw stacji w Polsce. 

