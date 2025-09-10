import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SaveEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Silk Song Save Editor")
        self.root.geometry("600x1000")

        # Variables
        self.save_data = {}
        self.filename = ""
        self.output_filename = ""
        self.enemy_kill_data = {}  # To track enemy kill counts

        # Frame for Achievements
        self.ach_frame = ttk.LabelFrame(root, text="Achievements", padding="10")
        self.ach_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.ach_vars = {}

        # Frame for Quests
        self.quest_frame = ttk.LabelFrame(root, text="Quests", padding="10")
        self.quest_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.quest_vars = {}

        # Frame for Journal Entries
        self.journal_frame = ttk.LabelFrame(root, text="Journal Entries", padding="10")
        self.journal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.journal_vars = {}

        # Stats Frame
        self.stats_frame = ttk.LabelFrame(root, text="Player Stats", padding="10")
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.stats_vars = {
            "health": tk.StringVar(value="99"),
            "maxHealth": tk.StringVar(value="99"),
            "geo": tk.StringVar(value="999999"),
            "silk": tk.StringVar(value="3"),
            "silkMax": tk.StringVar(value="9")
        }

        # Stats Entries
        ttk.Label(self.stats_frame, text="Health:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.stats_frame, textvariable=self.stats_vars["health"]).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.stats_frame, text="Max Health:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.stats_frame, textvariable=self.stats_vars["maxHealth"]).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.stats_frame, text="Geo:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(self.stats_frame, textvariable=self.stats_vars["geo"]).grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(self.stats_frame, text="Silk:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Entry(self.stats_frame, textvariable=self.stats_vars["silk"]).grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(self.stats_frame, text="Max Silk:").grid(row=4, column=0, padx=5, pady=5)
        ttk.Entry(self.stats_frame, textvariable=self.stats_vars["silkMax"]).grid(row=4, column=1, padx=5, pady=5)

        # Text Viewer
        self.text_frame = ttk.LabelFrame(root, text="Save Data Viewer", padding="10")
        self.text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_view = tk.Text(self.text_frame, height=10, width=70)
        self.text_view.pack(padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Load Save (.dat)", command=self.load_save).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Set All Journal Complete", command=self.set_all_journal_complete).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Save as New .txt", command=self.save_changes).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Exit", command=root.quit).grid(row=0, column=3, padx=5)

        # Load initial data
        self.load_achievements()
        self.load_quests()
        self.load_journal_entries()

    def load_achievements(self):
        achievements = [
            "FIRST_TOOL", "ALL_TOOLS", "FIRST_SILK_SKILL", "ALL_SILK_SKILLS", "FIRST_CREST", "ALL_CRESTS",
            "FIRST_MASK", "ALL_MASKS", "FIRST_SILK_SPOOL", "ALL_SILK_SPOOLS", "ALL_SILK_HEARTS", "ALL_MAPS",
            "BELLWAYS_FULL", "BELLWAY_MELODY", "TUBES_FULL", "JOURNAL_HALF", "JOURNAL_FULL", "FLEAS_HALF",
            "FLEAS_ALL", "DEFEATED_BELLBEAST", "DEFEATED_LACE_1", "DEFEATED_SONG_GOLEM", "DEFEATED_WIDOW",
            "DEFEATED_LAST_JUDGE_1", "DEFEATED_COGWORK_DANCERS", "DEFEATED_TROBBIO", "DEFEATED_LACE_2",
            "DEFEATED_PHANTOM_1", "DEFEATED_FIRST_SINNER", "DEFEATED_CORAL_KING", "DEFEATED_FLOWER_QUEEN",
            "DEFEATED_HUNTER_QUEEN", "DEFEATED_GREEN_PRINCE", "FIRST_WISH", "GOURMAND_WISH", "SHAKRA_FINAL_QUEST",
            "GARMOND_FINAL_QUEST", "PINSTRESS_WISH", "EVA_FINAL_QUEST", "BELLHOME", "CITADEL_SONG",
            "WHITE_FLOWER_GAINED", "ENDING_A", "ENDING_C", "ENDING_D", "ENDING_E", "HERALD_WISH", "COMPLETION",
            "SPEEDRUN_1", "SPEED_COMPLETION", "STEEL_SOUL", "STEEL_SOUL_FULL"
        ]
        row = 0
        for ach in achievements:
            var = tk.BooleanVar(value=False)
            self.ach_vars[ach] = var
            ttk.Checkbutton(self.ach_frame, text=ach.replace("_", " ").title(), variable=var).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            row += 1

    def load_quests(self):
        quests = [
            "shermaQuestActive", "shermaHealerActive", "mapperRosaryConvo", "mapperMentorConvo", "mapperQuillConvo",
            "mapperMappingConvo", "mapperCalledConvo", "mapperHauntedBellhartConvo", "mapperBellhartConvo",
            "mapperTubeConvo", "mapperBrokenBenchConvo", "mapperCursedConvo", "mapperMaggottedConvo",
            "mapperSellingTubePins", "mapperMasterAfterConvo", "druidTradeIntro", "dicePilgrimDefeated",
            "garmondMoorwingConvo", "garmondPurposeConvo", "garmondFinalQuestReady", "pilgrimRestMerchant_SingConvo",
            "nuuIntroAct3", "gillyIntroduced", "ShakraFinalQuestAppear"
        ]
        row = 0
        for quest in quests:
            var = tk.BooleanVar(value=False)
            self.quest_vars[quest] = var
            ttk.Checkbutton(self.quest_frame, text=quest.replace("_", " ").title(), variable=var).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            row += 1

    def load_journal_entries(self):
        journal_entries = [
            "hasJournal", "seenJournalMsg", "seenMateriumMsg", "seenJournalQuestUpdateMsg", "HasSeenMapUpdated",
            "HasSeenMapMarkerUpdated", "HasMossGrottoMap", "HasWildsMap", "HasBoneforestMap", "HasDocksMap",
            "HasGreymoorMap", "HasBellhartMap", "HasShellwoodMap", "HasCrawlMap", "HasHuntersNestMap",
            "HasJudgeStepsMap", "HasDustpensMap", "HasSlabMap", "HasPeakMap", "HasCitadelUnderstoreMap",
            "HasCoralMap", "HasSwampMap", "HasCloverMap", "HasAbyssMap", "HasHangMap", "HasSongGateMap",
            "HasHallsMap", "HasWardMap", "HasCogMap", "HasLibraryMap", "HasCradleMap", "HasArboriumMap",
            "HasAqueductMap", "HasWeavehomeMap", "act3MapUpdated"
        ]
        row = 0
        # Map journal entries to potential enemy names for kill tracking
        self.journal_to_enemy = {
            "HasMossGrottoMap": "MossBone Crawler",
            "HasWildsMap": "Bone Thumper",
            "HasBoneforestMap": "Bone Roller",
            "HasDocksMap": "Aspid Collector",
            "HasGreymoorMap": "Pilgrim 01",
            "HasBellhartMap": "Bone Flyer",
            "HasShellwoodMap": "Mossbone Mother",
            "HasCrawlMap": "Bone Goomba",
            "HasHuntersNestMap": "Bone Goomba Large",
            "HasJudgeStepsMap": "Pilgrim Moss Spitter",
            "HasDustpensMap": "Bone Circler",
            "HasSlabMap": "Pilgrim 03"
        }
        for entry in journal_entries:
            var = tk.BooleanVar(value=False)
            self.journal_vars[entry] = var
            # Bind checkbox to update kill count
            def toggle_kill(var_copy=var, entry_copy=entry):
                if var_copy.get() and entry_copy in self.journal_to_enemy and "playerData" in self.save_data and "EnemyJournalKillData" in self.save_data["playerData"]:
                    enemy_name = self.journal_to_enemy[entry_copy]
                    for record in self.save_data["playerData"]["EnemyJournalKillData"]["list"]:
                        if record["Name"] == enemy_name and record["Record"]["Kills"] == 0:
                            record["Record"]["Kills"] = 1
                            self.text_view.delete(1.0, tk.END)
                            self.text_view.insert(tk.END, json.dumps(self.save_data, indent=2))
            var.trace('w', lambda *args, v=var, e=entry: toggle_kill(v, e))
            ttk.Checkbutton(self.journal_frame, text=entry.replace("_", " ").title(), variable=var).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            row += 1

    def set_all_journal_complete(self):
        for entry in self.journal_vars:
            self.journal_vars[entry].set(True)
        if "playerData" in self.save_data and "EnemyJournalKillData" in self.save_data["playerData"]:
            for record in self.save_data["playerData"]["EnemyJournalKillData"]["list"]:
                record["Record"]["Kills"] = 1
        self.text_view.delete(1.0, tk.END)
        self.text_view.insert(tk.END, json.dumps(self.save_data, indent=2))
        messagebox.showinfo("Success", "All journal entries set to complete and enemy kills set to 1!")

    def load_save(self):
        try:
            self.filename = tk.filedialog.askopenfilename(filetypes=[("DAT files", "*.dat"), ("JSON files", "*.json")])
            if not self.filename:
                return
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.save_data = json.load(file)
            
            # Load achievements
            for ach in self.ach_vars:
                full_key = f"HollowKnight.Achievement.{ach}.IsAchieved"
                self.ach_vars[ach].set(self.save_data.get(full_key, "0") == "1")
            
            # Load quests
            player_data = self.save_data.get("playerData", {})
            for quest in self.quest_vars:
                self.quest_vars[quest].set(player_data.get(quest, False))
            
            # Load journal entries
            for entry in self.journal_vars:
                self.journal_vars[entry].set(player_data.get(entry, False))
            
            # Load stats
            self.stats_vars["health"].set(str(player_data.get("health", 99)))
            self.stats_vars["maxHealth"].set(str(player_data.get("maxHealth", 99)))
            self.stats_vars["geo"].set(str(player_data.get("geo", 999999)))
            self.stats_vars["silk"].set(str(player_data.get("silk", 3)))
            self.stats_vars["silkMax"].set(str(player_data.get("silkMax", 9)))

            # Initialize enemy kill data
            self.enemy_kill_data = {record["Name"]: record["Record"]["Kills"] for record in player_data.get("EnemyJournalKillData", {}).get("list", [])}

            # Update viewer
            self.text_view.delete(1.0, tk.END)
            self.text_view.insert(tk.END, json.dumps(self.save_data, indent=2))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load save: {str(e)}. Ensure it's a valid .dat or .json file.")

    def save_changes(self):
        try:
            if not self.filename:
                messagebox.showwarning("Warning", "Please load a save file first!")
                return

            # Update achievements
            for ach in self.ach_vars:
                full_key = f"HollowKnight.Achievement.{ach}.IsAchieved"
                self.save_data[full_key] = "1" if self.ach_vars[ach].get() else "0"

            # Update quests
            if "playerData" not in self.save_data:
                self.save_data["playerData"] = {}
            player_data = self.save_data["playerData"]
            for quest in self.quest_vars:
                player_data[quest] = self.quest_vars[quest].get()

            # Update journal entries
            for entry in self.journal_vars:
                player_data[entry] = self.journal_vars[entry].get()

            # Update stats
            player_data["health"] = int(self.stats_vars["health"].get())
            player_data["maxHealth"] = int(self.stats_vars["maxHealth"].get())
            player_data["geo"] = int(self.stats_vars["geo"].get())
            player_data["silk"] = int(self.stats_vars["silk"].get())
            player_data["silkMax"] = int(self.stats_vars["silkMax"].get())

            # Save as new .txt file
            base_name = os.path.splitext(self.filename)[0]
            self.output_filename = f"{base_name}_edited.txt"
            with open(self.output_filename, 'w', encoding='utf-8') as file:
                json.dump(self.save_data, file, indent=2)
            
            # Update viewer
            self.text_view.delete(1.0, tk.END)
            self.text_view.insert(tk.END, json.dumps(self.save_data, indent=2))
            messagebox.showinfo("Success", f"Save file saved as {self.output_filename}. Your original file is unchanged!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditorGUI(root)
    root.mainloop()