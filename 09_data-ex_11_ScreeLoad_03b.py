# 09_data-ex_11_ScreeLoad_03b.py 22-06-2026
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from io import StringIO

# --- 1. Die Grundgesamtheit ---
# df_old = pd.read_csv("Auto.csv") oder
df_old = pd.read_csv("Audo.csv")

df_old['modell'] = df_old['name']
df_old['name'] = '____'

feats = ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration']

df = df_old.copy()

df['name'] = df['name'].str.split(' ').str[0]

# --- 2. GUI & Layout ---
# %matplotlib notebook
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
plt.subplots_adjust(bottom=0.22, wspace=0.25)

is_drawing = False

def update():
    global is_drawing
    if is_drawing or len(df) < 3: return
    is_drawing = True
    fig.texts.clear()
    ax1.clear(); ax2.clear()
    ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    ax2.axvline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    
    # PCA-Berechnung auf dem verbliebenen Rumpf-Datensatz
    X = StandardScaler().fit_transform(df[feats])
    vals, vecs = np.linalg.eig(np.cov(X, rowvar=False))
    idx = np.argsort(vals)[::-1]
    vals, vecs = vals[idx], vecs[:, idx]
    
    # Links: Scree-Diagramm
    ax1.bar(range(1, 7), vals/sum(vals), alpha=0.6, color='royalblue')
    ax1.step(range(1, 7), np.cumsum(vals/sum(vals)), where='mid', color='red')
    ax1.set_title(f"Scree-Diagramm (n={len(df)})"); ax1.set_ylim(0, 1.05)
    
    # Rechts: Projektion
    color_indices = df['name'].astype('category').cat.codes
    p1, p2 = X @ vecs[:, 0], X @ vecs[:, 1]
    coords = np.column_stack((p1, p2))

    # 2. Bestehender Scatter-Plot-Aufruf (aktualisiert die Punkte)
    scatter = ax2.scatter(p1, p2, alpha=0.6, c=df.index, cmap='viridis')
    for i in range(len(p1)):
        ax2.text(p1[i] + 0.10, p2[i] - 0.05, str(df.index.values[i]).rjust(3), fontsize=8)

    # ax2.scatter(p1, p2, c=df['cylinders'], cmap='coolwarm', edgecolors='k', s=40, zorder=2)
    # scatter = ax2.scatter(p1, p2, alpha=0.6, c=df.index, cmap='viridis')

    ax2.set_title("P1 PC2 Scatter")
    
    # WICHTIG: Achsen festfrieren, damit man das Wandern der Punkte und des Zentroids im Raum sieht!
    ax2.set_xlim(-4, 5)
    ax2.set_ylim(-3, 3)
    
    for i, txt in enumerate(df['name']):
        ax2.annotate(txt.split()[:2], (p1[i], p2[i]), fontsize=7, alpha=0.5)
        
    # Medoid-Suchschleife nach deinem Ansatz
    min_mean_dist = float('inf')
    best_idx = 0
    for i in range(len(coords)):
        dists = np.sqrt(np.sum((coords - coords[i])**2, axis=1))
        if np.mean(dists) < min_mean_dist:
            min_mean_dist = np.mean(dists)
            best_idx = i
            
    # Aqua-Blob einzeichnen
    ax2.scatter(coords[best_idx, 0], coords[best_idx, 1],color='aqua', edgecolor='black',
                linewidth=1.5, s=200,label=f"Zentroid: {' '.join(df.iloc[best_idx]['name'].split()[:2])}", zorder=3)
    ax2.legend(loc='lower left', fontsize=8)
    
    is_drawing = False
    fig.canvas.draw_idle()

# --- 3. Interaktive Steuerung ---
tx_box = plt.axes([0.25, 0.04, 0.35, 0.06])
re_box = plt.axes([0.62, 0.04, 0.10, 0.06])

box = TextBox(tx_box, 'Dauerhaft sperren: ', initial='')
btn = Button(re_box, 'Reset', color='firebrick', hovercolor='red')
btn.label.set_color('white')

def on_submit(text):
    while ax2.texts: ax2.texts[0].remove()
    global df,p1,p2
    if text.strip():
        df = df[~df['name'].str.contains(text, case=False, na=False)].copy()
        box.set_val('')
        update()

def on_reset(event):
    global df
    df = df_old.copy()
    box.set_val('')
    update()

box.on_submit(on_submit)
btn.on_clicked(on_reset)

update()
plt.show()
