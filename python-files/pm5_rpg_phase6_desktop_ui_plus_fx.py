
# PM5-Powered RPG — Phase 6 Desktop (UI+FX)
# -----------------------------------------
# Adds:
# - Health bars for hero and current enemy (in combat panel + above sprites)
# - Floating numbers for damage/heal/guard (rise and fade above entities)
# - Keeps: minimap, inventory compare, font fallbacks, PM5/BLE support
#
# Run:
#   pip install pygame bleak
#   python pm5_rpg_phase6_desktop_ui_plus_fx.py

import os, sys, time, json, random, asyncio, threading, collections
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict
from copy import deepcopy

try:
    import pygame
except Exception:
    pygame = None

try:
    from bleak import BleakClient, BleakScanner, BleakError
except Exception:
    BleakClient = BleakScanner = None
    class BleakError(Exception): pass

# -------------------- Config -------------------------------------------------
WIDTH, HEIGHT = 1280, 800
MAP_COLS, MAP_ROWS = 32, 20
TILE_SIZE = 32
SIDEBAR_W = 520
FPS = 60

STEP_BASE = 0.9
STEP_SCALE = 0.0035
STEP_MIN = 0.15
STEP_MAX = 1.2

PM5_MODE = "auto"   # "auto" | "force" | "off"
SIM_RANGE = (70, 220)
SIM_INTERVAL = (0.8, 1.6)

# Tile IDs
WALL=1; FLOOR=0; EXIT=2; SHRINE=3; TRAP=4; START=5

# Colors
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(70,70,70); LIGHT_GRAY=(180,180,180)
DARK=(18,18,18); GREEN=(60,200,100); RED=(220,60,60); BLUE=(90,160,255)
GOLD=(235,200,60); PURPLE=(145,90,200); ORANGE=(235,180,60)

# Diablo-like rarity colors
RARITY_COLORS={
    "normal":LIGHT_GRAY,
    "magic":BLUE,
    "rare":ORANGE,
    "set":GREEN,
    "unique":GOLD,
    "common":LIGHT_GRAY,  # compatibility
    "epic":PURPLE,
    "legendary":GOLD,
}

# -------------------- Loot Tables (simplified) -------------------------------
BASE_WEAPONS = [
    ("Dagger", 7, 12, 16),
    ("Short Sword", 9, 14, 22),
    ("Long Sword", 12, 18, 28),
    ("War Axe", 14, 22, 34),
]
BASE_ARMORS = [
    ("Leather Armor", 7, 10, 18),
    ("Scale Mail", 10, 14, 24),
    ("Plate Mail", 12, 18, 30),
    ("Dragon Mail", 16, 22, 36),
]

PREFIXES = [
    ("Sturdy",      {"def": 2, "max_hp": 10}),
    ("Fortified",   {"def": 4, "max_hp": 18}),
    ("Sharp",       {"atk": 3}),
    ("Deadly",      {"atk": 6}),
    ("Fiery",       {"atk": 3, "w_mult": 3}),
    ("Frozen",      {"atk": 3, "w_mult": 2}),
    ("Arcane",      {"max_mana": 12}),
    ("Vampiric",    {"atk": 2, "max_hp": 6}),
]
SUFFIXES = [
    ("of the Fox",     {"max_hp": 12}),
    ("of the Bear",    {"max_hp": 22}),
    ("of the Titan",   {"atk": 5}),
    ("of Thorns",      {"def": 3}),
    ("of Focus",       {"max_mana": 14}),
    ("of Haste",       {"w_mult": 6}),
]

UNIQUE_ITEMS = [
    ("The Butcher's Cleaver", "weapon", 26, 0, {"atk": 10, "w_mult": 8}),
    ("Skin of the Vipermagi", "armor", 0, 22, {"def": 8, "max_mana": 20}),
    ("Arreat's Edge", "weapon", 30, 0, {"atk": 12, "max_hp": 20}),
]

# -------------------- Data Models -------------------------------------------
@dataclass
class SetBonus:
    set_name: str
    thresholds: Dict[int, Dict[str, int]]
    def total_bonus(self, pieces:int)->Dict[str,int]:
        bonus={}
        for t in sorted(self.thresholds.keys()):
            if pieces >= t:
                for k,v in self.thresholds[t].items():
                    bonus[k] = bonus.get(k,0)+v
        return bonus

@dataclass
class Item:
    name:str
    slot:str             # weapon/armor/consumable
    power:int=0
    defense:int=0
    heal:int=0
    rarity:str="normal"  # normal/magic/rare/set/unique
    price:int=0
    set_name:Optional[str]=None
    biome_tag:Optional[str]=None
    ilvl:int=1
    req_level:int=1
    prefix:Optional[str]=None
    suffix:Optional[str]=None
    mods:Dict[str,int]=field(default_factory=dict)
    unique_key:Optional[str]=None
    def tooltip(self)->List[str]:
        tips=[f"{self.name} [{self.rarity}]  (req {self.req_level})"]
        if self.slot=="weapon": tips.append(f"Base ATK +{self.power}")
        if self.slot=="armor": tips.append(f"Base DEF +{self.defense}")
        for k in ["atk","def","max_hp","max_mana","w_mult"]:
            v=self.mods.get(k,0)
            if v:
                label = {"atk":"ATK","def":"DEF","max_hp":"Max HP","max_mana":"Max Mana","w_mult":"W Mult %"}[k]
                tips.append(f"{label} +{v}")
        if self.slot=="consumable" and self.heal:
            tips.append(f"Heal {self.heal} HP")
        if self.set_name: tips.append(f"Set: {self.set_name}")
        if self.price: tips.append(f"Value: {self.price}c")
        if self.biome_tag: tips.append(f"Biome: {self.biome_tag}")
        return tips

@dataclass
class Ability:
    key:str; name:str; cost:int; power:int; kind:str="damage"; cooldown:int=2; cd_remaining:int=0

@dataclass
class Monster:
    name:str; hp:int; atk:int; pos:Tuple[int,int]; guard:bool=False; elem:str="phys"; boss:bool=False
    max_hp:int=0
    def __post_init__(self):
        if not self.max_hp or self.max_hp <= 0:
            self.max_hp = self.hp
    def alive(self)->bool: return self.hp>0

@dataclass
class Quest:
    id:int; text:str; goal:str; target:str; needed:int=1; progress:int=0; completed:bool=False

@dataclass
class Achievement:
    key:str; text:str; unlocked:bool=False; when:str=""

@dataclass
class Hero:
    x:int=1; y:int=1
    hp:int=100; max_hp:int=100
    level:int=1; xp:int=0
    base_atk:int=0; base_def:int=0
    mana:int=100; max_mana:int=100; coins:int=60
    step_cooldown:float=STEP_MAX; stride_dir:Tuple[int,int]=(0,0)
    inventory:List[Item]=field(default_factory=list)
    weapon:Optional[Item]=None; armor:Optional[Item]=None
    abilities:Dict[str,Ability]=field(default_factory=dict)
    set_bonuses:Dict[str,SetBonus]=field(default_factory=dict)
    history:List[str]=field(default_factory=list)
    quests:List[Quest]=field(default_factory=list)
    achievements:Dict[str,Achievement]=field(default_factory=dict)
    title:str="Novice"

    def log(self,msg:str):
        self.history.append(msg)
        if len(self.history)>14: self.history.pop(0)

    def pieces_in_set(self, sname:str)->int:
        cnt=0
        for it in [self.weapon, self.armor]:
            if it and it.set_name==sname: cnt+=1
        return cnt

    def aggregate_set_bonuses(self)->Dict[str,int]:
        total={}
        for sname,sb in self.set_bonuses.items():
            b=sb.total_bonus(self.pieces_in_set(sname))
            for k,v in b.items(): total[k]=total.get(k,0)+v
        return total

    def item_mod_total(self, key:str)->int:
        total=0
        for it in (self.weapon, self.armor):
            if it and it.mods: total += it.mods.get(key,0)
        return total

    def effective_max_hp(self)->int:
        return self.max_hp + self.aggregate_set_bonuses().get("max_hp",0) + self.item_mod_total("max_hp")

    def effective_max_mana(self)->int:
        return self.max_mana + self.aggregate_set_bonuses().get("max_mana",0) + self.item_mod_total("max_mana")

    def attack_power(self)->int:
        base = 8 + self.base_atk + (self.weapon.power if self.weapon else 0)
        base += self.item_mod_total("atk")
        sets=self.aggregate_set_bonuses()
        base+=sets.get("atk",0)
        return base

    def defense(self)->int:
        base = self.base_def + (self.armor.defense if self.armor else 0)
        base += self.item_mod_total("def")
        sets=self.aggregate_set_bonuses()
        return base+sets.get("def",0)

    def watts_multiplier(self)->float:
        sets=self.aggregate_set_bonuses()
        item_w = self.item_mod_total("w_mult")
        return 1.0 + (sets.get("w_mult",0)/100.0) + (item_w/100.0)

    def equip(self,item:Item)->Optional[Item]:
        prev=None
        if item.slot=="weapon":
            prev=self.weapon; self.weapon=item
        elif item.slot=="armor":
            prev=self.armor; self.armor=item
        self.log(f"Equipped {item.name} [{item.rarity}]")
        self.hp=min(self.hp, self.effective_max_hp())
        self.mana=min(self.mana, self.effective_max_mana())
        return prev

    def consume(self, idx:int)->str:
        if not(0<=idx<len(self.inventory)): return "Invalid index."
        it=self.inventory[idx]
        if it.slot!="consumable": return "Not a consumable."
        self.hp=min(self.effective_max_hp(),self.hp+it.heal); self.inventory.pop(idx)
        return f"Used {it.name}. (+{it.heal} HP)"

    def add_power(self,watts:int):
        watts=int(watts*self.watts_multiplier())
        self.power=max(0,watts)
        cd=STEP_BASE-self.power*STEP_SCALE
        self.step_cooldown=max(STEP_MIN,min(STEP_MAX,cd))

    def init_default_abilities(self):
        self.abilities={
            "1":Ability("1","Power Strike",15,18,"damage",2),
            "2":Ability("2","Guard",10,0,"guard",3),
            "3":Ability("3","Heal",20,22,"heal",3),
            "4":Ability("4","Cyclone",25,26,"damage",4),
        }

    def xp_to_next(self)->int: return 40 + 20*(self.level**2)
    def gain_xp(self, amount:int)->int:
        levels=0; self.xp += amount
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next(); self.level += 1; levels += 1
            self.max_hp += 10; self.max_mana += 5; self.base_atk += 1; self.base_def += 1
            self.hp = self.effective_max_hp(); self.mana = self.effective_max_mana()
            if self.level==3: self.title="Adventurer"
            elif self.level==5: self.title="Champion"
            elif self.level==8: self.title="Boss-Slayer"
            elif self.level>=12: self.title="Mythic"
        return levels

    def add_quest(self, q:Quest):
        if not any(qq.id==q.id for qq in self.quests):
            self.quests.append(q); self.log(f"Quest added: {q.text}")
    def check_quest(self, goal:str, target:str, amount:int=1):
        updated=False
        for q in self.quests:
            if q.completed: continue
            if q.goal==goal and (q.target==target or q.target=="*"):
                q.progress += amount
                if q.progress>=q.needed:
                    q.completed=True; self.log(f"Quest complete: {q.text}"); updated=True
        return updated
    def grant_achievement(self, key:str, text:str):
        ach=self.achievements.get(key)
        if ach and ach.unlocked: return
        self.achievements[key]=Achievement(key,text,True,when=time.strftime("%Y-%m-%d %H:%M:%S"))
        self.log(f"🏅 Achievement unlocked: {text}")

