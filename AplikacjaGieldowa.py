import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv

class AplikacjaGieldowa:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizator Giełdowy")
        self.root.geometry("1500x600")

        # --- BAZA DANYCH APLIKACJI ---
        self.dane_spolek = []      # Lista przechowująca pobrane dane (DataFrame)
        self.nazwy_spolek = []     # Lista przechowująca nazwy (Tickery)
        self.lista_spolek = []     # Lista przechowująca nazwy spółek z pliku CSV
        self.aktualny_indeks = -1  # Wskazuje, który wykres aktualnie wyświetlamy

        self.apro1 = None  # Placeholder for Aproksymacja 1
        self.apro2 = None  # Placeholder for Aproksymacja 2

        
        print("Inicjalizacja aplikacji giełdowej...")
        self.buduj_interfejs()
        print("Interfejs zbudowany.")
        print("Wczytywanie nazw spółek z pliku CSV...")
        self.wczytaj_nazwy_spolek('spolki.csv')  # Wczytanie nazw spółek z pliku CSV
        print("Nazwy spółek wczytane.")
        

    def buduj_interfejs(self):
        # ==========================================
        # GŁÓWNY PODZIAŁ OKNA (LEWA I PRAWA STRONA)
        # ==========================================
        self.lewy_panel = tk.Frame(self.root, width=250, bg="#f0f0f0", padx=10, pady=10)
        self.lewy_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.srodek_panel = tk.Frame(self.root, width=10, bg="#d0d0d0")
        self.srodek_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.prawy_panel = tk.Frame(self.root, bg="white", bd=2, relief=tk.SUNKEN)
        self.prawy_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        

        # ==========================================
        # LEWY PANEL - 3 SEGMENTY
        # ==========================================
        
        # --- SEGMENT 1: Import spółki ---
        frame_import = tk.LabelFrame(self.lewy_panel, text="1. Import Spółki", padx=5, pady=5, bg="#f0f0f0")
        frame_import.pack(fill=tk.X, pady=10)

        tk.Label(frame_import, text="Podaj Ticker (np. AAPL, CDR.WA):", bg="#f0f0f0").pack(anchor=tk.W)
        self.pole_ticker = tk.Entry(frame_import)
        self.pole_ticker.pack(fill=tk.X, pady=5)

        tk.Label(frame_import, text="Kategoria spółki:", bg="#f0f0f0").pack(anchor=tk.W)
        self.wybor_kategorii = ttk.Combobox(frame_import, values=["PolskaGielda", "FunduszeETF", "IndeksyGieldowe", "Waluty", "Surowce", "Kryptowaluty", "Inne"])
        self.wybor_kategorii.set("FunduszeETF") # Domyślna wartość
        self.wybor_kategorii.pack(fill=tk.X, pady=5)
        
        btn_wczytaj = tk.Button(frame_import, text="Pobierz dane", command=self.wczytaj_dane)
        btn_wczytaj.pack(fill=tk.X)

        # --- SEGMENT 2: Ustawienia ---
        frame_ustawienia = tk.LabelFrame(self.lewy_panel, text="2. Ustawienia", padx=5, pady=5, bg="#f0f0f0")
        frame_ustawienia.pack(fill=tk.X, pady=10)

        tk.Label(frame_ustawienia, text="Aproksymacja 1", bg="#f0f0f0").pack(anchor=tk.W)
        self.pole_Apro1 = tk.Entry(frame_ustawienia)
        self.pole_Apro1.pack(fill=tk.X, pady=5)
        tk.Label(frame_ustawienia, text="Aproksymacja 2", bg="#f0f0f0").pack(anchor=tk.W)
        self.pole_Apro2 = tk.Entry(frame_ustawienia)
        self.pole_Apro2.pack(fill=tk.X, pady=5)

        btn_update_settings = tk.Button(frame_ustawienia, text="Zaktualizuj ustawienia", command=self.zaktualizuj_ustawienia)
        btn_update_settings.pack(fill=tk.X)

        # --- SEGMENT 3: Status / Wczytane spółki ---
        frame_status = tk.LabelFrame(self.lewy_panel, text="3. Pobrane Spółki", padx=5, pady=5, bg="#f0f0f0")
        frame_status.pack(fill=tk.BOTH, expand=True, pady=10)

        self.lista_spolek_widget = tk.Listbox(frame_status)
        self.lista_spolek_widget.pack(fill=tk.BOTH, expand=True)

        # ==========================================
        # SRODEK PANEL - SEPARATOR
        # ==========================================

        
        
        # --- Obszar na wykres ---
        self.obszar_wykresu = tk.Frame(self.srodek_panel, bg="white")
        self.obszar_wykresu.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.obszar_wykresu, text="Wczytaj spółkę, aby zobaczyć wykres", bg="white").pack(pady=200)

        # --- Panel Nawigacji (Prev / Next) ---
        panel_nawigacji = tk.Frame(self.srodek_panel, bg="#e0e0e0", pady=5)
        panel_nawigacji.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_prev = tk.Button(panel_nawigacji, text="<<< Poprzedni", command=self.pokaz_poprzedni, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=20)

        self.etykieta_pozycji = tk.Label(panel_nawigacji, text="Brak danych", bg="#e0e0e0")
        self.etykieta_pozycji.pack(side=tk.LEFT, expand=True)

        self.btn_next = tk.Button(panel_nawigacji, text="Następny >>>", command=self.pokaz_nastepny, state=tk.DISABLED)
        self.btn_next.pack(side=tk.RIGHT, padx=20)


        # ==========================================
        # PRAWY PANEL - WYKRES I NAWIGACJA
        # ==========================================

        self.obszar_tabeli = tk.Frame(self.prawy_panel, bg="white")
        self.obszar_tabeli.pack(fill=tk.BOTH, expand=True)

        # ==========================================
        # TABELA DANYCH (Treeview)
        # ==========================================
        # Definiujemy identyfikatory kolumn
        kolumny = ("nr", "nazwa", "zysk")
        
        # Tworzymy widżet tabeli (show="headings" ukrywa domyślną pustą kolumnę z lewej strony)
        self.tabela = ttk.Treeview(self.obszar_tabeli, columns=kolumny, show="headings")

        # Ustawiamy nagłówki kolumn
        self.tabela.heading("nr", text="Nr")
        self.tabela.heading("nazwa", text="Nazwa akcji")
        self.tabela.heading("zysk", text="Zysk")

        # Formatujemy szerokość i wyrównanie tekstu w kolumnach
        self.tabela.column("nr", width=50, anchor=tk.CENTER)
        self.tabela.column("nazwa", width=150, anchor=tk.W) # W = West (do lewej)
        self.tabela.column("zysk", width=100, anchor=tk.E)  # E = East (do prawej)

        # Tworzymy pionowy pasek przewijania
        scrollbar = ttk.Scrollbar(self.obszar_tabeli, orient=tk.VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscroll=scrollbar.set)

        # Umieszczamy scrollbar i tabelę w ramce
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ==========================================
    # LOGIKA APLIKACJI
    # ==========================================
    def wczytaj_nazwy_spolek(self,file_name):
        try:
            with open('spolki.csv', mode='r', encoding='utf-8') as plik:
                # DictReader automatycznie traktuje pierwszy wiersz jako nazwy kolumn
                czytnik = csv.DictReader(plik)
            
                for wiersz in czytnik:
                    # Dodajemy każdy wiersz do naszego "wektora"
                    self.lista_spolek.append({
                        "ticker": wiersz["Ticker"], 
                        "kategoria": wiersz["Kategoria"]
                    })

                    ticker=wiersz["Ticker"].strip().upper()  # Pobranie i przetworzenie tickera
                    kategoria=wiersz["Kategoria"].strip()  # Pobranie i przetworzenie kategorii
                    # Pobieranie danych z yfinance
                    spolka = yf.Ticker(ticker)
                    df = spolka.history(period="max")

                    if df.empty:
                        messagebox.showerror("Błąd", f"Nie znaleziono danych dla: {ticker}")
                        return

                    # Zapisanie do "bazy"
                    self.dane_spolek.append(df)
                    self.nazwy_spolek.append(f"{ticker} ({kategoria})")

                    # Dodanie do listy w interfejsie
                    self.lista_spolek_widget.insert(tk.END, self.nazwy_spolek[-1])

                # Ustawienie ostatniej spółki jako aktualnej i narysowanie
                self.aktualny_indeks = len(self.dane_spolek) - 1
                self.rysuj_wykres()
        except Exception as e:
                    messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania:\n{str(e)}")

    def wczytaj_dane(self):
        ticker = self.pole_ticker.get().upper().strip()
        kategoria = self.wybor_kategorii.get()

        if not ticker:
            messagebox.showwarning("Błąd", "Wpisz symbol spółki!")
            return
        if ticker in [nazwa.split()[0] for nazwa in self.nazwy_spolek]:
            messagebox.showwarning("Błąd", f"Dane dla {ticker} już zostały wczytane!")
            return

        try:
            # Pobieranie danych z yfinance
            spolka = yf.Ticker(ticker)
            df = spolka.history(period="max")

            if df.empty:
                messagebox.showerror("Błąd", f"Nie znaleziono danych dla: {ticker}")
                return

            # Zapisanie do "bazy"
            self.dane_spolek.append(df)
            self.nazwy_spolek.append(f"{ticker} ({kategoria})")
            
            # Dodanie do listy w interfejsie
            self.lista_spolek_widget.insert(tk.END, self.nazwy_spolek[-1])

            # Ustawienie nowej spółki jako aktualnej i narysowanie
            self.aktualny_indeks = len(self.dane_spolek) - 1
            self.rysuj_wykres()

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas pobierania:\n{str(e)}")

    def zaktualizuj_ustawienia(self):
        apro1 = self.pole_Apro1.get().strip()
        apro2 = self.pole_Apro2.get().strip()

        # Tutaj można dodać logikę do aktualizacji ustawień w aplikacji
        messagebox.showinfo("Ustawienia", f"Aproksymacja 1: {apro1}\nAproksymacja 2: {apro2}")

    def rysuj_wykres(self):
        if self.aktualny_indeks < 0 or not self.dane_spolek:
            return

        # 1. Czyszczenie starego wykresu
        for widget in self.obszar_wykresu.winfo_children():
            widget.destroy()

        # 2. Pobranie odpowiednich danych
        df = self.dane_spolek[self.aktualny_indeks]
        tytul = self.nazwy_spolek[self.aktualny_indeks]

        # 3. Rysowanie nowego wykresu mplfinance
        fig, axlist = mpf.plot(
            df,
            type='candle',
            style='yahoo',
            title=tytul,
            ylabel='Cena',
            returnfig=True,
            figsize=(8, 5)
        )

        # 4. Osadzenie w oknie
        canvas = FigureCanvasTkAgg(fig, master=self.obszar_wykresu)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Ważne: zamykamy figurę w pamięci Matplotlib, aby nie wyciekał RAM
        plt.close(fig)

        self.aktualizuj_przyciski()

    def pokaz_poprzedni(self):
        if self.aktualny_indeks > 0:
            self.aktualny_indeks -= 1
            self.rysuj_wykres()

    def pokaz_nastepny(self):
        if self.aktualny_indeks < len(self.dane_spolek) - 1:
            self.aktualny_indeks += 1
            self.rysuj_wykres()

    def aktualizuj_przyciski(self):
        # Wyświetlanie np. "1 z 3"
        total = len(self.dane_spolek)
        current = self.aktualny_indeks + 1
        self.etykieta_pozycji.config(text=f"Wykres {current} z {total}")

        # Włączanie/wyłączanie przycisku Poprzedni
        if self.aktualny_indeks > 0:
            self.btn_prev.config(state=tk.NORMAL)
        else:
            self.btn_prev.config(state=tk.DISABLED)

        # Włączanie/wyłączanie przycisku Następny
        if self.aktualny_indeks < len(self.dane_spolek) - 1:
            self.btn_next.config(state=tk.NORMAL)
        else:
            self.btn_next.config(state=tk.DISABLED)
