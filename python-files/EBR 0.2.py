import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional, Tuple

# =========================
# Data structures
# =========================

@dataclass
class CountryState:
    """Represents a sovereign or subjugated country (kept even if conquered so we can restore it in rebellions)."""
    name: str
    provinces: List[str] = field(default_factory=list)
    borders: Set[str] = field(default_factory=set)   # names of neighboring sovereign countries
    points: int = 1                                   # points per country (default 1)
    alive: bool = True                                # sovereign (True) or subjugated (False)
    overlord: Optional[str] = None                    # name of conqueror if subjugated

@dataclass
class Alliance:
    """A multi-country alliance. Countries are by name. Alliances have no shared pool of points; members hold points individually."""
    members: Set[str] = field(default_factory=set)

class World:
    def __init__(self,
                 countries: Dict[str, CountryState],
                 alliances: List[Alliance] = None,
                 seed: Optional[int] = None):
        self.countries: Dict[str, CountryState] = countries
        self.alliances: List[Alliance] = alliances or []
        self.turn: int = 0
        if seed is not None:
            random.seed(seed)
        # Ensure every sovereign has at least 1 point
        for c in self.alive_countries():
            c.points = max(1, c.points)

    # ---------- Helpers ----------
    def alive_country_names(self) -> List[str]:
        return [n for n, c in self.countries.items() if c.alive]

    def alive_countries(self) -> List[CountryState]:
        return [c for c in self.countries.values() if c.alive]

    def get_alliance_of(self, country_name: str) -> Optional[Alliance]:
        for a in self.alliances:
            if country_name in a.members:
                return a
        return None

    def in_same_alliance(self, a: str, b: str) -> bool:
        A = self.get_alliance_of(a)
        return A is not None and b in A.members

    def remove_empty_alliances(self):
        self.alliances = [a for a in self.alliances if len(a.members) > 0]

    def normalize_borders(self):
        """Keep borders symmetric and only among alive sovereigns."""
        alive = set(self.alive_country_names())
        for name, c in self.countries.items():
            if not c.alive:
                continue
            # Drop non-alive and self
            c.borders.intersection_update(alive - {name})
        # Symmetry
        for name, c in self.countries.items():
            if not c.alive:
                continue
            for nb in list(c.borders):
                if name not in self.countries[nb].borders:
                    self.countries[nb].borders.add(name)

    # ---------- Game Actions ----------
    def action_alliance(self) -> Optional[str]:
        """Try to form or grow an alliance per rules."""
        alive = self.alive_country_names()
        if len(alive) < 2:
            return None
        
        all_in_alliance = all(self.get_alliance_of(c) is not None for c in alive)
        if all_in_alliance:
            # Default to war instead of doing nothing
            return self.action_war()

        attempts = 0
        max_attempts = 20
        while attempts < max_attempts:
            attempts += 1
            a, b = random.sample(alive, 2)
            a_all = self.get_alliance_of(a)
            b_all = self.get_alliance_of(b)

            if a_all and b_all:
                # Both are already in some alliance -> discard and retry
                continue
            elif a_all and not b_all:
                # b joins a's alliance
                a_all.members.add(b)
                # Increase points of *all* alliance members by 1
                for m in a_all.members:
                    self.countries[m].points += 1
                self.normalize_borders()
                return f"Alliance grows: {b} joins alliance with {', '.join(sorted(a_all.members - {b}))}."
            elif b_all and not a_all:
                # a joins b's alliance
                b_all.members.add(a)
                for m in b_all.members:
                    self.countries[m].points += 1
                self.normalize_borders()
                return f"Alliance grows: {a} joins alliance with {', '.join(sorted(b_all.members - {a}))}."
            else:
                # Neither in an alliance -> create new alliance with a and b
                new_all = Alliance(members={a, b})
                self.alliances.append(new_all)
                # +1 point to the two selected countries
                self.countries[a].points += 1
                self.countries[b].points += 1
                self.normalize_borders()
                return f"New alliance formed between {a} and {b}."

        return None  # couldn't find a valid pair (unlikely)

    def action_war(self) -> Optional[str]:
        """Pick a random attacker, attack a bordering non-ally. If none but allies, split the alliance as specified."""
        alive = self.alive_country_names()
        if len(alive) < 2:
            return None

        attacker = self.countries[random.choice(alive)]
        # Candidate defenders: alive, border, and NOT allied with attacker
        candidates = [n for n in attacker.borders if self.countries[n].alive and not self.in_same_alliance(attacker.name, n)]

        if not candidates:
            # If the country has no choices other than attacking an ally -> split its alliance per rule
            alln = self.get_alliance_of(attacker.name)
            if alln is None or len(alln.members) < 2:
                # Not in an alliance or single-member alliance -> no valid war can be launched this turn
                return f"{attacker.name} wants war but only borders allies/none and isn't in a splittable alliance. Nothing happens."
            # Split the alliance randomly into two non-empty parts
            members = list(alln.members)
            if len(members) == 2:
                # Disband: revert both to no alliance, points back to 1 each
                a1, a2 = members
                alln.members.clear()
                self.remove_empty_alliances()
                self.countries[a1].points = 1
                self.countries[a2].points = 1
                return f"Alliance between {a1} and {a2} disbands."
            else:
                # Random bipartition
                random.shuffle(members)
                cut = random.randint(1, len(members) - 1)
                group1 = set(members[:cut])
                group2 = set(members[cut:])
                # Replace old alliance with two new ones
                self.alliances.remove(alln)
                if group1:
                    self.alliances.append(Alliance(members=group1))
                if group2:
                    self.alliances.append(Alliance(members=group2))
                # Assign points equal to size of NEW alliance for each member
                for g in (group1, group2):
                    s = len(g)
                    for m in g:
                        self.countries[m].points = s if s >= 2 else 1
                return f"Alliance split into two groups: [{', '.join(sorted(group1))}] and [{', '.join(sorted(group2))}]."

        defender_name = random.choice(candidates)
        defender = self.countries[defender_name]

        # Success chance = AttackerPoints / DefenderPoints
        # If defender points are 0 (shouldn't happen), treat as auto-win
        p_att = max(0.0, attacker.points)
        p_def = max(1e-9, defender.points)
        success_prob = min(1.0, p_att / p_def)
        win = random.random() < success_prob

        if win:
            outcome = self._resolve_conquest(attacker.name, defender_name)
            return f"WAR: {attacker.name} attacks {defender_name} → SUCCESS. {outcome}"
        else:
            return f"WAR: {attacker.name} attacks {defender_name} → FAIL."

    def _resolve_conquest(self, attacker: str, defender: str) -> str:
        """Attacker conquers defender. Merge provinces, transfer borders, record subjugation."""
        A = self.countries[attacker]
        D = self.countries[defender]

        # Remove defender from any alliance it is in
        alln = self.get_alliance_of(defender)
        if alln:
            alln.members.discard(defender)
            self.remove_empty_alliances()

        # Mark defender as subjugated and record its last state (we keep it in dict)
        D.alive = False
        D.overlord = attacker

        # Merge provinces
        A.provinces.extend(D.provinces)
        # Borders: attacker gains defender's neighbors, minus attacker and dead
        A.borders.update({n for n in D.borders if n != attacker and self.countries[n].alive})
        # Everyone who had borders with defender now borders attacker instead
        for n in list(D.borders):
            if n == attacker:
                continue
            if self.countries[n].alive:
                self.countries[n].borders.discard(defender)
                self.countries[n].borders.add(attacker)
        # Defender loses its borders
        D.borders.clear()

        # Normalize borders
        self.normalize_borders()

        return f"{defender} is conquered by {attacker}."

    def action_rebellion(self) -> Optional[str]:
        """Attempt a rebellion per rules. Only allowed up to turn 100 (handled in run loop)."""
        alive = self.alive_countries()
        if not alive:
            return None

        # Pick a random country to experience rebellion pressure
        host = random.choice(alive)

        # Rebellion success chance = 1 / (points per country + 1) for the host
        p = 1.0 / (host.points + 1.0)
        success = random.random() < p
        if not success:
            return f"REBELLION in {host.name} fails."

        # If success:
        # 1) If host has conquered countries → one of them gains independence
        subjugated = [c for c in self.countries.values() if (not c.alive and c.overlord == host.name)]
        if subjugated:
            to_free = random.choice(subjugated)
            return self._restore_independence(to_free)

        # 2) Else pick a province inside the country and give independence
        if host.provinces:
            prov = random.choice(host.provinces)
            host.provinces.remove(prov)
            new_name = f"{prov} of {host.name}"
            prov = f"Rebel Group"
            # Borders: for simplicity, inherit the host's current borders + host itself
            new_borders = set(host.borders) | {host.name}
            self._spawn_country(new_name, provinces=[prov], borders=new_borders)
            return f"REBELLION succeeds in {host.name}: '{new_name}' becomes independent."
        else:
            # 3) If no provinces remain, create a generic rebel group
            new_name = f"Splintered Group of {host.name}"
            # Give it a placeholder province
            prov = f"Splintered Group"
            new_borders = set(host.borders) | {host.name}
            self._spawn_country(new_name, provinces=[prov], borders=new_borders)
            return f"REBELLION succeeds in {host.name}: {new_name} emerges."

    def _restore_independence(self, c: CountryState) -> str:
        """Bring a subjugated country back as sovereign, preserving its last known provinces and borders."""
        c.alive = True
        host = c.overlord
        c.overlord = None
        # Remove its provinces from the former overlord
        if host and host in self.countries:
            H = self.countries[host]
            # Remove exactly those province names that belong to c
            taken = set(c.provinces)
            H.provinces = [p for p in H.provinces if p not in taken]
            # Borders: both get each other as neighbors now
            H.borders.add(c.name)
            c.borders.add(H.name)
        # Normalize borders
        self.normalize_borders()
        return f"{c.name} gains independence from {host}."

    def _spawn_country(self, name: str, provinces: List[str], borders: Set[str]):
        """Create a brand new sovereign country."""
        self.countries[name] = CountryState(
            name=name,
            provinces=list(provinces),
            borders=set(borders),
            points=1,
            alive=True,
            overlord=None
        )
        # All neighbors must add this country as a border too
        for nb in borders:
            if nb in self.countries and self.countries[nb].alive:
                self.countries[nb].borders.add(name)
        self.normalize_borders()

    # ---------- Simulation ----------
    def step(self, enable_rebellion: bool = True) -> str:
        """Run a single turn. Returns a human-readable log line."""
        self.turn += 1

        # Decide action
        actions: List[Tuple[str, callable]] = [("Alliance", self.action_alliance),
                                               ("War", self.action_war)]
        if enable_rebellion:
            actions.append(("Rebellion", self.action_rebellion))

        action_name, fn = random.choice(actions)
        msg = fn()
        if msg is None:
            msg = f"{action_name}: no valid move."
        survivors = self.alive_country_names()
        return f"[Turn {self.turn}] {msg}"

    def run(self, verbose: bool = True):
        """Run until 1 sovereign remains. Rebellions disabled after turn 100."""
        logs = []
        while len(self.alive_country_names()) > 1:
            enable_reb = self.turn < 100  # cap rebellions at turn 100 (i.e., disabled from turn 101 onward)
            line = self.step(enable_rebellion=enable_reb)
            if verbose:
                print(line)
            logs.append(line)
        print(f"\nWINNER: {self.alive_country_names()[0]} on turn {self.turn}.")
        return logs

