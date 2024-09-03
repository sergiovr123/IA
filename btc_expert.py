import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from finta import TA
#yahoo finance portal
import yfinance as yf
#clips import
import clips
# Variable global para mantener el canvas actual
canvas = None

def expert_system(df):
    sistemaExperto= clips.Environment()
    sistemaExperto.clear()
    #se definen las reglas
    reglaComprar = ("(defrule reglaComprar (comprar) => (assert(comprarDivisa)))")
    reglaVender = ("(defrule reglaVender (vender) => (assert(venderDivisa)))")
    sistemaExperto.build(reglaComprar)
    sistemaExperto.build(reglaVender)

    df['SMA30'] = TA.SMA(df, 30)
    df['RSI14'] = TA.RSI(df, 14)
    
    # Estrategia de compra basada en RSI
    buy_signal = (df['RSI14'] < 30)
    print(buy_signal)
    # si cumple estrategia entonces inserta hecho para habilitar la compra
    if buy_signal.iloc[-1]:
        print("Cumple RSI compra")
        sistemaExperto.assert_string('(comprar)')

     # Estrategia de venta basada en RSI
    sell_signal = (df['RSI14'] > 70)
    if sell_signal.iloc[-1]:
        print("Cumple RSI venta")
        sistemaExperto.assert_string('(vender)')

    for r in sistemaExperto.rules():
        print(r)

    sistemaExperto.run()
    for fact in sistemaExperto.facts():
        factString=str(fact)
        if "comprarDivisa" in factString:
            print ("comprarDivisa")
            return "Comprar Divisa AHORA!"
        elif "venderDivisa" in factString:
            print ("Vender divisa")
            return "Vender divisa AHORA!"

# Función para obtener datos de BTC usando yfinance
def get_btc_data(start_date,end_date):
    # Descargar datos históricos de BTC
    #df = yf.download('BTC-USD', start='2024-06-01', end='2024-06-29', interval='1d')
    df = yf.download('BTC-USD', start=start_date, end=end_date, interval='1d')
    df.reset_index(inplace=True)
    return df

# Función para mostrar el gráfico
def plot_data(df):
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(12, 8), sharex=True)

    # Gráfico del precio
    ax1.plot(df['Date'], df['Close'], label='BTC Price', color='blue')
    ax1.plot(df['Date'], df['SMA30'], label='SMA 30', color='red')
    ax1.set_ylabel('Precio (USD)')
    ax1.set_title('Gráfico del BTC')
    ax1.legend()
    
    # Gráfico del RSI
    ax2.plot(df['Date'], df['RSI14'], label='RSI 14', color='green')
    ax2.axhline(y=70, color='r', linestyle='--', label='Sobrecompra')
    ax2.axhline(y=30, color='b', linestyle='--', label='Sobreventa')
    ax2.set_xlabel('Fecha')
    ax2.set_ylabel('RSI')
    ax2.set_title('RSI del BTC')
    ax2.legend()
    
    return fig

# Función para actualizar la interfaz gráfica
def update_gui():
    sistemaExperto= clips.Environment()
    sistemaExperto.clear()
    global canvas
    start_date = entry_start_date.get()
    end_date = entry_end_date.get()
    
    if not start_date or not end_date:
        messagebox.showerror("Error", "Por favor, ingrese las fechas de inicio y fin.")
        return
    
    df = get_btc_data(start_date,end_date)
    recommendation = expert_system(df)
    
    fig = plot_data(df)
    
    # Mostrar recomendación en un cuadro de diálogo
    messagebox.showinfo("Recomendación de Compra", f"Recomendación: {recommendation}")
    
     # Eliminar el canvas anterior si existe
    if canvas is not None:
        canvas.get_tk_widget().destroy()
    # Mostrar gráfico en tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Configuración de la interfaz gráfica
window = tk.Tk()
window.title("Análisis de BTC")
window.geometry("800x600")

button = tk.Button(window, text="Actualizar Análisis", command=update_gui)
button.pack(pady=20)
# Etiquetas y campos de texto para las fechas
tk.Label(window, text="Fecha de Inicio (YYYY-MM-DD):").pack(pady=5)
entry_start_date = tk.Entry(window)
entry_start_date.pack(pady=5)

tk.Label(window, text="Fecha de Fin (YYYY-MM-DD):").pack(pady=5)
entry_end_date = tk.Entry(window)
entry_end_date.pack(pady=5)

window.mainloop()