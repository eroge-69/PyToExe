# Create CSVs for Chapter 1 variables/switches and scene checklist

import pandas as pd
from caas_jupyter_tools import display_dataframe_to_user

# ---------- Variables & Switches CSV ----------
vars_switches = [
    {"ID":"V001","Name":"Judgement_Stance","Kind":"Variable","Type":"Enum {0=None,1=Cruel,2=Atoning,3=Exploit}","Init":"0","Set In":"SCN-1.80","Used By":"CH1 Epilogue, CH2 onboarding","Effect":"Determines vendor/faction access; shifts city state"},
    {"ID":"V002","Name":"CityState_Slums_Order","Kind":"Variable","Type":"Int (-100..+100)","Init":"0","Set In":"SCN-1.50, SCN-1.80","Used By":"Patrol density, prices","Effect":">+20 spawns more guards; <−20 spawns more crime events"},
    {"ID":"V003","Name":"CityState_Slums_Compassion","Kind":"Variable","Type":"Int (-100..+100)","Init":"0","Set In":"SCN-1.50, SCN-1.80","Used By":"Sidequest availability","Effect":"≥+20 unlocks 'Soup Line' quest chain"},
    {"ID":"V004","Name":"ArchitectAttention","Kind":"Variable","Type":"Int (0..100)","Init":"5","Set In":"SCN-1.40, SCN-1.60, SCN-1.80","Used By":"Ambient haunt events","Effect":"≥25 triggers 'Whisper Surge' ambush chance"},
    {"ID":"V005","Name":"CompanionLoyalty_Cynic","Kind":"Variable","Type":"Int (0..100)","Init":"30","Set In":"SCN-1.30, SCN-1.65, SCN-1.80","Used By":"Camp scenes, skill unlocks","Effect":"≥60 unlocks 'Clear-Sight' branch later"},
    {"ID":"V006","Name":"Debt_To_Faction_Lantern","Kind":"Variable","Type":"Int (0..3)","Init":"0","Set In":"SCN-1.35, SCN-1.80","Used By":"Faction shop tier","Effect":"1..3 increases stock and discounts"},
    {"ID":"V007","Name":"Ledger_Puzzle_State","Kind":"Variable","Type":"Enum {0=Unseen,1=Seen,2=Solved,3=Failed}","Init":"0","Set In":"SCN-1.20","Used By":"SCN-1.25, SCN-1.40","Effect":"Solved grants Compassion; Failed nudges Order"},
    {"ID":"V008","Name":"Valve_Tutorial_Seen","Kind":"Variable","Type":"Bool","Init":"0","Set In":"SCN-1.33","Used By":"SCN-1.70","Effect":"Skips duplicate prompts"},
    {"ID":"V009","Name":"Crossroads_Tutorial_Shown","Kind":"Variable","Type":"Bool","Init":"0","Set In":"SCN-1.80","Used By":"—","Effect":"One-time systems tutorial toggle"},
    {"ID":"V010","Name":"Cynic_Recruited","Kind":"Variable","Type":"Bool","Init":"0","Set In":"SCN-1.30 / SCN-1.65","Used By":"SCN-1.70, Camps","Effect":"Enables Embalmer combat role"},
    {"ID":"V011","Name":"Echoes_Total","Kind":"Variable","Type":"Int (currency)","Init":"0","Set In":"Throughout","Used By":"Vendors, crafts, class nodes","Effect":"Spend gate for class nodes"},
    {"ID":"V012","Name":"Contaminant_Total","Kind":"Variable","Type":"Int (currency)","Init":"0","Set In":"Elites/Boss/Choices","Used By":"Crafts, forbidden skills","Effect":"Overuse may cost Sanity; unlocks potent items"},
    {"ID":"S101","Name":"Has_Ether_Dose","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.30","Used By":"SCN-1.60, SCN-1.70","Effect":"Enables Cynic rescue choice"},
    {"ID":"S102","Name":"Foreman_Alive","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"ON","Set In":"SCN-1.70","Used By":"SCN-1.80","Effect":"Alters Crossroads options and variants"},
    {"ID":"S103","Name":"Union_Meeting_Known","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.35","Used By":"SCN-1.50","Effect":"Adds peaceful infiltration path"},
    {"ID":"S104","Name":"Ledger_Forgery_Exposed","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.25","Used By":"SCN-1.40","Effect":"Opens Audit confrontation lines"},
    {"ID":"S105","Name":"Baron_PhaseHint_Learned","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.33 / SCN-1.60","Used By":"SCN-1.70","Effect":"Improves boss hinting"},
    {"ID":"S106","Name":"Lantern_Safehouse_Unlocked","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.80 (Atoning)","Used By":"Chapter 2","Effect":"Grants rest/vendor in CH2"},
    {"ID":"S107","Name":"BlackMarket_Access","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.80 (Exploit)","Used By":"Chapter 2","Effect":"Enables clandestine shop"},
    {"ID":"S108","Name":"Foreman_Signet_Obtained","Kind":"Switch","Type":"Switch (OFF/ON)","Init":"OFF","Set In":"SCN-1.80 (Cruel)","Used By":"Chapter 2","Effect":"Echo gain trinket path"}
]

df_vars = pd.DataFrame(vars_switches, columns=["ID","Name","Kind","Type","Init","Set In","Used By","Effect"])
vars_csv_path = "/mnt/data/ch1_variables_switches.csv"
df_vars.to_csv(vars_csv_path, index=False)

# ---------- Scene Checklist CSV ----------
scenes = [
    {"SceneID":"SCN-1.10","Title":"Canal of Candles","Location":"Slum Canals","Trigger":"Auto-run after fade-in","Optional":"No","Conditions":"—","KeyBeats":"Bodies in wax; inciting letter; set tone & Journal","Choices":"—","FlagsSet":"+ArchitectAttention (V004 +3)","LockPoint":"No","Rejoin":"—","Dependencies":"None"},
    {"SceneID":"SCN-1.20","Title":"Weights & Tithes","Location":"Weighhouse Office","Trigger":"Inspect ledger","Optional":"No","Conditions":"—","KeyBeats":"3 mismatched entries; Truth ability puzzle","Choices":"Puzzle success/failure","FlagsSet":"V007 set; if Solved: V003 +10, S104 ON; if Failed: V002 +8; +Echoes","LockPoint":"No","Rejoin":"To SCN-1.25","Dependencies":"SCN-1.10"},
    {"SceneID":"SCN-1.25","Title":"Voices in Tallow","Location":"Alleyway","Trigger":"Exit Weighhouse","Optional":"No","Conditions":"—","KeyBeats":"Rumors; optional Echo pickup","Choices":"—","FlagsSet":"If V007=2: 'Auditor' tag for next scenes","LockPoint":"No","Rejoin":"Always","Dependencies":"SCN-1.20"},
    {"SceneID":"SCN-1.30","Title":"Ether & Ethics","Location":"Back-alley surgery","Trigger":"Enter marked door","Optional":"No","Conditions":"—","KeyBeats":"Meet Cynic; guest joins","Choices":"C-1: Coin / Info / Threaten","FlagsSet":"V005 +/-; V003 +5 (Coin); V002 +5 (Threaten); S101 ON if Info","LockPoint":"No","Rejoin":"Always","Dependencies":"SCN-1.25"},
    {"SceneID":"SCN-1.33","Title":"Steam & Valves","Location":"Tallow Works catwalks","Trigger":"Step onto catwalk","Optional":"No","Conditions":"—","KeyBeats":"Valve tutorial; first Elite (Grease Imps)","Choices":"—","FlagsSet":"S105 ON; V008=1","LockPoint":"No","Rejoin":"Always","Dependencies":"SCN-1.30"},
    {"SceneID":"SCN-1.35","Title":"Lantern Lighters’ Leaflet","Location":"Side office","Trigger":"Interact with pamphlet board","Optional":"Yes","Conditions":"—","KeyBeats":"Faction rumor; lore pickup","Choices":"—","FlagsSet":"S103 ON; V006 +1","LockPoint":"No","Rejoin":"Unlocks Union Pass in SCN-1.50","Dependencies":"SCN-1.33"},
    {"SceneID":"SCN-1.40","Title":"Foreman’s Books","Location":"Foreman’s office","Trigger":"Enter office","Optional":"No","Conditions":"If V002≥10, guards present","KeyBeats":"Audit confrontation or skirmish","Choices":"Audit (S104=ON) or Skirmish","FlagsSet":"Audit: V003 +5, V004 +2; Skirmish: V002 +5; gain Foreman Key","LockPoint":"No","Rejoin":"Key obtained; proceed","Dependencies":"SCN-1.33"},
    {"SceneID":"SCN-1.50","Title":"Render Unto Oil","Location":"Factory floor","Trigger":"Use Foreman Key; choose approach","Optional":"No","Conditions":"If S103=ON, Union Pass available","KeyBeats":"Traversal set-piece; vats hazard; Elite(s)","Choices":"Union Pass / Force / Stealth","FlagsSet":"Union: V003 +5; Force: V002 +5; Stealth: V004 +2","LockPoint":"No","Rejoin":"Pre-boss staging","Dependencies":"SCN-1.40"},
    {"SceneID":"SCN-1.60","Title":"Bones in Wax","Location":"Staging room (camp)","Trigger":"First camp","Optional":"No","Conditions":"If S101=ON, Ether option appears","KeyBeats":"Cynic micro-arc; camp systems","Choices":"C-2: Give Ether / Intervene / Let be","FlagsSet":"V005 +/-; S101=OFF if used; on fail: V004 +3","LockPoint":"No","Rejoin":"Always","Dependencies":"SCN-1.50"},
    {"SceneID":"SCN-1.65","Title":"A Price of Help","Location":"Catwalk to arena","Trigger":"Walk-and-talk","Optional":"No","Conditions":"If V005≥50 recruit now","KeyBeats":"Recruitment gate for Cynic","Choices":"—","FlagsSet":"If V005≥50: V010=TRUE","LockPoint":"No","Rejoin":"Always","Dependencies":"SCN-1.60"},
    {"SceneID":"SCN-1.70","Title":"The Tallow-Baron","Location":"Boiler hall (boss)","Trigger":"Boss start","Optional":"No","Conditions":"—","KeyBeats":"Three-phase boss; valves; Profit Margin/Audit; Meltdown","Choices":"Post-fight: Spare/Execute Foreman","FlagsSet":"Rewards; S102 set; +Contaminant; S105 hints used","LockPoint":"No","Rejoin":"Victory required","Dependencies":"SCN-1.65"},
    {"SceneID":"SCN-1.80","Title":"Judgment Crossroads","Location":"Weighhouse dais","Trigger":"Post-boss ceremony","Optional":"No","Conditions":"—","KeyBeats":"Major judgment; tutorial if first time","Choices":"C-3: Cruel / Atoning / Exploit","FlagsSet":"Set V001; adjust V002/V003/V004; S106 or S107 or S108","LockPoint":"Yes","Rejoin":"Converges to SCN-1.90","Dependencies":"SCN-1.70"},
    {"SceneID":"SCN-1.90","Title":"Port Gate Opens","Location":"City edge","Trigger":"Travel to edge","Optional":"No","Conditions":"—","KeyBeats":"Epilogue with variants based on V001","Choices":"—","FlagsSet":"If Exploit: V004 +2; item/unlocks vary","LockPoint":"No","Rejoin":"Chapter 2 starts","Dependencies":"SCN-1.80"},
    {"SceneID":"OE-1","Title":"Drip Line","Location":"Alleys","Trigger":"World encounter","Optional":"Yes","Conditions":"V002≥15","KeyBeats":"Patrol stealth or fight","Choices":"Hide / Bribe / Fight","FlagsSet":"+Echoes or +Contaminant; Order/Compassion shifts","LockPoint":"No","Rejoin":"Always","Dependencies":"Any time after SCN-1.33"},
    {"SceneID":"OE-2","Title":"Soup Line","Location":"Union Ward","Trigger":"Talk to organizer","Optional":"Yes","Conditions":"V001=2 (Atoning)","KeyBeats":"Short relief quest","Choices":"—","FlagsSet":"Gain Union Banner trinket","LockPoint":"No","Rejoin":"Always","Dependencies":"After SCN-1.80 (Atoning)"},
    {"SceneID":"OE-3","Title":"Duel in Grease","Location":"Hidden ring","Trigger":"Speak to fixer","Optional":"Yes","Conditions":"V001=3 (Exploit)","KeyBeats":"1v1 elite duel","Choices":"—","FlagsSet":"Gain Ledger Knife; +ArchitectAttention","LockPoint":"No","Rejoin":"Always","Dependencies":"After SCN-1.80 (Exploit)"}
]

df_scenes = pd.DataFrame(scenes, columns=["SceneID","Title","Location","Trigger","Optional","Conditions","KeyBeats","Choices","FlagsSet","LockPoint","Rejoin","Dependencies"])
scenes_csv_path = "/mnt/data/ch1_scene_checklist.csv"
df_scenes.to_csv(scenes_csv_path, index=False)

# Display to the user
display_dataframe_to_user("Chapter 1 Variables & Switches", df_vars)
display_dataframe_to_user("Chapter 1 Scene Checklist", df_scenes)

vars_csv_path, scenes_csv_path
