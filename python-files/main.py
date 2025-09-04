import pygame, sys, random, math, itertools
from collections import deque
import time
import random

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(128)
bounce_sounds = [pygame.mixer.Sound(f"sound{i}.mp3") for i in range(1, 6)]
reaction_sound = pygame.mixer.Sound("sound6.mp3")
selected_species = None
show_info = True

WIN_W, WIN_H = 1920, 1080
SIDEBAR_W = 360
WORLD_W = WIN_W - SIDEBAR_W
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("YAMAN'S PARTICLE COLLIDER!!!!!!!!!!")
FPS = 60
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Cambria Math", 12)
FONT_SMALL = pygame.font.SysFont("Cambria Math", 15)
FONT_BIG = pygame.font.SysFont("Cambria Math", 20, bold=True)
BG = (10, 12, 16)
SIDEBAR_BG = (22, 24, 32)

PARTICLES = {
    # Leptons
    "e-": {"name":"Electron","symbol":"e⁻","mass":0.511,"color":(50,150,255),"radius":7,"anti":"e+","spin":1/2},
    "e+": {"name":"Positron","symbol":"e⁺","mass":0.511,"color":(255,120,50),"radius":7,"anti":"e-","spin":1/2},
    "mu-":{"name":"Muon","symbol":"μ⁻","mass":105.7,"color":(180,130,255),"radius":8,"anti":"mu+","spin":1/2},
    "mu+":{"name":"Anti Muon","symbol":"μ⁺","mass":105.7,"color":(255,150,200),"radius":8,"anti":"mu-","spin":1/2},
    "tau-":{"name":"Tau","symbol":"τ⁻","mass":1776.9,"color":(240,100,255),"radius":9,"anti":"tau+","spin":1/2},
    "tau+":{"name":"Anti Tau","symbol":"τ⁺","mass":1776.9,"color":(255,120,230),"radius":9,"anti":"tau-","spin":1/2},
    "nu_e":{"name":"Electron Neutrino","symbol":"νₑ","mass":0.0001,"color":(0,255,100),"radius":4,"anti":"nu_eanti","spin":1/2},
    "nu_eanti":{"name":"Electron Anti Neutrino","symbol":"ν̅ₑ","mass":0.0001,"color":(100,255,0),"radius":4,"anti":"nu_e","spin":1/2},
    "nu_mu":{"name":"Muon Neutrino","symbol":"ν_μ","mass":0.0002,"color":(0,220,180),"radius":4,"anti":"nu_muanti","spin":1/2},
    "nu_muanti":{"name":"Muon Anti Neutrino","symbol":"ν̅_μ","mass":0.0002,"color":(0,180,220),"radius":4,"anti":"nu_mu","spin":1/2},
    "nu_tau":{"name":"Tau Neutrino","symbol":"ν_τ","mass":0.0003,"color":(0,255,180),"radius":4,"anti":"nu_tauanti","spin":1/2},
    "nu_tauanti":{"name":"Tau Anti Neutrino","symbol":"ν̅_τ","mass":0.0003,"color":(0,200,150),"radius":4,"anti":"nu_tau","spin":1/2},
    # Quarks
    "u":{"name":"Up Quark","symbol":"u","mass":2.2,"color":(255,80,80),"radius":6,"anti":"ū","spin":1/2},
    "ū":{"name":"Anti Up Quark","symbol":"ū","mass":2.2,"color":(180,40,40),"radius":6,"anti":"u","spin":1/2},
    "d":{"name":"Down Quark","symbol":"d","mass":4.7,"color":(80,255,80),"radius":6,"anti":"d̄","spin":1/2},
    "d̄":{"name":"Anti Down Quark","symbol":"d̄","mass":4.7,"color":(40,180,40),"radius":6,"anti":"d","spin":1/2},
    "s":{"name":"Strange Quark","symbol":"s","mass":95,"color":(0,255,200),"radius":6,"anti":"s̄","spin":1/2},
    "s̄":{"name":"Anti Strange Quark","symbol":"s̄","mass":95,"color":(0,180,140),"radius":6,"anti":"s","spin":1/2},
    "c":{"name":"Charm Quark","symbol":"c","mass":1275,"color":(180,100,255),"radius":6,"anti":"c̄","spin":1/2},
    "c̄":{"name":"Anti Charm Quark","symbol":"c̄","mass":1275,"color":(140,60,200),"radius":6,"anti":"c","spin":1/2},
    "b":{"name":"Bottom Quark","symbol":"b","mass":4180,"color":(60,60,255),"radius":7,"anti":"b̄","spin":1/2},
    "b̄":{"name":"Anti Bottom Quark","symbol":"b̄","mass":4180,"color":(40,40,180),"radius":7,"anti":"b","spin":1/2},
    "t":{"name":"Top Quark","symbol":"t","mass":173100,"color":(255,255,100),"radius":7,"anti":"t̄","spin":1/2},
    "t̄":{"name":"Anti Top Quark","symbol":"t̄","mass":173100,"color":(200,200,60),"radius":7,"anti":"t","spin":1/2},
    # Bosons
    "photon":{"name":"Photon","symbol":"γ","mass":0.0,"color":(255,255,180),"radius":4,"spin":1},
    "gluon":{"name":"Gluon","symbol":"g","mass":0.0,"color":(255,150,255),"radius":4,"spin":1},
    "W+":{"name":"W+ Boson","symbol":"W⁺","mass":80379,"color":(255,140,100),"radius":7,"spin":1},
    "W-":{"name":"W- Boson","symbol":"W⁻","mass":80379,"color":(255,100,140),"radius":7,"spin":1},
    "Z0":{"name":"Z Boson","symbol":"Z⁰","mass":91187,"color":(160,255,160),"radius":7,"spin":1},
    "H0":{"name":"Higgs Boson","symbol":"H","mass":125100,"color":(220,180,255),"radius":8,"spin":0},
    # Hadrons
    "p":{"name":"Proton","symbol":"p","mass":938.27,"color":(255,50,50),"radius":9,"anti":"panti","spin":1/2},
    "panti":{"name":"Anti Proton","symbol":"p̅","mass":938.27,"color":(255,100,180),"radius":9,"anti":"p","spin":1/2},
    "n":{"name":"Neutron","symbol":"n","mass":939.57,"color":(180,100,255),"radius":9,"anti":"nanti","spin":1/2},
    "nanti":{"name":"Anti Neutron","symbol":"n̅","mass":939.57,"color":(140,60,200),"radius":9,"anti":"n","spin":1/2},
    "Lambda0": {"name":"Lambda0","symbol":"Λ⁰","mass":1115.7,"color":(180,140,220),"radius":9,"anti":"Lambda0_anti","spin":1/2},
    "Lambda0_anti": {"name":"Anti Lambda0","symbol":"Λ̄⁰","mass":1115.7,"color":(140,100,180),"radius":9,"anti":"Lambda0","spin":1/2},
    "Lambda":{"name":"Lambda","symbol":"Λ","mass":1115.7,"color":(180,140,220),"radius":9,"anti":"Lambda_anti","spin":1/2},
    "Lambda_anti":{"name":"Anti Lambda","symbol":"Λ̄","mass":1115.7,"color":(140,100,180),"radius":9,"anti":"Lambda","spin":1/2},
    "Sigma+":{"name":"Sigma+","symbol":"Σ⁺","mass":1189.4,"color":(255,120,200),"radius":9,"anti":"Sigma-","spin":1/2},
    "Sigma0":{"name":"Sigma0","symbol":"Σ⁰","mass":1192.6,"color":(200,180,255),"radius":9,"anti":"Sigma0_anti","spin":1/2},
    "Sigma-":{"name":"Sigma-","symbol":"Σ⁻","mass":1197.4,"color":(180,120,200),"radius":9,"anti":"Sigma+","spin":1/2},
    "Sigma0_anti":{"name":"Anti Sigma0","symbol":"Σ̄⁰","mass":1192.6,"color":(160,140,200),"radius":9,"anti":"Sigma0","spin":1/2},
    "Xi0":{"name":"Xi0","symbol":"Ξ⁰","mass":1314.9,"color":(160,200,255),"radius":9,"anti":"Xi0_anti","spin":1/2},
    "Xi-":{"name":"Xi-","symbol":"Ξ⁻","mass":1321.7,"color":(140,100,255),"radius":9,"anti":"Xi+","spin":1/2},
    "Xi0_anti":{"name":"Anti Xi0","symbol":"Ξ̄⁰","mass":1314.9,"color":(100,160,200),"radius":9,"anti":"Xi0","spin":1/2},
    "Xi+":{"name":"Xi+","symbol":"Ξ⁺","mass":1321.7,"color":(200,120,255),"radius":9,"anti":"Xi-","spin":1/2},
    "Omega-":{"name":"Omega-","symbol":"Ω⁻","mass":1672.5,"color":(60,120,255),"radius":9,"anti":"Omega+","spin":3/2},
    "Omega+":{"name":"Anti Omega","symbol":"Ω⁺","mass":1672.5,"color":(100,200,255),"radius":9,"anti":"Omega-","spin":3/2},
    # Delta family (kept for spin-changer use)
    "Delta++":{"name":"Delta++","symbol":"Δ⁺⁺","mass":1232,"color":(255,80,80),"radius":9,"anti":"Delta--","spin":3/2},
    "Delta+":{"name":"Delta+","symbol":"Δ⁺","mass":1232,"color":(255,120,120),"radius":9,"anti":"Delta-","spin":3/2},
    "Delta0":{"name":"Delta0","symbol":"Δ⁰","mass":1232,"color":(220,180,240),"radius":9,"anti":"Delta0_anti","spin":3/2},
    "Delta-":{"name":"Delta-","symbol":"Δ⁻","mass":1232,"color":(200,120,160),"radius":9,"anti":"Delta+","spin":3/2},
    "Delta--":{"name":"Anti Delta--","symbol":"Δ̄⁻⁻","mass":1232,"color":(160,80,140),"radius":9,"anti":"Delta++","spin":3/2},
    "Delta-_anti": {"name":"Anti Delta-","symbol":"Δ̄⁻","mass":1232,"color":(160,100,160),"radius":9,"anti":"Delta-","spin":3/2},
    "Delta+_anti": {"name":"Anti Delta+","symbol":"Δ̄⁺","mass":1232,"color":(200,120,180),"radius":9,"anti":"Delta+","spin":3/2},
    # Pions
    "pi+":{"name":"Pion+","symbol":"π⁺","mass":139.6,"color":(255,180,100),"radius":8,"anti":"pi-","spin":0},
    "pi-":{"name":"Pion-","symbol":"π⁻","mass":139.6,"color":(200,100,60),"radius":8,"anti":"pi+","spin":0},
    "pi0":{"name":"Pion0","symbol":"π⁰","mass":135.0,"color":(220,220,220),"radius":7,"anti":"pi0","spin":0},  # self-antiparticle
    # Kaons
    "K+":{"name":"Kaon+","symbol":"K⁺","mass":493.7,"color":(220,220,100),"radius":8,"anti":"K-","spin":0},
    "K-":{"name":"Kaon-","symbol":"K⁻","mass":493.7,"color":(180,180,60),"radius":8,"anti":"K+","spin":0},
    "K0":{"name":"Kaon0","symbol":"K⁰","mass":497.6,"color":(120,200,255),"radius":8,"anti":"K0anti","spin":0},
    "K0anti":{"name":"Anti Kaon0","symbol":"K̄0","mass":497.6,"color":(100,160,220),"radius":8,"anti":"K0","spin":0},
    "rho+": {"name":"Rho+","symbol":"ρ⁺","mass":775.26,"color":(240,160,100),"radius":8,"anti":"rho-","spin":1},
    "rho-": {"name":"Rho-","symbol":"ρ⁻","mass":775.26,"color":(200,120,80),"radius":8,"anti":"rho+","spin":1},
    "rho0": {"name":"Rho0","symbol":"ρ⁰","mass":775.26,"color":(220,200,160),"radius":8,"anti":"rho0","spin":1},  # self-antiparticle
    "phi": {"name":"Phi","symbol":"φ","mass":1019.461,"color":(100,200,200),"radius":8,"anti":"phi","spin":1},
    "eta": {"name":"Eta","symbol":"η","mass":547.862,"color":(200,180,240),"radius":7,"anti":"eta","spin":0},
    # Heavy Quarkonia
    "psi": {"name":"Ψ","symbol":"Ψ","mass":3096.9,"color":(200,120,255),"radius":7,"anti":"psi","spin":1},
    "Upsilon": {"name":"Upsilon","symbol":"Υ","mass":9460.3,"color":(160,120,255),"radius":7,"anti":"Upsilon","spin":1},
    # D/B Mesons
    "D+": {"name":"D+ Meson","symbol":"D⁺","mass":1.870,"color":(255,100,180),"radius":7,"anti":"D-","spin":0},
    "D0": {"name":"D0 Meson","symbol":"D⁰","mass":1.865,"color":(180,200,255),"radius":7,"anti":"D0anti","spin":0},
    "B+": {"name":"B+ Meson","symbol":"B⁺","mass":5.279,"color":(255,100,50),"radius":7,"anti":"B-","spin":0},
    "B0": {"name":"B0 Meson","symbol":"B⁰","mass":5.280,"color":(100,255,100),"radius":7,"anti":"B0anti","spin":0},
	# POSSIBILITES
	"lepton": {"name":"Lepton","symbol":"ℓ","mass":0,"color":(0,255,150),"radius":7,"anti":"ℓ+","spin":1/2},
	"lepton+": {"name":"Lepton+","symbol":"ℓ⁺","mass":0,"color":(150,255,0),"radius":7,"anti":"ℓ","spin":1/2},
	"q":{"name":"Quark","symbol":"q","mass":0,"color":(150,50,200),"radius":6,"anti":"q⁻","spin":1/2},
	"q-":{"name":"Quark-","symbol":"q⁻","mass":0,"color":(200,50,150),"radius":6,"anti":"q","spin":1/2},
	"V":{"name":"Vector Boson","symbol":"V","mass":0,"color":(200,150,0),"radius":6,"anti":"q","spin":1/2},
	# GAMECHANGERS
    "BREAKER":{"name":"BREAKER","symbol":"×","mass":0.0,"color":(255,255,255),"radius":10,"anti":"","spin":"?"},
    "SPINCHANGER":{"name":"SPINCHANGER","symbol":"♦","mass":0.0,"color":(255,255,0),"radius":10,"anti":"","spin":"?"},
	"QUANTUMCHANGER":{"name":"QUANTUMCHANGER","symbol":"¿","mass":0.0,"color":(0,255,255),"radius":15,"anti":"","spin":"?"},
    "DECAYER":{"name":"DECAYER","symbol":"#","mass":0.0,"color":(0,255,0),"radius":10,"anti":"","spin":"Uncertain"},
	"ENERGY": {"name":"ENERGY","symbol":"ɇ","mass":0.0,"color":(255,100,100),"radius":20,"anti":"","spin":"?"},
	"VIRTUALIZER": {"name":"VIRTUALIZER","symbol":"⍟","mass":0.0,"color":(235,200,100),"radius":9, "anti":"","spin":"?"},
    "VIRTUAL PARTICLE": {"name":"VIRTUAL PARTICLE","symbol":"Ø","mass":0.0,"color":(196,216,254),"radius":5, "anti":"","spin":"?"},
	"EMPTY": {"name":"EMPTY","symbol":" ","mass":0.0,"color":(0,0,0),"radius":0, "anti":"","spin":"?"},
}

