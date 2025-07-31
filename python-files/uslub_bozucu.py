
import tkinter as tk
import random

synonyms = {
    "yaptım": ["halleettim", "başardım", "çözdüm"],
    "iş": ["mevzu", "konu", "durum"],
    "kimse": ["kimseler", "hiç kimse", "adam akıllı biri"],
    "söylemedim": ["bahsetmedim", "çaktırmadım", "duyurmadım"],
    "ben": ["bende", "tarafımdan", "ben var ya"],
    "bu": ["şu", "mevcut", "bahsi geçen"],
    "hallettim": ["bitirdim", "çözdüm", "yoluna koydum"],
    "duymadı": ["duymamıştır", "haberi olmadı", "kulak asmadı"],
}

def stil_boz(cumle):
    kelimeler = cumle.split()
    yeni_cumle = []
    for kelime in kelimeler:
        temiz = kelime.lower().strip(".,!?")
        if temiz in synonyms:
            yeni_kelimeler = synonyms[temiz]
            yeni_cumle.append(random.choice(yeni_kelimeler))
        else:
            yeni_cumle.append(kelime)
    if len(yeni_cumle) > 4:
        idx = random.randint(1, len(yeni_cumle)-2)
        yeni_cumle.insert(0, yeni_cumle.pop(idx))
    return " ".join(yeni_cumle)

def run_app():
    def cevir():
        giris = input_text.get("1.0", tk.END).strip()
        cikis = stil_boz(giris)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, cikis)

    window = tk.Tk()
    window.title("Üslup Bozucu 3000")
    window.geometry("600x400")

    tk.Label(window, text="Orijinal Cümle:").pack()
    input_text = tk.Text(window, height=5)
    input_text.pack(fill=tk.X, padx=10)

    tk.Button(window, text="Stili Boz", command=cevir).pack(pady=10)

    tk.Label(window, text="Bozulmuş Cümle:").pack()
    output_text = tk.Text(window, height=5)
    output_text.pack(fill=tk.X, padx=10)

    window.mainloop()

if __name__ == "__main__":
    run_app()
