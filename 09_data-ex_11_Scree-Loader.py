# 09_data-ex_11_Scree-Loader.py 22-06-2026
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
# pip install scikit-learn !
# --- 1. Deine reale, unvollkommene Grundgesamtheit (Auto.csv-Auszug) ---
data = """mpg,cylinders,displacement,horsepower,weight,acceleration,year,origin,name
18,8,307,130,3504,12,70,1,chevrolet chevelle malibu
15,8,350,165,3693,11.5,70,1,buick skylark 320
18,8,318,150,3436,11,70,1,plymouth satellite
16,8,304,150,3433,12,70,1,amc rebel sst
17,8,302,140,3449,10.5,70,1,ford torino
15,8,429,198,4341,10,70,1,ford galaxie 500
14,8,454,220,4354,9,70,1,chevrolet impala
14,8,440,215,4312,8.5,70,1,plymouth fury iii
14,8,455,225,4425,10,70,1,pontiac catalina
15,8,390,190,3850,8.5,70,1,amc ambassador dpl
15,8,383,170,3563,10,70,1,dodge challenger se
14,8,340,160,3609,8,70,1,plymouth 'cuda 340
15,8,400,150,3761,9.5,70,1,chevrolet monte carlo
14,8,455,225,3086,10,70,1,buick estate wagon (sw)
24,4,113,95,2372,15,70,3,toyota corona mark ii
22,6,198,95,2833,15.5,70,1,plymouth duster
18,6,199,97,2774,15.5,70,1,amc hornet
21,6,200,85,2587,16,70,1,ford maverick
27,4,97,88,2130,14.5,70,3,datsun pl510
26,4,97,46,1835,20.5,70,2,volkswagen 1131 deluxe sedan
25,4,110,87,2672,17.5,70,2,peugeot 504
24,4,107,90,2430,14.5,70,2,audi 100 ls
25,4,104,95,2375,17.5,70,2,saab 99e
26,4,121,113,2234,12.5,70,2,bmw 2002
21,6,199,90,2648,15,70,1,amc gremlin
10,8,360,215,4615,14,70,1,ford f250
10,8,307,200,4376,15,70,1,chevy c20
11,8,318,210,4382,13.5,70,1,dodge d200
9,8,304,193,4732,18.5,70,1,hi 1200d
27,4,97,88,2130,14.5,71,3,datsun pl510
28,4,140,90,2264,15.5,71,1,chevrolet vega 2300
25,4,113,95,2228,14,71,3,toyota corona
25,4,98,90,2046,19,71,1,ford pinto
19,6,232,100,2634,13,71,1,amc gremlin
16,6,225,105,3439,15.5,71,1,plymouth satellite custom
17,6,250,100,3329,15.5,71,1,chevrolet chevelle malibu
19,6,250,88,3302,15.5,71,1,ford torino 500
18,6,232,100,3288,15.5,71,1,amc matador
14,8,350,165,4209,12,71,1,chevrolet impala
14,8,400,175,4464,11.5,71,1,pontiac catalina brougham
14,8,351,153,4154,13.5,71,1,ford galaxie 500
14,8,318,150,4096,13,71,1,plymouth fury iii
12,8,383,180,4955,11.5,71,1,dodge monaco (sw)
13,8,400,170,4746,12,71,1,ford country squire (sw)
13,8,400,175,5140,12,71,1,pontiac safari (sw)
18,6,258,110,2962,13.5,71,1,amc hornet sportabout (sw)
22,4,140,72,2408,19,71,1,chevrolet vega (sw)
19,6,250,100,3282,15,71,1,pontiac firebird
18,6,250,88,3139,14.5,71,1,ford mustang
23,4,122,86,2220,14,71,1,mercury capri 2000
28,4,116,90,2123,14,71,2,opel 1900
30,4,79,70,2074,19.5,71,2,peugeot 304
30,4,88,76,2065,14.5,71,2,fiat 124b
31,4,71,65,1773,19,71,3,toyota corolla 1200
35,4,72,69,1613,18,71,3,datsun 1200
27,4,97,60,1834,19,71,2,volkswagen model 111
26,4,91,70,1955,20.5,71,1,plymouth cricket"""

# Daten laden (das '?' beim Pinto haben wir im String oben bereits durch 90 PS ersetzt)
from io import StringIO
df = pd.read_csv("Auto-tabloid.csv") # StringIO(data))
features = ['mpg', 'cylinders', 'displacement', 'horsepower', 'weight', 'acceleration']