PARTICLES_KEYS = list(PARTICLES.keys())

# KEY MAP
DIGITS = [str(i) for i in range(1,10)]
LETTERS = [chr(c) for c in range(ord('a'), ord('z')+1)]
KEY_BIND_ORDER = DIGITS + LETTERS
KEY_TO_PARTICLES = {k: sp for k, sp in zip(KEY_BIND_ORDER, PARTICLES_KEYS)}

def pygame_event_to_key(ev):
    if hasattr(ev, 'unicode') and ev.unicode:
        c = ev.unicode.lower()
        if c in LETTERS or c in DIGITS:
            return c
    return None

EXTRA_FKEY_MAP = {
    pygame.K_F1:  "p",
    pygame.K_F2:  "panti",
    pygame.K_F3:  "n",
    pygame.K_F4:  "nanti",
    pygame.K_F5:  "pi+",
    pygame.K_F6:  "pi-",
    pygame.K_F7:  "pi0",
    pygame.K_F8:  "K+",
    pygame.K_F9:  "K-",
    pygame.K_F10: "K0",
    pygame.K_F11: "Lambda",
    pygame.K_F12: "Omega-",
}

NAV_KEYS = [
    pygame.K_INSERT,
    pygame.K_HOME,
    pygame.K_PAGEUP,
    pygame.K_DELETE,
    pygame.K_END,
    pygame.K_PAGEDOWN,
	pygame.K_RIGHT,
	pygame.K_NUMLOCK,
	pygame.K_QUOTEDBL,
	pygame.K_COMMA,
	pygame.K_TAB,
	pygame.K_CAPSLOCK,
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LALT,
    pygame.K_RALT,
    pygame.K_LEFT,
	pygame.K_KP1,
	pygame.K_KP2,
    pygame.K_KP3,
    pygame.K_KP4,
    pygame.K_KP5,
    pygame.K_KP6,
    pygame.K_KP7,
    pygame.K_KP8,
    pygame.K_KP9,
    pygame.K_KP0,
	pygame.K_MINUS,
	pygame.K_KP_MULTIPLY,
	pygame.K_ASTERISK,
	pygame.K_KP_DIVIDE,
    pygame.K_UP,
    pygame.K_BACKSPACE,
    pygame.K_DOWN,
	pygame.K_PAUSE,
	pygame.K_SCROLLLOCK,
	pygame.K_PRINT,
	pygame.K_KP_ENTER,
    pygame.K_RETURN,
	pygame.K_KP_MINUS,
]