# =========================
# Example setup & run
# =========================

def WorldofBR(seed: Optional[int] = 42) -> World:
    
    countries: Dict[str, CountryState] = {
        "Albania":   CountryState(name="Albania",   provinces=["Shkoder","Kukes","Lezhe","Diber","Durres","Elbasan","Fier","Berat","Korce","Vlore","Gjirokaster","Tirane"], points=1, alive=True),
        "Andorra":  CountryState(name="Andorra",  provinces=["Ordino","Canillo","La Massana","Encamp","Les Escaldes","Sant Julia de Loria"], points=1, alive=True),
        "Austria":    CountryState(name="Austria",    provinces=["Vorarlberg","Tyrol","Salzburg","Carinthia","Styria","Burgenland","Vienna"], points=1, alive=True),
        "Belarus":   CountryState(name="Belarus",   provinces=["Hronda","Brest","Vitsyebsk","Mahilyow","Homyel","Minsk"], points=1, alive=True),
        "Belgium":     CountryState(name="Belgium",     provinces=["West Flanders","East Flanders","Antwerp","Hainaut","Limburg","Liege","Namur","Walloon Brabant","Flemish Brabant","Brussels"], points=1, alive=True),
        "Bosnia":     CountryState(name="Bosnia",     provinces=["Herzegovina","Tropolje","Krajina","Donji Kraji","Glaz","Usora","Soli","Podrinje"], points=1, alive=True),
        "Bulgaria":     CountryState(name="Bulgaria",     provinces=["Burgas","Haskovo","Plovdiv","Varna","Razgrad","Lovech","Montana","Sofia"], points=1, alive=True),
        "Croatia":     CountryState(name="Croatia",     provinces=["Slavonia","Istria","Kvarner","Zadar","Sibenik","Split","Dubrovnik"], points=1, alive=True),
        "Czechia":     CountryState(name="Czechia",     provinces=["Karlovy Vary","Usti nad Labem","Liberec","Plzen","Hradec Kralove","Pardubice","Olomouc","Zlin","Bohemia","Moravia","Prague"], points=1, alive=True),
        "Denmark":     CountryState(name="Denmark",     provinces=["Nordjylland","Midtjylland","Syddanmark","Sjaeland","Hovedstaden"], points=1, alive=True),
        "Estonia":     CountryState(name="Estonia",     provinces=["Saare","Hiiu","Laane","Harju","Rapla","Parnu","Viru","Ida","Jarva","Jogeva","Vilijandi","Tartu","Valga","Polva","Varu"], points=1, alive=True),
        "Finland":     CountryState(name="Finland",     provinces=["Lappi","Oulu","Vaasa","Keskisuomi","Kuopio","Pohjoiskarjala","Mikkeli","Kymi","Hame","Turku ja Pori","Hame","Ahvenanmaa","Uusimaa"], points=1, alive=True),
        "France":     CountryState(name="France",     provinces=["Bretagne","Normandie","Hauts","Grand Est","Pays de la Loire","Centreval de la Loire","Bourgogne Franche Comte","Nouvelle Aquitaine","Auvergne Rhone Alpes","Occitanie","Provence Alpes Cote D Azure","Corse","Ile"], points=1, alive=True),
        "Germany":     CountryState(name="Germany",     provinces=["Schleswig Holstein","Hamburg","Lower Saxony","Bremen","Mecklenburg Vorpommern","Saxony Anhalt","Saxony","Bavaria","Saarland","Baden Wurttemberg","Rhineland Palatinate","Hessen","Thuringia","Brandenberg"], points=1, alive=True),
        "Greece":     CountryState(name="Greece",     provinces=["Crete","Macedonia","Thrace","Thessaly","Epirus","Peloponnese","Ionian Islands","Dodecanese","Cyclades","Sporades","Aegean Islands","Mount Athos","Attica"], points=1, alive=True),
        "Hungary":     CountryState(name="Hungary",     provinces=["Nyugat Dunantul","Kozep Dunantul","Del Dunantul","Eszak Magyarorzag","Eszak Alfold","Del Alfold","Kozep Magyarorzag"], points=1, alive=True),
        "Iceland":     CountryState(name="Iceland",     provinces=["Vestfirdir","Nordurland Vestra","Vesturland","Austurland","Halshreppur","Sudurland","Sudurnes","Hofudborgarsvaedi"], points=1, alive=True),
        "Ireland":     CountryState(name="Ireland",     provinces=["Ulster","Connacht","Leinster","Munster"], points=1, alive=True),
        "Italy":     CountryState(name="Italy",     provinces=["Sicily","Sardinia","Calabria","Basilicata","Campania","Puglia","Molise","Lazio","Abruzzo","Le Marche","Umbria","Tuscany","Liguria","Emilia Romagna","Veneto","Piedmont","Aosta Valley","Lombardy","Trentino Alto Adige","Friuli Venezia Giulia"], points=1, alive=True),
        "Kosovo":     CountryState(name="Kosovo",     provinces=["Mitrovica","Peja","Gjakova","Prizreni","Ferizaji","Gjilani","Prishtina"], points=1, alive=True),
        "Latvia":     CountryState(name="Latvia",     provinces=["Kurzemes","Zemgales","Rigas","Vidzemes","Latgales"], points=1, alive=True),
        "Liechtenstein":     CountryState(name="Liechtenstein",     provinces=["Ruggel","Schellenberg","Gamprin","Mauren","Eschen","Schaan","Balzers","Triesenberg","Vaduz","Triesen"], points=1, alive=True),
        "Lithuania":     CountryState(name="Lithuania",     provinces=["Samogita","Aukstaitija","Sudovia","Dzukija"], points=1, alive=True),
        "Luxembourg":     CountryState(name="Luxembourg",     provinces=["Clerveaux","Wiltz","Vianden","Diekirch","Redange","Mersch","Echternag","Grevenmargen","Capellen","Campagne","Esch Sur Alzette","Remich"], points=1, alive=True),
        "Malta":     CountryState(name="Malta",     provinces=["Gozo","Comino","Knights of Rhodes"], points=1, alive=True),
        "Moldova":     CountryState(name="Moldova",     provinces=["Transistria","Nord","Centru","Sud","Gagauzia","Chisinau"], points=1, alive=True),
        "Monaco":     CountryState(name="Monaco",     provinces=["La Rousse","La Larvotto","Monte-Carlo","Ravin de Sainte-Devote","Les Moneghetti","La Condamine","Monaco-Ville","Jardin Exotique","Fontvieille"], points=1, alive=True),
        "Montenegro":     CountryState(name="Montenegro",     provinces=["Ulcinj","Bar","Budva","Centije","Tivat","Kotor","Herceg Novi","Podgorica","Danilovgard","Niksic","Kolasin","Plav","Andrijevica","Savnik","Pluzine","Zablijak","Pljevlja","Mojkovac","Bijelo Polje","Berane","Rozaje"], points=1, alive=True),
        "Netherlands":     CountryState(name="Netherlands",     provinces=["Friesland","Groningen","Drenthe","Flevoland","Overijssel","Gelderland","Utrecht","Zeeland","Holland"], points=1, alive=True),
        "North Macedonia":     CountryState(name="North Macedonia",     provinces=["Pelagonien","Vardar","Sudwesten","Sudosten","Polog","Osten","Nordosten","Skopje"], points=1, alive=True),
        "Norway":     CountryState(name="Norway",     provinces=["Nordnorge","Trondelag","Vestland","Sorlandet","Ostlandet"], points=1, alive=True),
        "Poland":     CountryState(name="Poland",     provinces=["Pomeranian","Warmian Masurian","Podlachian","Lublin","Subcarpathian","Silesian","Swietokizyskie","Lodz","Opole","Masovian"], points=1, alive=True),
        "Portugal":     CountryState(name="Portugal",     provinces=["Norte","Centro","Oesto e Vale do Tejo","Grande Lisboa","Peninsula de Setubal","Alentejo","Algarve"], points=1, alive=True),
        "Romania":     CountryState(name="Romania",     provinces=["Transilvania","Crisana","Banat","Maramures","Bucovina","Basarabia","Dobrogea","Muntenia","Oltenia"], points=1, alive=True),
        "Russia":     CountryState(name="Russia",     provinces=["Zapadnyy","Tsentralnyy","Yuzhnyy","Kavkazshkiy","Privolzhskiy","Uralskiy","Sibirskiy","Dalnevostochnyy"], points=1, alive=True),
        "San Marino":     CountryState(name="San Marino",     provinces=["Serravalle","Domagnano","Borgo Maggiore","Acquaviva","Faetano","Montegiardino","Fiorentino","Chiesanouva"], points=1, alive=True),
        "Serbia":     CountryState(name="Serbia",     provinces=["Vojvodina","Sumadija","Sesr","Belgrade"], points=1, alive=True),
        "Slovakia":     CountryState(name="Slovakia",     provinces=["Presov","Kosice","Banska Bystrica","Zilina","Trencin","Nitra","Trnava","Bratislava"], points=1, alive=True),
        "Slovenia":     CountryState(name="Slovenia",     provinces=["Prekmurje","Stajerska","Koroska","Gorenjska","Dolenjska","Primorska","Notranjska"], points=1, alive=True),
        "Spain":     CountryState(name="Spain",     provinces=["Catalonia","Aragon","Navara","Basque Country","La Rioja","Cantabria","Asturias","Galicia","Castilla Y Leon","Valencia","Balearic Islands","Andalusia","Extremadura","Castilla la Mancha","Madrid"], points=1, alive=True),
        "Sweden":     CountryState(name="Sweden",     provinces=["Norrland","Svealand","Gotaland","Gotland"], points=1, alive=True),
        "Switzerland":     CountryState(name="Switzerland",     provinces=["Jura","Lake Geneva","Bernese Lowlands","Bernese Oberland","Valais","Ticino","Graubunden","Zurich"], points=1, alive=True),
        "Turkey":     CountryState(name="Turkey",     provinces=["Marmara","Aegean","Anatolia","Black Sea","Mediterranean"], points=1, alive=True),
        "Ukraine":     CountryState(name="Ukraine",     provinces=["Crimea","Donbas","Carpathia","Bukovina","Podolia","Polissia","Transcarpathia","Volhynia"], points=1, alive=True),
        "United Kingdom":     CountryState(name="United Kingdom",     provinces=["Scotland","Wales","Northern Ireland","Yorkshire","Midlands","England","London"], points=1, alive=True),
        "Vatican City":     CountryState(name="Vatican City",     provinces=["Orthodox Sector","Protestant Sector","Anglican Sector","Baptist Sector","Evangelist Sector","Mormon Sector"], points=1, alive=True),
        "Armenia":     CountryState(name="Armenia",     provinces=["Lori","Shirak","Aragatsotn","Tavush","Kotayk","Armariv","Yerevan","Ararat","Gegharkunik","Vayots Dzor","Syunik"], points=1, alive=True),
        "Azerbaijan":     CountryState(name="Azerbaijan",     provinces=["Nakhchivan","Ganja","Sheki","Nagorno Karabakh","Talysh","Baku"], points=1, alive=True),
        "Cyprus":     CountryState(name="Cyprus",     provinces=["Northern Cyprus","Larnaca","Limassol","Paphos","Nicosia"], points=1, alive=True),
        "Georgia":     CountryState(name="Georgia",     provinces=["Abkhazia","Svaneti","Guria","Ajaria","Imereti","Javakheti","Kartli","Mtianeti","Kakheti","Tbilisi"], points=1, alive=True),
        "Kazakhstan":     CountryState(name="Kazakhstan",     provinces=["Atyrau","Mangghystau","Aqtobe","Qostanay","Aqmola","Pavlodar","Qaraghandy","Almaty","Zhambyl","Qyzylorda"], points=1, alive=True),
    }

    borders = {
        "Albania": {"Montenegro","Kosovo","North Macedonia","Greece"},
        "Andorra": {"Spain","France"},
        "Austria": {"Liechtenstein","Italy","Slovenia","Hungary","Slovakia","Czechia","Germany","Switzerland"},
        "Belarus": {"Russia","Ukraine","Poland","Latvia","Lithuania"},
        "Belgium": {"France","Germany","Netherlands","Luxembourg"},
        "Bosnia": {"Croatia","Montenegro","Serbia"},
        "Bulgaria": {"North Macedonia","Greece","Turkey","Serbia","Romania"},
        "Croatia": {"Bosnia","Slovenia","Hungary","Serbia","Montenegro"},
        "Czechia": {"Germany","Austria","Slovakia","Poland"},
        "Denmark": {"Sweden","Germany"},
        "Estonia": {"Finland","Latvia","Russia"},
        "Finland": {"Norway","Sweden","Estonia","Russia"},
        "France": {"Monaco","Andorra","Italy","Switzerland","Belgium","Luxembourg","Germany","United Kingdom"},
        "Germany": {"Denmark","Poland","Czechia","Austria","Switzerland","France","Luxembourg","Belgium","Netherlands"},
        "Greece": {"Albania","North Macedonia","Bulgaria","Turkey"},
        "Hungary": {"Serbia","Croatia","Slovenia","Austria","Slovakia","Ukraine","Romania"},
        "Iceland": {"Ireland","United Kingdom","Norway"},
        "Ireland": {"Iceland","United Kingdom"},
        "Italy": {"France","Switzerland","Austria","Slovenia","San Marino","Vatican City","Malta"},
        "Kosovo": {"Albania","Montenegro","Serbia","Bulgaria","North Macedonia"},
        "Latvia": {"Estonia","Russia","Lithuania","Belarus"},
        "Liechtenstein": {"Switzerland","Austria"},
        "Lithuania": {"Russia","Latvia","Poland","Belarus"},
        "Luxembourg": {"Belgium","Germany","France"},
        "Malta": {"Italy"},
        "Moldova": {"Romania","Ukraine"},
        "Monaco": {"France"},
        "Montenegro": {"Croatia","Bosnia","Albania","Serbia","Kosovo"},
        "Netherlands": {"Belgium","Germany"},
        "North Macedonia": {"Albania","Kosovo","Serbia","Bulgaria","Greece"},
        "Norway": {"Finland","Sweden","Iceland"},
        "Poland": {"Russia","Lithuania","Belarus","Ukraine","Slovakia","Czechia","Germany"},
        "Portugal": {"Spain"},
        "Romania": {"Bulgaria","Serbia","Hungary","Ukraine","Moldova"},
        "Russia": {"Finland","Estonia","Latvia","Belarus","Ukraine","Georgia","Azerbaijan","Kazakhstan","Poland"},
        "San Marino": {"Italy"},
        "Serbia": {"Kosovo","Montenegro","Bosnia","Croatia","Hungary","Romania","Bulgaria"},
        "Slovakia": {"Hungary","Austria","Czechia","Poland","Ukraine"},
        "Slovenia": {"Italy","Austria","Hungary","Croatia"},
        "Spain": {"Portugal","France","Andorra"},
        "Sweden": {"Denmark","Norway","Finland"},
        "Switzerland": {"Italy","France","Germany","Austria","Liechtenstein"},
        "Turkey": {"Greece","Bulgaria","Cyprus","Georgia","Armenia","Azerbaijan"},
        "Ukraine": {"Belarus","Russia","Moldova","Romania","Hungary","Slovakia","Poland"},
        "United Kingdom": {"Ireland","France","Iceland"},
        "Vatican City": {"Italy"},
        "Armenia": {"Georgia","Azerbaijan","Turkey"},
        "Azerbaijan": {"Armenia","Turkey","Georgia","Russia"},
        "Cyprus": {"Turkey"},
        "Georgia": {"Azerbaijan","Russia","Armenia","Turkey"},
        "Kazakhstan": {"Russia"},
    }

    for name, bs in borders.items():
        countries[name].borders = set(bs)

    world = World(countries=countries, alliances=[], seed=seed)
    world.normalize_borders()
    return world

if __name__ == "__main__":
    world = WorldofBR(seed=None)
    world.run(verbose=True)
