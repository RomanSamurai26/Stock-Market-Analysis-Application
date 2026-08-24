# ogolno dostepne importy
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math as m

# prywatne klasy i funkcje do obsługi aplikacji giełdowej
import AplikacjaGieldowa as ag

# Uruchomienie aplikacji
if __name__ == "__main__":
    root = tk.Tk()
    app = ag.AplikacjaGieldowa(root)
    root.mainloop()