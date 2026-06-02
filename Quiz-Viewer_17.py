# Quiz-Viewer_17.py 29-05-26 Idee R.Wurdack 228_Zeilen-Script Google-Gemini
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import random
import textwrap
#-------------------Start-Bedingungen----------------------------
load_index = 0     # 0: Learn-Modus mit Loesung  1: Quiz-Modus
startzeile = 1     # Verschiebbarer Zeiger auf die erste Frage
#-------------------Quiz-Ablauf---------------------------------
def load_data(fragen_file, antworten_file, info_file, start_zeile):
    questions = []
    erg = 'kein Fehler'
    bad= []
    try:
        with open(fragen_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            lines = lines[(start_zeile-1)*12:]            
        for i in range(0, len(lines), 12):                      
            questions.append(lines[i:i+12])                     
        with open(antworten_file, 'r', encoding='utf-8') as f:
            answers = [line.strip() for line in f if line.strip()]
            answers = answers[(start_zeile-1):]
        with open(info_file, 'r', encoding='utf-8') as f:
            infos = [line.strip() for line in f if line.strip()]
            infos = infos[(start_zeile-1):]
            
    except: return []
    # return main dictionary !
    return [{"q_lines": q, "ans": a, "inf":inftxt , "id": i+1 } for i, (q, a, inftxt) in enumerate(zip(questions, answers,infos))]

class QuizViewer:
    def __init__(self, quiz_data, load_index, startzeile):
        self.quiz_data = quiz_data
        self.load_index = load_index
        self.startzeile = startzeile
        self.num_to_pick = min(len(quiz_data), 160)      # 152
        self.level = 0 # 0=gelöst ,1=Linear, 2=Zufall, 3=Streng, 4=Kein Zurück!
        self.index = 0
        self.guess = "?"
        self.show_answer = False
        self.score = 0
        self.blame = 0
        self.answered_ids = set()
        self.answered_bad = set()
        self.erg = 'kein Fehler'
        self.bad = []
        self.current_pool = []
        self.fig, self.ax = plt.subplots(figsize=(11, 5.5))
        plt.subplots_adjust(left=0.01, bottom=0.05)                                                            #00
        self.ax.axis('off')
        self.txt_q = self.ax.text(0.01, 0.99, "", va='top', fontsize=11, family='monospace')
        self.txt_feedback = self.ax.text(0.17, 0.233, "",va='top',fontsize=12,fontweight='bold')               #01
        # self.txt_feedback.set_text(f"Antwort steht an ...      \n             \n               ")       
        self.txt_score1 = self.ax.text(0.50, 0.99, "", va='top',fontsize=13,color='darkblue',fontweight='bold') #02
        self.txt_score2 = self.ax.text(0.01, 0.14, "", va='top',fontsize=13,color='magenta' )                #03
        self.txt_score3 = self.ax.text(0.01, 0.10, "", va='top',fontsize=13,color='darkblue' )               #04
        self.txt_score3.set_text(f"info-zeile")
        # Antwort-Buttons
        self.btn_choices = []
        for i, label in enumerate(['a', 'b', 'c', 'd']):
            ax_c = plt.axes([0.785, 0.36 - (i * 0.06), 0.04, 0.05])                                            #05#
            btn = Button(ax_c, label)
            btn.on_clicked(lambda e, l=label: self.make_guess(l))
            self.btn_choices.append(btn)
        # Navigation mit Buttons
        self.btn_prev = Button(plt.axes([0.70, 0.227, 0.07, 0.132]), '<<')                                      #06#
        self.btn_num = Button(plt.axes([0.55, 0.297, 0.14, 0.06]), f'Fragenzahl : {self.num_to_pick}')          #07#
        self.lvl_txt = ["0 (gelöst)","1 (linear)", "2 (Zufall)", "3 (streng)", "4 (kein zurück)"]
        self.btn_lvl = Button(plt.axes([0.55, 0.227, 0.14, 0.06]), f'Mode {self.lvl_txt[self.level]}')          #08#
        self.btn_next = Button(plt.axes([0.84, 0.227, 0.07, 0.132]), '>>')                                      #09#
        ax_box = self.fig.add_axes([0.01, 0.18, 0.10, 0.06])                                                    #10
        self.text_box = TextBox(ax_box, '', initial=str(startzeile))
        self.text_box.label.set_text('Startzeile:')
        self.text_box.label.set_position((1.3, 1.3))
        ax_btn = self.fig.add_axes([0.12, 0.18, 0.03, 0.06])                                                    #11
        self.btn_submit = Button(ax_btn, 'OK')
        self.text_box.on_submit(self.zeilen_eingabe) # submit-trigger
        self.btn_submit.on_clicked(self.eingabe_absenden)
        self.btn_prev.on_clicked(lambda x: self.move(-1))
        self.btn_next.on_clicked(lambda x: self.move(1))
        self.btn_num.on_clicked(self.toggle_num)
        self.btn_lvl.on_clicked(self.toggle_level)
        self.reset_quiz()
        plt.show()

    def zeilen_eingabe(self, text):
        try:
            wert = int(text)
            # Prüfen, ob die Zahl im erlaubten Bereich liegt
            if 1 <= wert <= 155:
                self.startzeile = wert
                self.reload_data(self)
                print(self.startzeile)
            else:
                raise ValueError("Zahl außerhalb des Bereichs.")
        except ValueError:
            self.startzeile = 1
        plt.draw()
    def eingabe_absenden(self, event):
           """Absenden, falls User nicht Enter drückt."""
           self.zeilen_eingabe(self.text_box.text)     

    def reload_data(self, *args):
        # 1. Daten neu aus der Datei laden
        if self.load_index == 0:
           self.quiz_data = load_data('geloest.txt', 'antworten.txt','info.txt', self.startzeile)
        elif self.load_index == 1:
           self.quiz_data = load_data('fragen.txt', 'antworten.txt','info.txt', self.startzeile)
        # 2. Pool für Anzeige neu überschreiben
        self.current_pool = self.quiz_data 
        # 3. Index auf die erste Frage (0)
        self.index = 0   
        # 4. Anzeige neu
        if len(self.current_pool) > 0:
           self.update_display()
        else:
           print("Konsole: neuer Fragen-Pool leer!")        

    def toggle_num(self, event):
        self.num_to_pick = (self.num_to_pick % len(self.quiz_data)) + 1
        self.btn_num.label.set_text(f'Anzahl: {self.num_to_pick}')
        self.reset_quiz()

    def toggle_level(self, event):
        # Zahlenring 0,1 -> 2 -> 3 -> 4 -> 0
        self.level = (self.level + 1) % 5
        self.btn_lvl.label.set_text(f'Mode {self.lvl_txt[self.level]}')
        self.reset_quiz()

    def reset_quiz(self):
        self.score = 0
        self.blame = 0
        self.answered_ids = set()
        self.answered_bad = set()
        self.erg = 'kein Fehler'
        self.bad = []
        self.index = 0
        self.txt_feedback.set_text(f"Antwort steht an ...      \n             \n               ")
        self.txt_q.set_fontsize(15)
        if self.level == 0:
            self.load_index = 0
            self.startzeile = 1
            self.reload_data(self)
            self.current_pool = self.quiz_data[:self.num_to_pick]
            # self.txt_q.set_fontsize(15)
            self.ax.figure.canvas.draw_idle()            
        if self.level == 1:
            self.load_index = 1
            self.startzeile = 1
            self.reload_data(self)
            self.current_pool = self.quiz_data[:self.num_to_pick]
            # self.txt_q.set_fontsize(11)
            self.ax.figure.canvas.draw_idle()            
        elif self.level == 2:
            self.load_index = 0
            self.startzeile = 1
            self.reload_data(self)
            self.current_pool = random.sample(self.quiz_data, self.num_to_pick)
        elif self.level >= 3:
            self.load_index = 1
            self.startzeile = 1
            self.reload_data(self)
            # Stufe 3 und 4 nutzen beide den strengen Zufall (shuffled)
            temp_pool = list(self.quiz_data)
            random.shuffle(temp_pool)
            self.current_pool = temp_pool[:self.num_to_pick]
        self.update_display()

    def make_guess(self, label):
        if not self.show_answer:
            item = self.current_pool[self.index]
            correct = item['ans'].split('.')[-1].strip().lower()
            if label.lower() == correct and item['id'] not in self.answered_ids:
                self.score += 1
                self.answered_ids.add(item['id'])
            if label.lower() != correct and item['id'] not in self.answered_bad:
                self.blame += 1
                self.answered_bad.add(item['id'])
            self.guess, self.show_answer = label, True
            self.update_display()

    def update_display(self):
        item = self.current_pool[self.index]
        lvl_names = ["0 (gelöst)","1 (linear)", "2 (Zufall)", "3 (streng)", "4 (kein zurück)"]
        mode_text = lvl_names[self.level]
        self.txt_q.set_text(f"Mode {mode_text}|Frage {self.index+1}/{len(self.current_pool)}\n\n"+"\n".join(item['q_lines']))
        self.txt_score1.set_text(f"richtig: {self.score} von {len(self.current_pool)}")
        self.bad = sorted(list(self.answered_bad))
        self.erg = "/".join(f"{z:03d}" for z in self.bad)
        self.txt_score2.set_text(f"{self.blame} falsch:{self.erg}")
        # Ausgabe der aktuellen info-zeile aus dem quiz_data-dictionary key "inf" entspr. aktueller Fensterbreite
        window_width_pixels = self.fig.get_window_extent().width
        zeichen_breite = max(20, int(window_width_pixels / 10))  # Schätzung ca 10 Pixel pro Zeichen
        if self.level == 0:
           info_txt = self.quiz_data[self.index]["inf"]
           self.txt_score3.set_text(textwrap.fill(info_txt, width=zeichen_breite))
        else:
           self.txt_score3.set_text(f"self.index : {self.index}") 
        # Zurück-Button ausgrauen/sperren in Stufe 4
        if self.level == 4:
            self.btn_prev.ax.set_facecolor('gray')
            self.btn_prev.label.set_color('white')
        else:
            self.btn_prev.ax.set_facecolor('0.85')
            self.btn_prev.label.set_color('black')
        if self.show_answer:
            correct = item['ans'].split('.')[-1].strip().lower()
            is_correct = self.guess.lower() == correct
            self.txt_feedback.set_text(f"Vermutung: {self.guess}\nLösung: {item['ans']}")
            self.txt_feedback.set_color("green" if is_correct else "red")
        self.fig.canvas.draw_idle()

    def move(self, step):
        # In Stufe 4 blockieren wir den Rückwärtsschritt
        self.txt_feedback.set_text(f"Antwort steht an ...      \n             \n               ")
        if self.level == 4 and step < 0:
            return 
        if len(self.current_pool) > 0:
            self.index = (self.index + step) % len(self.current_pool)
            self.guess, self.show_answer = "?", False
            self.update_display()
#-------------------Daten-Auswahl--------------------------------
quiz_data0 = load_data('geloest.txt', 'antworten.txt','info.txt',startzeile)
quiz_data1 = load_data('fragen.txt', 'antworten.txt','info.txt',startzeile)
if load_index == 0:
   QuizViewer(quiz_data0,load_index,startzeile)
if load_index == 1:
   QuizViewer(quiz_data1,load_index,startzeile)
#-------------------Ende_des_Scripts-----------------------------
            