already_assigned_species = set(KEY_TO_PARTICLES.values()) | set(EXTRA_FKEY_MAP.values())
unassigned_species = [sp for sp in PARTICLES_KEYS if sp not in already_assigned_species]

EXTRA_NAV_MAP = {k: sp for k, sp in zip(NAV_KEYS, unassigned_species)}

EXTRA_PARTICLES_TO_KEY = {}

for i, (k, sp) in enumerate(EXTRA_FKEY_MAP.items(), start=1):
    EXTRA_PARTICLES_TO_KEY[sp] = f"F{i}"

NAV_KEY_LABELS = {
    pygame.K_INSERT: "Ins",
    pygame.K_HOME: "Home",
    pygame.K_PAGEUP: "PgUp",
    pygame.K_DELETE: "Del",
    pygame.K_END: "End",
    pygame.K_PAGEDOWN: "PgDn",
}
for k, sp in EXTRA_NAV_MAP.items():
    EXTRA_PARTICLES_TO_KEY[sp] = NAV_KEY_LABELS.get(k, pygame.key.name(k).title())

def react_key(*args):
    return tuple(sorted(args))

REACTIONS = {
    react_key("BREAKER","D+"): {"products":["c","d̄"],"note":"D⁺ → c + d̄"},
    react_key("BREAKER","D0"): {"products":["c","ū"],"note":"D⁰ → c + ū"},
    react_key("BREAKER","B+"): {"products":["b","ū"],"note":"B+ → b + ū"},
    react_key("BREAKER","B0"): {"products":["b̄","d"],"note":"B0 → b + d̄"},
    react_key("BREAKER","K0"): {"products":["d","s̄"], "note":"K0 → d+s̄"},
    react_key("BREAKER","K0anti"): {"products":["d̄","s"], "note":"K̄0 → d̄+s"},
    react_key("BREAKER","pi+"): {"products":["u","d̄"], "note":"π⁺ → u + d̄"},
    react_key("BREAKER","pi-"): {"products":["d","ū"], "note":"π⁻ → d + ū"},
    react_key("BREAKER","pi0"): {"products":["u","ū"], "note":"π⁰ → u + ū"},
    react_key("c","d̄"): {"products":["D+"],"note":"c + d̄ → D⁺"},
    react_key("c","ū"): {"products":["D0"],"note":"c + ū → D⁰"},
    react_key("b","ū"): {"products":["B+"],"note":"c + ū → B⁺"},
    react_key("b","d̄"): {"products":["B0"],"note":"c + ū → B⁰"},
    react_key("d","s̄"): {"products":["K0"], "note":"d s̄ → K0"},
    react_key("d̄","s"): {"products":["K0anti"], "note":"d̄ s → K̄0"},
    react_key("u","d̄"): {"products":["pi+"], "note":"u d̄ → π⁺"},
    react_key("d","ū"): {"products":["pi-"], "note":"d ū → π⁻"},
    react_key("d","d̄"): {"products":["pi0"], "note":"d d̄ → π⁰"},
    react_key("mu-","mu+"): {"products":["mu-","mu+"], "note":"μ⁻μ⁺ → NOT ENOUGH ENERGY"},
    react_key("mu-","mu+","ENERGY"): {"products":["Z0"], "note":"μ⁻μ⁺ → Z⁰"},
    react_key("tau-","tau+"): {"products":["tau-","tau+"], "note":"τ⁻τ⁺ → NOT ENOUGH ENERGY"},
    react_key("tau-","tau+","ENERGY"): {"products":["Z0"], "note":"τ⁻τ⁺ → Z⁰"},
    react_key("nu_e","nu_eanti"): {"products":["nu_e","nu_eanti"], "note":"νₑ ν̅ₑ → NOT ENOUGH ENERGY"},
    react_key("nu_e","nu_eanti","ENERGY"): {"products":["Z0"], "note":"νₑ ν̅ₑ → Z⁰"},
    react_key("nu_mu","nu_muanti"): {"products":["nu_mu","nu_muanti"], "note":"ν_μ ν̅_μ → NOT ENOUGH ENERGY"},
    react_key("nu_mu","nu_muanti","ENERGY"): {"products":["Z0"], "note":"ν_μ ν̅_μ → Z⁰"},
    react_key("nu_tau","nu_tauanti"): {"products":["nu_tau","nu_tauanti"], "note":"ν_τ ν̅_τ → NOT ENOUGH ENERGY"},
    react_key("nu_tau","nu_tauanti","ENERGY"): {"products":["Z0"], "note":"ν_τ ν̅_τ → Z⁰"},
    react_key("n","nanti"): {"products":["n","nanti"], "note":"n n̅ → NOT ENOUGH ENERGY!"},
    react_key("n","nanti","ENERGY"): {"products":["pi+","pi+","pi-","pi-","pi0"], "note":"n n̅ → 2π⁺ + 2π⁻ + π⁰"},
    react_key("K+","K-"): {"products":["K+","K-"], "note":"K⁺ K⁻ → NOT ENOUGH ENERGY"},
	react_key("K+","K-","ENERGY"): {"products":["pi0","pi0"], "note":"K⁺ K⁻ → π⁰ π⁰"},
    react_key("K0","K0anti"): {"products":["K0","K0anti"], "note":"K0 K̄0 → NOT ENOUGH ENERGY"},
	react_key("K0","K0anti","ENERGY"): {"products":["pi+","pi-"], "note":"K0 K̄0 → π⁺ π⁻"},
    react_key("rho+","rho-"): {"products":["rho+","rho-"], "note":"ρ⁺ ρ⁻ → NOT ENOUGH ENERGY"},
	react_key("rho+","rho-","ENERGY"): {"products":["pi+","pi-"], "note":"ρ⁺ ρ⁻ → π⁺ π⁻"},
    react_key("Lambda","Lambda_anti"): {"products":["Lambda","Lambda_anti"], "note":"Λ Λ̄ → NOT ENOUGH ENERGY"},
	react_key("Lambda","Lambda_anti","ENERGY"): {"products":["pi+","pi-","K+","K-"], "note":"Λ Λ̄ → π⁺ + π⁻ + K⁺ + K⁻"},
    react_key("Lambda0","Lambda0_anti"): {"products":["Lambda0","Lambda0_anti"], "note":"Λ⁰ Λ̄⁰ → NOT ENOUGH ENERGY"},
	react_key("Lambda0","Lambda0_anti","ENERGY"): {"products":["pi+","pi-","K+","K-"], "note":"Λ⁰ Λ̄⁰ → π⁺ + π⁻ + K⁺ + K⁻"},
    react_key("Sigma+","Sigma-"): {"products":["Sigma+","Sigma-"], "note":"Σ⁺ Σ⁻ → NOT ENOUGH ENERGY"},
	react_key("Sigma+","Sigma-","ENERGY"): {"products":["pi+","pi-","K+","K-","pi0"], "note":"Σ⁺ Σ⁻ → π⁺ + π⁻ + π⁰ + K⁺ + K⁻"},
    react_key("Sigma0","Sigma0_anti"): {"products":["Sigma0","Sigma0_anti"], "note":"Σ⁰ Σ̄⁰ → NOT ENOUGH ENERGY"},
	react_key("Sigma0","Sigma0_anti","ENERGY"): {"products":["pi+","pi-","K+","K-","pi0"], "note":"Σ⁰ Σ̄⁰ → π⁺ + π⁻ + + π⁰ + K⁺ + K⁻"},
    react_key("Xi0","Xi0_anti"): {"products":["Xi0","Xi0_anti"], "note":"Ξ⁰ Ξ̄⁰ → NOT ENOUGH ENERGY"},
	react_key("Xi0","Xi0_anti","ENERGY"): {"products":["pi+","pi-","K+","K-"], "note":"Ξ⁰ Ξ̄⁰ → π⁺ + π⁻ + K⁺ + K⁻"},
    react_key("Xi-","Xi+"): {"products":["Xi+","Xi-"], "note":"Ξ⁻ Ξ⁺ → NOT ENOUGH ENERGY"},
	react_key("Xi-","Xi+","ENERGY"): {"products":["pi+","pi-","K+","K-"], "note":"Ξ⁻ Ξ⁺ → π⁺ + π⁻ + K⁺ + K⁻"},
    react_key("Omega-","Omega+"): {"products":["Omega+","Omega-"], "note":"Ω⁻ Ω⁺ → NOT ENOUGH ENERGY"},
	react_key("Omega-","Omega+","ENERGY"): {"products":["pi+","pi-","K+","K-","pi0"], "note":"Ω⁻ Ω⁺ → π⁺ + π⁻ + π⁰ + K⁺ + K⁻"},
    react_key("Delta++","Delta--"): {"products":["Delta++","Delta--"], "note":"Δ⁺⁺ Δ⁻⁻ → NOT ENOUGH ENERGY"},
	react_key("Delta++","Delta--","ENERGY"): {"products":["pi+","pi-","pi0"], "note":"Δ⁺⁺ Δ⁻⁻ → π⁺ + π⁻ + π⁰"},
    react_key("Delta+","Delta-"): {"products":["Delta+","Delta-"], "note":"Δ⁺ Δ⁻ → NOT ENOUGH ENERGY"},
	react_key("Delta+","Delta-","ENERGY"): {"products":["pi+","pi-","pi0"], "note":"Δ⁺ Δ⁻ → π⁺ + π⁻ + π⁰"},
    react_key("Delta0","Delta0_anti"): {"products":["Delta0","Delta0_anti"], "note":"Δ⁰ Δ̄⁰ → NOT ENOUGH ENERGY"},
	react_key("Delta0","Delta0_anti","ENERGY"): {"products":["pi+","pi-","pi0"], "note":"Δ⁰ Δ̄⁰ → π⁺ + π⁻ + π⁰"},
    react_key("e-","e+"): {"products":["photon","photon"], "note":"e⁻ e⁺ → 2γ"},
    react_key("p","panti"): {"products":["p","panti"], "note":"p p̅ → NOT ENOUGH ENERGY"},
	react_key("p","panti","ENERGY"): {"products":["pi+","pi-","pi0"], "note":"p p̅ → π⁺ + π⁻ + π⁰"},
    react_key("pi+","pi-"): {"products":["pi+","pi-"], "note":"π⁺ π⁻ → NOT ENOUGH ENERGY"},
	react_key("pi+","pi-","ENERGY"): {"products":["photon","photon"], "note":"π⁺ π⁻ → 2γ"},
    react_key("d","s̄"): {"products":["K0"], "note":"ds̄ → K0"},
    react_key("d̄","s"): {"products":["K0anti"], "note":"ds̄ → K̄0"},
    react_key("BREAKER","p"): {"products":["u","u","d"], "note":"p → u+u+d"},
    react_key("BREAKER","n"): {"products":["u","d","d"], "note":"n → u+d+d"},
    react_key("DECAYER","n"): {"products":["p","e-","nu_eanti"], "note":"n →(W⁻) p e- ν̅ₑ"},
    react_key("DECAYER","pi0"): {"products":["photon","photon"], "note":"π⁰ → γ+γ"},
    react_key("DECAYER","pi+"): {"products":["mu+","nu_mu"], "note":"π⁺ → μ⁺+νμ"},
    react_key("DECAYER","pi-"): {"products":["mu-","nu_muanti"], "note":"π⁻ → μ⁻+ν̅μ"},
    react_key("DECAYER","K+"): {"products":["mu+","nu_mu"], "note":"K⁺ → μ⁺+νμ"},
    react_key("DECAYER","K-"): {"products":["mu-","nu_muanti"], "note":"K⁻ → μ⁻+ν̅μ"},
    react_key("DECAYER","K0"): {"products":["pi+","pi-"], "note":"K⁰ → π⁺+π⁻"},
    react_key("DECAYER","Lambda0"): {"products":["p","pi-"], "note":"Λ⁰ → p+π⁻"},
    react_key("DECAYER","Sigma+"): {"products":["p","pi0"], "note":"Σ⁺ → p+π⁰"},
    react_key("DECAYER","Sigma0"): {"products":["Lambda0","photon"], "note":"Σ⁰ → Λ⁰+γ"},
    react_key("DECAYER","Sigma-"): {"products":["n","pi-"], "note":"Σ⁻ → n+π⁻"},
    react_key("DECAYER","Xi0"): {"products":["Lambda0","pi0"], "note":"Ξ⁰ → Λ⁰+π⁰"},
    react_key("DECAYER","Xi-"): {"products":["Lambda0","pi-"], "note":"Ξ⁻ → Λ⁰+π⁻"},
    react_key("DECAYER","Omega-"): {"products":["Lambda0","K-"], "note":"Ω⁻ → Λ⁰+K⁻"},
    react_key("DECAYER","Delta++"): {"products":["p","pi+"], "note":"Δ⁺⁺ → p+π⁺"},
    react_key("DECAYER","Delta+"): {"products":["p","pi0"], "note":"Δ⁺ → p+π⁰"},
    react_key("DECAYER","Delta0"): {"products":["n","pi0"], "note":"Δ⁰ → n+π⁰"},
    react_key("DECAYER","Delta-"): {"products":["n","pi-"], "note":"Δ⁻ → n+π⁻"},
    react_key("BREAKER","Lambda"): {"products":["u","d","s"], "note":"Λ → uds"},
    react_key("BREAKER","Lambda_anti"): {"products":["ū","d̄","s̄"], "note":"Λ̄ → ū+d̄+s̄"},
    react_key("BREAKER","Sigma+"): {"products":["u","u","s"], "note":"Σ⁺ → uus"},
    react_key("BREAKER","Sigma0"): {"products":["u","d","s"], "note":"Σ⁰ → uds"},
    react_key("BREAKER","Sigma-"): {"products":["d","d","s"], "note":"Σ⁻ → dds"},
    react_key("BREAKER","Xi0"): {"products":["u","s","s"], "note":"Ξ⁰ → uss"},
    react_key("BREAKER","Xi-"): {"products":["d","s","s"], "note":"Ξ⁻ → dss"},
    react_key("BREAKER","Omega-"): {"products":["s","s","s"], "note":"Ω⁻ → sss"},
    react_key("BREAKER","Delta++"): {"products":["u","u","u"], "note":"Δ⁺⁺ → uuu"},
    react_key("BREAKER","Delta+"): {"products":["u","u","d"], "note":"Δ⁺ → uud"},
    react_key("BREAKER","Delta0"): {"products":["u","d","d"], "note":"Δ⁰ → udd"},
    react_key("BREAKER","Delta-"): {"products":["d","d","d"], "note":"Δ⁻ → ddd"},
	react_key("BREAKER","panti"): {"products":["ū","ū","d̄"], "note":"p̅ → ū+ū+d̄"},
    react_key("BREAKER","nanti"): {"products":["ū","d̄","d̄"], "note":"n̅ → ū+d̄+d̄"},
    react_key("BREAKER","Sigma0_anti"): {"products":["ū","d̄","s̄"], "note":"Σ̄⁰ → ū+d̄+s̄"},
    react_key("BREAKER","Xi0_anti"): {"products":["ū","s̄","s̄"], "note":"Ξ̄⁰ → ū+s̄+s̄"},
    react_key("BREAKER","Xi+"): {"products":["d̄","s̄","s̄"], "note":"Ξ⁺ → d̄+s̄+s̄"},
    react_key("BREAKER","Omega+"): {"products":["s̄","s̄","s̄"], "note":"Ω⁺ → s̄+s̄+s̄"},
    react_key("BREAKER","Delta--"): {"products":["d̄","d̄","d̄"], "note":"Δ̄⁻⁻ → d̄+d̄+d̄"},
    react_key("BREAKER","Delta0_anti"): {"products":["ū","d̄","d̄"], "note":"Δ̄⁰ → ū+d̄+d̄"},
    react_key("u","u","d"): {"products":["Delta+"], "note":"uud → Δ⁺"},
    react_key("u","d","d"): {"products":["Delta0"], "note":"udd → Δ⁰"},
	react_key("u","u","d"): {"products":["p"], "note":"uud → p"},
    react_key("u","d","d"): {"products":["n"], "note":"udd → n"},
	react_key("SPINCHANGER","p"): {"products":["Delta+"], "note":"p → Δ⁺"},
	react_key("SPINCHANGER","n"): {"products":["Delta0"], "note":"p → Δ⁰"},
    react_key("SPINCHANGER","Delta+"): {"products":["p"], "note":"Δ⁺ → p"},
    react_key("SPINCHANGER","Delta0"): {"products":["n"], "note":"Δ⁰ → n"},
    react_key("u","d","s"): {"products":["Lambda"], "note":"uds → Λ"},
    react_key("ū","d̄","s̄"): {"products":["Lambda_anti"], "note":"ūd̄s̄ → Λ̄"},
    react_key("u","u","s"): {"products":["Sigma+"], "note":"uus → Σ⁺"},
    react_key("u","d","s"): {"products":["Sigma0"], "note":"uds → Σ⁰"},
    react_key("d","d","s"): {"products":["Sigma-"], "note":"dds → Σ⁻"},
    react_key("u","s","s"): {"products":["Xi0"], "note":"uss → Ξ⁰"},
    react_key("d","s","s"): {"products":["Xi-"], "note":"dss → Ξ⁻"},
    react_key("s","s","s"): {"products":["Omega-"], "note":"sss → Ω⁻"},
    react_key("u","u","u"): {"products":["Delta++"], "note":"uuu → Δ⁺⁺"},
    react_key("d","d","d"): {"products":["Delta-"], "note":"ddd → Δ⁻"},
	react_key("ū","ū","d̄"): {"products":["panti"], "note":"ū ū d̄ → p̅"},
    react_key("ū","d̄","d̄"): {"products":["nanti"], "note":"ūd̄d̄ → n̅"},
    react_key("ū","d̄","s̄"): {"products":["Sigma0_anti"], "note":"ūd̄s̄ → Σ̄⁰"},
    react_key("ū","s̄","s̄"): {"products":["Xi0_anti"], "note":"ūs̄s̄ → Ξ̄⁰"},
    react_key("d̄","s̄","s̄"): {"products":["Xi+"], "note":"d̄s̄s̄ → Ξ⁺"},
    react_key("s̄","s̄","s̄"): {"products":["Omega+"], "note":"s̄s̄s̄ → Ω⁺"},
    react_key("ū","ū","ū"): {"products":["Delta--"], "note":"ūūū → Δ̄⁻⁻"},
    react_key("ū","ū","d̄"): {"products":["Delta-_anti"], "note":"ūūd̄ → Δ̄⁻"},
    react_key("ū","d̄","d̄"): {"products":["Delta0_anti"], "note":"ūd̄d̄ → Δ̄⁰"},
    react_key("d̄","d̄","d̄"): {"products":["Delta+"], "note":"d̄d̄d̄ → Δ̄⁺"},
    react_key("u","s̄"): {"products":["K+"], "note":"u s̄ → K⁺"},
    react_key("s","ū"): {"products":["K-"], "note":"s ū → K⁻"},
    react_key("s","s̄"): {"products":["s","s̄"], "note":"s s̄ → NOT ENOUGH ENERGY"},
	react_key("s","s̄","ENERGY"): {"products":["phi"], "note":"s s̄ → φ"},
    react_key("c","c̄"): {"products":["c","c̄"], "note":"c c̄ → NOT ENOUGH ENERGY"},
	react_key("c","c̄","ENERGY"): {"products":["psi"], "note":"c c̄ → Ψ"},
    react_key("b","b̄"): {"products":["b","b̄"], "note":"b b̄ → NOT ENOUGH ENERGY"},
	react_key("b","b̄","ENERGY"): {"products":["Upsilon"], "note":"b b̄ → ϒ"},
	react_key("BREAKER","rho+"): {"products":["u","d̄"], "note":"ρ⁺ → u + d̄"},
    react_key("BREAKER","rho-"): {"products":["d","ū"], "note":"ρ⁻ → d + ū"},
    react_key("BREAKER","rho0"): {"products":["u","ū"], "note":"ρ⁰ → u + ū"},
    react_key("BREAKER","phi"): {"products":["s","s̄"], "note":"φ → s + s̄"},
    react_key("BREAKER","eta"): {"products":["u","ū"], "note":"η → u + ū"},
    react_key("BREAKER","eta_prime"): {"products":["s","s̄"], "note":"η′ → s + s̄"},
    react_key("BREAKER","psi"): {"products":["c","c̄"], "note":"Ψ → c + c̄"},
    react_key("BREAKER","Upsilon"): {"products":["b","b̄"], "note":"ϒ → b + b̄"},
    react_key("phi","phi"): {"products":["phi","phi"], "note":"φ φ → NOT ENOUGH ENERGY"},
	react_key("phi","phi","ENERGY"): {"products":["K+","K-"], "note":"φ φ → K⁺ + K⁻"},
    react_key("u","ū"): {"products":["eta"], "note":"u ū → η"},
    react_key("QUANTUMCHANGER","pi+"): {"products":["rho+"], "note":"π⁺ → ρ⁺"},
    react_key("QUANTUMCHANGER","pi-"): {"products":["rho-"], "note":"π⁻ → ρ⁻"},
    react_key("QUANTUMCHANGER","pi0"): {"products":["rho0"], "note":"π⁰ → ρ⁰"},
    react_key("QUANTUMCHANGER","rho+"): {"products":["pi+"], "note":"ρ⁺ → π⁺"},
    react_key("QUANTUMCHANGER","rho-"): {"products":["pi-"], "note":"ρ⁻ → π⁻"},
    react_key("QUANTUMCHANGER","rho0"): {"products":["pi0"], "note":"ρ⁰ → π⁰"},
	react_key("DECAYER","tau-"): {"products":["mu-","nu_tau","nu_muanti"], "note":"τ⁻ →(W⁻) μ⁻ ν̅_μ ν_τ"},
	react_key("n","nu_mu","ENERGY"): {"products":["mu-","p"], "note":"n + ν_μ → μ⁻ + p"},
	react_key("n","nu_mu"): {"products":["nu_mu","n"], "note":"n + ν_μ → NOT ENOUGH ENERGY"},
	react_key("n","nu_mu","ENERGY"): {"products":["mu-","p"], "note":"n + ν_μ → μ⁻ + p"},
	react_key("DECAYER","D+"): {"products":["mu+","nu_mu"], "note":"D⁺ → μ⁺ ν_μ"},
	react_key("DECAYER","B0"): {"products":["mu+","mu-"], "note":"B⁰ → μ⁺ μ⁻"},
	react_key("DECAYER","mu-"): {"products":["nu_mu","nu_eanti","e-"], "note":"μ⁻ →(W⁻) ν_μ ν̅ₑ e⁻"},
    react_key("DECAYER","p"): {"products":["n","nu_e","e+"], "note":"p → ν_e n e⁺"},
	react_key("DECAYER","ENERGY","pi+"): {"products":["mu+","nu_mu"], "note":"π⁺ →(W⁺) ν_μ μ⁺"},
	react_key("DECAYER","ENERGY","K+"): {"products":["mu+","nu_mu"], "note":"K⁺ →(W⁺) ν_μ μ⁺"},
	react_key("mu-","p"): {"products":["n","nu_mu"], "note":"μ⁻ p → ν_μ n"},
	react_key("u","ū"): {"products":["tau-","tau+"], "note":"u ū → τ⁻ τ⁺"},
	react_key("u","ū","DECAYER"): {"products":["pi-","nu_tau","pi+","nu_tauanti"], "note":"u ū →  π⁻ ν_τ , π⁺ ν̅_τ"},
    react_key("DECAYER","D+"): {"products":["tau-","tau+"], "note":"u ū →(W⁻) τ⁻ τ⁺"},
	react_key("DECAYER","Z0"): {"products":["mu-","mu+"], "note":"Z⁰ → μ⁻ μ⁺"},
	react_key("e-","nu_tau"): {"products":["nu_tau","e-"], "note":" ν_τ e⁻ →(Z⁰) ν_τ e⁻"},
	react_key("DECAYER","W+"): {"products":["mu+","nu_muanti"], "note":"Z⁰ → ν̅_μ μ⁺"},
	react_key("DECAYER","mu+"): {"products":["nu_eanti","nu_muanti","e-"], "note":"μ⁺ →(W⁻) ν̅_μ e⁻ ν̅ₑ"},
	react_key("DECAYER","psi"): {"products":["mu+","mu-"], "note":"Ψ → μ⁻ μ⁺"},
	react_key("DECAYER","p","ENERGY"): {"products":["n","nu_e","e+"], "note":"p → ν_e n e⁺"},
	react_key("tau+","nu_tauanti","b̄"): {"products":["t̄"], "note":"τ⁺ + ν̅_τ →(W⁺) + b̄ → t̄"},
	react_key("DECAYER","Xi+"): {"products":["Lambda+","pi0"], "note":"Ξ⁺ → Λ⁰+π⁰"},
	react_key("gluon","gluon","ENERGY"): {"products":["q","q-"], "note":"g g →(Z⁰) q q⁻"},
	react_key("gluon","gluon","tau-","tau+","VIRTUALIZER","H0"): {"products":["lepton+","lepton+","lepton+","lepton+"], "note":"g g t̄ t⁺ → H⁰ → Z⁰ Z⁰ → ℓ⁺ ℓ⁺ ℓ⁺ ℓ⁺"},
	react_key("lepton-","lepton+"): {"products":["photon","photon"], "note":"ℓ ℓ⁺ → 2γ"},
	react_key("lepton-","lepton+","ENERGY"): {"products":["Z0"], "note":"ℓ ℓ⁺ → Z⁰"},
	react_key("gluon","gluon","b","b̄","VIRTUALIZER","ENERGY"): {"products":["H0"], "note":"g g b̄ b → (b̄⇆b) H⁰"},
	react_key("q","q-","V","H0","VIRTUALIZER","DECAYER"): {"products":["b","b̄"], "note":"q q̄ → (V) → (H⁰) → b b̄"},
	react_key("q","q-","V","VIRTUALIZER","DECAYER"): {"products":["q","q-"], "note":"q q̄ → (V) → q q̄"},
	react_key("DECAYER","d⁻"): {"products":["u","W-"], "note":"d⁻ → W⁻ u"},
	react_key("gluon","gluon","ENERGY"): {"products":["H0","tau-","tau+"], "note":"g g → t̄ τ⁺ H⁰"},
	react_key("q","q-","V","VIRTUALIZER","ENERGY"): {"products":["V","H0"], "note":"q q̄ → (V) → H⁰ V"},
	react_key("ENERGY","ENERGY"): {"products":["photon","photon","photon","photon","photon","photon","photon","photon","photon","photon"], "note":" → γ γ γ γ γ γ γ γ γ γ"},
    react_key("VIRTUALIZER","e-"): {"products":["VIRTUAL PARTICLE"], "note":"e⁻ → (e⁻)"},
    react_key("VIRTUALIZER","e+"): {"products":["VIRTUAL PARTICLE"], "note":"e⁺ → (e⁺)"},
    react_key("VIRTUALIZER","mu-"): {"products":["VIRTUAL PARTICLE"], "note":"μ⁻ → (μ⁻)"},
    react_key("VIRTUALIZER","mu+"): {"products":["VIRTUAL PARTICLE"], "note":"μ⁺ → (μ⁺)"},
    react_key("VIRTUALIZER","tau-"): {"products":["VIRTUAL PARTICLE"], "note":"τ⁻ → (τ⁻)"},
    react_key("VIRTUALIZER","tau+"): {"products":["VIRTUAL PARTICLE"], "note":"τ⁺ → (τ⁺)"},
    react_key("VIRTUALIZER","nu_e"): {"products":["VIRTUAL PARTICLE"], "note":"νₑ → (νₑ)"},
    react_key("VIRTUALIZER","nu_eanti"): {"products":["VIRTUAL PARTICLE"], "note":"ν̅ₑ → (ν̅ₑ)"},
    react_key("VIRTUALIZER","nu_mu"): {"products":["VIRTUAL PARTICLE"], "note":"ν_μ → (ν_μ)"},
    react_key("VIRTUALIZER","nu_muanti"): {"products":["VIRTUAL PARTICLE"], "note":"ν̅_μ → (ν̅_μ)"},
    react_key("VIRTUALIZER","nu_tau"): {"products":["VIRTUAL PARTICLE"], "note":"ν_τ → (ν_τ)"},
    react_key("VIRTUALIZER","nu_tauanti"): {"products":["VIRTUAL PARTICLE"], "note":"ν̅_τ → (ν̅_τ)"},
    react_key("VIRTUALIZER","u"): {"products":["VIRTUAL PARTICLE"], "note":"u → (u)"},
    react_key("VIRTUALIZER","ū"): {"products":["VIRTUAL PARTICLE"], "note":"ū → (ū)"},
    react_key("VIRTUALIZER","d"): {"products":["VIRTUAL PARTICLE"], "note":"d → (d)"},
    react_key("VIRTUALIZER","d̄"): {"products":["VIRTUAL PARTICLE"], "note":"d̄ → (d̄)"},
    react_key("VIRTUALIZER","s"): {"products":["VIRTUAL PARTICLE"], "note":"s → (s)"},
    react_key("VIRTUALIZER","s̄"): {"products":["VIRTUAL PARTICLE"], "note":"s̄ → (s̄)"},
    react_key("VIRTUALIZER","c"): {"products":["VIRTUAL PARTICLE"], "note":"c → (c)"},
    react_key("VIRTUALIZER","c̄"): {"products":["VIRTUAL PARTICLE"], "note":"c̄ → (c̄)"},
    react_key("VIRTUALIZER","b"): {"products":["VIRTUAL PARTICLE"], "note":"b → (b)"},
    react_key("VIRTUALIZER","b̄"): {"products":["VIRTUAL PARTICLE"], "note":"b̄ → (b̄)"},
    react_key("VIRTUALIZER","t"): {"products":["VIRTUAL PARTICLE"], "note":"t → (t)"},
    react_key("VIRTUALIZER","t̄"): {"products":["VIRTUAL PARTICLE"], "note":"t̄ → (t̄)"},
    react_key("VIRTUALIZER","photon"): {"products":["VIRTUAL PARTICLE"], "note":"γ → (γ)"},
    react_key("VIRTUALIZER","gluon"): {"products":["VIRTUAL PARTICLE"], "note":"g → (g)"},
    react_key("VIRTUALIZER","W+"): {"products":["VIRTUAL PARTICLE"], "note":"W⁺ → (W⁺)"},
    react_key("VIRTUALIZER","W-"): {"products":["VIRTUAL PARTICLE"], "note":"W⁻ → (W⁻)"},
    react_key("VIRTUALIZER","Z0"): {"products":["VIRTUAL PARTICLE"], "note":"Z⁰ → (Z⁰)"},
    react_key("VIRTUALIZER","H0"): {"products":["VIRTUAL PARTICLE"], "note":"H → (H)"},
    react_key("VIRTUALIZER","p"): {"products":["VIRTUAL PARTICLE"], "note":"p → (p)"},
    react_key("VIRTUALIZER","panti"): {"products":["VIRTUAL PARTICLE"], "note":"p̅ → (p̅)"},
    react_key("VIRTUALIZER","n"): {"products":["VIRTUAL PARTICLE"], "note":"n → (n)"},
    react_key("VIRTUALIZER","nanti"): {"products":["VIRTUAL PARTICLE"], "note":"n̅ → (n̅)"},
    react_key("VIRTUALIZER","Lambda0"): {"products":["VIRTUAL PARTICLE"], "note":"Λ⁰ → (Λ⁰)"},
    react_key("VIRTUALIZER","Lambda0_anti"): {"products":["VIRTUAL PARTICLE"], "note":"Λ̄⁰ → (Λ̄⁰)"},
    react_key("VIRTUALIZER","Lambda"): {"products":["VIRTUAL PARTICLE"], "note":"Λ → (Λ)"},
    react_key("VIRTUALIZER","Lambda_anti"): {"products":["VIRTUAL PARTICLE"], "note":"Λ̄ → (Λ̄)"},
    react_key("VIRTUALIZER","Sigma+"): {"products":["VIRTUAL PARTICLE"], "note":"Σ⁺ → (Σ⁺)"},
    react_key("VIRTUALIZER","Sigma0"): {"products":["VIRTUAL PARTICLE"], "note":"Σ⁰ → (Σ⁰)"},
    react_key("VIRTUALIZER","Sigma-"): {"products":["VIRTUAL PARTICLE"], "note":"Σ⁻ → (Σ⁻)"},
    react_key("VIRTUALIZER","Sigma0_anti"): {"products":["VIRTUAL PARTICLE"], "note":"Σ̄⁰ → (Σ̄⁰)"},
    react_key("VIRTUALIZER","Xi0"): {"products":["VIRTUAL PARTICLE"], "note":"Ξ⁰ → (Ξ⁰)"},
    react_key("VIRTUALIZER","Xi-"): {"products":["VIRTUAL PARTICLE"], "note":"Ξ⁻ → (Ξ⁻)"},
    react_key("VIRTUALIZER","Xi0_anti"): {"products":["VIRTUAL PARTICLE"], "note":"Ξ̄⁰ → (Ξ̄⁰)"},
    react_key("VIRTUALIZER","Xi+"): {"products":["VIRTUAL PARTICLE"], "note":"Ξ⁺ → (Ξ⁺)"},
    react_key("VIRTUALIZER","Omega-"): {"products":["VIRTUAL PARTICLE"], "note":"Ω⁻ → (Ω⁻)"},
    react_key("VIRTUALIZER","Omega+"): {"products":["VIRTUAL PARTICLE"], "note":"Ω⁺ → (Ω⁺)"},
    react_key("VIRTUALIZER","Delta++"): {"products":["VIRTUAL PARTICLE"], "note":"Δ⁺⁺ → (Δ⁺⁺)"},
    react_key("VIRTUALIZER","Delta+"): {"products":["VIRTUAL PARTICLE"], "note":"Δ⁺ → (Δ⁺)"},
    react_key("VIRTUALIZER","Delta0"): {"products":["VIRTUAL PARTICLE"], "note":"Δ⁰ → (Δ⁰)"},
    react_key("VIRTUALIZER","Delta-"): {"products":["VIRTUAL PARTICLE"], "note":"Δ⁻ → (Δ⁻)"},
    react_key("VIRTUALIZER","Delta--"): {"products":["VIRTUAL PARTICLE"], "note":"Δ̄⁻⁻ → (Δ̄⁻⁻)"},
    react_key("VIRTUALIZER","Delta-_anti"): {"products":["VIRTUAL PARTICLE"], "note":"Δ̄⁻ → (Δ̄⁻)"},
    react_key("VIRTUALIZER","Delta+_anti"): {"products":["VIRTUAL PARTICLE"], "note":"Δ̄⁺ → (Δ̄⁺)"},
    react_key("VIRTUALIZER","pi+"): {"products":["VIRTUAL PARTICLE"], "note":"π⁺ → (π⁺)"},
    react_key("VIRTUALIZER","pi-"): {"products":["VIRTUAL PARTICLE"], "note":"π⁻ → (π⁻)"},
    react_key("VIRTUALIZER","pi0"): {"products":["VIRTUAL PARTICLE"], "note":"π⁰ → (π⁰)"},
    react_key("VIRTUALIZER","K+"): {"products":["VIRTUAL PARTICLE"], "note":"K⁺ → (K⁺)"},
    react_key("VIRTUALIZER","K-"): {"products":["VIRTUAL PARTICLE"], "note":"K⁻ → (K⁻)"},
    react_key("VIRTUALIZER","K0"): {"products":["VIRTUAL PARTICLE"], "note":"K⁰ → (K⁰)"},
    react_key("VIRTUALIZER","K0anti"): {"products":["VIRTUAL PARTICLE"], "note":"K̄0 → (K̄0)"},
    react_key("VIRTUALIZER","rho+"): {"products":["VIRTUAL PARTICLE"], "note":"ρ⁺ → (ρ⁺)"},
    react_key("VIRTUALIZER","rho-"): {"products":["VIRTUAL PARTICLE"], "note":"ρ⁻ → (ρ⁻)"},
    react_key("VIRTUALIZER","rho0"): {"products":["VIRTUAL PARTICLE"], "note":"ρ⁰ → (ρ⁰)"},
    react_key("VIRTUALIZER","phi"): {"products":["VIRTUAL PARTICLE"], "note":"φ → (φ)"},
    react_key("VIRTUALIZER","eta"): {"products":["VIRTUAL PARTICLE"], "note":"η → (η)"},
    react_key("VIRTUALIZER","psi"): {"products":["VIRTUAL PARTICLE"], "note":"Ψ → (Ψ)"},
    react_key("VIRTUALIZER","Upsilon"): {"products":["VIRTUAL PARTICLE"], "note":"Υ → (Υ)"},
    react_key("VIRTUALIZER","D+"): {"products":["VIRTUAL PARTICLE"], "note":"D⁺ → (D⁺)"},
    react_key("VIRTUALIZER","D0"): {"products":["VIRTUAL PARTICLE"], "note":"D⁰ → (D⁰)"},
    react_key("VIRTUALIZER","B+"): {"products":["VIRTUAL PARTICLE"], "note":"B⁺ → (B⁺)"},
    react_key("VIRTUALIZER","B0"): {"products":["VIRTUAL PARTICLE"], "note":"B⁰ → (B⁰)"},
    react_key("VIRTUALIZER","lepton"): {"products":["VIRTUAL PARTICLE"], "note":"ℓ → (ℓ)"},
    react_key("VIRTUALIZER","lepton+"): {"products":["VIRTUAL PARTICLE"], "note":"ℓ⁺ → (ℓ⁺)"},
    react_key("VIRTUALIZER","q"): {"products":["VIRTUAL PARTICLE"], "note":"q → (q)"},
    react_key("VIRTUALIZER","q-"): {"products":["VIRTUAL PARTICLE"], "note":"q⁻ → (q⁻)"},
    react_key("VIRTUALIZER","V"): {"products":["VIRTUAL PARTICLE"], "note":"V → (V)"},
    react_key("VIRTUALIZER","BREAKER"): {"products":["VIRTUAL PARTICLE"], "note":"× → (×)"},
    react_key("VIRTUALIZER","SPINCHANGER"): {"products":["VIRTUAL PARTICLE"], "note":"♦ → (♦)"},
    react_key("VIRTUALIZER","QUANTUMCHANGER"): {"products":["VIRTUAL PARTICLE"], "note":"¿ → (¿)"},
    react_key("VIRTUALIZER","DECAYER"): {"products":["VIRTUAL PARTICLE"], "note":"# → (#)"},
    react_key("VIRTUALIZER","ENERGY"): {"products":["VIRTUAL PARTICLE"], "note":"ɇ → (ɇ)"},
    react_key("VIRTUALIZER","VIRTUALIZER"): {"products":["VIRTUAL PARTICLE"], "note":"⍟ → (⍟)"},
    react_key("VIRTUALIZER","VIRTUAL PARTICLE"): {"products":["VIRTUAL PARTICLE"], "note":"Ø → (Ø)"},
    react_key("VIRTUAL PARTICLE","DECAYER"): {"products":["EMPTY"], "note":"Ø → "},
	react_key("nanti","nu_tau","Z0","QUANTUMCHANGER"): {"products":["psi"], "note":"YBT → Ψ (COMBINATION ACCEPTED)"},
	react_key("Upsilon","B0","tau-","QUANTUMCHANGER"): {"products":["psi"], "note":"YBT → Ψ (COMBINATION ACCEPTED)"},
}

