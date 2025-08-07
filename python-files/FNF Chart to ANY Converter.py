"""
TUTORIAL:

Set Up:
1. Download it as ZIP
2. Extracted the downloaded ZIP
3. Open the Extracted ZIP
4. Create 2 folders being "in" and "out"
5. Ensure that Python is Installed with the needed libraries: pip install msgspec, pretty_midi, tqdm

Get Started:
1. Grab a .json file that is psych engine compatible.
2. Place it in "in" folder.
3. Open CMD and type (or copy and paste) "python "FNF Chart to ANY Converter.py"" and Press ENTER.
4. Type the number corresponding to the file name.
5. Choose which you want to be converted.
6. Depending on the .json size, this will take a while, or 0 seconds.
7. It is now converted.

TIPS:
The "in" folder is where you insert your json files into this folder, and the program will find it and add it there.
The "out" folder is where your converted files are stored to, if it fails to find one, it'll make one.
"""

from msgspec.json import decode
from glob import glob
from os import mkdir
from os.path import exists
from pretty_midi import Note, PrettyMIDI, Instrument
from tqdm import tqdm
from sys import exit

bpmMult = float(input("Before starting, Please set the amount of BPM to multiply, Higher means spammier.\nNote that it's only used for Clone Hero and not the rest of them.\n> "))

