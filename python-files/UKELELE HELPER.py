import tkinter as tk
from tkinter import messagebox, scrolledtext

songs = {
    1: {
        "title": "How Great Thou Art",
        "content": """G         C               F 
O Lord my God!  When I in awesome wonder
          C       G                   C
Consider all the works Thy hands have made,
  G        C                F
I see the stars, I hear the mighty thunder,
                 C        G            C
Thy power throughout the universe displayed.


Chorus:
               C        F              C
Then sings my soul, my Savior God to Thee;
               G                    C
How great Thou art!  How great Thou art!
               C        F             C
Then sings my soul, my Savior God to Thee;
               Dm         G         C
How great Thou art!  How great Thou art!

Verse 2 (Same Chords Repeated)
When through the woods, the forest glades I wander
And hear the birds sing sweetly in the trees,
When I look down from lofty mountain grandeur
And hear the brook and feel the gentle breeze...

Verse 3
And when I think that God, His Son not sparing,
Sent Him to die, I scarce can take it in;
That on the cross, my burden gladly bearing,
He bled and died to take away my sin...

Verse 4
When Christ shall come with shout of acclamation
And take me home, what joy shall fill my heart!
Then I shall bow in humble adoration
And there proclaim, my God how great Thou art!




Source: www.ukulele-tabs.com"""
    },

    2: {
        "title": "Thandri Deva",
        "content": """G
Thandri Deva, Thandri Deva
Am
Naa Sarvam Neevayya
D              G
Neevunte Naaku Chaalu
 
[Post Chorus]
 
G                            C
Naa Priyudaa Naa Praanama – Ninnaaraadhinchedan
Am                           D
Naa Jeevamaa Naa Snehamaa – Ninnaaraadhinchedan
 
[Verse 1]
 
G                       C
Nee Prema Varninchuta – Naa Valla Kaadayya
Am                          D
Nee Kaaryamu Vivarinchuta – Naa Brathuku Chaaladayya
G               C
Thandri Devaa - Naa Aanandama
Am               G
Nee Vodilo Naaku Sukhamu
 
[Verse 2]
 
G                        C
Naa Praana Snehithuda – Nee Sannidhi Parimalame
Am                   D
Junte Thene Kanna – Nee Prema Madhuramayya
G               C
Thandri Deva - Naa Aanandama
Am               G
Nee Vodilo Naaku Sukhamu"""
    },
    
    3: {
            "title": "Sundaruda",
            "content": """[Chorus]
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
 
 
[Verse 1]
G            Em              C                D
పదివేలలో నీవు అతిసుందరుడవు - నా ప్రాణప్రియుడవు నీవే
G             Em               C               D
షారోను పుష్పమా లోయలోని పద్మమా - నిను నేను కనుగొంటినే
G            Em              C                D
పదివేలలో నీవు అతిసుందరుడవు - నా ప్రాణప్రియుడవు నీవే
G             Em               C               D
షారోను పుష్పమా లోయలోని పద్మమా - నిను నేను కనుగొంటినే
 
     
[Chorus]
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
 
 
[Verse 2]
G              Em                  C             D
నిను చూడాలని - నీ ప్రేమలో ఉండాలని - నేనాశించుచున్నాను
G              Em                  C             D
నిను చూడాలని - నీ ప్రేమలో ఉండాలని - నేనాశించుచున్నాను

G              Em                  C             D
నిను చూడాలని - నీ ప్రేమలో ఉండాలని - నేనాశించుచున్నాను
G              Em                  C             D
నిను చూడాలని - నీ ప్రేమలో ఉండాలని - నేనాశించుచున్నాను
 
 
[Chorus]
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
 
 
[Bridge]
G          Bm         Am           D
యేసయ్యా నా యేసయ్యా - నీ వంటి వారెవ్వరు
G           Bm        Am         D
యేసయ్యా నా యేసయ్యా - నీలాగ లేరెవ్వరు
G          Bm         Am           D
యేసయ్యా నా యేసయ్యా - నీ వంటి వారెవ్వరు
G           Bm        Am         D
యేసయ్యా నా యేసయ్యా - నీలాగ లేరెవ్వరు
 
 
[Chorus]
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా
       G        Em             Am         D
సుందరుడా అతిశయుడా - మహోన్నతుడా నా ప్రియుడా"""
    }
} 

        

print("\t\tWELCOME!")
print("\nHERE ARE THE LIST OF SONGS THAT ARE AVAIALBLE (MORE TO BE ADDED)")
for number, song in songs.items():
    print(f"\n{number}. {song['title']}")
selectsong=int(input("\nTYPE THE NUMBER OF THE SONG TO OPEN THE CHORDS AND LYRICS OF THE SONG: "))
if selectsong in songs:
    print(f"{selectsong}. {songs[selectsong]['title']} \n\n{songs[selectsong]['content']}")

   
    
def show_lyrics():
    try:
        num = int(entry.get())
        if num in songs:
            song = songs[num]
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, f"{song['title']}\n\n{song['content']}")
        else:
            messagebox.showwarning("Invalid", "That song number doesn't exist.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")

root = tk.Tk()
root.title("Ukulele Song Helper")
root.geometry("600x500")

welcome_label = tk.Label(root, text="\nWELCOME!\nAvailable Songs:", font=("Helvetica", 14))
welcome_label.pack()

for num, song in songs.items():
    tk.Label(root, text=f"{num}. {song['title']}").pack()

entry_label = tk.Label(root, text="\nEnter song number:")
entry_label.pack()

entry = tk.Entry(root)
entry.pack()

submit_btn = tk.Button(root, text="Show Lyrics & Chords", command=show_lyrics)
submit_btn.pack(pady=10)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
text_area.pack(pady=10)

root.mainloop()