# -------------------- World / Items -----------------------------------------
@dataclass
class Zone:
    key:str; name:str
    color:Tuple[int,int,int]
    dungeon_size:Tuple[int,int]
    wall_density:float
    monster_table:List[str]
    shop_bias:str
    set_drops:List[Item]

def mk_item(name,slot,**kw): return Item(name,slot,**kw)

SET_BONUSES={
    "Storm":   SetBonus("Storm",{2:{"atk":4,"w_mult":10}}),
    "Dragon":  SetBonus("Dragon",{2:{"atk":5,"def":3}, 3:{"atk":10,"def":6,"max_hp":20,"max_mana":10,"w_mult":15}}),
    "Frost":   SetBonus("Frost",{2:{"def":4}, 3:{"def":8,"w_mult":8}}),
    "Inferno": SetBonus("Inferno",{2:{"atk":6}, 3:{"atk":12,"w_mult":12}}),
}

FROST_ITEMS=[ mk_item("Frost Brand","weapon",power=15,price=40,rarity="set",set_name="Frost",biome_tag="Ruins"),
              mk_item("Frost Guard","armor",defense=12,price=34,rarity="set",set_name="Frost",biome_tag="Ruins") ]
INFERNO_ITEMS=[ mk_item("Inferno Saber","weapon",power=16,price=42,rarity="set",set_name="Inferno",biome_tag="Cavern"),
                mk_item("Inferno Plate","armor",defense=11,price=36,rarity="set",set_name="Inferno",biome_tag="Cavern") ]

BASE_STOCK=[
    mk_item("Potion","consumable",heal=25,price=8,rarity="normal"),
    mk_item("Mega Potion","consumable",heal=50,price=18,rarity="magic"),
    mk_item("Iron Sword","weapon",power=10,price=20,rarity="normal"),
    mk_item("Steel Armor","armor",defense=10,price=22,rarity="normal"),
] + FROST_ITEMS + INFERNO_ITEMS

ZONES=[
    Zone("town","Hearthvale", (60,60,120), (42,30), 0.12, ["Rat","Thug","Bandit"], "neutral", []),
    Zone("forest","Dark Forest", (30,70,40), (46,32), 0.16, ["Wolf","Spider","Bandit","Wraith"], "poison", [FROST_ITEMS[0], FROST_ITEMS[1]]),
    Zone("ruins","Frozen Ruins", (60,90,120), (46,32), 0.18, ["Ice Bat","Wraith","Skeleton"], "cold", FROST_ITEMS),
    Zone("cavern","Volcanic Cavern", (120,70,40), (48,34), 0.20, ["Imp","Orc","Fire Wisp"], "fire", INFERNO_ITEMS),
]

RARITY_PRICE_MULT={"normal":1.0,"magic":1.3,"rare":1.7,"set":2.0,"unique":2.2,"epic":1.6,"legendary":2.0}

def roll_affixes(ilvl:int, want:int)->Tuple[Optional[str], Optional[str], Dict[str,int]]:
    mods={}; prefix=None; suffix=None
    cand_prefix = PREFIXES.copy(); cand_suffix = SUFFIXES.copy()
    random.shuffle(cand_prefix); random.shuffle(cand_suffix)
    take_p = 1 if want>=1 else 0; take_s = 1 if want>=2 else 0
    if want>=3 and random.random()<0.5:
        if random.random()<0.5: take_p+=1
        else: take_s+=1
    if take_p>0:
        prefix = cand_prefix[0][0]
        for k,v in cand_prefix[0][1].items(): mods[k]=mods.get(k,0)+v
        if take_p>1 and len(cand_prefix)>1:
            for k,v in cand_prefix[1][1].items(): mods[k]=mods.get(k,0)+v
            prefix = cand_prefix[1][0] + " " + prefix
    if take_s>0:
        suffix = cand_suffix[0][0]
        for k,v in cand_suffix[0][1].items(): mods[k]=mods.get(k,0)+v
        if take_s>1 and len(cand_suffix)>1:
            for k,v in cand_suffix[1][1].items(): mods[k]=mods.get(k,0)+v
            suffix = suffix + " & " + cand_suffix[1][0]
    return prefix, suffix, mods

def price_from_stats(base_price:int, rarity:str, mods:Dict[str,int])->int:
    mod_score = abs(mods.get("atk",0))*2 + abs(mods.get("def",0))*2 + abs(mods.get("max_hp",0))*0.6 + abs(mods.get("max_mana",0))*0.6 + abs(mods.get("w_mult",0))*1.5
    return int(base_price * RARITY_PRICE_MULT.get(rarity,1.0) * (1.0 + mod_score/40.0))

def roll_base(slot:str, dlvl:int)->Tuple[str,int,int,int]:
    if slot=="weapon":
        name, low, mid, high = random.choice(BASE_WEAPONS)
        power = random.randint(mid, high) + dlvl//4
        return name, power, 0, 18 + dlvl
    else:
        name, low, mid, high = random.choice(BASE_ARMORS)
        defense = random.randint(mid, high) + dlvl//4
        return name, 0, defense, 18 + dlvl

