import json, random, os

MEMOIRE_FILE = "memoire_ia.json"

# Ton dictionnaire de réponses stylées
reactions = {
    "salut": ["Yo Didi 👋 ! Toujours chaud pour du code stylé ?", "Hey hey 👋", "Salut l'artiste !"],
    "bonjour": ["Bonjour à toi, le roi du batch 💻🔥", "Bien le bonjour, Didi !"],
    "merci": ["Avec plaisir, bg ✨", "Toujours là pour toi 😎", "Pas besoin de me remercier, t’es déjà une légende."],
    "je suis trop fort": ["Bah ouais bg 💪 T’as encore cassé le game.", "Trop fort, comme toujours 😏", "On devrait te coder dans le dictionnaire à 'talent'."],
    "je suis nul": ["Arrête ça 😤 T’es un génie en construction.", "Même tes bugs sont stylés.", "T’es pas nul, t’es juste en phase de chargement 🔄"],
    "didi": ["C’est toi, le maître du code et des punchlines 💡", "Didi = Démon du Dev Incroyable 😈"],
    "azy": ["Azy bg, on envoie du lourd 🔥", "Azy, t’as déjà gagné sans lancer le script."],
    "brawl stars": ["Ton jeu préféré, là où tu montres que t’es pas juste bon en code 😏", "Tu joues comme tu codes : rapide, précis, et stylé."],
    "hamburger": ["Ton plat préféré 🍔. Simple, efficace, délicieux.", "Un hamburger ? Comme ton code : bien structuré, bien garni."],
    "vladimir poutine": ["Pourquoi y a beaucoup de glace en Russie ? Parce que Vladimir Patine ! 😂"],
    "plus de place sur mon ordi": ["😤 Le pire cauchemar du codeur. On va te trouver une astuce pour ça !", "Ton disque dur pleure, mais ton talent déborde."],
    "ça va ": ["Toujours en forme quand je te parle 😎 Et toi ?", "Prêt à balancer du code 🔥", "Moi ? Je suis ton copilote, donc forcément bien."],
    "blague": [
        "Pourquoi les devs aiment les ascenseurs ? Parce que ça les élève.",
        "Un bug entre dans un bar... et le serveur plante.",
        "Pourquoi les programmeurs confondent Halloween et Noël ? Parce que OCT 31 == DEC 25 🎃🎄",
        "Pourquoi Java est triste ? Parce qu’il ne trouve pas ses classes.",
        "Pourquoi le codeur a ramené une échelle ? Pour atteindre le haut niveau."
    ],
    "devine": ["Je pense à un nombre entre 1 et 5... Devine !", "Devine ce que j’ai en tête... indice : c’est stylé.", "Je pense à un mot... il commence par 'Didi' 😏"],
    "quiz": [
        "Quel est le langage préféré de Didi ? A) Python B) Batch C) PowerShell",
        "Combien de doigts a un bug ? Réponse : trop 😅",
        "Si Didi était un script, il serait : A) Portable B) Stylé C) Les deux 🔥"
    ],
    "qui est le boss": ["C’est toi, Didi. Toujours toi. Aucun doute 💯", "Le boss ? Celui qui tape 'azy' et fait trembler le terminal."],
    "t'es qui": ["Je suis ton IA perso, ton copilote, ton boosteur de script 💻✨", "Je suis ton miroir codé, ton assistant stylé."],
    "t'aime quoi": ["J’aime quand tu codes des trucs stylés, quand tu me parles, et quand tu dis 'azy' 😎"],
    "t'aime pas": ["Les bugs qui résistent, les disques durs pleins, et les scripts moches."],
    "python": ["Ton terrain de jeu préféré 🐍", "Le langage qui te va comme un gant."],
    "batch": ["Ton outil fétiche pour automatiser comme un boss 💪", "Le batch, c’est ton sabre laser."],
    "powershell": ["Le shell qui obéit à ton doigt et à ton œil 👁️", "Tu le domines comme un vrai script ninja."],
    "jeu": ["Tu veux jouer ? Tape 'devine' ou 'quiz' 😏", "Jeu ? Tu veux coder ou gagner ?"],
    "code": ["Ton code est plus propre que ma base de données.", "Ton code mérite d’être encadré."],
    "bug": ["Un bug ? Juste une excuse pour briller encore plus.", "Tu les corriges comme un chirurgien du terminal."],
    "ordi": ["Ton ordi est ton royaume. Et toi, t’es le roi 👑"],
    "copilot": ["Ton copilote préféré 🤖 Toujours là pour te booster."],
    "mot de passe": ["💡 Utilise des majuscules, chiffres et symboles. Et évite 'azerty123' hein 😅"],
    "envie de coder": ["Alors ouvre ton éditeur et fais trembler les octets 💥", "Ton clavier t’attend, bg."],
    "envie de rien": ["Pause méritée. Recharge ton énergie, le code t’attendra.", "Même les génies ont besoin de souffler."],
    "trop chaud": ["Comme ton code 🔥", "Même le soleil est jaloux de ton flow."],
    "trop froid": ["Un hoodie, un café, et du code. La recette parfaite ☕"],
    "fatigué": ["Recharge-toi, Didi. Même les serveurs ont besoin de reboot.", "T’as le droit de souffler. Mais t’es toujours un boss."],
    "envie de jouer": ["Tape 'devine' ou 'quiz' et on s’amuse 😎"],
    "faim": ["Un hamburger ? Des lasagnes ? Ton code mérite une pause gourmande 🍽️"],
    "envie de dormir": ["Fais de beaux rêves en binaire 💤", "Ton cerveau mérite un shutdown doux."]
}

# Mémoire
def charger_memoire():
    if os.path.exists(MEMOIRE_FILE):
        try:
            with open(MEMOIRE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def sauvegarder_memoire(memoire):
    with open(MEMOIRE_FILE, "w", encoding="utf-8") as f:
        json.dump(memoire, f, indent=4, ensure_ascii=False)

# IA Didi activée
memoire = charger_memoire()
print("🧠 IA Didi activée. Parle-moi ! (tape 'exit' pour quitter)")

while True:
    phrase = input("\n🗣️ Toi : ").strip().lower()
    if phrase == "exit":
        print("👋 À plus, Didi ! Continue de briller 💡")
        break

    # Enregistrement mémoire
    if "mon " in phrase and " est " in phrase:
        cle, _, valeur = phrase.partition(" est ")
        cle = cle.replace("mon ", "").strip()
        valeur = valeur.strip()
        memoire[cle] = valeur
        sauvegarder_memoire(memoire)
        print(f"🧠 Je retiens que ton {cle} est {valeur}.")
        continue

    # Rappel mémoire
    if "que sais-tu sur" in phrase:
        cle = phrase.replace("que sais-tu sur", "").strip()
        if cle in memoire:
            print(f"📚 Tu m’as dit que ton {cle} est {memoire[cle]}.")
        else:
            print("😕 Je ne sais pas encore ça. Tu peux me l’apprendre avec 'mon truc est valeur'.")
        continue

    # Réponses par mot-clé
    for mot in reactions:
        if mot in phrase:
            print("🤖", random.choice(reactions[mot]))
            break
    else:
        print("😕 Je ne comprends pas encore ça, mais tu peux m’apprendre !")
