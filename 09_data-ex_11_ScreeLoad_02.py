# 09_data-ex_11_ScreeLoad_02.py 22-06-2026
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from io import StringIO

# --- 1. Die 57 Autos (Kompakter Datenblock) ---
df_original = pd.read_csv("Auto-tabloid.csv")

feats = ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration']
df = df_original.copy()  # Unser dynamisches, schrumpfendes Arbeits-Universum

# --- 2. GUI & Layout ---
# %matplotlib notebook
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
plt.subplots_adjust(bottom=0.22, wspace=0.25)

is_drawing = False

def update():
    global is_drawing
    if is_drawing or len(df) < 3: return
    is_drawing = True
    ax1.clear(); ax2.clear()
    
    # Der Gauß/Lagrange Algorithmus auf Diät
    X = StandardScaler().fit_transform(df[feats])
    vals, vecs = np.linalg.eig(np.cov(X, rowvar=False))
    idx = np.argsort(vals)[::-1]
    vals, vecs = vals[idx], vecs[:, idx]
    
    # Plot 1: Die Beute der Determinanten-Schrumpfung
    ax1.bar(range(1, 7), vals/sum(vals), alpha=0.6, color='royalblue')
    ax1.step(range(1, 7), np.cumsum(vals/sum(vals)), where='mid', color='red')
    ax1.set_title(f"Scree Plot (n={len(df)})"); ax1.set_ylim(0, 1.05)
    
    # Plot 2: Das flache 2D-Flugzeug
    p1, p2 = X @ vecs[:, 0], X @ vecs[:, 1]
    ax2.scatter(p1, p2, c=df['cylinders'], cmap='coolwarm', edgecolors='k', s=40, zorder=2)
    # ax2.scatter(p1, p2, c=df['cylinders'], cmap='coolwarm', edgecolors='k', s=40)
    ax2.set_title("Plattgedrückte Autokarte")
    
    for i, txt in enumerate(df['name']):
        ax2.annotate(txt.split()[0], (p1[i], p2[i]), fontsize=7, alpha=0.6)
        
    is_drawing = False
    fig.canvas.draw_idle()

# --- 3. Interaktive Steuerung (Kumulativ & Reset) ---
tx_box = plt.axes([0.25, 0.04, 0.35, 0.06])
re_box = plt.axes([0.62, 0.04, 0.10, 0.06]) # 10% breiter Resetknopf daneben

box = TextBox(tx_box, 'Dauerhaft sperren: ', initial='')
btn = Button(re_box, 'Reset', color='firebrick', hovercolor='red')
btn.label.set_color('white')

def on_submit(text):
    global df
    if text.strip():
        df = df[~df['name'].str.contains(text, case=False, na=False)].copy()
        box.set_val('') # Box leeren für das nächste Opfer
        update()

def on_reset(event):
    global df
    df = df_original.copy() # Volle Ladung wiederherstellen
    box.set_val('')
    update()

box.on_submit(on_submit)
btn.on_clicked(on_reset)

update()
plt.show()
