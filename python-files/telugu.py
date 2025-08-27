import sys

# ---------------------------
# 🔤 Unicode → Anu Mapping
# ---------------------------
# ⚠️ This mapping is based on standard Anu fonts (Anu Script 7.0).
#    It may require fine-tuning depending on the exact Anu font version.
telugu_to_anu = {
    # Vowels
    "అ": "A", "ఆ": "B", "ఇ": "C", "ఈ": "D", "ఉ": "E", "ఊ": "F",
    "ఋ": "R", "ౠ": "RR", "ఎ": "G", "ఏ": "H", "ఐ": "I", "ఒ": "J", "ఓ": "K", "ఔ": "L",

    # Consonants
    "క": "k", "ఖ": "K", "గ": "g", "ఘ": "G", "ఙ": "f",
    "చ": "c", "ఛ": "C", "జ": "j", "ఝ": "J", "ఞ": "F",
    "ట": "t", "ఠ": "T", "డ": "d", "ఢ": "D", "ణ": "N",
    "త": "w", "థ": "W", "ద": "x", "ధ": "X", "న": "n",
    "ప": "p", "ఫ": "P", "బ": "b", "భ": "B", "మ": "m",
    "య": "y", "ర": "r", "ల": "l", "వ": "v",
    "శ": "S", "ష": "z", "స": "s", "హ": "h",
    "ళ": "q", "క్ష": "R", "ఱ": "Z",

    # Vowel Signs (matras)
    "ా": "a", "ి": "i", "ీ": "I", "ు": "u", "ూ": "U",
    "ృ": "q", "ె": "e", "ే": "E", "ై": "ai", "ొ": "o", "ో": "O", "ౌ": "au",

    # Others
    "ం": "M", "ః": "H", "్": "", "౦": "0", "౧": "1", "౨": "2", "౩": "3",
    "౪": "4", "౫": "5", "౬": "6", "౭": "7", "౮": "8", "౯": "9",
    "।": ".", "॥": "..",
}

def unicode_to_anu(text):
    """Convert Telugu Unicode text to Anu ASCII encoding"""
    output = ""
    for ch in text:
        if ch in telugu_to_anu:
            output += telugu_to_anu[ch]
        else:
            output += ch  # keep as-is if not mapped
    return output

# ---------------------------
# 🔽 Main Function
# ---------------------------
if _name_ == "_main_":
    if len(sys.argv) > 1:
        # If text is passed via command line
        input_text = " ".join(sys.argv[1:])
    else:
        # Or ask user input
        input_text = input("Enter Telugu Unicode text: ")

    converted = unicode_to_anu(input_text)
    print("\n✅ Unicode Telugu :", input_text)
    print("➡️  Anu ASCII      :", converted)
    print("\n📋 Copy the Anu ASCII text into CorelDraw and apply Anu font.")