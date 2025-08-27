#!/usr/bin/env python3
"""
Chroniken - Vollständige GUI (Tkinter)

- Jeder Text wird einzeln angezeigt (vorheriger wird ausgeblendet).
- Szenen laufen automatisch ab (kein Enter nötig).
- Hauptmenü hat zusätzlich einen Button zum Speichern (fortschritt sichern).
- Fenster ist dynamisch (passt sich automatisch der Größe an).
- ANSI-Farbcodes (z. B. blau/rot) werden in GUI-Farben umgesetzt.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# ---------------------------------------------------------------------------
# Szenenliste
# ---------------------------------------------------------------------------
SCENES = [
       "Tote Bäume ragen wie Finger in den Himmel, der Wind trägt Asche und Staub. Ein kleiner Trupp Überlebender, abgerissen, müde, vom Staub grau, schleppt sich zu einer halb eingestürzten Ruine.",
    "Dort entzünden sie ein kleines Feuer. Fleischstücke, kaum genießbar, drehen sich auf Spießen über der Glut.",
    "Alle setzen sich in einem Kreis. Stille. Nur das Knacken der Glut und das Pfeifen des Windes.",
    "Ein alter Mann tritt hervor. Er trägt einen Mantel aus Fetzen, das Gesicht zerfurcht, die Augen tief, als hätten sie zu viel gesehen.",
    "Er setzt sich ans Feuer. Seine Stimme ist kratzig, aber intensiv. Er räuspert sich und fängt fast krächzend an zu erzählen: ",
    "\033[34mLasst mich euch eine Geschichte erzählen. Eine Geschichte unserer Vorväter.\033[0m",
    "\033[34mEine Geschichte wie Azgaroth entstanden ist.\033[0m",
    "Der alte Erzähler räuspert sich, nimmt einen Schluck aus einem Metallbecher und fährt fort.",
    "\033[34mWir schreiben das Jahr 2025. Die Welt, wie wir sie kannten, ist nur noch eine ferne Erinnerung.\033[0m",
    "\033[34mMehrere Katastrophen, die das Gefüge unserer Realität zerrissen, führten zu einer gewaltigen Wende, die die Erde für immer veränderte.\033[0m",
    "\033[34mZuerst wurden Grabungen in den Tiefen der Meere veranlasst, die das Rühren eines Wesens auslösten welches lieber nicht hätte geweckt werden sollen, das seit Äonen in den Tiefen des Ozeans schlief.\033[0m",
    "\033[34mWährenddessen bewegten sich die Sterne am Himmel in entgegengesetzte Richtungen und bildeten eine Konstellation, die nach den Gesetzen der Astronomie unmöglich war.\033[0m",
    "\033[34mDann folgte alles Schlag auf Schlag: Eine einst versunkene Stadt, weit größer als jede irdische Metropole,\033[0m",
    "\033[34mstieg mit einem riesigen Turm aus unbekanntem Material aus den Fluten empor, eine monolithische Struktur, höher als es möglich sein sollte.\033[0m",
    "\033[34mVon den Sternen jenseits unseres Verstandes griffen sie an. Sie brachten Verderben, Tod und Wahnsinn mit sich.\033[0m",
    "\033[34mKosmische Wesen mit Fledermausflügeln und widerlich verdrehten Hörnern, Wesen mit Drachenschwingen und Oktopus-Merkmalen,\033[0m",
    "\033[34mGestalten, die entfernt an verstümmelte und entstellte Rösser erinnerten, und mehr groteske Lebensformen, als unser Verstand verarbeiten konnte, brachen über uns herein.\033[0m",
    "\033[34mWährend das Militär mit diesem kosmischen Alptraum beschäftigt war, bemerkte niemand die wahre Gefahr, die bereits auf Erden war und aus den Meeren emporstieg.\033[0m",
    "\033[34mDer ewige Träumende, der Herold des Untergangs, der Hohepriester erwachte aus seinem Äonenschlaf.\033[0m",
    "\033[34mEr zeigte den Großen Alten von Außen den Weg aus ihrem Gefängnis zwischen den Dimensionen in unsere Welt.\033[0m",
    "\033[34mDiese Wesen, die ohne Verständnis für menschliche Moralvorstellungen, übermächtige Götter und jenseits des Seins sind, durchbrachen eine Barriere,\033[0m",
    "\033[34mdie vor der Entstehung der Erde von den sogenannten Alten Göttern, den Schutzpatronen und Hütern des Gleichgewichts, errichtet wurde.\033[0m",
    "\033[34mDiese Barriere existierte einzig und allein, um die Dimensionen und somit die Magie wegzuschließen.\033[0m",
    "\033[34mAls sie diese Membran durchstießen, schwappten Magie, Landmassen und Bewohner anderer Dimensionen in unsere Welt.\033[0m",
    "\033[34mDie Erde veränderte sich drastisch. Die einst getrennten Welten verschmolzen zu einer einzigen, \033[0m",
    "\033[34mund die Erde erhielt ihren neuen, schrecklichen Namen: Azgaroth, die Untergangene.\033[0m",
    "\033[34mIn der nun fusionierten Welt kämpften und bekriegten sich die Bewohner gegeneinander.\033[0m",
    "Ein Kind schreit auf und versteckt sich hinter einem Erwachsenen, scheinbar der Vater des Kindes. Gespannt hört die Gruppe weiter zu.",
    "\033[34mDas namenlose Grauen, wie die Alten nun genannt wurden, verschwand, um ihre Kräfte zu sammeln, da der\033[0m",
    "\033[34mÜbertritt nicht leicht für sie war.\033[0m",
    "\033[34mIn den Namenlosen Landen, den Ruinen des einst mächtigen R'lyeh, warteten sie auf einen Moment der\033[0m",
    "\033[34mUnachtsamkeit, um alle Völker ein für alle Mal zu unterdrücken.\033[0m",
    "\033[34mMit der Zeit schlossen sich immer mehr Alptraumwesen den Namenlosen an. Wesen, die durch die Luft gleiten,\033[0m",
    "\033[34mdiese kontrollieren und sich mit Unsichtbarkeit tarnen konnten, wobei sie Klick- und Pfeifgeräusche von sich gaben.\033[0m",
    "\033[34mRiesenhafte Kreaturen mit gewaltigen Hörnern, mehreren Gliedmaßen und dickem Fell, die eine Affinität zu Schneestürmen besaßen.\033[0m",
    "\033[34mWesen, gehüllt in Flammen, mit gewaltigen Tentakeln, die wie Quallen durch die Luft schwebten.\033[0m",
    "\033[34mUnd Wesen, die Jagd auf Geistwandler machten, wenn man ihnen begegnete, war Flucht zwecklos, da sie den Raum krümmen konnten.\033[0m",
    "\033[34mEntstellt und blutbesessen erinnerten sie entfernt an Hunde oder Wölfe.\033[0m",
    "\033[34mWährend die Fronten der Namenlosen immer stärker wurden, dezimierten sich die anderen Völker zunehmend aufgrund von belanglosen Dingen\033[0m",
    "\033[34mwie Territorium, Macht, Ansehen und Ressourcen anstatt gemeinsam gegen die Bedrohung vorzugehen.\033[0m",
    "\033[34mAuch Drachen, Elfen, Menschen und andere schlossen sich den Reihen der Finsternis an.\033[0m",
    "\033[34mDas namenlose Grauen sah nun die Chance, alle Völker zu unterjochen. Fast vollständig vernichtet, bildeten die neuen Bewohner eine Allianz, doch trotz\033[0m",
    "\033[34mvereinter Kraft schien das Bündnis dem Untergang geweiht.\033[0m",
    "\033[34mDoch aus dem Schlachtgetümmel schälte sich eine Gruppe von sieben Helden heraus, gesegnet mit der Macht der Alten Götter.\033[0m",
    "\033[34mIhre Kraft übertraf alles Dagewesene, und sie begannen, den Wahnsinn langsam zurückzudrängen. In der letzten Schlacht, \033[0m",
    "\033[34mdem sogenannten Falskur (Entscheidungskampf), sammelte die Gruppe ihre ganze Kraft und verbannte das Grauen und die Namenlosen auf die Namenlosen Lande.\033[0m",
    "\033[34mDoch der Sieg hatte einen hohen Preis: Die Helden ließen ihr Leben, um unseres zu retten.\033[0m",
    "\033[34mVor ihrem Ableben gaben sie ihr Können jedoch an würdige Nachfolger weiter, und so wurde die Gruppierung der Wächter gegründet.\033[0m",
    "\033[34mDie Schutzpatrone der Erde, auch wenn sie physisch nicht mehr existierten, erwählten sie die neuen Wächter mit Hilfe der sogenannten Regenbogendrachen,\033[0m",
    "\033[34mdie Boten der Alten Götter. Man gab den Wächtern den Namen Wächter des Gleichgewichts.\033[0m",
    "\033[34mAlle lebten in relativer Harmonie, bis die Wächter vor vier Jahren spurlos verschwanden. Allerdings stehen alle Zeichen dafür das sich das Namenlose bald wieder rührt.\033[0m",
    "\033[34mUnd damit erheben sich auch die Wächter wieder. Ich fühle das dies die entscheidende Schlacht aller Völker und der Welt ist.\033[0m",
    "\033[34mEs bleibt abzuwarten was passieren wird.  Nun lebt wohl!\033[0m",
    "Der alte Mann steht auf, nachdem seine Erzählung vollendet ist. Ein verbittertes Grinsen zeichnet sich auf sein bereits faltige Gesicht ab.",
    "\033[34mIch danke euch für die Suppe.\033[0m",
    "sagt er, dreht sich um und verschwindet in die Dunkelheit.",
    "Einige Leute rufen ihm entsetzt hinterher und stürmen ebenfalls in die Dunkelheit, nur um verwirrt mit leeren Händen wiederzukommen und",
    "\033[31mEr ist weg!\033[0m",
    "zu rufen. Ein Raunen geht durch die Gemeinde der Überlebenden.",
]

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def save_progress(scene_index, player_class):
    save_data = {
        "scene_index": scene_index,
        "player_class": player_class
    }
    file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Savegame", "*.json")])
    if file:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4)
        messagebox.showinfo("Gespeichert", "Fortschritt wurde gespeichert!")


def insert_colored(text_widget, raw_text):
    """Parst ANSI-Farbcodes und färbt Text entsprechend ein."""
    parts = raw_text.split("\033")
    tag = None
    for part in parts:
        if part.startswith("[34m"):
            tag = "blue"
            text_widget.insert("end", part[4:], tag)
        elif part.startswith("[31m"):
            tag = "red"
            text_widget.insert("end", part[4:], tag)
        elif part.startswith("[0m"):
            tag = None
            text_widget.insert("end", part[3:], tag)
        else:
            text_widget.insert("end", part, tag)

# ---------------------------------------------------------------------------
# GUI-Klassen
# ---------------------------------------------------------------------------

class ChronikenGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.minsize(600, 400)

        # Toolbar (initially hidden)
        self.toolbar = ttk.Frame(self)
        self.toolbar.grid(row=1, column=0, sticky="ew")
        self.btn_save = ttk.Button(self.toolbar, text="Speichern", command=lambda: save_progress(self.scene_index, self.player_class))
        self.btn_save.pack(side="left", padx=5, pady=2)
        self.btn_load = ttk.Button(self.toolbar, text="Laden", command=self.load_progress)
        self.btn_load.pack(side="left", padx=5, pady=2)
        self.toolbar.grid_remove()
        self.title("Chroniken - Die Erzählung von Azgaroth")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Spielzustand
        self.scene_index = 0
        self.player_class = None

        # Frames
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartFrame, SceneFrame, ClassSelectionFrame, GameFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('StartFrame')

    
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if name == "StartFrame":
            self.toolbar.grid_remove()
        else:
            self.toolbar.grid()



    def load_progress(self):
        file = filedialog.askopenfilename(filetypes=[("Savegame", "*.json")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.scene_index = data.get("scene_index", 0)
            self.player_class = data.get("player_class", None)
            self.show_frame("SceneFrame")
            self.frames["SceneFrame"].reset()

class StartFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = ttk.Label(self, text="Willkommen bei den Chroniken!", font=(None, 24))
        title.pack(pady=20)

        subtitle = ttk.Label(self, text="Bitte teile mir mit was du machen möchtest:", font=(None, 12))
        subtitle.pack(pady=6)

        btn_new = ttk.Button(self, text="Neues Spiel", command=self.start_game)
        btn_new.pack(pady=6)
        btn_load = ttk.Button(self, text="Spielstand laden", command=controller.load_progress)
        btn_load.pack(pady=6)

        
        btn_quit = ttk.Button(self, text="Beenden", command=controller.destroy)
        btn_quit.pack(pady=6)

    def start_game(self):
        self.controller.scene_index = 0
        self.controller.show_frame('SceneFrame')
        self.controller.frames['SceneFrame'].reset()


class SceneFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.text = tk.Text(self, wrap="word", font=(None, 16))
        self.text.pack(expand=True, fill="both", padx=20, pady=20)
        # Neue Buttons im Intro
        btn_skip_line = tk.Button(self, text="Überspringen", bg="blue", fg="white",
                                  command=self.skip_line)
        btn_skip_line.pack(pady=5)

        btn_skip_intro = tk.Button(self, text="Intro Überspringen", bg="blue", fg="white",
                                   command=self.skip_intro)
        btn_skip_intro.pack(pady=5)


        # Tags für Farben
        self.text.tag_configure("blue", foreground="blue")
        self.text.tag_configure("red", foreground="red")

    def reset(self):
        self.controller.scene_index = 0
        self.show_scene()

    def show_scene(self):
        if self.controller.scene_index >= len(SCENES):
            self.controller.show_frame('ClassSelectionFrame')
            return

        scene_text = SCENES[self.controller.scene_index]
        self.text.delete("1.0", "end")
        insert_colored(self.text, scene_text)

        self.controller.scene_index += 1
        self.after_id = self.after(5500, self.show_scene)  # alle 5,5 Sek nächste Szene



    def skip_line(self):
        self.after_cancel(self.after_id)
        self.show_scene()

    def skip_intro(self):
        self.controller.show_frame('ClassSelectionFrame')
class ClassSelectionFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        lbl = ttk.Label(self, text='Bitte wähle deine Klasse aus.', font=(None, 16))
        lbl.pack(pady=14)

        classes = ["Magier", "Hexe", "Krieger", "Heiler"]
        for cls in classes:
            b = ttk.Button(self, text=cls, command=lambda c=cls: self.select_class(c))
            b.pack(pady=4)

    def select_class(self, classname):
        self.controller.player_class = classname
        self.controller.show_frame('GameFrame')
        self.controller.frames['GameFrame'].set_player(classname)


class GameFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = ttk.Label(self, text='Das Spiel beginnt...', font=(None, 18))
        self.label.pack(pady=10)

        self.player_info = ttk.Label(self, text='Keine Klasse gewählt')
        self.player_info.pack(pady=6)

        ttk.Button(self, text='Zum Hauptmenü', command=lambda: controller.show_frame('StartFrame')).pack(pady=10)

    def set_player(self, classname):
        self.player_info.config(text=f'Gewählte Klasse: {classname}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    app = ChronikenGUI()
    app.mainloop()

if __name__ == '__main__':
    main()