def roll_loot(dlvl:int, zone:Zone, boss:bool=False)->Item:
    w_normal=58; w_magic=28; w_rare=10; w_set=2; w_unique=2
    bump = min(18, dlvl//3)
    w_magic += bump; w_rare += bump//2
    if boss:
        w_magic += 8; w_rare += 6; w_set += 3; w_unique += 3
    tiers=["normal","magic","rare","set","unique"]
    rarity = random.choices(tiers, weights=[w_normal,w_magic,w_rare,w_set,w_unique], k=1)[0]

    slot = "weapon" if random.random()<0.55 else "armor"
    bname, base_power, base_def, base_price = roll_base(slot, dlvl)
    ilvl = max(1, dlvl + random.randint(-1,2)); req = max(1, min(20, 1 + dlvl//2))

    if rarity=="set" and zone.set_drops:
        proto = deepcopy(random.choice(zone.set_drops))
        proto.ilvl=ilvl; proto.req_level=req; proto.rarity="set"
        proto.price = price_from_stats(proto.price or base_price, "set", proto.mods if proto.mods else {})
        return proto

    if rarity=="unique" and UNIQUE_ITEMS:
        u = random.choice([u for u in UNIQUE_ITEMS if u[1]==slot])
        name, _, pwr, deff, mods = u
        it = Item(name, slot, power=pwr, defense=deff, rarity="unique", price=base_price, ilvl=ilvl, req_level=req, mods=mods.copy(), unique_key=name)
        it.price = price_from_stats(it.price, "unique", it.mods)
        return it

    want = 0 if rarity=="normal" else (1 if rarity=="magic" else random.choice([2,3]))
    pre, suf, mods = roll_affixes(ilvl, want)
    full_name = f"{pre+' ' if pre else ''}{bname}{' '+suf if suf else ''}"
    it = Item(full_name, slot, power=base_power, defense=base_def, rarity=rarity, price=base_price, ilvl=ilvl, req_level=req, prefix=pre, suffix=suf, mods=mods, biome_tag=zone.key)
    it.price = price_from_stats(it.price, rarity, mods)
    return it

# -------------------- Dungeon -------------------------------------------------
class Dungeon:
    def __init__(self,w:int,h:int, level:int, zone:Zone):
        self.w=w; self.h=h; self.level=level; self.zone=zone
        self.grid=[[1 for _ in range(w)] for _ in range(h)]
        self.fog=[[True for _ in range(w)] for _ in range(h)]
        self.exit_pos=(w-2,h-2)
        self.monsters:List[Monster]=[]
        self.generate()

    def generate(self):
        x,y=1,1; self.grid[y][x]=FLOOR; self.grid[1][1]=START
        for _ in range(self.w*self.h//2):
            dx,dy=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            x=min(self.w-2,max(1,x+dx)); y=min(self.h-2,max(1,y+dy))
            self.grid[y][x]=FLOOR
        for yy in range(1,self.h-1):
            for xx in range(1,self.w-1):
                if random.random()<(1.0-self.zone.wall_density): self.grid[yy][xx]=FLOOR
        for _ in range(8):
            ex,ey=random.randint(2,self.w-3),random.randint(2,self.h-3)
            if self.grid[ey][ex]==FLOOR: self.grid[ey][ex]=random.choice([SHRINE,TRAP])
        ex,ey=self.exit_pos; self.grid[ey][ex]=EXIT
        self.ensure_exit_reachable()
        boss_spawned=False
        if self.level % 5 == 0:
            for _t in range(120):
                bx,by=random.randint(2,self.w-3),random.randint(2,self.h-3)
                if self.grid[by][bx] in (FLOOR,TRAP,SHRINE):
                    self.monsters.append(Monster(
                        name=random.choice(["Minotaur","Lich","Wyvern","Fire Titan"]),
                        hp=120+self.level*20, atk=16+self.level*3,
                        pos=(bx,by), boss=True, elem=random.choice(["fire","cold","poison","phys"])
                    )); boss_spawned=True; break
        for _ in range(6 + self.level + (2 if boss_spawned else 0)):
            for _t in range(60):
                mx,my=random.randint(1,self.w-2),random.randint(1,self.h-2)
                if self.grid[my][mx] in (FLOOR,TRAP,SHRINE,START):
                    base=random.choice(self.zone.monster_table)
                    hp=random.randint(34,68)+self.level*7; atk=random.randint(6,13)+self.level
                    elem=random.choice(["phys","cold","fire","poison"])
                    self.monsters.append(Monster(base,hp,atk,(mx,my),False,elem,False)); break

    def ensure_exit_reachable(self):
        start=(1,1); goal=self.exit_pos
        q=collections.deque([start]); prev={start:None}
        while q:
            x,y=q.popleft()
            if (x,y)==goal: break
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx,ny=x+dx,y+dy
                if 0<=nx<self.w and 0<=ny<self.h and (nx,ny) not in prev and self.grid[ny][nx]!=WALL:
                    prev[(nx,ny)]=(x,y); q.append((nx,ny))
        if goal not in prev:
            x,y=start
            while (x,y)!=goal:
                if x<goal[0]: x+=1
                elif x>goal[0]: x-=1
                elif y<goal[1]: y+=1
                elif y>goal[1]: y-=1
                if self.grid[y][x]==WALL: self.grid[y][x]=FLOOR
    def in_bounds(self,x:int,y:int)->bool: return 0<=x<self.w and 0<=y<self.h
    def is_walkable(self,x:int,y:int)->bool: return self.in_bounds(x,y) and self.grid[y][x] in (FLOOR,EXIT,TRAP,SHRINE,START)
    def reveal_radius(self,x:int,y:int,r:int=4):
        for yy in range(y-r,y+r+1):
            for xx in range(x-r,x+r+1):
                if self.in_bounds(xx,yy): self.fog[yy][xx]=False

# -------------------- Shop ---------------------------------------------------
class Shop:
    def __init__(self, hero:"Hero", zone:Zone):
        self.hero=hero; self.zone=zone
        self.stock:List[Item]=[]; self.restock_cost=8
        self.roll_stock()
    def pick_zone_items(self)->List[Item]:
        pool = [it for it in BASE_STOCK if it.biome_tag in (None,self.zone.name,self.zone.key,"Town")]
        pool += self.zone.set_drops; return pool
    def roll_stock(self):
        self.stock.clear()
        for _ in range(3):
            it = roll_loot(dlvl=1, zone=self.zone, boss=False); self.stock.append(it)
        pool=self.pick_zone_items()
        take=min(6-len(self.stock),len(pool))
        chosen=random.sample(pool,k=take) if take>0 else []
        for proto in chosen:
            it=deepcopy(proto)
            it.price=int((it.price or 12)*RARITY_PRICE_MULT.get(it.rarity,1.0))
            self.stock.append(it)
    def restock(self)->str:
        if self.hero.coins < self.restock_cost: return "Not enough coins to restock."
        self.hero.coins-=self.restock_cost; self.roll_stock(); return f"Shop restocked for {self.restock_cost}c."
    def buy(self, idx:int)->str:
        if not(0<=idx<len(self.stock)): return "Invalid item."
        it=self.stock[idx]
        if self.hero.level < it.req_level: return f"Requires level {it.req_level}."
        if self.hero.coins<it.price: return "Not enough coins."
        self.hero.coins-=it.price
        if it.slot=="consumable": self.hero.inventory.append(it)
        else:
            prev=self.hero.equip(it)
            if prev: self.hero.inventory.append(prev)
        self.hero.check_quest("buy","*")
        return f"Bought {it.name} for {it.price}c."
    def sell_value(self, it:Item)->int: return max(1,int(0.45*max(1,it.price)))

# -------------------- Sprite Factory ----------------------------------------
class SpriteFactory:
    def __init__(self): self.cache={}
    def _surf(self, w=TILE_SIZE, h=TILE_SIZE, color=(50,50,50)):
        s=pygame.Surface((w,h), pygame.SRCALPHA); s.fill(color); return s
    def tile_floor(self, tint):
        key=("floor",tint)
        if key in self.cache: return self.cache[key]
        s=self._surf()
        for y in range(0,TILE_SIZE,4):
            for x in range(0,TILE_SIZE,4):
                c=(tint[0]+(x%8)*2, tint[1]+(y%8)*2, tint[2]+((x+y)%8))
                c=tuple(max(0,min(255,v)) for v in c)
                pygame.draw.rect(s, c, (x,y,4,4))
        self.cache[key]=s; return s
    def tile_wall(self, tint):
        key=("wall",tint)
        if key in self.cache: return self.cache[key]
        s=self._surf()
        base=(max(0,tint[0]-44), max(0,tint[1]-44), max(0,tint[2]-44)); s.fill(base)
        for y in range(0,TILE_SIZE,8):
            for x in range(0,TILE_SIZE,8):
                pygame.draw.rect(s, (base[0]+10,base[1]+10,base[2]+10), (x+1,y+1,6,6), 1)
        self.cache[key]=s; return s
    def tile_special(self, kind):
        key=("special",kind)
        if key in self.cache: return self.cache[key]
        s=self._surf()
        if kind=="exit":
            pygame.draw.rect(s,(40,120,40),(0,0,TILE_SIZE,TILE_SIZE))
            pygame.draw.rect(s,(80,180,80),(6,6,TILE_SIZE-12,TILE_SIZE-12),2)
        elif kind=="shrine":
            s.fill((60,40,100)); pygame.draw.circle(s,(180,160,240),(TILE_SIZE//2,TILE_SIZE//2),10)
        elif kind=="trap":
            s.fill((120,60,60))
            for i in range(4): pygame.draw.line(s,(220,180,180),(4,4+i*6),(TILE_SIZE-4,TILE_SIZE-4-i*6),1)
        elif kind=="start":
            s.fill((60,60,140))
            pygame.draw.polygon(s,(180,180,240),[(8,TILE_SIZE-8),(TILE_SIZE//2,8),(TILE_SIZE-8,TILE_SIZE-8)],2)
        self.cache[key]=s; return s
    def hero(self, frame=0):
        key=("hero",frame)
        if key in self.cache: return self.cache[key]
        s=self._surf(); body=(220,230,120); edge=(40,40,40)
        pygame.draw.rect(s, body, (4,6,TILE_SIZE-8,TILE_SIZE-8))
        pygame.draw.rect(s, edge, (4,6,TILE_SIZE-8,TILE_SIZE-8),2)
        eye_y=10 if frame%2==0 else 11
        pygame.draw.circle(s, BLACK, (TILE_SIZE//2-4, eye_y), 2)
        pygame.draw.circle(s, BLACK, (TILE_SIZE//2+4, eye_y), 2)
        self.cache[key]=s; return s
    def monster(self, boss=False, frame=0):
        key=("mon",boss,frame)
        if key in self.cache: return self.cache[key]
        s=self._surf(); color=ORANGE if boss else PURPLE
        pygame.draw.rect(s, color, (6,6,TILE_SIZE-12,TILE_SIZE-12))
        eye_w=6 if frame%4!=0 else 2; pygame.draw.rect(s, BLACK, (TILE_SIZE//2-eye_w//2, 10, eye_w, 3))
        self.cache[key]=s; return s

# -------------------- Renderer (UI + FX) -------------------------------------
class Renderer:
    def __init__(self):
        if pygame is None: raise RuntimeError("pygame required (pip install pygame)")
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH+SIDEBAR_W,HEIGHT))
        pygame.display.set_caption("PM5 Dungeon — Phase 6 (Desktop UI+FX)")
        self.clock=pygame.time.Clock()
        # Font fallbacks
        try:
            self.font=pygame.font.SysFont("consolas",18)
            self.font_big=pygame.font.SysFont("consolas",26)
            self.font_small=pygame.font.SysFont("consolas",16)
        except Exception:
            self.font=pygame.font.Font(None,18)
            self.font_big=pygame.font.Font(None,26)
            self.font_small=pygame.font.Font(None,16)
        self.toast_timer=0; self.toast_text=""
        self.sf=SpriteFactory(); self.frame=0
        self.pm5_status="Starting…"
        self.hinted_start=False
        self.fog_tile=pygame.Surface((TILE_SIZE,TILE_SIZE)); self.fog_tile.set_alpha(150); self.fog_tile.fill(BLACK)
        # FX: floating texts
        self.float_texts=[]  # list of dicts: {'x','y','off','life','text','color','size'}

    # ---- FX helpers
    def add_float(self, grid_pos:Tuple[int,int], text:str, color:Tuple[int,int,int], size:str="normal", life:int=45):
        gx,gy=grid_pos
        self.float_texts.append({
            "x":gx, "y":gy, "off":0.0, "life":life, "text":text, "color":color, "size":size
        })

    def draw_floats(self, camera:Tuple[int,int]):
        cx,cy=camera
        next_list=[]
        for ft in self.float_texts:
            life=ft["life"]
            if life<=0: continue
            gx,gy=ft["x"],ft["y"]
            # screen pos center of tile
            sx=(gx-cx)*TILE_SIZE + TILE_SIZE//2
            sy=(gy-cy)*TILE_SIZE + 6 + int(-ft["off"])
            # choose font size
            f = self.font_big if ft["size"]=="big" else self.font
            # fade alpha as life drains
            alpha = max(40, min(255, int(255 * (life/60.0))))
            txtsurf=f.render(ft["text"], True, ft["color"])
            # apply manual alpha by copying onto surface with alpha
            surf = pygame.Surface(txtsurf.get_size(), pygame.SRCALPHA)
            surf.fill((255,255,255,0))
            surf.blit(txtsurf,(0,0))
            surf.set_alpha(alpha)
            self.screen.blit(surf,(sx - txtsurf.get_width()//2, sy - txtsurf.get_height()))
            # update
            ft["off"] += 0.7
            ft["life"] -= 1
            if ft["life"]>0: next_list.append(ft)
        self.float_texts = next_list

    def draw_entity_bar(self, gx:int, gy:int, ratio:float, color=(60,200,100)):
        # draw a small bar above the tile at (gx,gy) in map coords
        r=max(0.0,min(1.0,ratio))
        w=28; h=5
        x = gx*TILE_SIZE + (TILE_SIZE - w)//2
        y = gy*TILE_SIZE - 6
        pygame.draw.rect(self.screen, (30,30,30), (x, y, w, h))
        pygame.draw.rect(self.screen, color, (x+1, y+1, int((w-2)*r), h-2))

    def draw_map(self, dungeon:"Dungeon", hero:"Hero", camera:Tuple[int,int], in_combat:bool=False, enemy:Optional["Monster"]=None):
        cx,cy=camera; vis_w,vis_h=MAP_COLS,MAP_ROWS
        # tiles + fog
        for ry in range(vis_h):
            for rx in range(vis_w):
                tx,ty=cx+rx,cy+ry
                if not dungeon.in_bounds(tx,ty): continue
                cell=dungeon.grid[ty][tx]; tint=dungeon.zone.color
                if cell==WALL: tile=self.sf.tile_wall(tint)
                elif cell==FLOOR: tile=self.sf.tile_floor(tint)
                elif cell==EXIT: tile=self.sf.tile_special("exit")
                elif cell==SHRINE: tile=self.sf.tile_special("shrine")
                elif cell==TRAP: tile=self.sf.tile_special("trap")
                elif cell==START: tile=self.sf.tile_special("start")
                else: tile=self.sf.tile_floor(tint)
                self.screen.blit(tile,(rx*TILE_SIZE,ry*TILE_SIZE))
                if dungeon.fog[ty][tx]:
                    self.screen.blit(self.fog_tile,(rx*TILE_SIZE,ry*TILE_SIZE))
        # monsters
        for m in dungeon.monsters:
            if not m.alive(): continue
            if cx<=m.pos[0]<cx+vis_w and cy<=m.pos[1]<cy+vis_h:
                px=(m.pos[0]-cx)*TILE_SIZE; py=(m.pos[1]-cy)*TILE_SIZE
                self.screen.blit(self.sf.monster(m.boss,self.frame),(px,py))
        # hero
        if cx<=hero.x<cx+vis_w and cy<=hero.y<cy+vis_h:
            hx=(hero.x-cx)*TILE_SIZE; hy=(hero.y-cy)*TILE_SIZE
            self.screen.blit(self.sf.hero(self.frame),(hx,hy))

        # Above-entity HP bars during combat
        if in_combat and enemy:
            # enemy bar
            if cx<=enemy.pos[0]<cx+vis_w and cy<=enemy.pos[1]<cy+vis_h:
                gx,gy=enemy.pos
                ratio = max(0.0, min(1.0, enemy.hp / float(max(1, enemy.max_hp))))
                self.draw_entity_bar(gx-cx, gy-cy, ratio, color=(220,60,60))
            # hero bar
            if cx<=hero.x<cx+vis_w and cy<=hero.y<cy+vis_h:
                ratio_h = hero.hp / float(max(1, hero.effective_max_hp()))
                self.draw_entity_bar(hero.x-cx, hero.y-cy, ratio_h, color=(60,200,100))

        # Minimap
        self.draw_minimap(dungeon, hero, (8,8), size=(220,170))

        # Floating damage/heal numbers
        self.draw_floats((cx,cy))

    def draw_minimap(self, dungeon:"Dungeon", hero:"Hero", pos:Tuple[int,int], size:Tuple[int,int]):
        mw,mh=size; sx=mw/max(1,dungeon.w); sy=mh/max(1,dungeon.h)
        mini=pygame.Surface((mw,mh), pygame.SRCALPHA); mini.fill((0,0,0,120))
        for y in range(dungeon.h):
            for x in range(dungeon.w):
                if dungeon.fog[y][x]: continue
                cell=dungeon.grid[y][x]
                if cell==WALL: c=(40,40,40,255)
                elif cell==EXIT: c=(40,160,60,255)
                elif cell==SHRINE: c=(160,120,200,255)
                elif cell==TRAP: c=(180,80,80,255)
                else: c=(120,120,120,255)
                rx=int(x*sx); ry=int(y*sy)
                pygame.draw.rect(mini,c,(rx,ry,max(1,int(sx)),max(1,int(sy))))
        hx=int(hero.x*sx); hy=int(hero.y*sy)
        pygame.draw.rect(mini,(235,235,60,255),(hx,hy,max(2,int(sx)),max(2,int(sy))))
        pygame.draw.rect(mini,(220,220,220,200), mini.get_rect(), 2)
        self.screen.blit(mini,pos)

    def draw_sidebar(self, hero:"Hero", dungeon:"Dungeon", in_combat:bool, enemy:Optional["Monster"],
                     abilities:Dict[str,Ability], shop_open:bool, inv_open:bool, map_open:bool,
                     zone:"Zone", quest_log:List[Quest], achievements:Dict[str,"Achievement"],
                     shop:"Shop", inv_items:List[Tuple[Item,bool]], world_zones:List["Zone"], world_cursor:int):
        x0=WIDTH; 
        pygame.draw.rect(self.screen,DARK,(x0,0,SIDEBAR_W,HEIGHT))
        self.screen.blit(self.font_big.render("PM5 Dungeon — Phase 6 (UI+FX)",True,WHITE),(x0+16,12))
        y=60
        for label,val,color in [
            ("Zone", zone.name, WHITE),
            ("Title", hero.title, GOLD),
            ("HP",f"{hero.hp}/{hero.effective_max_hp()}", GREEN if hero.hp>hero.effective_max_hp()*0.5 else RED),
            ("LVL",hero.level, WHITE),
            ("XP",f"{hero.xp}/{hero.xp_to_next()}", WHITE),
            ("MANA",f"{hero.mana}/{hero.effective_max_mana()}", BLUE),
            ("ATK",hero.attack_power(), WHITE),
            ("DEF",hero.defense(), WHITE),
            ("Watts",getattr(hero,'power',0), GOLD),
            ("Coins",hero.coins, GOLD),
            ("PM5", getattr(self, "pm5_status","n/a"), WHITE),
        ]:
            self.screen.blit(self.font.render(f"{label}: ",True,LIGHT_GRAY),(x0+16,y))
            vtxt=str(val); col = color if isinstance(color, tuple) else WHITE
            self.screen.blit(self.font.render(vtxt,True,col),(x0+180,y)); y+=24
        y+=8; self.screen.blit(self.font.render("Step Cooldown",True,LIGHT_GRAY),(x0+16,y)); y+=20
        bar_w=SIDEBAR_W-32
        cd_ratio=(hero.step_cooldown-STEP_MIN)/(STEP_MAX-STEP_MIN); cd_ratio=max(0.0,min(1.0,cd_ratio))
        pygame.draw.rect(self.screen,GRAY,(x0+16,y,bar_w,12))
        pygame.draw.rect(self.screen,BLUE,(x0+16,y,int(bar_w*cd_ratio),12)); y+=24
        self.screen.blit(self.font.render("Abilities (1-4)",True,LIGHT_GRAY),(x0+16,y)); y+=18
        for key in ["1","2","3","4"]:
            ab=abilities.get(key); 
            if not ab: continue
            txt=f"{key}. {ab.name}  Cost:{ab.cost}  CD:{ab.cd_remaining}/{ab.cooldown}"
            col=WHITE if ab.cd_remaining==0 and hero.mana>=ab.cost else LIGHT_GRAY
            self.screen.blit(self.font.render(txt,True,col),(x0+16,y)); y+=18
        y+=10
        controls="[Arrows] Move  [B] Shop@Start  [I] Inventory  [M] World Map  [F5] Save  [F9] Load  [Space] Attack  [1-4] Abilities  [X] Stop  [Esc] Quit"
        self.screen.blit(self.font_small.render(controls,True,LIGHT_GRAY),(x0+16,y)); y+=24
        self.screen.blit(self.font.render("Quests",True,GOLD),(x0+16,y)); y+=18
        anyq=False
        for q in quest_log[-5:]:
            anyq=True
            status = "✓" if q.completed else f"{q.progress}/{q.needed}"
            self.screen.blit(self.font_small.render(f"• {q.text} [{status}]",True,WHITE),(x0+16,y)); y+=18
        if not anyq:
            self.screen.blit(self.font_small.render("(none)",True,LIGHT_GRAY),(x0+16,y)); y+=18
        y+=6; self.screen.blit(self.font.render("Recent Log",True,LIGHT_GRAY),(x0+16,y)); y+=18
        for line in hero.history[-9:]:
            self.screen.blit(self.font.render(line,True,WHITE),(x0+16,y)); y+=18
        if in_combat and enemy: self.draw_combat_panel(hero, enemy)
        if shop_open: self.draw_shop_panel(hero, shop, zone)
        if inv_open: self.draw_inventory_panel(hero, inv_items)
        if map_open: self.draw_world_map(world_zones, world_cursor)
        if self.toast_timer>0 and self.toast_text:
            self.toast_timer -= 1
            self.draw_toast(self.toast_text)
        self.frame = (self.frame + 1) % 60

    def _hp_bar(self, x:int, y:int, w:int, h:int, ratio:float, fill_color:Tuple[int,int,int]):
        pygame.draw.rect(self.screen,(30,30,30),(x,y,w,h))
        pygame.draw.rect(self.screen,fill_color,(x+1,y+1,int((w-2)*max(0.0,min(1.0,ratio))),h-2))

    def draw_combat_panel(self, hero:"Hero", enemy:"Monster"):
        panel_h=160; surf=pygame.Surface((WIDTH,panel_h)); surf.set_alpha(220); surf.fill((15,15,22))
        self.screen.blit(surf,(0,HEIGHT-panel_h))
        name = ("👑 " if enemy.boss else "") + enemy.name
        self.screen.blit(self.font_big.render(f"⚔️ Combat: {name}",True,WHITE),(16,HEIGHT-panel_h+10))
        # Enemy and Hero HP bars
        # Enemy
        ex=16; ey=HEIGHT-panel_h+46; ew=360; eh=16
        ratio_e = enemy.hp / float(max(1,enemy.max_hp))
        self._hp_bar(ex,ey,ew,eh,ratio_e,(220,60,60))
        self.screen.blit(self.font_small.render(f"Enemy HP: {max(0,enemy.hp)}/{enemy.max_hp}  ATK: {enemy.atk}",True,GOLD),(ex,ey+eh+6))
        # Hero
        hx=16; hy=HEIGHT-panel_h+90; hw=360; hh=16
        ratio_h = hero.hp / float(max(1,hero.effective_max_hp()))
        self._hp_bar(hx,hy,hw,hh,ratio_h,(60,200,100))
        self.screen.blit(self.font_small.render(f"Your HP: {max(0,hero.hp)}/{hero.effective_max_hp()}  DEF: {hero.defense()}",True,WHITE),(hx,hy+hh+6))
        # Tips
        self.screen.blit(self.font_small.render("[Space] Attack   [1-4] Abilities   [Guard reduces next hit]",True,LIGHT_GRAY),(16,HEIGHT-panel_h+130))

    def draw_shop_panel(self, hero:"Hero", shop:"Shop", zone:"Zone"):
        panel_h=320; surf=pygame.Surface((WIDTH,panel_h)); surf.set_alpha(240); surf.fill((20,20,28))
        self.screen.blit(surf,(0,HEIGHT-panel_h))
        title=f"🏪 {zone.name} Shop (Coins: {hero.coins}) — [1-6] Buy  [R] Restock  [B] Close"
        self.screen.blit(self.font_big.render(title,True,WHITE),(16,HEIGHT-panel_h+8))
        y=HEIGHT-panel_h+44
        for i,it in enumerate(shop.stock, start=1):
            color=RARITY_COLORS.get(it.rarity,WHITE)
            line=f"{i}. {it.name} [{it.rarity}] — {it.price}c"
            self.screen.blit(self.font.render(line,True,color),(16,y)); y+=22
            cmp_line = self._compare_line(hero,it)
            if cmp_line:
                self.screen.blit(self.font_small.render("   " + cmp_line,True,GOLD),(32,y)); y+=18
            for t in it.tooltip():
                self.screen.blit(self.font_small.render("   • "+t,True,LIGHT_GRAY),(32,y)); y+=18
            y+=6

    def _compare_line(self, hero:"Hero", it:"Item")->str:
        if it.slot not in ("weapon","armor"): return ""
        cur_atk = hero.attack_power(); cur_def = hero.defense()
        cur_hpmax = hero.effective_max_hp(); cur_manamax = hero.effective_max_mana()
        old_weapon, old_armor = hero.weapon, hero.armor
        if it.slot=="weapon": hero.weapon = it
        else: hero.armor = it
        new_atk = hero.attack_power(); new_def = hero.defense()
        new_hpmax = hero.effective_max_hp(); new_manamax = hero.effective_max_mana()
        hero.weapon, hero.armor = old_weapon, old_armor
        da,dd,dh,dm = new_atk-cur_atk, new_def-cur_def, new_hpmax-cur_hpmax, new_manamax-cur_manamax
        def fmt(n): return f"+{n}" if n>0 else (f"{n}" if n<0 else "±0")
        return f"ΔATK {fmt(da)}  ΔDEF {fmt(dd)}  ΔHPcap {fmt(dh)}  ΔMANAcap {fmt(dm)}"

    def draw_inventory_panel(self, hero:"Hero", inv_items:List[Tuple[Item,bool]]):
        panel_h=340; surf=pygame.Surface((WIDTH,panel_h)); surf.set_alpha(240); surf.fill((28,20,20))
        self.screen.blit(surf,(0,HEIGHT-panel_h))
        hdr=f"🎒 Inventory — Coins:{hero.coins} | [↑/↓] Move  [E] Equip/Use  [S] Sell  [D] Drop  [I/Esc] Close"
        self.screen.blit(self.font_big.render(hdr,True,WHITE),(16,HEIGHT-panel_h+8))
        y=HEIGHT-panel_h+44
        wep=hero.weapon.name if hero.weapon else "None"
        arm=hero.armor.name if hero.armor else "None"
        self.screen.blit(self.font.render(f"Equipped — Weapon: {wep}   Armor: {arm}",True,WHITE),(16,y)); y+=24
        sets=hero.aggregate_set_bonuses()
        if sets:
            bonuses="  ".join([f"{k}+{v}" for k,v in sets.items()])
            self.screen.blit(self.font.render(f"Set Bonuses: {bonuses}",True,GOLD),(16,y)); y+=24
        else:
            self.screen.blit(self.font.render("Set Bonuses: (none)",True,LIGHT_GRAY),(16,y)); y+=24
        if not inv_items:
            self.screen.blit(self.font.render("(empty)",True,LIGHT_GRAY),(16,y)); return
        for idx,(it,sel) in enumerate(inv_items):
            color=RARITY_COLORS.get(it.rarity,WHITE)
            prefix="▶ " if sel else "   "
            eq_flag = (it is hero.weapon) or (it is hero.armor)
            name_txt = it.name + ("  [EQUIPPED]" if eq_flag else "")
            self.screen.blit(self.font.render(f"{prefix}{name_txt}",True,color),(16,y)); y+=22
            cmp_line = self._compare_line(hero,it)
            if cmp_line:
                self.screen.blit(self.font_small.render("   " + cmp_line,True,GOLD),(32,y)); y+=18
            for t in it.tooltip():
                self.screen.blit(self.font_small.render("   • "+t,True,LIGHT_GRAY),(32,y)); y+=18
            y+=4

    def draw_world_map(self, world_zones:List["Zone"], world_cursor:int):
        panel_h=360; surf=pygame.Surface((WIDTH,panel_h)); surf.set_alpha(235); surf.fill((22,22,26))
        self.screen.blit(surf,(0,HEIGHT-panel_h))
        self.screen.blit(self.font_big.render("🗺 World Map — [←/→] Select Zone  [Enter] Travel  [M] Close",True,WHITE),(16,HEIGHT-panel_h+8))
        y=HEIGHT-panel_h+48
        start_x=16
        for idx,z in enumerate(world_zones):
            box=pygame.Rect(start_x+idx*300, y, 280, 220)
            pygame.draw.rect(self.screen, z.color, box, border_radius=8)
            name_col=WHITE if idx!=world_cursor else GOLD
            self.screen.blit(self.font_big.render(z.name,True,name_col),(box.x+12,box.y+12))
            self.screen.blit(self.font_small.render(f"Monsters: {', '.join(z.monster_table[:3])}...",True,WHITE),(box.x+12,box.y+58))
            self.screen.blit(self.font_small.render(f"Wall density: {z.wall_density}",True,WHITE),(box.x+12,box.y+78))
            self.screen.blit(self.font_small.render(f"Dungeon size: {z.dungeon_size[0]}x{z.dungeon_size[1]}",True,WHITE),(box.x+12,box.y+98))
            if idx==world_cursor: pygame.draw.rect(self.screen, GOLD, box, 3, border_radius=8)

    def draw_toast(self, text:str):
        surf=pygame.Surface((WIDTH,40)); surf.set_alpha(220); surf.fill((10,10,10))
        self.screen.blit(surf,(0,0))
        self.screen.blit(self.font.render(text,True,GOLD),(16,8))

    def flip(self): pygame.display.flip()
    def tick(self): self.clock.tick(FPS)

# -------------------- PM5 / BLE Manager -------------------------------------
PM5_SERVICE_UUID="CE060000-43E5-11E4-916C-0800200C9A66"
PM5_CHAR_UUID   ="CE060030-43E5-11E4-916C-0800200C9A66"

class Simulator:
    def __init__(self,hero:"Hero"):
        self.hero=hero; self.running=False; self._t=None
    def start(self):
        if self.running: return
        self.running=True; self._t=threading.Thread(target=self._loop,daemon=True); self._t.start()
    def stop(self):
        self.running=False
        t=self._t
        if t and t.is_alive():
            t.join(timeout=1.0)
    def _loop(self):
        while self.running:
            watts=random.randint(*SIM_RANGE); self.hero.add_power(watts)
            time.sleep(random.uniform(*SIM_INTERVAL))

class PM5Manager:
    def __init__(self, hero:"Hero", renderer:"Renderer"):
        self.hero=hero; self.renderer=renderer
        self.sim=Simulator(hero)
        self._loop=None; self._thread=None
        self._use_ble = (BleakScanner is not None and BleakClient is not None)
        self._connected=False
        self._stop=False
        self.mode=PM5_MODE
    def start(self):
        if self.mode=="off" or not self._use_ble:
            self.renderer.pm5_status="SIM (BLE unavailable)" if not self._use_ble else "SIM (PM5 off by config)"
            self.sim.start(); return
        self._loop=asyncio.new_event_loop()
        def run():
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._runner())
            except Exception:
                pass
        self._thread=threading.Thread(target=run,daemon=True); self._thread.start()
    def stop(self):
        self._stop=True
        try:
            if self._loop: self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception: pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.sim.stop()
    async def _runner(self):
        while not self._stop:
            try:
                self.renderer.pm5_status="Scanning…"
                dev=None
                try:
                    devices=await BleakScanner.discover(timeout=6.0)
                    dev=next((d for d in devices if d.name and ("PM5" in d.name or "Concept2" in d.name)),None)
                except Exception:
                    dev=None
                if dev is None:
                    if self.mode in ("auto",):
                        if not self._connected:
                            self.renderer.pm5_status="SIM (no PM5 found)"
                            self.sim.start()
                        await asyncio.sleep(5.0)
                        continue
                    elif self.mode=="force":
                        self.renderer.pm5_status="PM5 required — not found"
                        await asyncio.sleep(5.0); continue
                # connect
                self.sim.stop()
                self.renderer.pm5_status=f"Connecting → {getattr(dev,'name','PM5')}"
                async with BleakClient(dev) as client:
                    self._connected=True
                    self.renderer.pm5_status="PM5 connected"
                    def on_data(_s,data:bytearray):
                        watts=int.from_bytes(data[4:6],"little",signed=False) if len(data)>=6 else 0
                        self.hero.add_power(watts)
                    try:
                        await client.start_notify(PM5_CHAR_UUID,on_data)
                    except BleakError:
                        self.renderer.pm5_status="Notify failed; retrying…"
                        self._connected=False
                        continue
                    while not self._stop and client.is_connected:
                        await asyncio.sleep(0.5)
                self._connected=False
                if self.mode=="auto":
                    self.renderer.pm5_status="Disconnected — reverting to SIM"
                    self.sim.start()
                    await asyncio.sleep(3.0)
            except Exception as e:
                self.renderer.pm5_status=f"PM5 error: {type(e).__name__}"
                if self.mode=="auto" and not self.sim.running:
                    self.sim.start()
                await asyncio.sleep(3.0)

# -------------------- Save/Load ----------------------------------------------
SAVE_FILE = "pm5_save.json"
def item_to_dict(it:Item)->Dict: return asdict(it)
def item_from_dict(d:Dict)->Item:
    return Item(
        d.get("name","?"), d.get("slot","weapon"),
        d.get("power",0), d.get("defense",0), d.get("heal",0),
        d.get("rarity","normal"), d.get("price",0), d.get("set_name"), d.get("biome_tag"),
        d.get("ilvl",1), d.get("req_level",1), d.get("prefix"), d.get("suffix"),
        d.get("mods",{}), d.get("unique_key")
    )
def hero_to_dict(hero:"Hero", zone_key:str, floor:int)->Dict:
    return {
        "hero": {
            "hp": hero.hp, "max_hp": hero.max_hp,
            "level": hero.level, "xp": hero.xp,
            "base_atk": hero.base_atk, "base_def": hero.base_def,
            "power": getattr(hero,"power",0),
            "mana": hero.mana, "max_mana": hero.max_mana,
            "coins": hero.coins, "title": hero.title,
            "weapon": item_to_dict(hero.weapon) if hero.weapon else None,
            "armor": item_to_dict(hero.armor) if hero.armor else None,
            "inventory": [item_to_dict(it) for it in hero.inventory],
            "quests": [asdict(q) for q in hero.quests],
            "achievements": {k:asdict(v) for k,v in hero.achievements.items()},
        },
        "zone_key": zone_key, "floor": floor,
    }
REQUIRED_KEYS=("hero","zone_key","floor")
def hero_from_dict(data:Dict, existing_hero:"Hero")->Tuple["Hero",str,int]:
    if not all(k in data for k in REQUIRED_KEYS): 
        raise ValueError("Corrupt save (missing keys)")
    h=existing_hero
    h.hp = int(data["hero"].get("hp",100))
    h.max_hp = int(data["hero"].get("max_hp",100))
    h.level = int(data["hero"].get("level",1))
    h.xp = int(data["hero"].get("xp",0))
    h.base_atk = int(data["hero"].get("base_atk",0))
    h.base_def = int(data["hero"].get("base_def",0))
    h.power = int(data["hero"].get("power",0))
    h.mana = int(data["hero"].get("mana",100))
    h.max_mana = int(data["hero"].get("max_mana",100))
    h.coins = int(data["hero"].get("coins",0))
    h.title = data["hero"].get("title","Novice")
    w = data["hero"].get("weapon"); a = data["hero"].get("armor")
    h.weapon = item_from_dict(w) if w else None
    h.armor  = item_from_dict(a) if a else None
    h.inventory = [item_from_dict(it) for it in data["hero"].get("inventory",[]) if isinstance(it,dict) and "name" in it and "slot" in it]
    h.quests = [Quest(**qd) for qd in data["hero"].get("quests",[]) if isinstance(qd,dict) and "id" in qd]
    h.achievements = {k:Achievement(**v) for k,v in data["hero"].get("achievements",{}).items() if isinstance(v,dict) and "key" in v}
    zone_key = data.get("zone_key","town"); floor = int(data.get("floor",1))
    return h, zone_key, floor

# -------------------- Game ---------------------------------------------------
class Game:
    def __init__(self):
        self.world_zones = ZONES; self.world_cursor = 0; self.zone = self.world_zones[self.world_cursor]
        self.hero=Hero(); self.hero.init_default_abilities(); self.hero.set_bonuses=SET_BONUSES
        self.hero.add_quest(Quest(1,"Reach Floor 3","reach_floor","3",needed=1))
        self.hero.add_quest(Quest(2,"Defeat 5 monsters","kill","*",needed=5))
        self.hero.add_quest(Quest(3,"Buy an item from a shop","buy","*",needed=1))
        self.shop=Shop(self.hero, self.zone)
        w,h = self.zone.dungeon_size
        self.dungeon=Dungeon(w,h,level=1, zone=self.zone)
        self.renderer=Renderer()
        self.camera=(0,0); self.running=True
        self.last_step_time=time.time(); self.in_combat=False; self.enemy:Optional[Monster]=None
        self.inv_open=False; self.inv_cursor=0; self.inv_items=[]
        self.map_open=False; self.guard_active=False
        self.shop_ui_open=False
        self.dungeon.reveal_radius(self.hero.x,self.hero.y,r=4)
        self.pm5=PM5Manager(self.hero, self.renderer)
        self.hero.log("PM5 mode: %s" % PM5_MODE)
        self.hero.log("Explore with [M]ap. Shop@Start [B]. Inventory [I]. Save [F5], Load [F9].")
        self._start_hint_shown=False

    def desired_cooldown(self)->float:
        return max(STEP_MIN,min(STEP_MAX, STEP_BASE - getattr(self.hero,'power',0)*STEP_SCALE))

    def try_step(self):
        if self.hero.hp<=0: return
        if self.in_combat or self.shop_ui_open or self.inv_open or self.map_open: return
        now=time.time()
        if now-self.last_step_time < self.desired_cooldown(): return
        dx,dy=self.hero.stride_dir
        if dx==0 and dy==0: return
        nx,ny=self.hero.x+dx,self.hero.y+dy
        if not self.dungeon.is_walkable(nx,ny):
            self.hero.log("Bumped a wall."); self.last_step_time=now; return
        self.hero.x,self.hero.y=nx,ny; self.last_step_time=now
        self.dungeon.reveal_radius(self.hero.x,self.hero.y,r=4)
        self.resolve_tile_events(); self.check_cell()

    def resolve_tile_events(self):
        t=self.dungeon.grid[self.hero.y][self.hero.x]
        if t==START and not self._start_hint_shown:
            self._start_hint_shown=True
            self.renderer.toast_text="Press B at the START tile to open the Shop."
            self.renderer.toast_timer=FPS*3
        if t==TRAP and random.random()<0.55:
            dmg=random.randint(5,11); self.hero.hp=max(0,self.hero.hp-dmg)
            self.hero.log(f"💥 Trap! You take {dmg} damage.")
            self.renderer.add_float((self.hero.x,self.hero.y), f"-{dmg}", RED, size="big")
        elif t==SHRINE and random.random()<0.55:
            heal=random.randint(6,14); self.hero.hp=min(self.hero.effective_max_hp(),self.hero.hp+heal)
            self.hero.mana=min(self.hero.effective_max_mana(),self.hero.mana+8)
            self.hero.log(f"✨ Shrine blesses you (+{heal} HP, +8 mana).")
            self.renderer.add_float((self.hero.x,self.hero.y), f"+{heal}", GREEN)

    def start_combat(self,m:Monster):
        self.in_combat=True; self.enemy=m
        self.hero.log(f"⚔️ {m.name} ({'boss' if m.boss else 'foe'}) engages!")

    def end_combat(self,victory:bool):
        if victory:
            xp = 10 + self.dungeon.level*2 + (12 if (self.enemy and self.enemy.boss) else 0)
            coins = random.randint(3,9) + self.dungeon.level + (5 if (self.enemy and self.enemy.boss) else 0)
            pre_level=self.hero.level
            self.hero.coins+=coins
            lvls = self.hero.gain_xp(xp)
            if lvls>0:
                self.renderer.toast_text=f"LEVEL UP! → {pre_level} ➜ {self.hero.level}"
                self.renderer.toast_timer=FPS*3
                self.hero.log(f"Level {self.hero.level}! Stats increased.")
            drop_chance = 0.28 + self.dungeon.level*0.005 + (0.25 if (self.enemy and self.enemy.boss) else 0.0)
            if random.random()<drop_chance:
                it = roll_loot(self.dungeon.level, self.zone, boss=(self.enemy.boss if self.enemy else False))
                self.hero.inventory.append(it)
                self.hero.log(f"Loot: {it.name} [{it.rarity}]")
            self.hero.log(f"Victory! (+{xp} XP, +{coins}c)")
            self.renderer.add_float((self.hero.x,self.hero.y), f"+{xp} XP", GOLD)
            if self.enemy and self.enemy.boss and pre_level<5:
                self.hero.grant_achievement("boss_first","First Boss Down")
        self.in_combat=False; self.enemy=None; self.guard_active=False

    def enemy_turn(self):
        if not self.enemy or not self.enemy.alive(): return
        if random.random()<0.2:
            self.hero.log(f"{self.enemy.name} raises its guard."); self.enemy.guard=True; self.tick_cooldowns(); return
        dmg=max(1,self.enemy.atk-self.hero.defense())
        if self.guard_active:
            reduce=8; dmg=max(0,dmg-reduce); self.guard_active=False
            self.renderer.add_float((self.hero.x,self.hero.y), "Guard!", BLUE, life=35)
        self.hero.hp-=dmg; self.hero.log(f"{self.enemy.name} hits you for {dmg}.")
        self.renderer.add_float((self.hero.x,self.hero.y), f"-{dmg}", RED, size="big" if dmg>=18 else "normal")
        if self.hero.hp<=0:
            self.hero.hp=0; self.hero.stride_dir=(0,0)
            self.hero.log("You are defeated. Press Esc or F9.")
            self.renderer.toast_text="You died! Press F9 to load your last save."
            self.renderer.toast_timer=FPS*3
        self.tick_cooldowns()

    def tick_cooldowns(self):
        for ab in self.hero.abilities.values():
            if ab.cd_remaining>0: ab.cd_remaining-=1

    def hero_basic_attack(self):
        if not(self.in_combat and self.enemy): return
        raw=max(1,self.hero.attack_power())
        if self.enemy.guard: dmg=max(1,raw-8); self.enemy.guard=False
        else: dmg=raw - self.enemy.atk//4
        dmg=max(1,dmg); self.enemy.hp-=dmg
        self.hero.log(f"You hit {self.enemy.name} for {dmg}.")
        self.renderer.add_float(self.enemy.pos, f"-{dmg}", ORANGE, size="big" if dmg>=20 else "normal")
        if self.enemy.hp<=0: 
            self.hero.check_quest("kill","*")
            self.end_combat(True); return
        self.enemy_turn()

    def cast_ability(self,key:str):
        if not(self.in_combat and self.enemy): return
        ab=self.hero.abilities.get(key)
        if not ab: return
        if ab.cd_remaining>0: self.hero.log(f"{ab.name} on cooldown."); return
        if self.hero.mana<ab.cost: self.hero.log("Not enough mana."); return
        self.hero.mana-=ab.cost
        if ab.kind=="damage":
            dmg=max(1,ab.power+(getattr(self.hero,'power',0)//20)); self.enemy.hp-=dmg; self.hero.log(f"{ab.name} hits for {dmg}!")
            self.renderer.add_float(self.enemy.pos, f"-{dmg}", ORANGE, size="big")
        elif ab.kind=="heal":
            heal=ab.power; self.hero.hp=min(self.hero.effective_max_hp(),self.hero.hp+heal); self.hero.log(f"You heal {heal} HP.")
            self.renderer.add_float((self.hero.x,self.hero.y), f"+{heal}", GREEN)
        else:
            self.guard_active=True; self.hero.log("You brace to reduce the next hit!")
            self.renderer.add_float((self.hero.x,self.hero.y), "Guard", BLUE, life=40)
        ab.cd_remaining=ab.cooldown
        if self.enemy.hp<=0: 
            self.hero.check_quest("kill","*")
            self.end_combat(True); return
        self.enemy_turn()

    def check_cell(self):
        if self.dungeon.grid[self.hero.y][self.hero.x]==EXIT:
            self.hero.log("You found the stairs → Descend!"); self.next_floor(); return
        for m in self.dungeon.monsters:
            if m.alive() and (m.pos==(self.hero.x,self.hero.y)): self.start_combat(m); break

    def check_reach_floor(self, floor:int):
        for q in self.hero.quests:
            if q.goal=="reach_floor" and not q.completed:
                try: target = int(q.target)
                except Exception: target = 1_000_000
                if floor >= target:
                    q.progress=q.needed; q.completed=True; self.hero.log(f"Quest complete: {q.text}")

    def next_floor(self):
        new_floor = self.dungeon.level+1
        self.check_reach_floor(new_floor)
        w,h = self.zone.dungeon_size
        self.dungeon=Dungeon(w,h,level=new_floor, zone=self.zone)
        self.hero.x,self.hero.y=1,1; self.dungeon.reveal_radius(self.hero.x,self.hero.y,r=4)
        self.hero.mana=min(self.hero.effective_max_mana(), self.hero.mana+12)
        self.shop.roll_stock()
        self.renderer.toast_text="Floor %d" % self.dungeon.level
        self.renderer.toast_timer=FPS*2
        self.hero.log(f"{self.zone.name} — Floor {self.dungeon.level}. Foes and rewards increase.")
        self._start_hint_shown=False

    # Inventory Overlay
    def open_inventory(self):
        self.inv_open=True; self.rebuild_inventory_list()
    def rebuild_inventory_list(self):
        self.inv_items=[(it, False) for it in self.hero.inventory]
        if self.inv_items:
            self.inv_cursor = max(0, min(self.inv_cursor, len(self.inv_items)-1))
            self.inv_items[self.inv_cursor]=(self.inv_items[self.inv_cursor][0], True)
        else: self.inv_cursor=0
    def inv_move(self,delta:int):
        if not self.inv_items: return
        self.inv_items[self.inv_cursor]=(self.inv_items[self.inv_cursor][0], False)
        self.inv_cursor=(self.inv_cursor+delta)%len(self.inv_items)
        self.inv_items[self.inv_cursor]=(self.inv_items[self.inv_cursor][0], True)
    def inv_equip_or_use(self):
        if not self.inv_items: return
        it=self.inv_items[self.inv_cursor][0]
        if it.slot=="consumable":
            msg=self.hero.consume(self.inv_cursor); self.hero.log(msg); self.renderer.add_float((self.hero.x,self.hero.y), "+HP", GREEN, life=30)
            self.rebuild_inventory_list()
        else:
            prev=self.hero.equip(it); del self.hero.inventory[self.inv_cursor]
            if prev: self.hero.inventory.append(prev)
            self.rebuild_inventory_list()
    def inv_sell(self):
        if not self.inv_items: return
        it=self.inv_items[self.inv_cursor][0]
        if it is self.hero.weapon or it is self.hero.armor:
            self.hero.log("Unequip before selling."); return
        val=self.shop.sell_value(it)
        self.hero.coins+=val; del self.hero.inventory[self.inv_cursor]
        self.hero.log(f"Sold {it.name} for {val}c."); self.rebuild_inventory_list()
    def inv_drop(self):
        if not self.inv_items: return
        it=self.inv_items[self.inv_cursor][0]
        if it is self.hero.weapon or it is self.hero.armor:
            self.hero.log("Cannot drop equipped item."); return
        del self.hero.inventory[self.inv_cursor]
        self.hero.log(f"Dropped {it.name}."); self.rebuild_inventory_list()

    # Map / Shop UI
    def shop_open(self)->bool: return self.shop_ui_open
    def toggle_shop(self, open_flag:bool): self.shop_ui_open = open_flag
    def open_map(self): self.map_open=True
    def close_map(self): self.map_open=False
    def travel_to_selected_zone(self):
        if self.world_cursor<0 or self.world_cursor>=len(self.world_zones): return
        dest=self.world_zones[self.world_cursor]
        if dest.key==self.zone.key: self.hero.log("You are already here."); return
        cost=5
        if self.hero.coins<cost: self.hero.log("Not enough coins to travel."); return
        self.hero.coins-=cost
        self.zone=dest; self.shop=Shop(self.hero, self.zone)
        w,h = self.zone.dungeon_size
        self.dungeon=Dungeon(w,h, level=1, zone=self.zone)
        self.hero.x,self.hero.y=1,1; self.dungeon.reveal_radius(self.hero.x,self.hero.y,r=4)
        self.hero.log(f"Traveled to {self.zone.name}. (-{cost}c)")
        evt=random.choice(["ambush","blessing","merchant","nothing"])
        if evt=="ambush":
            self.hero.log("⚠️ Travel ambush! You are struck for 7 HP."); self.hero.hp=max(0,self.hero.hp-7)
            self.renderer.add_float((self.hero.x,self.hero.y), "-7", RED)
        elif evt=="blessing":
            self.hero.log("✨ Travel blessing! Healed 10 HP."); self.hero.hp=min(self.hero.effective_max_hp(),self.hero.hp+10)
            self.renderer.add_float((self.hero.x,self.hero.y), "+10", GREEN)
        elif evt=="merchant":
            self.hero.log("🛒 Roaming merchant sold you a Potion for 5c.")
            self.hero.coins=max(0,self.hero.coins-5); self.hero.inventory.append(Item("Potion","consumable",heal=25,price=8,rarity="normal"))

    # IO / Save
    def do_save(self):
        data = hero_to_dict(self.hero, self.zone.key, self.dungeon.level)
        try:
            with open(SAVE_FILE,"w",encoding="utf-8") as f:
                json.dump(data,f,indent=2)
            self.hero.log("💾 Game saved."); self.renderer.toast_text="Game saved"; self.renderer.toast_timer=FPS*2
        except Exception as e:
            self.hero.log(f"Save failed: {e}")
    def do_load(self):
        if not os.path.exists(SAVE_FILE):
            self.hero.log("No save file found."); return
        try:
            with open(SAVE_FILE,"r",encoding="utf-8") as f:
                data=json.load(f)
            self.hero, zone_key, floor = hero_from_dict(data, self.hero)
            self.zone = next((z for z in self.world_zones if z.key==zone_key), self.world_zones[0])
            self.shop=Shop(self.hero, self.zone)
            w,h = self.zone.dungeon_size
            self.dungeon=Dungeon(w,h, level=max(1,floor), zone=self.zone)
            self.hero.x,self.hero.y=1,1; self.dungeon.reveal_radius(self.hero.x,self.hero.y,r=4)
            self.hero.log("📂 Game loaded."); self.renderer.toast_text="Game loaded"; self.renderer.toast_timer=FPS*2
        except Exception as e:
            self.hero.log(f"Load failed: {e}")

    # Events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.running=False
            elif event.type==pygame.KEYDOWN:
                if self.hero.hp<=0 and event.key not in (pygame.K_F9, pygame.K_ESCAPE): continue
                if event.key==pygame.K_ESCAPE:
                    if self.inv_open: self.inv_open=False
                    elif self.map_open: self.close_map()
                    elif self.shop_open(): self.toggle_shop(False)
                    else: self.running=False
                elif event.key==pygame.K_F5: self.do_save()
                elif event.key==pygame.K_F9: self.do_load()
                elif self.inv_open:
                    if event.key==pygame.K_UP: self.inv_move(-1)
                    elif event.key==pygame.K_DOWN: self.inv_move(1)
                    elif event.key==pygame.K_e: self.inv_equip_or_use()
                    elif event.key==pygame.K_s: self.inv_sell()
                    elif event.key==pygame.K_d: self.inv_drop()
                    elif event.key in (pygame.K_i, pygame.K_TAB): self.inv_open=False
                elif self.map_open:
                    if event.key==pygame.K_LEFT: self.world_cursor=(self.world_cursor-1)%len(self.world_zones)
                    elif event.key==pygame.K_RIGHT: self.world_cursor=(self.world_cursor+1)%len(self.world_zones)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER): self.travel_to_selected_zone(); self.close_map()
                    elif event.key==pygame.K_m: self.close_map()
                elif self.shop_open():
                    if event.key==pygame.K_b: self.toggle_shop(False)
                    elif event.key==pygame.K_r: self.hero.log(self.shop.restock())
                    elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6):
                        idx={pygame.K_1:0,pygame.K_2:1,pygame.K_3:2,pygame.K_4:3,pygame.K_5:4,pygame.K_6:5}[event.key]
                        msg=self.shop.buy(idx); self.hero.log(msg)
                elif not self.in_combat:
                    if event.key==pygame.K_UP: self.hero.stride_dir=(0,-1)
                    elif event.key==pygame.K_DOWN: self.hero.stride_dir=(0,1)
                    elif event.key==pygame.K_LEFT: self.hero.stride_dir=(-1,0)
                    elif event.key==pygame.K_RIGHT: self.hero.stride_dir=(1,0)
                    elif event.key==pygame.K_x: self.hero.stride_dir=(0,0)
                    elif event.key==pygame.K_b and self.dungeon.grid[self.hero.y][self.hero.x]==START:
                        self.toggle_shop(True); self.hero.log(f"{self.zone.name} Shop opened.")
                    elif event.key in (pygame.K_i, pygame.K_TAB): self.open_inventory()
                    elif event.key==pygame.K_m: self.open_map()
                else:
                    if event.key==pygame.K_SPACE: self.hero_basic_attack()
                    elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4):
                        key={pygame.K_1:"1",pygame.K_2:"2",pygame.K_3:"3",pygame.K_4:"4"}[event.key]
                        self.cast_ability(key)
            elif event.type==pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    self.hero.stride_dir=(0,0)

    # Camera / Loop
    def update_camera(self):
        cx=max(0,min(self.hero.x-MAP_COLS//2, self.dungeon.w-MAP_COLS))
        cy=max(0,min(self.hero.y-MAP_ROWS//2, self.dungeon.h-MAP_ROWS))
        self.camera=(cx,cy)

    def run(self):
        self.pm5.mode=PM5_MODE; self.pm5.start()
        while self.running:
            self.handle_events(); self.try_step(); self.update_camera()
            self.renderer.draw_map(self.dungeon,self.hero,self.camera, in_combat=self.in_combat, enemy=self.enemy)
            self.renderer.draw_sidebar(
                hero=self.hero, dungeon=self.dungeon, in_combat=self.in_combat, enemy=self.enemy,
                abilities=self.hero.abilities, shop_open=self.shop_open(), inv_open=self.inv_open, map_open=self.map_open,
                zone=self.zone, quest_log=self.hero.quests, achievements=self.hero.achievements,
                shop=self.shop, inv_items=self.inv_items, world_zones=self.world_zones, world_cursor=self.world_cursor
            )
            self.renderer.flip(); self.renderer.tick()
        self.pm5.stop()
        if pygame: pygame.quit()

# Entry
if __name__=="__main__":
    if pygame is None:
        print("This build requires pygame. Install: pip install pygame"); sys.exit(1)
    print("PM5 Dungeon — Phase 6 (Desktop UI+FX). Arrows move, X stop, B=Shop@Start, I=Inventory, M=Map, F5 Save, F9 Load, Space/1-4 combat, Esc quit.")
    game=Game(); game.run()
