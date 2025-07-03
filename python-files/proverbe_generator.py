import random

# Baza de componente pentru generarea proverbelor
subiecte = [
    "Zâmbetul", "Prietenia", "Minciuna", "Vorbele", "Interesul", "Dragostea",
    "Adevărul", "Înțelepciunea", "Răbdarea", "Cuvântul", "Inima", "Sufletul",
    "Timpul", "Viața", "Lumina", "Umbra", "Calea", "Destinul", "Speranța",
    "Încrederea", "Respectul", "Bunătatea", "Mândria", "Smerenia", "Curajul",
    "Frica", "Iubirea", "Ura", "Pacea", "Războiul", "Tăcerea", "Cuvintele"
]

adjective_pozitive = [
    "adevărat", "sincer", "cald", "frumos", "puternic", "nobil", "curat",
    "luminos", "înțelept", "blând", "generos", "curajos", "fidel", "onest",
    "drept", "milostiv", "iertător", "îndurator", "vrednic", "trainic"
]

adjective_negative = [
    "fals", "rece", "înșelător", "urât", "slab", "josnic", "murdar",
    "întunecat", "prost", "aspru", "lacom", "fricos", "necredincios", "mincinos",
    "strâmb", "necruțător", "răzbunător", "neîndurător", "nedemn", "fragil"
]

verbe_pozitive = [
    "încălzește", "luminează", "vindecă", "construiește", "unește", "consolează",
    "întărește", "protejează", "îmbogățește", "înfrumusețează", "binecuvântează",
    "dăruiește", "iartă", "salvează", "ajută", "susține", "încurajează", "ridică"
]

verbe_negative = [
    "ascunde", "strică", "rupe", "distruge", "desparte", "întristează",
    "slăbește", "amenință", "sărăcește", "urâțește", "blestemă",
    "fură", "condamnă", "pierde", "înșală", "trădează", "descurajează", "doboară"
]

obiecte_metaforice = [
    "punți peste prăpastii", "balsam pentru suflet", "sămânța adevărului",
    "lumina în întuneric", "apă pentru flori", "hrană pentru minte",
    "cheile înțelepciunii", "comoara ascunsă", "oglinda sufletului",
    "calea către fericire", "poarta cerului", "rădăcinile vieții",
    "fructele răbdării", "parfumul virtuții", "muzica inimii"
]

def genereaza_proverb():
    """Generează un proverb românesc aleatoriu f