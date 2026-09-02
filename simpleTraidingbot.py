import csv
from alpaca_trade_api.rest import REST, TimeFrame
import time

from matplotlib.pylab import size
import strategy as str
##importowanie kluczy
import os
from pathlib import Path
from dotenv import load_dotenv

sciezka_env = Path(r"C:\Users\AzjaM\Desktop\Mateusz Pęcak\Programowanie\TaraidingBot_01\Keys.env")
load_dotenv(dotenv_path=sciezka_env)

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
base_url = os.getenv("BASE_URL")
##
api = REST(api_key, api_secret, base_url)

#account = api.get_account()
#print(account.status)

tickers_to_monitor = ["INTC", "DAL","T"]
lista_spolek = []
l_spolek=0

BASE_DIR = Path(__file__).resolve().parent
sciezka_pliku = BASE_DIR / "spolki.csv"
try:
    with open(sciezka_pliku, mode='r', encoding='utf-8') as plik:
        czytnik = csv.reader(plik)
        
        # Pominięcie nagłówka (pierwszego wiersza z nazwami)
        next(czytnik, None)

        for wiersz in czytnik:
            # Pobiera pierwsze 4 kolumny niezależnie od ich nazw
            if len(wiersz) >= 4:
                lista_spolek.append(wiersz[:4])
                print(f"Dodano spółkę: {wiersz[0]} z parametrami: {wiersz[1]}, {wiersz[2]}, {wiersz[3]}")

    print(f"Załadowano {len(lista_spolek)} wierszy.")

except Exception as e:
    print(f"Błąd podczas wczytywania:\n{e}")

while True:
    for i in range(0, len(lista_spolek)):
        ticker=lista_spolek[i][0]  # Pobranie i przetworzenie tickera
        window_fast=int(lista_spolek[i][2])
        window_slow=int(lista_spolek[i][3])
        bars = api.get_bars(ticker, TimeFrame.Hour, limit=100).df
        # Zabezpieczenie przed pustą tabelą w weekendy:
        if bars.empty:
            print(f"Giełda zamknięta - brak danych dla {ticker}")
            continue

        signal = str.simple_moving_average_strat(bars, window_fast, window_slow)
        print(f"Signal for {ticker} = {signal}")
        str.place_order(signal, ticker, 1, api)
    time.sleep(900)
    