MAX_REACTANTS = 6  # MAX REACTANS

# TEXT
class Text:
    def __init__(self, text, pos, color=(255,240,180), lifetime=2.2):
        self.text = text
        self.x, self.y = float(pos[0]), float(pos[1])
        self.vx = random.uniform(-10,10)
        self.vy = random.uniform(-30,-10)
        self.color = color
        self.age = 0.0
        self.lifetime = lifetime
    def step(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
    def alive(self): return self.age < self.lifetime
    def draw(self, surf):
        alpha = max(0, 255 * (1 - self.age / self.lifetime))
        surf_txt = FONT_BIG.render(self.text, True, self.color)
        surf_txt.set_alpha(int(alpha))
        surf.blit(surf_txt, (int(self.x - surf_txt.get_width()/2), int(self.y - surf_txt.get_height()/2)))

# PARTICLE CLASS
class Particle:
    _id_ctr = 0
    def __init__(self, species, pos, vel=(0,0)):
        if species not in PARTICLES:
            raise KeyError(f"Species {species} unknown")
        self.id = Particle._id_ctr; Particle._id_ctr += 1
        self.species = species
        self.symbol = PARTICLES[species]["symbol"]
        self.color = PARTICLES[species]["color"]
        self.mass = PARTICLES[species]["mass"]
        self.radius = PARTICLES[species]["radius"]
        self.pos = [float(pos[0]), float(pos[1])]
        self.vel = [float(vel[0]), float(vel[1])]
        self.trail = deque(maxlen=140)
    def step(self, dt):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt

        bounced = False

        if self.pos[0] < self.radius:
            self.pos[0] = self.radius; self.vel[0] *= -1; bounced = True
        if self.pos[0] > WORLD_W - self.radius:
            self.pos[0] = WORLD_W - self.radius; self.vel[0] *= -1; bounced = True
        if self.pos[1] < self.radius:
            self.pos[1] = self.radius; self.vel[1] *= -1; bounced = True
        if self.pos[1] > WIN_H - self.radius:
            self.pos[1] = WIN_H - self.radius; self.vel[1] *= -1; bounced = True
        if bounced:
            random.choice(bounce_sounds).play()
        self.trail.append((self.pos[0], self.pos[1]))
	
    def draw(self, surf):
        # TRAIL
        pts = list(self.trail)
        if len(pts) > 1:
            for i in range(1, len(pts)):
                x1, y1 = pts[i-1]
                x2, y2 = pts[i]
                col = (*self.color, int(180 * i / len(pts)))
                pygame.draw.aaline(surf, col, (x1, y1), (x2, y2))
        # PARTICLE
        pygame.draw.circle(surf, (10,10,12), (int(self.pos[0]), int(self.pos[1])), int(self.radius+2))
        pygame.draw.circle(surf, self.color, (int(self.pos[0]), int(self.pos[1])), int(self.radius))
        # CONTRAST SYMBOL
        r, g, b = self.color
        brightness = (r + g + b) / 3
        text_color = (0,0,0) if brightness > 150 else (255,255,255)
        sym_surf = FONT.render(self.symbol, True, text_color)
        surf.blit(sym_surf, (int(self.pos[0]-sym_surf.get_width()/2), int(self.pos[1]-sym_surf.get_height()/2)))
# SIMULATOR
class Simulator:
    def __init__(self):
        self.particles = []
        self.texts = []
        self.time = 0.0
        self.last_reaction = ""
    def add(self, particle):
        self.particles.append(particle)

    def _react(self, parts, products, note):
        # CENTER DOT
        mx = sum(p.pos[0] for p in parts) / len(parts)
        my = sum(p.pos[1] for p in parts) / len(parts)
        # DELETE REACTANS
        for p in parts:
            if p in self.particles:
                self.particles.remove(p)
        # RANDOM MOMENTUM
        for prod in products:
            angle = random.random() * 2 * math.pi
            speed = random.uniform(40, 220)
            vx, vy = math.cos(angle)*speed, math.sin(angle)*speed
            self.add(Particle(prod, (mx, my), (vx, vy)))
        self.texts.clear()
        self.texts.append(Text(note, (mx, my)))
        self.last_reaction = note
        reaction_sound.play()

    def _clustered(self, parts):
        # RANGE OF COLLIDING
        for a,b in itertools.combinations(parts, 2):
            dx,dy = b.pos[0]-a.pos[0], b.pos[1]-a.pos[1]
            dist = math.hypot(dx,dy)
            if dist > (a.radius + b.radius):
                return False
        return True

    def step(self, dt):
        self.time += dt
        for p in list(self.particles):
            p.step(dt)
        # FIRST TRY MORE COMPLEX REACTIONS
        self._find_and_apply_reactions()
        for t in self.texts:
            t.step(dt)
        self.texts = [t for t in self.texts if t.alive()]

    def _find_and_apply_reactions(self):
        # 6 BODY IS MORE IMORTANT (AS A MAX)
        for k in (6, 5, 4, 3, 2):
            combos = list(itertools.combinations(self.particles, k))
            for parts in combos:
                # RANGE IF
                if not self._clustered(parts):
                    continue
                rk = react_key(*[p.species for p in parts])
                if rk in REACTIONS:
                    data = REACTIONS[rk]
                    self._react(parts, data["products"], data["note"])
                    time.sleep(0.2)
                    return  # 0.2 SECOND WAIT FOR REACTION

# HUD
def hud(sim, selected_species, paused):
    total_ke = sum(0.5 * p.mass * (p.vel[0]**2 + p.vel[1]**2) for p in sim.particles)
    total_px = sum(p.mass * p.vel[0] for p in sim.particles)
    total_py = sum(p.mass * p.vel[1] for p in sim.particles)

    line1 = f"Time: {sim.time:.2f} s  Particles: {len(sim.particles)}"
    surf1 = FONT_BIG.render(line1, True, (240,240,240))
    screen.blit(surf1, (12, 10))
	
    line1 = f"YAMAN'S PARTICLE COLLIDER!"
    surf1 = FONT_BIG.render(line1, True, (240,240,150))
    screen.blit(surf1, (1293, 10))
	
    line1 = f"MADE BY YAMAN BILGI TV!"
    surf1 = FONT_BIG.render(line1, True, (240,240,150))
    screen.blit(surf1, (1325, 1050))

    sym = PARTICLES[selected_species].get('symbol','')
    line2 = f"Selected: {selected_species} ({sym})  Paused: {paused}"
    surf2 = FONT.render(line2, True, (200,200,200))
    screen.blit(surf2, (12, 28))

    help_txt = "Click and Drag: Spawn | SPACE: Pause/Play | <: Clear | Show/Hide Info: . / 0"
    surf_help = FONT_SMALL.render(help_txt, True, (200,200,200))
    screen.blit(surf_help, (12, 44))

# SIDEBAR
def sideanti(sim, selected_species):
    pygame.draw.rect(screen, SIDEBAR_BG, (WORLD_W, 0, SIDEBAR_W, WIN_H))
    x, y = WORLD_W + 12, 10

    # HEADER
    title = FONT_BIG.render("KEY - PARTICLES", True, (230,230,230))
    screen.blit(title, (x, y))
    y += 20

    for sp in PARTICLES_KEYS:
        data = PARTICLES[sp]
        col = data["color"]
        sym = data["symbol"]
        nm = data["name"]

        key = next((k for k,v in KEY_TO_PARTICLES.items() if v==sp), None)
        if not key:
            key = EXTRA_PARTICLES_TO_KEY.get(sp, None)
        tag = f"[{key}]" if key else "[ ]"

        txt = f"{tag} {sp} ({sym}) — {nm}"
        surf = FONT.render(txt, True, col)
        screen.blit(surf, (x, y))

        if sp == selected_species:
            mark = FONT.render("⫷", True, (255,220,0))
            screen.blit(mark, (WORLD_W + SIDEBAR_W - 16, y))
        y += 11  # TEXT SPACING

    # LAST REACTION BOX
    if sim.last_reaction:
        y += 10
        box_h = 36
        pygame.draw.rect(screen, (50,20,20), (x-6, y, SIDEBAR_W-20, box_h))
        screen.blit(FONT_BIG.render("Last Reaction:", True, (255,200,200)), (x, y+2))
        screen.blit(FONT.render(sim.last_reaction, True, (255,160,160)), (x, y+18))

# MAIN
def main():
    global show_info
    sim = Simulator()
    cx,cy = WORLD_W/2, WIN_H/2
    # STARTER PARTICLES
    sim.add(Particle("e-",(cx-100,cy),(+120,0)))
    sim.add(Particle("e+",(cx+100,cy),(-120,0)))
    sim.add(Particle("p",(cx,cy-100),(0,40)))
    sim.add(Particle("panti",(cx,cy+100),(0,-40)))
    sim.add(Particle("ENERGY",(cx-0,cy),(0,0)))

    paused=False
    selected_species = PARTICLES_KEYS[0]
    dragging=False; drag_start=(0,0)

    while True:
        dt = clock.tick(FPS)/1000.0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key == pygame.K_0:
                    show_info = not show_info
                if ev.key == pygame.K_0:  # 0 BUTTON
                    if selected_species:
                        show_info = False
                if ev.key == pygame.K_PERIOD:  # . BUTTON
                    if selected_species:
                        show_info = True
                if ev.key==pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key==pygame.K_SPACE:
                    paused=not paused
                if ev.key==pygame.K_LESS:
                    sim.particles.clear(); sim.texts.clear(); sim.last_reaction=""
                # FIRST ALPHABET AND NUMBER BUTTONS
                k = pygame_event_to_key(ev)
                if k and k in KEY_TO_PARTICLES:
                    selected_species = KEY_TO_PARTICLES[k]
                # AFTER F BUTTONS
                if ev.key in EXTRA_FKEY_MAP:
                    selected_species = EXTRA_FKEY_MAP[ev.key]
                # AFTER HOME INSTERT E.T.C BUTTONS
                if ev.key in EXTRA_NAV_MAP:
                    selected_species = EXTRA_NAV_MAP[ev.key]
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                mx,my = ev.pos
                if mx<WORLD_W-4:
                    dragging=True; drag_start=ev.pos
            if ev.type==pygame.MOUSEBUTTONUP and ev.button==1 and dragging:
                mx,my = ev.pos; sx,sy = drag_start
                vx,vy = (mx-sx)*2.5, (my-sy)*2.5
                if sx<WORLD_W:
                    # SPAWN SELECTED PARTICLES
                    sim.add(Particle(selected_species,(sx,sy),(vx,vy)))
                dragging=False
			
        if not paused:
            sim.step(dt)

        screen.fill(BG)
        for p in sim.particles:
            p.draw(screen)
        for t in sim.texts:
            t.draw(screen)
        hud(sim, selected_species, paused)
        sideanti(sim, selected_species)
        if show_info and selected_species:
            sp = PARTICLES[selected_species]
            info_lines = [
                f"Name: {sp['name']}",
                f"Symbol: {sp['symbol']}",
				f"Spin: {sp['spin']}",
                f"Mass: {sp['mass']} MeV",
            ]
            info_lines.append("REACTIONS WITH THIS PARTICLE:")
            for reactants, products in REACTIONS.items():
                if selected_species in reactants:
                    rhs = " + ".join(products['products'])
                    lhs = " + ".join(reactants)
                    info_lines.append(f"As input: {lhs} → {rhs}")

            if selected_species in products['products']:
                rhs = " + ".join(products['products'])
                lhs = " + ".join(reactants)
                info_lines.append(f"As output: {lhs} → {rhs}")

            for reactants, products in REACTIONS.items():
                if selected_species in products['products']:
                    info_lines.append("Recipe: " + " + ".join(reactants))

            for i, line in enumerate(info_lines):
                y = WIN_H - 10 - (len(info_lines)-i)*16
                screen.blit(FONT.render(line, True, (255,255,255)), (10, y))

        if dragging:
            mx,my = pygame.mouse.get_pos(); sx,sy = drag_start
            pygame.draw.line(screen,(200,200,200),(sx,sy),(mx,my),2)
            pygame.draw.circle(screen,(255,240,100),(sx,sy),6,1)
            preview=f"{PARTICLES[selected_species]['symbol']} — {PARTICLES[selected_species]['name']}"
            screen.blit(FONT_SMALL.render(preview,True,(255,255,200)),(sx+8,sy-18))
        pygame.display.flip()

if __name__=="__main__":
    main()