# --- 2. Das interaktive Grafik-Layout aufbauen ---
# %matplotlib notebook
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
plt.tight_layout()
plt.subplots_adjust(bottom=0.25) # Platz für das Textfeld schaffen

# Globale Kontroll-Variablen für das Event-Management
is_drawing = False
excluded_name = ""

def berechne_und_plotte():
    """ Berechnet das gesamte Universum basierend auf dem aktuellen Filter neu """
    global is_drawing
    if is_drawing:
        return # Event-Blockade: Wenn bereits gezeichnet wird, ignorieren
        
    is_drawing = True
    
    # Achsen säubern für die Neugeburt
    ax1.clear()
    ax2.clear()
    
    # Datensatz filtern
    if excluded_name.strip():
        # Filtert Autos, deren Name den eingegebenen Text enthält (case-insensitive)
        df_filtered = df[~df['name'].str.contains(excluded_name, case=True, na=False)].copy()
    else:
        df_filtered = df.copy()
        
    if len(df_filtered) < 3:
        ax1.text(0.5, 0.5, "Zu wenige Daten!", ha='center')
        ax2.text(0.5, 0.5, "Zu wenige Daten!", ha='center')
        is_drawing = False
        fig.canvas.draw_idle()
        return

    # 1. Normalisierung (Die Zähmung der Skalen)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_filtered[features])
    
    # 2. Kovarianzmatrix (Das Dimensions-Mikado) & Herr Bessel (rowvar=False)
    cov_matrix = np.cov(X_scaled, rowvar=False)
    
    # 3. Der Lagrange/Gauß-Sturzflug in die Eigenwerte (Lambdas)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    # Sortieren nach der Größe der Lambdas (Dominanz)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Varianzanteile für den Scree-Plot berechnen
    total_var = np.sum(eigenvalues)
    var_explained = eigenvalues / total_var
    cum_var_explained = np.cumsum(var_explained)
    
    # --- PLOT 1: Scree Plot (ax1) ---
    ax1.bar(range(1, 7), var_explained, alpha=0.7, align='center', label='Indiv. Lambda', color='skyblue')
    ax1.step(range(1, 7), cum_var_explained, where='mid', label='Kumuliert', color='red', lw=2)
    ax1.set_ylabel('Erklärter Varianzanteil')
    ax1.set_xlabel('Hauptkomponente (PC Index)')
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc='lower right')
    ax1.set_title(f'Scree Plot (n={len(df_filtered)} Autos)')
    ax1.grid(True, alpha=0.3)
    
    # --- PLOT 2: Das flachgedrückte 2D-Pseudovolumen (ax2) ---
    PC1 = X_scaled @ eigenvectors[:, 0]
    PC2 = X_scaled @ eigenvectors[:, 1]
    
    scatter = ax2.scatter(PC1, PC2, alpha=0.8, c=df_filtered['cylinders'], cmap='coolwarm', edgecolors='black', s=50)
    ax2.set_xlabel('PC1: Wucht (Gewicht/PS/Hubraum vs MPG)')
    ax2.set_ylabel('PC2: Unabhängige Rest-Dynamik')
    ax2.set_title('Das entwirrte Vektor-Feld')
    ax2.grid(True, alpha=0.3)
    
    # Einzelne Autonamen als feine Beschriftung an die Punkte hängen
    for i, txt in enumerate(df_filtered['name']):
        # Nur einen kurzen Teil des Namens drucken, damit es übersichtlich bleibt
        kurzname = txt.split()[0]
        ax2.annotate(kurzname, (PC1[i], PC2[i]), fontsize=7, alpha=0.7, xytext=(3,3), textcoords='offset points')

    # Status-Text einblenden, wer gerade eliminiert wurde
    if excluded_name.strip():
        fig.suptitle(f"Universum ohne: '{excluded_name}'", color='darkred', fontsize=12, fontweight='bold')
    else:
        fig.suptitle("Vollständiges Auto-Universum (Alle 57 Datenpunkte)", color='darkgreen', fontsize=12)

    # Beide Grafiken sanft im nächsten Idle-Zyklus neu rendern lassen
    is_drawing = False
    fig.canvas.draw_idle()

# --- 4. Das interaktive Textfeld einklinken ---
ax_box = plt.axes([0.3, 0.05, 0.4, 0.075]) # Position unten in der Mitte
text_box = TextBox(ax_box, 'Auto sperren:\n(z.B. ford, volkswagen) ', initial='')

def on_submit(text):
    global excluded_name
    excluded_name = text
    berechne_und_plotte()

text_box.on_submit(on_submit)

# Der initiale Urknall-Aufruf beim Start des Skripts
berechne_und_plotte()
plt.show()
