#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Σύστημα αναζήτησης πειστηρίων & ταυτοποίησης (A1–H8)
====================================================

Ροή λειτουργίας (non‑stop):
1. Ο χρήστης εισάγει συντεταγμένες (γράμμα A–H + αριθμό 1–8).
2. Αν οι συντεταγμένες είναι από τις «γνωστές» (A2, E4, F7, H3, H6) τότε
   καλείται να «ονομάσει το εύρημα» ‑ επιλέγοντας κατηγορία (Εργαλείο, Χαρτί, Γάντι).
3. Εφόσον ταιριάζει, εμφανίζεται μενού 3 επιλογών ταυτοποίησης
   (DNA, Αποτύπωμα, Υπογραφή).
4. Το πρόγραμμα επιστρέφει το καταγεγραμμένο όνομα (αν υπάρχει) ή
   μήνυμα «Δεν υπάρχει κάτι καταγεγραμμένο…».
5. Πατώντας Enter, η οθόνη καθαρίζει και ξεκινά νέα αναζήτηση.
6. Για έξοδο: πληκτρολογήστε q (ή Ctrl‑C) στη φάση των συντεταγμένων.
"""
from __future__ import annotations
import os
import sys
from typing import Dict, Tuple

# ---------------------------------------
# Βοηθητικές σταθερές & λεξικά
# ---------------------------------------
ITEM_OPTIONS: Dict[str, str] = {
    "1": "ΕΡΓΑΛΕΙΟ",
    "2": "ΧΑΡΤΙ",
    "3": "ΓΑΝΤΙ",
}
EVIDENCE_OPTIONS: Dict[str, str] = {
    "1": "DNA",
    "2": "ΑΠΟΤΥΠΩΜΑ",
    "3": "ΥΠΟΓΡΑΦΗ",
}

# Συντεταγμένη → προβλεπόμενη κατηγορία εύρηματος
ITEM_MAP: Dict[str, str] = {
    "A2": "ΕΡΓΑΛΕΙΟ",
    "E4": "ΕΡΓΑΛΕΙΟ",
    "F7": "ΧΑΡΤΙ",
    "H3": "ΧΑΡΤΙ",
    "H6": "ΓΑΝΤΙ",
}

# (Συντεταγμένη, Evidence ID) → Όνομα υπόπτου
EVIDENCE_MAP: Dict[Tuple[str, str], str] = {
    ("A2", "1"): "ΜΑΡΙΑ ΡΗΓΑ",     # DNA
    ("E4", "2"): "ΑΝΝΑ ΜΑΝΟΥ",     # Αποτύπωμα
    ("F7", "2"): "ΕΛΕΝΑ ΖΟΥΝΗ",    # Αποτύπωμα
    ("F7", "3"): "ΜΑΡΙΑ ΡΗΓΑ",     # Υπογραφή
    ("H3", "2"): "ΑΝΝΑ ΜΑΝΟΥ",     # Αποτύπωμα
    ("H3", "3"): "ΝΙΚΗ ΣΤΑΥΡΙΔΟΥ",  # Υπογραφή
    ("H6", "2"): "ΕΛΕΝΑ ΖΟΥΝΗ",    # Αποτύπωμα
}

# ---------------------------------------
# Βοηθητικές συναρτήσεις
# ---------------------------------------

def clear_screen() -> None:
    """Καθαρίζει την κονσόλα σε Windows, macOS και Linux."""
    if os.name == "nt":
        os.system("cls")
    else:
        # ESC[2J = clear screen, ESC[H = cursor home
        print("\033[2J\033[H", end="", flush=True)


def is_valid_square(square: str) -> bool:
    """Ελέγχει αν το τετράγωνο ανήκει στο εύρος A1–H8."""
    return (
        len(square) == 2
        and square[0].upper() in "ABCDEFGH"
        and square[1] in "12345678"
    )


def prompt_menu(options: Dict[str, str], title: str) -> str:
    """Εμφανίζει αριθμημένο μενού και επιστρέφει το επιλεγμένο κλειδί."""
    while True:
        print(title)
        for key, label in options.items():
            print(f"{key}. {label}")
        choice = input("Επιλέξτε: ").strip()
        if choice in options:
            return choice
        print("Μη έγκυρη επιλογή. Προσπάθησε ξανά.\n")


# ---------------------------------------
# Κύριος βρόχος
# ---------------------------------------

def main() -> None:
    clear_screen()
    print("=== Σύστημα Αναζήτησης Πειστηρίων ===")
    try:
        while True:
            square = input("Δώσε συντεταγμένες (A1–H8) ή 'q' για έξοδο: ").strip()
            if square.lower() == "q":
                print("Αντίο!")
                break
            if not is_valid_square(square):
                print("Μη έγκυρες συντεταγμένες.\n")
                continue
            square = square.upper()

            # -----------------------------------
            # Βήμα 1: Ονοματοδοσία εύρηματος
            # -----------------------------------
            if square in ITEM_MAP:
                item_choice = prompt_menu(ITEM_OPTIONS, "Ονομάστε το εύρημά σας:")
                item_label = ITEM_OPTIONS[item_choice]
                expected_label = ITEM_MAP[square]
                if item_label != expected_label:
                    print("Δεν βρέθηκε καταχώριση για αυτό το εύρημα.")
                    input("\nΠάτησε Enter για επόμενη αναζήτηση…")
                    clear_screen()
                    continue
            else:
                print("Δεν υπάρχει καταχώριση στη βάση δεδομένων για αυτές τις συντεταγμένες.")
                input("\nΠάτησε Enter για επόμενη αναζήτηση…")
                clear_screen()
                continue

            # -----------------------------------
            # Βήμα 2: Τύπος ταυτοποίησης (3 επιλογές)
            # -----------------------------------
            evidence_choice = prompt_menu(EVIDENCE_OPTIONS, "Επιλέξτε μέθοδο ταυτοποίησης:")

            # Αναζήτηση στο λεξικό
            suspect = EVIDENCE_MAP.get((square, evidence_choice))
            if suspect:
                print(suspect)
            else:
                print("Δεν υπάρχει κάτι καταγεγραμμένο στη βάση δεδομένων.")

            # -----------------------------------
            # Επόμενη αναζήτηση
            # -----------------------------------
            input("\nΠάτησε Enter για επόμενη αναζήτηση…")
            clear_screen()
            print("=== Σύστημα Αναζήτησης Πειστηρίων ===")
    except KeyboardInterrupt:
        print("\nΑντίο!")


if __name__ == "__main__":
    main()