chartType = [['AYS (OPTIMIZED)', 'txt'], ['AYS (SSS)', 'txt'], ['GPOP', 'gpop'], ['OSU', 'osu'], ['MIDI (SLOW)', 'mid'], ['QUAVER', 'qua'], ['Clone Hero', 'chart']]
def convertJson(file, convert):
    try:
        print('Loading JSON (The program is not frozen.)')
        convert = chartType[convert]
        name = file[3:]
        file = open(file, "r")
        file = file.read()
        file = decode(file)
        sn = file['song']['song']
        bpm = file['song']['bpm']
        print('Loading CHART')
        notes = []
        for i in tqdm(range(len(file['song']['notes']))):
            mustHit = file['song']['notes'][i]['mustHitSection']
            for j in range(len(file['song']['notes'][i]['sectionNotes'])):
                add = []
                for k in range(3):
                    v = float(file['song']['notes'][i]['sectionNotes'][j][k])
                    if k == 1:
                        noteData = int(v)+1
                        if mustHit: noteData += 4
                        if noteData > 8: noteData -= 8
                        v = noteData
                    add.append(str(v))
                notes.append(add)

        if convert[0] == "MIDI (SLOW)": notes.append([notes[len(notes)-1][0], 0, 0])
        try: credit = file["song"]["songCredit"]
        except: credit = "Unknown"
        file = ""
        notes.sort(key=lambda x: float(x[0]))
        print(f"Note Count: {len(notes)}")
        print(f'Converting to {convert[0]}')
        converted = ""
        storage = []
        if convert[0] == "GPOP":
            ses = [0, 2, 4, 6]
            converted = '[{"type":"s2","dict":{"a":0,"a1":1,"s":2,"s1":3,"d":4,"d1":5,"f":6,"f1":7}}'
            noteUsed = [False, False, False, False]
            oldTime = 0
        if convert[0] == "MIDI (SLOW)":
            midi1 = PrettyMIDI(resolution=32767, initial_tempo=bpm)
            instrument1 = Instrument(program=0)
            midi2 = PrettyMIDI(resolution=32767, initial_tempo=bpm)
            instrument2 = Instrument(program=0)
        if convert[0] == "OSU":
            converted = f"""osu file format v14

[General]
AudioFilename:Inst.ogg
Mode:3

[Metadata]
Title:{sn}
Artist:{credit}
Creator:Nael's FNF to OSU converter [PYTHON SCRIPT]
Version:Normal
Source:FNF
GeneratedBy:Nael's FNF to OSU converter [PYTHON SCRIPT]

[Difficulty]
HPDrainRate:8
CircleSize:4
OverallDifficulty:7

[TimingPoints]
0,{60000/bpm},4,1,0,100,1,0

[HitObjects]
"""
        ses2 = [64, 192, 320, 448]
        if convert[0] == "QUAVER":
            oldTime = -1
            noteUsed = [False, False, False, False]
            converted = f"""AudioFile: audio.ogg
BackgroundFile: ''
MapId: -1
MapSetId: -1
Mode: Keys4
Title: "{sn}"
Artist: {credit}
Source: ''
Tags: ''
Creator: Nael2xd
DifficultyName: 'Normal'
Description: Created using Nael's FNF to QUAVER Converter [PYTHON SCRIPT]
BPMDoesNotAffectScrollVelocity: true
InitialScrollVelocity: 1
EditorLayers: []
CustomAudioSamples: []
SoundEffects: []
TimingPoints:
- Bpm: {bpm}
SliderVelocities: []
HitObjects:"""
        if convert[0] == "Clone Hero":
            converted = f"""[Song]
{{
  Name = "This"
  Artist = "That"
  Charter = "Nael's FNF to GH Converter"
  Offset = 0
  Resolution = 192
  Player2 = bass
  Difficulty = 0
  PreviewStart = 0
  PreviewEnd = 0
  Genre = "rock"
  MediaType = "cd"
}}
[SyncTrack]
{{
  0 = TS 4
  0 = B {round(312500 * bpmMult)}
}}
[Events]
{{
}}
[ExpertSingle]
""" + "{\n"
        for i in tqdm(range(len(notes)-1)):
            if convert[0] == "AYS (OPTIMIZED)":
                l = "{:.6f}".format(float(notes[i][0])/1000)
                converted += f"{l},{notes[i][1]}\n"
            elif convert[0] == "AYS (SSS)":
                p = "{:.6f}".format(float(notes[i][0])/1000)
                converted += "{" + p + "}: {" + notes[i][1] + "}: {}: {" + "{:.0f}".format(float(notes[i][2])) + "}\n"
            elif convert[0] == "GPOP" and int(notes[i][1]) > 4:
                l = "{:.3f}".format(round(float(notes[i][0])/1000, 3))
                if not noteUsed[int(notes[i][1])-5]:
                    converted += f",{str(ses[int(notes[i][1])-5])},{l}"
                    noteUsed[int(notes[i][1])-5] = True
                if oldTime != l:
                    oldTime = l
                    noteUsed = [False, False, False, False]
            elif convert[0] == "OSU" and int(notes[i][1]) > 4:
                n = ses2[int(notes[i][1])-5]
                isHold = float(notes[i][2]) > 0
                format = [notes[i][0], notes[i][2]]
                converted += f"{n},192,{format[0]},"
                if isHold:
                    p = "{:.6f}".format(float(format[0])+float(format[1]))
                    converted += f"128,0,{p}:0:0:0:0:\n"
                else: converted += "1,0,0:0:0:0:\n"
            elif convert[0] == "MIDI (SLOW)":
                s = (float(notes[i][0])/1000)
                n = Note(velocity=100, pitch=int(notes[i][1])+36, start=s, end=s+0.00025)
                if int(notes[i][1]) > 4: instrument2.notes.append(n)
                else: instrument1.notes.append(n)
            elif convert[0] == "QUAVER" and int(notes[i][1]) > 4:
                l = int(float(notes[i][0]))
                if not noteUsed[int(notes[i][1])-5]:
                    isHold = float(notes[i][2]) > 0
                    converted += f"\n- StartTime: {l}\n  Lane: {int(notes[i][1])-4}\n  KeySounds: []"
                    if isHold: converted += f"\n  EndTime: {l+int(float(notes[i][2]))}"
                    noteUsed[int(notes[i][1])-5] = True
                if oldTime != l:
                    oldTime = l
                    noteUsed = [False, False, False, False]
            elif convert[0] == "Clone Hero" and int(notes[i][1]) > 4:
                converted += f"  {int((float(notes[i][0]) * bpmMult) - (100 * bpmMult))} = N {int(notes[i][1]) % 4} {int(float(notes[i][2]) * bpmMult)}\n"
            if len(converted) > 1000000:
                storage.append(converted)
                converted = ""
            notes[i] = ""
        if convert[0] == "GPOP": converted += "]"
        if convert[0] == "Clone Hero": converted += "}"
        storage.append(converted)
        converted = ""
        out = f"out/{name}_{convert[0]}_OUT.{convert[1]}"
        for i in range(len(storage)):
            converted += storage[i]
            storage[i] = ""
        if convert[0] == "OSU":
            out = f"out/{credit} - {sn} (Nael's FNF to OSU [PYTHON SCRIPT]) [Normal].osu"
            save = open(out, "w")
            save.write(converted)
            save.close()
        elif convert[0] == "MIDI (SLOW)":
            print(f"BPM is set to {bpm}! Saving MIDI might take a while.")
            print('0/2')
            midi1.instruments.append(instrument1)
            midi1.write(f'out/{name}_{convert[0]}_OPPO_OUT.{convert[1]}')
            print('1/2')
            midi2.instruments.append(instrument2)
            midi2.write(f'out/{name}_{convert[0]}_BF_OUT.{convert[1]}')
        else:
            save = open(out, "w")
            save.write(converted)
            save.close()
        print(f'DONE! Saved in {out}.')
    except Exception as Err:
        print(f'Chart of {name} cannot be converted :(\nReason: {Err}')

print("TOOL BY NAEL2XD | https://github.com/NAEL2XD\n")
listsOfJsons = glob("in/*.json")
def main():
    while True:
        print("Which JSON do you wanna convert?\n   [E]: EXIT\n   [0]: ALL")
        for i in range(len(listsOfJsons)):
            print(f"   [{i+1}]: {listsOfJsons[i][3::1]}")
        keyword = input("> ")
        if keyword.lower() == "e": exit()
        keyword = int(keyword)-1
        print("Type of chart to convert?")
        for i in range(len(chartType)):
            print(f"   [{i}]: {chartType[i][0]}")
        chart = int(input("> "))
        if keyword == -1:
            for i in range(len(listsOfJsons)):
                print(f"ALL CONVERTING... {i+1}/{len(listsOfJsons)} ({listsOfJsons[i]})")
                convertJson(listsOfJsons[i], chart)
        else: convertJson(listsOfJsons[keyword], chart)

if not exists('in/'): mkdir('in')
if not exists('out/'): mkdir('out')

while True:
    try:
        main()
    except SystemExit:
        print('ok bye')
        break
    except:
        print('Invalid Number!')