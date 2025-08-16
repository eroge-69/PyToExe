from midiutil import MIDIFile

# Új MIDI fájl létrehozása 3 sávval: Gitár, Basszus, Dob
midi = MIDIFile(3)  
tempo = 140
track_guitar, track_bass, track_drums = 0, 1, 2

# Globális beállítások
midi.addTempo(track_guitar, 0, tempo)
midi.addTempo(track_bass, 0, tempo)
midi.addTempo(track_drums, 0, tempo)

# Hangnem: E-moll -> gyökhang: E (MIDI 40 basszus E, 52 gitár E)
# Gitár power chord riff (egyszerűsítve: csak gyökhang)
guitar_notes = [40, 43, 45, 47, 52, 50, 48]  # E, G, A, B, E', D, C
bass_notes = [28, 31, 33, 35, 40, 38, 36]    # basszus megfelelő hangjai

# Intro riff (4 ütem)
time = 0
for note in [40, 43, 45, 47]:  # E - G - A - B
    midi.addNote(track_guitar, 0, note, time, 1, 100)
    midi.addNote(track_bass, 1, note-12, time, 1, 90)
    time += 1

# Refrén akkordmenet (E - D - C - G ismétlés)
for _ in range(2):  # ismétlés
    for note in [40, 38, 36, 43]:
        midi.addNote(track_guitar, 0, note, time, 2, 100)
        midi.addNote(track_bass, 1, note-12, time, 2, 90)
        time += 2

# Dob groove (lábdob = 36, pergő = 38, lábcin = 42)
time = 0
for measure in range(8):  # 8 ütem
    for beat in range(4):
        # Lábcin minden 8-adon
        midi.addNote(track_drums, 9, 42, time + beat*0.5, 0.5, 80)
        # Lábdob 1. és 3. negyeden
        if beat in [0, 2]:
            midi.addNote(track_drums, 9, 36, time + beat, 0.25, 100)
        # Pergő 2. és 4. negyeden
        if beat in [1, 3]:
            midi.addNote(track_drums, 9, 38, time + beat, 0.25, 110)
    time += 4

# Fájl mentése
with open("tarjanyi_rock.mid", "wb") as f:
    midi.writeFile(f)

print("✅ Kész: tarjanyi_rock.mid")
