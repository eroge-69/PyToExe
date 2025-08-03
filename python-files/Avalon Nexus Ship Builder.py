import os
import json
import sys
import time
import random

def check_audio_files():
    """Check for audio files in ShipAssets folder and display status"""
    try:
        # Check for special startup tracks (5% chance)
        if random.random() < 0.05:
            special_tracks = [f"ShipAssets/sost{i}.wav" for i in range(1, 7)]
            existing_special = [track for track in special_tracks if os.path.exists(track) and os.path.getsize(track) > 0]
            if existing_special:
                selected_special = random.choice(existing_special)
                print(f"♪ Special track would play: {os.path.basename(selected_special)} (100% volume)")
            else:
                print("♪ Special track selected but no audio files found in ShipAssets/")
        
        # Check for regular OST tracks
        ost_tracks = [f"ShipAssets/ost{i}.wav" for i in range(1, 13)]
        existing_ost = [track for track in ost_tracks if os.path.exists(track) and os.path.getsize(track) > 0]
        
        if existing_ost:
            selected_ost = random.choice(existing_ost)
            print(f"♪ Background music would play: {os.path.basename(selected_ost)} (30% volume, looping)")
        else:
            print("♪ Audio system ready - add WAV files to ShipAssets/ for background music")
            
    except Exception as e:
        print("♪ Audio system ready - ShipAssets folder prepared for music files")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_orange(text):
    ORANGE = '\033[38;5;214m'
    RESET = '\033[0m'
    print(f"{ORANGE}{text}{RESET}")

def print_teal(text):
    TEAL = '\033[38;5;37m'
    RESET = '\033[0m'
    print(f"{TEAL}{text}{RESET}")

def print_red(text):
    RED = '\033[91m'
    RESET = '\033[0m'
    print(f"{RED}{text}{RESET}")

def print_green(text):
    GREEN = '\033[92m'
    RESET = '\033[0m'
    print(f"{GREEN}{text}{RESET}")

# Store organized by categories and subcategories with full starship components
store = {
    "frame": {
        "Eagle": {
            "type": "Light Scout / Interceptor",
            "hull_points": 1,
            "base_speed": 150,
            "base_power": 1,
            "hardpoints": 2,
            "utility_slots": 2,
            "substructure_space": 2,
            "base_ac": 16,
            "trait": "Evasive Design: Gains +1 AC if it moved at least 1 hex this turn.",
            "description": "The lightest and fastest frame available, the Eagle is ideal for recon, flanking, or hit-and-run tactics. Its high AC and mobility make it difficult to pin down, but it can't take much punishment."
        },
        "Bullsnake": {
            "type": "Balanced Patrol / Multi-role",
            "hull_points": 2,
            "base_speed": 100,
            "base_power": 2,
            "hardpoints": 2,
            "utility_slots": 3,
            "substructure_space": 3,
            "base_ac": 14,
            "trait": "Tactical Core: Twice per combat, reroll any roll that fails.",
            "description": "A general-purpose, reliable frame that supports both offensive and defensive loadouts. The bullsnake's flexibility makes it a popular choice for all kinds of mission profiles."
        },
        "Python": {
            "type": "Heavy Assault / Fortress",
            "hull_points": 5,
            "base_speed": 50,
            "base_power": 1,
            "hardpoints": 3,
            "utility_slots": 4,
            "substructure_space": 5,
            "base_ac": 9,
            "trait": "Critical Dampener: Once per battle, ignore the effects of a critical hit, or turn one of your attacks into a auto crit.",
            "description": "A tank of the stars. Designed to soak punishment and return fire with overwhelming force, the python is slow, but hard to kill. Best paired with support ships or distractions."
        },
        "Pelican": {
            "type": "Glass Cannon / Assassin",
            "hull_points": 2,
            "base_speed": 100,
            "base_power": 3,
            "hardpoints": 4,
            "utility_slots": 2,
            "substructure_space": 5,
            "base_ac": 15,
            "trait": "Scramble Spectrum: Once per battle, the Pelican can activate an emergency cloak that costs no energy. While cloaked, it can't be targeted at all. If the Pelican takes fatal damage, this activates automatically, saving it from death. Cloaking like this lasts for 1 minute",
            "description": "Built for maximum alpha strike potential, the Pelican is perfect for fast, brutal engagements where victory comes quickly—or not at all. Its survivability is limited, but its aggression is unmatched."
        },
        "Goliath Heron": {
            "type": "Energy Specialist / Tech Superiority",
            "hull_points": 3,
            "base_speed": 50,
            "base_power": 5,
            "hardpoints": 6,
            "utility_slots": 3,
            "substructure_space": 6,
            "base_ac": 8,
            "trait": "Surge Matrix: Once per combat, fully recharge all power back to max.",
            "description": "A power-core-rich platform for energy weapons and utility-heavy builds. If you want to play with shields, beams, cloaks, or advanced electronic warfare—this is your frame."
        },
        "Gaboon": {
            "type": "Support / Control",
            "hull_points": 4,
            "base_speed": 100,
            "base_power": 0,
            "hardpoints": 2,
            "utility_slots": 6,
            "substructure_space": 10,
            "base_ac": 11,
            "trait": "Tactical Defenses: Anytime you apply a repair drone, shield recharge, energy recharge, or any other supportive thing to an ally, the effect is doublely effective.",
            "description": "The backbone of any coordinated fleet, the Gaboon is built to empower allies, run support programs, and hold the line. Not as fast as a scout, not as tough as a tank—but invaluable in any serious skirmish."
        }
    },
    "hull": {
        "Stock-Standard Titanium": {
            "hull_points": 4,
            "ac": 1,
            "speed": 50,
            "power": 1,
            "description": "Basic hull for everyone to use."
        },
        "Reinforced Titanium": {
            "hull_points": 5,
            "ac": 1,
            "speed": 0,
            "power": 0,
            "description": "Hull designed for those who are a little scared of dying, it sacrifices a little weight"
        },
        "Steel Hull": {
            "hull_points": 7,
            "ac": 0,
            "speed": -100,
            "power": 0,
            "description": "Heavier, stronger, slower"
        },
        "Carbon fiber Hull": {
            "hull_points": 2,
            "ac": 3,
            "speed": 100,
            "power": 0,
            "weakness": "Plasma Weakness: Using this hull makes you take 50% more damage from plasma weaponry, as the super heated gas literally melts your carbon-fiber.",
            "description": "Lightweight, overall less protection though"
        },
        "Aerogel Hull": {
            "hull_points": 0,
            "ac": 5,
            "speed": 200,
            "power": 0,
            "resistance": "Immune to thermal weaponry. Resistant to plasma damage.",
            "description": "Extremely light, amazing insulator, and very brittle. Aerogel is an amazing insulator, and easily soaks up thermal weaponry, making you immune to it. As a bonus you're also resistant to plasma damage."
        },
        "Chromium-Tungsten Alloy": {
            "hull_points": 12,
            "ac": -3,
            "speed": -150,
            "power": 0,
            "resistance": "Resistant to thermal, plasma, and acid weaponry.",
            "description": "Super-heavy, high melting point hull designed to turn ships into a fortress. Given it's very high melting point, it's resistant to thermal and plasma weaponry. It's also resistant to acid!"
        },
        "Reactive Surface Composite": {
            "hull_points": 5,
            "ac": 1,
            "speed": 50,
            "power": 0,
            "resistance": "Immune to piercing damage, resistant to kinetic damage types (slashing, bludgeoning, force)",
            "weakness": "Vulnerable to thermal and plasma damage.",
            "description": "A variant of stock, allowing resistance to kinetic weaponry, at the cost of melting easily."
        },
        "Mirrored Surface Composite": {
            "hull_points": 3,
            "ac": 2,
            "speed": 50,
            "power": 0,
            "special": "When shot with any thermal weapon, it's reflected back towards the attacker, at half damage.",
            "weakness": "Vulnerable to bludgeoning damage.",
            "description": "Opposite of the reactive surface, this hull reflects lasers."
        },
        "Shielded Gold core latex hull": {
            "hull_points": 1,
            "ac": 3,
            "speed": 50,
            "power": 4,
            "shield_points": 1,
            "resistance": "Acid and piercing resistant",
            "weakness": "Vulnerable to bludgeoning",
            "special": "Whenever struck with a thermal weapon to hull, it recharges power back to maximum. This hull also is shielded, which recharges after 1 round.",
            "description": "Golden hull with some latex melted over it to make it nice and sealed. Excellent at transferring much more energy throughout the ship, while being chemically and kinetic resistant thanks to the latex."
        },
        "Biologically engineered hull": {
            "hull_points": 5,
            "ac": 0,
            "speed": 50,
            "power": 2,
            "special": "At the start of your turn, this hull starts to heal itself, recovering 50hp per round.",
            "weakness": "Vulnerable to acid damage",
            "description": "Squishy, wet, slimy hull inspired by some ancient entity, that can heal itself, thanks to being biological."
        }
    },
    "superstructure": {
        "generators": {
            "Stock power generator": {
                "sys_hp": 3,
                "power": 4,
                "recharge": "Recharges 1 power at the start of your turn",
                "description": "Stock, basic."
            },
            "Uranium power plant": {
                "sys_hp": 6,
                "power": 6,
                "speed": -50,
                "ac": -1,
                "recharge": "Recharges 2 power at the start of your turn",
                "description": "Large power plant, it's bulkier and provides more power."
            },
            "Erchius power generator": {
                "sys_hp": 1,
                "power": 2,
                "speed": 50,
                "ac": 1,
                "recharge": "Recharges 2 power at the start of your turn",
                "description": "Lightweight, low capacity quick recharging, commonly used on interceptors."
            },
            "Shielded power generator": {
                "sys_hp": 3,
                "power": 3,
                "special": "Provides a linked shield point to all superstructure and substructure systems",
                "recharge": "Recharges 1 power at the start of your turn, unless the internal shield is down. It'll recharge that instead.",
                "description": "Similar to stock, but with a recharging shield that takes some power, but protects it."
            },
            "Super Capacitor": {
                "sys_hp": 4,
                "power": 10,
                "ac": 1,
                "special": "When an ally transfers power to you, the amount is doubled.",
                "description": "A very big battery, that stores a ton of power, but doesn't generate any itself"
            },
            "Biologically engineered stomach": {
                "sys_hp": 5,
                "power": 7,
                "speed": -50,
                "recharge": "Recharges 1 power at the start of every other round, however if fed living biofuel, will immediately recharge 2 power",
                "special": "Automatic heals 1 sys hp at the start of your turn if not destroyed.",
                "description": "Who needs steel when you have flesh? This has a higher capacity, but a slow recharge rate. Takes the appearance of a large titanium box with a fleshy eldritch maw on the top, with a window showing the fleshy stomach inside. Eco friendly!"
            },
            "Solaris Array": {
                "sys_hp": 2,
                "power": 8,
                "speed": 50,
                "ac": 1,
                "special": "Can deploy and retract. While deployed, it will recharge 4 power at the end of your turn. However it's unprotected and vulnerable, being a large solar array your ship deploys. If at half hp, power generation is reduced to 2. Incoming power transferring is only half as effective.",
                "description": "Ultra-light space sail powered by stars."
            },
            "Dark matter generator": {
                "sys_hp": 6,
                "power": 7,
                "ac": -2,
                "recharge": "Recharges 1 power at the start of your turn",
                "special": "If you take hull damage, there's a chance the dark matter will destabilize (12 DC), causing an explosion somewhere in your ship, damaging a random system. However, if it doesn't explode, you immediately gain +2 power. You can activate overclock mode, destabilizing the dark matter to generate more power. Explosion chance on hit increases (to 19DC), however your power output increases to +5 at the start of your turn.",
                "description": "Utilizing unstable dark matter, you can generate tons of power, but again, it's unstable."
            }
        },
        "engines": {
            "Stock combustion engines": {
                "sys_hp": 3,
                "speed": 150,
                "ac": 1,
                "special": "Can consume 1 power to do a 15ft boost.",
                "description": "Basic, reliable."
            },
            "Lightweight aerogel engines": {
                "sys_hp": 1,
                "speed": 100,
                "ac": 2,
                "special": "Can consume 1 power to add +5 AC as a reaction against a single attack, as a dodge.",
                "description": "Super light, not as powerful but quick start up time, useful for dodging and weaving"
            },
            "Reinforced steel engines": {
                "sys_hp": 6,
                "speed": 200,
                "ac": 0,
                "special": "Increases ship weight, making attempts to move you against your will only half as effective. At half Sys hp, speed bonus from this is reduced to half.",
                "description": "Made to lift heavy weight, though slower start-up time allows for less useful maneuvering."
            },
            "Plasma booster engines": {
                "sys_hp": 4,
                "speed": 50,
                "ac": 0,
                "special": "Can consume 1 power, increasing speed to 300ft (6 hexes), and AC by 5 if you move while boosting. Lasts until the start of your next turn, where the boosters turn off and require a 2 round recharge.",
                "description": "Instead of sustaining constant speed, these can burst out a bunch of hot plasma for some incredible momentary speed, but require a recharge after."
            },
            "Maneuvering thrusters": {
                "sys_hp": 4,
                "speed": -50,
                "ac": 4,
                "special": "For each point of system damage it takes, the AC is reduced by 1, as a thruster is taken out. Takes no speed to turn",
                "description": "Instead of big engine blocks, you use tiny precise thrusters, allowing you to easily dodge attacks, but you can't move at all."
            }
        },
        "communications and sensors": {
            "Stock communications center": {
                "sys_hp": 2,
                "speed": 0,
                "ac": 0,
                "power": 1,
                "special": "If destroyed, your sensors break and you can't communicate outside of your ship.",
                "description": "Without this, your sensors won't work and you'll be blind. This is the basic variant."
            },
            "Lightweight comms antenna": {
                "sys_hp": 1,
                "speed": 50,
                "ac": 0,
                "power": 0,
                "special": "If destroyed, you'll be blind.",
                "description": "Fragile, lighter sensors."
            },
            "Multi-Array comms relay": {
                "sys_hp": 6,
                "speed": 0,
                "ac": -1,
                "power": 0,
                "special": "Having this equipped grants access to the alpha strike ability",
                "description": "Using heavier antenna and radios, these are much stronger, but rather bulky."
            },
            "AI controlled comms center": {
                "sys_hp": 3,
                "speed": 0,
                "ac": 0,
                "power": -1,
                "special": "You can talk to the friendly AI, and order it to control a utility system, hardpoint, or any other single system in your ship.",
                "description": "Slapping a quirky AI personality into the ships systems takes a little more power, but the AI is versatile."
            },
            "Synaptic node relay": {
                "sys_hp": 1,
                "speed": 0,
                "ac": 0,
                "power": 1,
                "special": "If its destroyed, it'll repair itself after a round, and is immune to EMP, being.. Biological.",
                "description": "You installed what on the ship? Instead of mechanical signals, this.. Bio-engineered comms relay accepts signals, somehow. Using a cluster of fleshy, slimy nodes, it turns that into data we can read. It's fragile, but if its destroyed, it'll repair itself after a round, and is immune to EMP, being.. Biological."
            }
        }
    },
    "substructure": {
        "shields": {
            "Stock shield generator": {
                "sys_hp": 2,
                "speed": 0,
                "ac": -1,
                "shield_points": 4,
                "shield_layers": 1,
                "special": "Damage doesn't bleed through shield layers to other layers or the hull. Once shield is broken, it needs to consume an amount of power to recharge. In this case consuming 1 power per round, and taking 2 rounds to redeploy, starting on your next turn. Shields take double damage from thermal, and some weapons can phase through it. Resistant to force",
                "description": "Basic shield used by many civilian vessels. Fairly cheap and light."
            },
            "Aerotech shield": {
                "sys_hp": 1,
                "speed": 50,
                "ac": 0,
                "shield_points": 2,
                "shield_layers": 1,
                "special": "Once broken, it takes a round to recalibrate before it starts it's recharge sequence (taking 2 rounds to redeploy)",
                "description": "Lightweight, weak, high-tech"
            },
            "Prismatic shield": {
                "sys_hp": 4,
                "speed": -50,
                "ac": -3,
                "shield_points": 12,
                "shield_layers": 2,
                "special": "One layer breaks at half shield hp. This shield has a special prismatic weave, which makes it extremely heavy, however it'll actually block most shield-phasing weaponry (cannons, plasma, stationary mines, drop-pods, torpedoes). Tele-mines can still be warped inside, though. Once broken, a small shockwave is sent out, reflecting any multi shot projectiles still incoming. It then enters a 1 round cool down phase, before consuming 8 power over the course of 4 rounds before redeploying.",
                "description": "Heavy duty, unbreakable, slow recharging shield."
            },
            "Multi-layered shield": {
                "sys_hp": 1,
                "speed": 50,
                "ac": -1,
                "shield_points": 1,
                "shield_layers": 5,
                "special": "A layer is broken every 5hp. Damage doesn't bleed through layers, so a 100 damage weapon shot is practically reduced to 5 damage. Exceedingly weak against burst lasers or gatling guns, though. Once broken it'll enter a 1 round cool down phase, then consume 5 power over the course of 5 rounds, recharging a layer each round.",
                "description": "A shield that focuses on many layers rather than layer strength. Making it powerful against high damage weapons, and horrible against quick multi-shot weaponry."
            },
            "Bi-weave shield": {
                "sys_hp": 2,
                "speed": -50,
                "ac": -1,
                "power": -1,
                "shield_points": 2,
                "shield_layers": 1,
                "special": "Once broken, it immediately starts recharging, consuming 1 power and popping back up at the end of your next turn.",
                "description": "A shield that takes from overall power capacity to skip the cool down phase, making for a quick recovery."
            }
        },
        "misc": {
            "Cargo bay": {
                "special": "A nice empty bay to store many things, such as more ammo (double for each weapon, drone system, etc), bombs (4 bombs), or anything you'd want to store. Can launch bombs within 100ft",
                "description": "A nice empty bay to store many things, such as more ammo (double for each weapon, drone system, etc), bombs (4 bombs), or anything you'd want to store. Can launch bombs within 100ft"
            },
            "Cloaking system": {
                "special": "A device that will cloak your ship, closing your heat vents and making your ship off the sensors and disappear visually. Halts power production, and consumes 1 power at the end of your round. If you're actively shooting there's a chance enemies will find you.",
                "description": "A device that will cloak your ship, closing your heat vents and making your ship off the sensors and disappear visually. Halts power production, and consumes 1 power at the end of your round. If you're actively shooting there's a chance enemies will find you."
            },
            "Repair drone system": {
                "special": "Controls repair drones that can deploy onto yourself or allies. Each drone will fully repair up to 2 systems and 4 hull points, over the course of 2 rounds. Repairing 1 sys and 2 hull a round. The drone is destroyed if the repairing ship is attacked, Holds 4 total drones. Can also deploy 1 raven",
                "description": "Controls repair drones that can deploy onto yourself or allies. Each drone will fully repair up to 2 systems and 4 hull points, over the course of 2 rounds. Repairing 1 sys and 2 hull a round. The drone is destroyed if the repairing ship is attacked, Holds 4 total drones. Can also deploy 1 raven"
            },
            "Expansion matrix": {
                "special": "Takes up a substructure space, but expands exterior slots on the ship, adding 1 hardpoint and 2 utility slots.",
                "description": "Takes up a substructure space, but expands exterior slots on the ship, adding 1 hardpoint and 2 utility slots."
            },
            "Hull reinforcement": {
                "hull_points": 2,
                "description": "Adds 2 hull points (200 hp)"
            },
            "Shield booster": {
                "shield_points": 3,
                "description": "Adds 3 shield points (75 hp)"
            },
            "System reinforcement": {
                "special": "Doubles all system hp",
                "description": "Doubles all system hp"
            },
            "Stealth drive": {
                "special": "Advanced cloaking system that provides improved stealth capabilities with reduced power consumption",
                "description": "Advanced cloaking system that provides improved stealth capabilities with reduced power consumption"
            },
            "Gravity well generator": {
                "special": "Creates gravitational fields that can manipulate enemy ship movement and disrupt FTL jumps",
                "description": "Creates gravitational fields that can manipulate enemy ship movement and disrupt FTL jumps"
            },
            "Neural interface": {
                "special": "Direct mental link to ship systems, improving reaction time and targeting accuracy",
                "description": "Direct mental link to ship systems, improving reaction time and targeting accuracy"
            },
            "Emergency ejection pod": {
                "special": "Provides crew survival option in case of catastrophic ship failure",
                "description": "Provides crew survival option in case of catastrophic ship failure"
            }
        }
    },
    "hardpoints": {
        "Stock pulse laser": {
            "attack": 6,
            "damage": "1d12+3",
            "damage_type": "thermal",
            "power_cost": 0,
            "ammo": "infinite",
            "description": "Fires a laser so brief it hardly consumes any power, however it's fairly weak. The most cost efficient weapon."
        },
        "Burst laser": {
            "attack": 4,
            "damage": "2d6",
            "damage_type": "thermal",
            "power_cost": 1,
            "shots": 3,
            "description": "Fires a quick burst of laser shots."
        },
        "Beam laser": {
            "attack": 7,
            "damage": "1d10+1",
            "damage_type": "thermal",
            "power_cost": 1,
            "special": "Once it hits, the beam locks onto the target, it continues to damage every turn without needing to hit again. Every time it deals damage though, it consumes 1 power. When it loses its lock, it needs to re-aim again. The lock is broken if the ship cloaks, scrambled, or preforms a evasion saving throw.",
            "description": "A powerful continuous beam that can lock onto targets."
        },
        "Gatling gun": {
            "attack": 3,
            "damage": "20d2 or 40d2",
            "damage_type": "piercing",
            "ammo": 200,
            "special": "Fires a burst of 20 or 40 bullets. If the attack misses, half the bullets hit anyway. Has a total of 200 bullets (10-5 bursts). You can choose if you want to shoot either 20 or 40 bullets.",
            "description": "Fires a long burst of small bullets"
        },
        "Cannon": {
            "attack": 4,
            "damage": "2d20+20",
            "damage_type": "bludgeoning",
            "ammo": 11,
            "special": "Cannonballs have 20hp, and can be shot by point defense (but rarely destroyed). 1 round travel delay.",
            "description": "Shoots a big slow cannonball that bypasses shields."
        },
        "Railgun": {
            "attack": 8,
            "damage": "4d12+12",
            "damage_type": "piercing",
            "power_cost": 2,
            "ammo": 5,
            "special": "Bleeds through shield layers. Can be shot 5 times before the internal rails need repaired either via drone, EVA, or AFMU",
            "description": "A big magnet gun that launches projectiles at high speed."
        },
        "Plasma accelerator": {
            "attack": 4,
            "damage": "14d4",
            "damage_type": "plasma",
            "power_cost": 2,
            "cooldown": 1,
            "special": "Damage is dealt to both shields and hull simultaneously. Infinite ammo, but needs a 1 round cooldown after it shoots.",
            "description": "Fires superheated gas to melt through enemy ships."
        },
        "Torpedo launcher": {
            "special": "Locks onto ships, shooting heavy, deadly warheads that bypass shields. Takes 1 round to lock onto targets, and can be loaded with a few different torpedos. Nuclear warhead: 200 force + 16d12 radiation. Shield breaker warhead: 50 force + instantly breaks shield. Incendiary warhead: 200 thermal + ignites for 1 minute. Mass-lock warhead: 50 force + reduces AC by -10 and speed by -150ft for 5 rounds.",
            "ammo": 3,
            "reload_time": 2,
            "description": "Locks onto ships, shooting heavy, deadly warheads that bypass shields. Takes 1 round to lock onto targets, and can be loaded with a few different torpedos."
        },        "Mining laser": {
            "attack": 4,
            "damage": "1d8+2",
            "damage_type": "thermal",
            "power_cost": 1,
            "special": "Double damage against asteroids and mining targets",
            "description": "Industrial laser repurposed for combat, excels at cutting through solid materials."
        },
        "EMP torpedo": {
            "attack": "Auto (guided)",
            "damage": "3d6",
            "damage_type": "ion",
            "ammo": 6,
            "special": "Disables all electronics on target for 3 rounds, double damage to shields",
            "description": "Electromagnetic pulse warhead that devastates electronic systems."
        },
        "Cluster bomb launcher": {
            "attack": 6,
            "damage": "8d4",
            "damage_type": "force",
            "ammo": 12,
            "special": "Area of effect 100ft radius, bypasses shields",
            "description": "Launches explosive clusters that detonate in a wide area."
        },
        "Antimatter cannon": {
            "attack": 5,
            "damage": "6d10+15",
            "damage_type": "force",
            "power_cost": 4,
            "ammo": 3,
            "special": "Massive damage, 2 round charge time, damages user's ship systems on critical miss",
            "description": "Devastating energy weapon that fires contained antimatter projectiles. Extremely dangerous to use."
        },
        "Disruptor beam": {
            "attack": 6,
            "damage": "2d8+3",
            "damage_type": "force",
            "power_cost": 2,
            "special": "Ignores shields completely, reduces target's AC by 2 for 3 rounds",
            "description": "Exotic energy weapon that disrupts molecular cohesion, bypassing most defenses."
        },
        "Acid sprayer": {
            "attack": 4,
            "damage": "3d6+5",
            "damage_type": "acid",
            "ammo": 20,
            "special": "Continues dealing 1d6 acid damage per round for 3 rounds",
            "description": "Short-range chemical weapon that sprays corrosive compounds over a wide area."
        },
    },
    "utilities": {
        "Point Defense Turret": {
            "power_cost": 1,
            "special": "Consumes 1 power to shoot at all large projectiles within 250ft as a reaction, for 2d12.",
            "description": "Consumes 1 power to shoot at all large projectiles within 250ft as a reaction, for 2d12."
        },
        "Weapons relay": {
            "special": "Allows you to use the alpha-strike ability.",
            "description": "Allows you to use the alpha-strike ability."
        },
        "Specialized hull shielding": {
            "power_cost": -1,
            "special": "Makes your hull resistant to a damage type of your choice. You can only equip one of these",
            "description": "Takes some power, but makes your hull resistant to a damage type of your choice. You can only equip one of these"
        },
        "Shield capacitor": {
            "power_cost": -1,
            "special": "Increases your shield layer by one, but makes it take an extra round to cool down before it starts to regenerate.",
            "description": "Increases your shield layer by one, but makes it take an extra round to cool down before it starts to regenerate."
        },
        "Flare cluster": {
            "special": "Can be used to deploy flares, briefly confusing lock-on. (But not for torpedoes) it also increases your AC by 5 until the start of your next round. Has 3 total flare clusters",
            "description": "Can be used to deploy flares, briefly confusing lock-on. (But not for torpedoes) it also increases your AC by 5 until the start of your next round. Has 3 total flare clusters"
        },
        "ECM": {
            "special": "Breaks the lock on all guided missiles and torpedoes within 150ft.",
            "description": "Breaks the lock on all guided missiles and torpedoes within 150ft."
        },        "Re-targeting computer": {
            "special": "After a round of computing, will restore the lock on already launched guided weaponry",
            "description": "After a round of computing, will restore the lock on already launched guided weaponry"
        },
        "Scope": {
            "special": "Increases all weapons to-hit chance by +2. Can only have 1 of these",
            "description": "Increases all weapons to-hit chance by +2. Can only have 1 of these"
        },
        "Overheat capacitor": {
            "special": "When activated, deals 1 sys damage to a system of your choosing, but doubles damage to the next attack. The extra damage from this is thermal damage, and you take this thermal damage as well when you shoot.",
            "description": "When activated, deals 1 sys damage to a system of your choosing, but doubles damage to the next attack."
        },
        "Pulse wave analyzer": {
            "special": "Pulse to reveal cloaked enemies within a 150ft radius.",
            "description": "Pulse to reveal cloaked enemies within a 150ft radius."
        },
        "Boarding clamps": {
            "special": "Heavy clamps to hook onto another ship that's next to you. If you're heavier, the other ship can't move and you can drag it around.",
            "description": "Heavy clamps to hook onto another ship that's next to you."
        },
        "Angled fins": {
            "ac_bonus": 1,
            "special": "Increases AC by +1",
            "description": "Increases AC by +1"
        },
        "Engine injectors": {
            "speed_bonus": 50,
            "special": "Increases speed by +50ft",
            "description": "Increases speed by +50ft"
        },
        "Psionic amplifier": {
            "special": "Amplifies psionic power, but increases chance of overdraw",
            "description": "Amplifies psionic power, but increases chance of overdraw"
        },
        "Psionic dampener": {
            "special": "Nullifies psionic energy, making it nice and calm, no magic but quick overdraw drop.",
            "description": "Nullifies psionic energy, making it nice and calm, no magic but quick overdraw drop."
        },
        "Repair arm": {
            "power_cost": 2,
            "special": "A foldable repair arm that can fix either your ship or an adjacent ship. Consumes 2 power to repair 1 hull and 1 sys after a round.",
            "description": "A foldable repair arm that can fix either your ship or an adjacent ship."
        },
        "Psionic resonator": {
            "power_cost": -1,
            "special": "Allows psionic spells to be used with ship weapon attacks. When activated, the resonator consumes 1 power (ontop of taking one off the capacity passively) and allows you to twin a spell with a weapon attack.",
            "description": "Allows psionic spells to be used with ship weapon attacks."
        },
        "Scanner antenna": {
            "power_cost": 1,
            "special": "Allows you to consume 1 power to tactically scan in a 150ft radius you can see, revealing cloaked units and darkness. Attacks against scanned enemies gain +2",
            "description": "Consume 1 power to tactically scan in a 150ft radius, revealing cloaked units."
        },
        "Drone scrambler": {
            "power_cost": 2,
            "special": "Consumes 2 power to disable all drones in a 150ft radius at a chosen point for 1d4 rounds. Their AC is reduced by -10 while disabled.",
            "description": "Consumes 2 power to disable all drones in a 150ft radius."
        },
        "Targeting computer": {
            "power_cost": 1,
            "special": "Consumes 1 power to mark a target. Marked targets lose -2 AC and the next lock-on is instant. Lasts until the end of the marker's next turn.",
            "description": "Consumes 1 power to mark a target for enhanced targeting."
        },
        "Defensive matrix": {
            "power_cost": 2,
            "special": "Activated as a reaction, consumes 2 power and adds a temporary 100hp shield with no layers. This shield lasts 2 rounds. After the shield breaks, it goes in a 1 round cool down sequence.",
            "description": "Activated as a reaction, adds a temporary 100hp shield."
        },
        "Shield arm": {
            "power_cost": 1,
            "special": "Consumes 1 power to repair 2d20 shield to a non broken shield within 400ft. Can remotely shoot a defensive matrix to an ally if you have one of those as well. Has a 1 round cool down.",
            "description": "Consumes 1 power to repair shield to a non broken shield within 400ft."
        },
        "Backup battery": {
            "power_bonus": 2,
            "special": "Increases power capacity by 2",
            "description": "Increases power capacity by 2"
        },
        "Emergency thrusters": {
            "power_cost": 1,
            "speed_bonus": 100,
            "special": "Consumes 1 power to gain +100ft speed for one round as a reaction.",
            "description": "Consumes 1 power to gain +100ft speed for one round as a reaction."
        },
        "Reactive armor plating": {
            "power_cost": -1,
            "special": "Reduces power capacity by 1 but provides damage reduction of 5 against the first attack each round.",
            "description": "Reduces power capacity by 1 but provides damage reduction of 5 against the first attack each round."
        },
        "Signal jammer": {
            "power_cost": 1,
            "special": "Consumes 1 power to create a 200ft radius jamming field that blocks enemy communications and targeting systems.",
            "description": "Consumes 1 power to create a 200ft radius jamming field."
        },
        "Stealth coating": {
            "power_cost": -1,
            "special": "Reduces power capacity by 1 but makes ship harder to detect, providing +3 AC against guided weapons.",
            "description": "Makes ship harder to detect, providing +3 AC against guided weapons."
        },
        "Combat computer": {
            "power_cost": 1,
            "special": "Consumes 1 power to provide tactical analysis, granting +1 to hit for all weapons for 3 rounds.",
            "description": "Consumes 1 power to provide tactical analysis, granting +1 to hit for all weapons."
        },
        "Electronic countermeasures": {
            "power_cost": 2,
            "special": "Advanced ECM suite that can spoof enemy sensors and break multiple weapon locks simultaneously.",
            "description": "Advanced ECM suite that can spoof enemy sensors and break multiple weapon locks."
        },
    }
}

# Ship starts with no frame chosen, base stats 0
ship = {
    "name": "Unnamed Vessel",
    "base_stats": {  # base stats come from frame only
        "hull_points": 0,
        "hull_hp": 0,
        "shield_points": 0,
        "shield_hp": 0,
        "ac": 0,
        "speed": 0,
        "power": 0,
        "sys_hp": 0
    },
    "stats": {  # actual stats after adding mods
        "hull_points": 0,
        "hull_hp": 0,
        "shield_points": 0,
        "shield_hp": 0,
        "ac": 0,
        "speed": 0,
        "power": 0,
        "sys_hp": 0
    },
    "frame": None,  # chosen frame item name
    "frame_data": {},  # store frame stats here
    "hull": None,  # chosen hull
    "hull_data": {},
    "superstructure": {
        "generators": None,
        "engines": None,
        "communications and sensors": None
    },
    "substructure": {
        "shields": None,
        "misc": []
    },
    "utilities": [],
    "hardpoints": {},  # Will be dynamically sized based on frame
    "resistances": [],
    "weaknesses": [],
    "special_abilities": []
}

inventory = []

def loading_animation():
    clear_screen()
    print_teal("Establishing Up-link...\n")
    total_length = 30
    for i in range(total_length + 1):
        bar = "[" + "#" * i + " " * (total_length - i) + "]"
        print(f"\r{bar} {int((i/total_length)*100)}%", end="")
        time.sleep(5/total_length)
    print("\nLoading complete.\n")
    print_orange("Up-link established. Welcome to the Avalon Nexus.")
    time.sleep(3)

def reverse_loading_animation():
    clear_screen()
    print_orange("Saving data... Cutting Nexus link...\n")
    total_length = 30
    for i in range(total_length, -1, -1):
        bar = "[" + "#" * i + " " * (total_length - i) + "]"
        print(f"\r{bar} {int((i/total_length)*100)}%", end="")
        time.sleep(5/total_length)
    print("\nProcess complete.\n")
    time.sleep(1)

def match_prefix(input_str, options):
    if len(input_str) < 3:
        return None
    prefix = input_str[:3].lower()
    for option in options:
        if option.lower().startswith(prefix):
            return option
    return None

def find_item_in_store(item_name):
    """Find an item in the store and return its category, subcategory, and data"""
    item_name_lower = item_name.lower()
    
    for cat in store:
        if isinstance(store[cat], dict):
            # Check if this category has subcategories by checking if any value is a dict
            has_subcategories = any(isinstance(v, dict) and not any(k in ['description', 'hull', 'shields', 'ac', 'speed', 'power', 'damage'] for k in v.keys()) for v in store[cat].values())
            
            if has_subcategories:
                # Search in subcategories
                for subcat in store[cat]:
                    if isinstance(store[cat][subcat], dict):
                        for item_key, item_data in store[cat][subcat].items():
                            if item_key.lower() == item_name_lower:
                                return cat, subcat, item_key, item_data
            else:
                # Search directly in category - this handles frame, hull, hardpoints, utilities
                for item_key, item_data in store[cat].items():
                    if isinstance(item_data, dict) and item_key.lower() == item_name_lower:
                        return cat, None, item_key, item_data
    
    return None, None, None, None

def buy_item(args, to_inventory=False):
    """Fixed buy_item function that properly handles purchases"""
    if not args:
        print_red("Specify an item to buy. Usage: buy [item name] [hpX (optional)]")
        time.sleep(2)
        return

    item_name_parts = []
    hp = None
    
    # Parse arguments to separate item name from hardpoint specification
    for p in args:
        if p.lower().startswith("hp") and len(p) > 2 and p[2:].isdigit():
            if p[2:] in ship["hardpoints"]:
                hp = p[2:]
            else:
                print_red(f"Invalid hardpoint number. Valid options: {', '.join(ship['hardpoints'].keys())}")
                time.sleep(2)
                return
        else:
            item_name_parts.append(p)

    item_name = " ".join(item_name_parts)
    
    # Find the item in the store
    category, subcategory, found_item, item_data = find_item_in_store(item_name)
    
    if not found_item:
        print_red(f"Item '{item_name}' not found in store.")
        time.sleep(2)
        return

    # Create inventory item
    inventory_item = {
        "name": found_item,
        "category": category,
        "subcategory": subcategory,
        "data": item_data.copy() if item_data else {}
    }

    if to_inventory:
        # Add to inventory
        inventory.append(inventory_item)
        print_green(f"Successfully purchased '{found_item}' and added to inventory!")
    else:
        # Install directly to ship
        success = install_item_to_ship(inventory_item, hp)
        if success:
            print_green(f"Successfully purchased and installed '{found_item}'!")
        else:
            # If installation failed, add to inventory instead
            inventory.append(inventory_item)
            print_green(f"Purchased '{found_item}' and added to inventory (installation failed).")
    
    time.sleep(2)

def install_item_to_ship(item, hardpoint=None):
    """Install an item from inventory to the ship"""
    category = item["category"]
    subcategory = item["subcategory"]
    item_name = item["name"]
    item_data = item["data"]
    
    try:
        if category == "frame":
            if ship["frame"] is not None:
                print_red("Frame already installed. Remove current frame first.")
                return False
            ship["frame"] = item_name
            ship["frame_data"] = item_data.copy()
            # Initialize hardpoints based on frame
            ship["hardpoints"] = {str(i+1): None for i in range(item_data.get("hardpoints", 0))}
            calculate_ship_stats()
            return True
            
        elif category == "hull":
            if ship["hull"] is not None:
                print_red("Hull already installed. Remove current hull first.")
                return False
            ship["hull"] = item_name
            ship["hull_data"] = item_data.copy()
            calculate_ship_stats()
            return True
            
        elif category == "superstructure":
            if subcategory in ship["superstructure"]:
                if ship["superstructure"][subcategory] is not None:
                    print_red(f"{subcategory.title()} already installed. Remove current {subcategory} first.")
                    return False
                ship["superstructure"][subcategory] = {"name": item_name, "data": item_data.copy()}
                calculate_ship_stats()
                return True
            else:
                print_red(f"Invalid superstructure subcategory: {subcategory}")
                return False
                
        elif category == "substructure":
            if subcategory == "shields":
                if ship["substructure"]["shields"] is not None:
                    print_red("Shield generator already installed. Remove current shields first.")
                    return False
                ship["substructure"]["shields"] = {"name": item_name, "data": item_data.copy()}
            else:
                ship["substructure"]["misc"].append({"name": item_name, "data": item_data.copy()})
            calculate_ship_stats()
            return True
            
        elif category == "utilities":
            ship["utilities"].append({"name": item_name, "data": item_data.copy()})
            calculate_ship_stats()
            return True
            
        elif category == "hardpoints":
            if not ship["frame"]:
                print_red("Install a frame first to determine available hardpoints.")
                return False
                
            if hardpoint is None:
                # Find first available hardpoint
                for hp in ship["hardpoints"]:
                    if ship["hardpoints"][hp] is None:
                        ship["hardpoints"][hp] = {"name": item_name, "data": item_data.copy()}
                        calculate_ship_stats()
                        return True
                print_red("No available hardpoints.")
                return False
            else:
                if hardpoint not in ship["hardpoints"]:
                    print_red(f"Invalid hardpoint {hardpoint}. Available: {', '.join(ship['hardpoints'].keys())}")
                    return False
                if ship["hardpoints"][hardpoint] is not None:
                    print_red(f"Hardpoint {hardpoint} already occupied by {ship['hardpoints'][hardpoint]['name']}")
                    return False
                ship["hardpoints"][hardpoint] = {"name": item_name, "data": item_data.copy()}
                calculate_ship_stats()
                return True
        
        return False
        
    except Exception as e:
        print_red(f"Error installing item: {str(e)}")
        return False

def calculate_ship_stats():
    """Recalculate ship stats based on installed components"""
    # Reset all stats
    for stat in ship["stats"]:
        ship["stats"][stat] = 0
    
    # Clear special properties
    ship["resistances"] = []
    ship["weaknesses"] = []
    ship["special_abilities"] = []
    
    # Apply frame base stats
    if ship["frame"] and ship["frame_data"]:
        frame_data = ship["frame_data"]
        ship["stats"]["hull_points"] += frame_data.get("hull_points", 0)
        ship["stats"]["ac"] += frame_data.get("base_ac", 0)
        ship["stats"]["speed"] += frame_data.get("base_speed", 0)
        ship["stats"]["power"] += frame_data.get("base_power", 0)
        if frame_data.get("trait"):
            ship["special_abilities"].append(f"Frame Trait: {frame_data['trait']}")
    
    # Apply hull modifications
    if ship["hull"] and ship["hull_data"]:
        hull_data = ship["hull_data"]
        ship["stats"]["hull_points"] += hull_data.get("hull_points", 0)
        ship["stats"]["ac"] += hull_data.get("ac", 0)
        ship["stats"]["speed"] += hull_data.get("speed", 0)
        ship["stats"]["power"] += hull_data.get("power", 0)
        ship["stats"]["shield_points"] += hull_data.get("shield_points", 0)
        
        if hull_data.get("resistance"):
            ship["resistances"].append(f"Hull: {hull_data['resistance']}")
        if hull_data.get("weakness"):
            ship["weaknesses"].append(f"Hull: {hull_data['weakness']}")
        if hull_data.get("special"):
            ship["special_abilities"].append(f"Hull: {hull_data['special']}")
    
    # Apply superstructure components
    for component_type, component in ship["superstructure"].items():
        if component and isinstance(component, dict):
            comp_data = component["data"]
            ship["stats"]["power"] += comp_data.get("power", 0)
            ship["stats"]["speed"] += comp_data.get("speed", 0)
            ship["stats"]["ac"] += comp_data.get("ac", 0)
            ship["stats"]["sys_hp"] += comp_data.get("sys_hp", 0)
            
            if comp_data.get("special"):
                ship["special_abilities"].append(f"{component_type.title()}: {comp_data['special']}")
            if comp_data.get("recharge"):
                ship["special_abilities"].append(f"{component_type.title()}: {comp_data['recharge']}")
    
    # Apply substructure components
    if ship["substructure"]["shields"]:
        shield_data = ship["substructure"]["shields"]["data"]
        ship["stats"]["shield_points"] += shield_data.get("shield_points", 0)
        ship["stats"]["speed"] += shield_data.get("speed", 0)
        ship["stats"]["ac"] += shield_data.get("ac", 0)
        ship["stats"]["power"] += shield_data.get("power", 0)
        ship["stats"]["sys_hp"] += shield_data.get("sys_hp", 0)
        
        if shield_data.get("special"):
            ship["special_abilities"].append(f"Shields: {shield_data['special']}")
    
    for misc_item in ship["substructure"]["misc"]:
        misc_data = misc_item["data"]
        ship["stats"]["hull_points"] += misc_data.get("hull_points", 0)
        ship["stats"]["shield_points"] += misc_data.get("shield_points", 0)
        ship["stats"]["sys_hp"] += misc_data.get("sys_hp", 0)
        
        if misc_data.get("special"):
            ship["special_abilities"].append(f"{misc_item['name']}: {misc_data['special']}")
    
    # Apply utility modifications
    for utility in ship["utilities"]:
        util_data = utility["data"]
        ship["stats"]["power"] += util_data.get("power_cost", 0)  # Note: this is usually negative
        
        if util_data.get("special"):
            ship["special_abilities"].append(f"{utility['name']}: {util_data['special']}")
    
    # Calculate actual HP values (hull points * 100)
    ship["stats"]["hull_hp"] = ship["stats"]["hull_points"] * 100
    ship["stats"]["shield_hp"] = ship["stats"]["shield_points"] * 25  # Assuming 25hp per shield point

def set_name(args):
    if args:
        ship["name"] = " ".join(args)
        print_green(f"Ship renamed to: {ship['name']}")
    else:
        print_red("Please specify a name for your ship.")
    time.sleep(2)

def view_menu():
    while True:
        clear_screen()
        print_orange(f"== {ship['name']} Ship Status ==")
        
        # Frame and Hull
        print(f"\nFrame: {ship['frame'] if ship['frame'] else 'None installed'}")
        
        # Display Frame Trait if frame is installed
        if ship['frame'] and ship['frame_data'] and ship['frame_data'].get('trait'):
            print(f"Frame Trait: {ship['frame_data']['trait']}")
        
        print(f"Hull: {ship['hull'] if ship['hull'] else 'None installed'}")
        
        # Core Stats
        print(f"\nCore Statistics:")
        print(f"  Hull Points: {ship['stats']['hull_points']} ({ship['stats']['hull_hp']} HP)")
        print(f"  Shield Points: {ship['stats']['shield_points']} ({ship['stats']['shield_hp']} HP)")
        print(f"  Armor Class: {ship['stats']['ac']}")
        print(f"  Speed: {ship['stats']['speed']} ft")
        print(f"  Power: {ship['stats']['power']}")
        
        # Separate System HP for each component
        print(f"\nSystem HP by Component:")
        total_sys_hp = 0
        
        # Superstructure system HP
        for component_type, component in ship["superstructure"].items():
            if component and isinstance(component, dict):
                comp_sys_hp = component["data"].get("sys_hp", 0)
                if comp_sys_hp > 0:
                    print(f"  {component_type.title()}: {comp_sys_hp} HP")
                    total_sys_hp += comp_sys_hp
                elif component:
                    print(f"  {component_type.title()}: 0 HP")
        
        # Shields system HP
        if ship["substructure"]["shields"]:
            shield_sys_hp = ship["substructure"]["shields"]["data"].get("sys_hp", 0)
            if shield_sys_hp > 0:
                print(f"  Shields: {shield_sys_hp} HP")
                total_sys_hp += shield_sys_hp
            else:
                print(f"  Shields: 0 HP")
        
        # Misc systems HP
        for misc_item in ship["substructure"]["misc"]:
            misc_sys_hp = misc_item["data"].get("sys_hp", 0)
            if misc_sys_hp > 0:
                print(f"  {misc_item['name']}: {misc_sys_hp} HP")
                total_sys_hp += misc_sys_hp
        
        # Show total
        print(f"  Total System HP: {total_sys_hp}")
        
        # Superstructure
        print(f"\nSuperstructure:")
        for component_type, component in ship["superstructure"].items():
            if component:
                print(f"  {component_type.title()}: {component['name']}")
            else:
                print(f"  {component_type.title()}: None installed")
        
        # Substructure
        print(f"\nSubstructure:")
        if ship["substructure"]["shields"]:
            print(f"  Shields: {ship['substructure']['shields']['name']}")
        else:
            print(f"  Shields: None installed")
        
        if ship["substructure"]["misc"]:
            print(f"  Misc Systems:")
            for misc_item in ship["substructure"]["misc"]:
                print(f"    - {misc_item['name']}")
        else:
            print(f"  Misc Systems: None")
        
        # Hardpoints
        print(f"\nHardpoints:")
        if ship["hardpoints"]:
            for hp, weapon in ship["hardpoints"].items():
                if weapon:
                    print(f"  HP{hp}: {weapon['name']}")
                else:
                    print(f"  HP{hp}: Empty")
        else:
            print("  No hardpoints (install frame first)")
        
        # Utilities
        print(f"\nUtilities:")
        if ship["utilities"]:
            for utility in ship["utilities"]:
                print(f"  - {utility['name']}")
        else:
            print("  None")
        
        # Special Abilities
        if ship["special_abilities"]:
            print(f"\nSpecial Abilities:")
            for ability in ship["special_abilities"]:
                print(f"  - {ability}")
        
        # Resistances and Weaknesses
        if ship["resistances"]:
            print(f"\nResistances:")
            for resistance in ship["resistances"]:
                print(f"  - {resistance}")
        
        if ship["weaknesses"]:
            print(f"\nWeaknesses:")
            for weakness in ship["weaknesses"]:
                print(f"  - {weakness}")
        
        # Inventory
        print(f"\nInventory ({len(inventory)} items):")
        if inventory:
            for i, item in enumerate(inventory):
                print(f"  {i+1}. {item['name']} ({item['category']})")
        else:
            print("  Empty")
        
        print("\nCommands:")
        print("- install [item number] [hp<number> (for hardpoints)]")
        print("- remove [component name]")
        print("- view [component name] (show detailed stats)")
        print("- inventory")
        print("- back")
        
        cmd = input("\nView > ").strip()
        if not cmd:
            continue
            
        parts = cmd.split()
        command = parts[0].lower()
        
        if command == "back":
            break
        elif command == "main":
            return "main"
        elif command == "install":
            install_from_inventory(parts[1:])
        elif command == "remove":
            remove_component(parts[1:])
        elif command == "view":
            if len(parts) > 1:
                view_component_details(" ".join(parts[1:]))
            else:
                print_red("Specify component name to view. Example: view Eagle")
                time.sleep(2)
        elif command == "inventory":
            view_inventory()
        else:
            print_red("Unknown command.")
            time.sleep(2)

def view_component_details(component_name):
    """View detailed stats and description of a specific installed component"""
    clear_screen()
    component_name_lower = component_name.lower()
    found = False
    
    # Check frame
    if ship["frame"] and ship["frame"].lower() == component_name_lower:
        print_orange(f"== {ship['frame']} Details ==")
        data = ship["frame_data"]
        print(f"Type: {data.get('type', 'N/A')}")
        print(f"Description: {data.get('description', 'No description available')}")
        print(f"\nBase Statistics:")
        print(f"  Hull Points: {data.get('hull_points', 0)}")
        print(f"  Base Speed: {data.get('base_speed', 0)} ft")
        print(f"  Base Power: {data.get('base_power', 0)}")
        print(f"  Hardpoints: {data.get('hardpoints', 0)}")
        print(f"  Utility Slots: {data.get('utility_slots', 0)}")
        print(f"  Substructure Space: {data.get('substructure_space', 0)}")
        print(f"  Base AC: {data.get('base_ac', 0)}")
        if data.get('trait'):
            print(f"\nSpecial Trait: {data['trait']}")
        found = True
    
    # Check hull
    elif ship["hull"] and ship["hull"].lower() == component_name_lower:
        print_orange(f"== {ship['hull']} Details ==")
        data = ship["hull_data"]
        print(f"Description: {data.get('description', 'No description available')}")
        print(f"\nModifications:")
        print(f"  Hull Points: {data.get('hull_points', 0):+}")
        print(f"  AC: {data.get('ac', 0):+}")
        print(f"  Speed: {data.get('speed', 0):+} ft")
        print(f"  Power: {data.get('power', 0):+}")
        if data.get('shield_points'):
            print(f"  Shield Points: {data.get('shield_points', 0):+}")
        if data.get('resistance'):
            print(f"\nResistances: {data['resistance']}")
        if data.get('weakness'):
            print(f"Weaknesses: {data['weakness']}")
        if data.get('special'):
            print(f"Special: {data['special']}")
        found = True
    
    # Check superstructure
    else:
        for component_type, component in ship["superstructure"].items():
            if component and component["name"].lower() == component_name_lower:
                print_orange(f"== {component['name']} Details ==")
                data = component["data"]
                print(f"Category: {component_type.title()}")
                print(f"Description: {data.get('description', 'No description available')}")
                print(f"\nSystem Statistics:")
                print(f"  System HP: {data.get('sys_hp', 0)}")
                if data.get('power'):
                    print(f"  Power: {data.get('power', 0):+}")
                if data.get('speed'):
                    print(f"  Speed: {data.get('speed', 0):+} ft")
                if data.get('ac'):
                    print(f"  AC: {data.get('ac', 0):+}")
                if data.get('recharge'):
                    print(f"\nRecharge: {data['recharge']}")
                if data.get('special'):
                    print(f"Special: {data['special']}")
                found = True
                break
    
    # Check substructure
    if not found:
        if ship["substructure"]["shields"] and ship["substructure"]["shields"]["name"].lower() == component_name_lower:
            component = ship["substructure"]["shields"]
            print_orange(f"== {component['name']} Details ==")
            data = component["data"]
            print(f"Category: Shield Generator")
            print(f"Description: {data.get('description', 'No description available')}")
            print(f"\nSystem Statistics:")
            print(f"  System HP: {data.get('sys_hp', 0)}")
            print(f"  Shield Points: {data.get('shield_points', 0)}")
            print(f"  Shield Layers: {data.get('shield_layers', 0)}")
            if data.get('speed'):
                print(f"  Speed: {data.get('speed', 0):+} ft")
            if data.get('ac'):
                print(f"  AC: {data.get('ac', 0):+}")
            if data.get('power'):
                print(f"  Power: {data.get('power', 0):+}")
            if data.get('special'):
                print(f"\nSpecial: {data['special']}")
            found = True
        
        else:
            for misc_item in ship["substructure"]["misc"]:
                if misc_item["name"].lower() == component_name_lower:
                    print_orange(f"== {misc_item['name']} Details ==")
                    data = misc_item["data"]
                    print(f"Category: Substructure Misc")
                    print(f"Description: {data.get('description', 'No description available')}")
                    if data.get('hull_points'):
                        print(f"\nHull Points: {data.get('hull_points', 0):+}")
                    if data.get('shield_points'):
                        print(f"Shield Points: {data.get('shield_points', 0):+}")
                    if data.get('sys_hp'):
                        print(f"System HP: {data.get('sys_hp', 0):+}")
                    if data.get('special'):
                        print(f"\nSpecial: {data['special']}")
                    found = True
                    break
    
    # Check hardpoints
    if not found:
        for hp, weapon in ship["hardpoints"].items():
            if weapon and weapon["name"].lower() == component_name_lower:
                print_orange(f"== {weapon['name']} Details ==")
                data = weapon["data"]
                print(f"Category: Hardpoint Weapon")
                print(f"Hardpoint: {hp}")
                print(f"Description: {data.get('description', 'No description available')}")
                print(f"\nWeapon Statistics:")
                if data.get('attack'):
                    print(f"  Attack Bonus: +{data.get('attack', 0)}")
                if data.get('damage'):
                    print(f"  Damage: {data.get('damage', 'N/A')}")
                if data.get('damage_type'):
                    print(f"  Damage Type: {data.get('damage_type', 'N/A')}")
                if data.get('power_cost'):
                    print(f"  Power Cost: {data.get('power_cost', 0)}")
                if data.get('ammo'):
                    print(f"  Ammo: {data.get('ammo', 'N/A')}")
                if data.get('cooldown'):
                    print(f"  Cooldown: {data.get('cooldown', 0)} rounds")
                if data.get('shots'):
                    print(f"  Shots per use: {data.get('shots', 1)}")
                if data.get('special'):
                    print(f"\nSpecial: {data['special']}")
                found = True
                break
    
    # Check utilities
    if not found:
        for utility in ship["utilities"]:
            if utility["name"].lower() == component_name_lower:
                print_orange(f"== {utility['name']} Details ==")
                data = utility["data"]
                print(f"Category: Utility")
                print(f"Description: {data.get('description', 'No description available')}")
                if data.get('power_cost'):
                    print(f"\nPower Cost: {data.get('power_cost', 0)}")
                if data.get('special'):
                    print(f"Special: {data['special']}")
                found = True
                break
    
    if not found:
        print_red(f"Component '{component_name}' not found on ship.")
    
    input("\nPress Enter to continue...")

def install_from_inventory(args):
    if not args:
        print_red("Specify item number to install.")
        time.sleep(2)
        return
    
    try:
        item_num = int(args[0]) - 1
        if item_num < 0 or item_num >= len(inventory):
            print_red("Invalid item number.")
            time.sleep(2)
            return
        
        # Check for hardpoint specification
        hardpoint = None
        if len(args) > 1 and args[1].lower().startswith("hp"):
            hp_num = args[1][2:]
            if hp_num in ship["hardpoints"]:
                hardpoint = hp_num
            else:
                print_red("Invalid hardpoint number.")
                time.sleep(2)
                return
        
        item = inventory[item_num]
        success = install_item_to_ship(item, hardpoint)
        
        if success:
            inventory.pop(item_num)
            print_green(f"Successfully installed {item['name']}!")
        
    except ValueError:
        print_red("Invalid item number.")
    
    time.sleep(2)

def remove_component(args):
    if not args:
        print_red("Specify component to remove (frame, hp1, hp2, etc.)")
        time.sleep(2)
        return
    
    component = args[0].lower()
    
    if component == "frame":
        if ship["frame"]:
            removed_item = {
                "name": ship["frame"],
                "category": "frame",
                "subcategory": None,
                "data": ship["frame_stats"].copy()
            }
            inventory.append(removed_item)
            ship["frame"] = None
            ship["frame_stats"] = {}
            # Reset base stats
            for stat in ship["base_stats"]:
                ship["base_stats"][stat] = 0
            calculate_ship_stats()
            print_green(f"Removed frame and added to inventory.")
        else:
            print_red("No frame installed.")
    elif component.startswith("hp") and component[2:] in ship["hardpoints"]:
        hp_num = component[2:]
        if ship["hardpoints"][hp_num]:
            # Find the weapon data in store
            weapon_name = ship["hardpoints"][hp_num]
            _, _, _, weapon_data = find_item_in_store(weapon_name)
            if weapon_data:
                removed_item = {
                    "name": weapon_name,
                    "category": "hardpoints",
                    "subcategory": None,
                    "data": weapon_data.copy()
                }
                inventory.append(removed_item)
            ship["hardpoints"][hp_num] = None
            print_green(f"Removed {weapon_name} from hardpoint {hp_num}.")
        else:
            print_red(f"Hardpoint {hp_num} is empty.")
    else:
        print_red("Invalid component specified.")
    
    time.sleep(2)

def view_inventory():
    clear_screen()
    print_orange("== Inventory ==")
    if inventory:
        for i, item in enumerate(inventory):
            print(f"{i+1}. {item['name']} ({item['category']})")
            if item['subcategory']:
                print(f"   Subcategory: {item['subcategory']}")
            print(f"   Description: {item['data'].get('description', 'No description')}")
            print()
    else:
        print("Inventory is empty.")
    
    input("Press Enter to continue...")

def show_help(args):
    clear_screen()
    print_orange("== Help ==")
    
    if args:
        command = args[0].lower()
        if command == "store":
            print("Store Command:")
            print("Navigate through different categories of ship components.")
            print("Use category names to browse items.")
        elif command == "buy":
            print("Buy Command:")
            print("Usage: buy [item name] [hp<number> (optional)]")
            print("Examples:")
            print("  buy Scout Frame")
            print("  buy Laser Cannon hp1")
            print("Purchases items and adds them to inventory by default.")
        elif command == "view":
            print("View Command:")
            print("Shows current ship configuration and inventory.")
            print("Allows installing/removing components.")
        elif command == "name":
            print("Name Command:")
            print("Usage: name [ship name]")
            print("Sets the name of your ship.")
        elif command == "save":
            print("Save Command:")
            print("Usage: save [filename]")
            print("Saves your ship configuration to a file.")
        elif command == "load":
            print("Load Command:")
            print("Usage: load [filename]")
            print("Loads a ship configuration from a file.")
        else:
            print("No help available for that command.")
    else:
        print("Available Commands:")
        print("- store: Browse and purchase ship components")
        print("- buy [item] [hp<number>]: Purchase items")
        print("- name [ship name]: Set ship name")
        print("- view: View ship status and manage components")
        print("- save [filename]: Save ship configuration")
        print("- load [filename]: Load ship configuration")
        print("- help [command]: Get help for specific commands")
        print("- main: Return to main menu")
        print("- exit: Exit the program")
    
    input("\nPress Enter to continue...")

def save_ship(filename):
    try:
        data = {
            "ship": ship,
            "inventory": inventory
        }
        with open(f"{filename}.json", 'w') as f:
            json.dump(data, f, indent=2)
        print_green(f"Ship saved as {filename}.json")
    except Exception as e:
        print_red(f"Error saving ship: {str(e)}")
    time.sleep(2)

def load_ship(filename):
    try:
        with open(f"{filename}.json", 'r') as f:
            data = json.load(f)
        
        global ship, inventory
        ship = data["ship"]
        inventory = data["inventory"]
        
        print_green(f"Ship loaded from {filename}.json")
    except FileNotFoundError:
        print_red(f"File {filename}.json not found.")
    except Exception as e:
        print_red(f"Error loading ship: {str(e)}")
    time.sleep(2)

def main_menu():
    while True:
        clear_screen()
        print_orange("== Avalon Nexus Ship Up-link ==")
        print("\nAvailable Commands:")
        print("- store")
        print("- buy [item name] [hp<number> (optional)] (from main menu buys direct to inventory)")
        print("- name [ship name]")
        print("- view")
        print("- help [command]")
        print("- save [filename]")
        print("- load [filename]")
        print("- main (go back here anytime)")
        print("- exit\n")

        cmd = input("Command > ").strip()
        if not cmd:
            continue

        parts = cmd.split()
        command_input = parts[0]
        command = match_prefix(command_input, ["store", "buy", "name", "view", "help", "save", "load", "main", "exit"])
        if not command:
            print_red("Unknown or incomplete command.")
            time.sleep(2)
            continue

        args = parts[1:]

        if command == "exit":
            reverse_loading_animation()
            clear_screen()
            print_orange("== Avalon Nexus Ship Up-link Terminated ==")
            break

        elif command == "main":
            continue

        elif command == "store":
            store_menu()

        elif command == "buy":
            buy_item(args, to_inventory=True)

        elif command == "name":
            set_name(args)

        elif command == "view":
            result = view_menu()
            if result == "main":
                continue

        elif command == "help":
            show_help(args)

        elif command == "save":
            if args:
                save_ship(args[0])
            else:
                print_red("Please specify a filename to save.")
                time.sleep(2)

        elif command == "load":
            if args:
                load_ship(args[0])
            else:
                print_red("Please specify a filename to load.")
                time.sleep(2)

def store_menu():
    while True:
        clear_screen()
        print_orange("== Avalon Nexus Ship Up-link ==")
        print("\nStore Categories:")
        # Print top level categories
        print("- Frame")
        print("- Hull")
        print("- Superstructure")
        print("- Substructure")
        print("- Hardpoints")
        print("- Utilities")
        print("- back\n")
        print("Type category name to open it, or 'main' to return to main menu, or 'exit' to save and exit.\n")

        cmd = input("Store > ").strip()
        if not cmd:
            continue

        # Match categories with prefix
        category = None
        cat_input = cmd.lower()
        if cat_input in ['frame', 'hull', 'substructure', 'hardpoints', 'utilities']:
            category = cat_input
        elif cat_input.startswith('sup'):
            category = 'superstructure'
        elif cat_input in ['back', 'main', 'exit']:
            if cat_input == 'back':
                break
            elif cat_input == 'main':
                return "main"
            elif cat_input == 'exit':
                reverse_loading_animation()
                sys.exit(0)
        else:
            print_red("Unknown category.")
            time.sleep(2)
            continue

        if category == "superstructure":
            # Show superstructure subcategories
            result = superstructure_menu()
            if result == "main":
                return "main"
        elif category == "substructure":
            # Show substructure subcategories
            result = substructure_menu()
            if result == "main":
                return "main"
        else:
            # Open normal category
            result = open_category(category)
            if result == "main":
                return "main"

def superstructure_menu():
    while True:
        clear_screen()
        print_orange("== Superstructure Categories ==")
        print("\n- Generators")
        print("- Engines")
        print("- Communications and Sensors")
        print("- back\n")
        print("Type subcategory name to open it, 'main' to go to main menu, or 'back' to store categories.\n")

        cmd = input("Superstructure > ").strip().lower()
        if not cmd:
            continue

        if cmd in ['generators', 'engines', 'communications', 'communications and sensors', 'comm', 'comm and sensors']:
            # Normalize keys for store
            if cmd.startswith('gen'):
                subcat = 'generators'
            elif cmd.startswith('eng'):
                subcat = 'engines'
            else:
                subcat = 'communications and sensors'
            result = open_category("superstructure", subcat)
            if result == "main":
                return "main"
        elif cmd == "back":
            break
        elif cmd == "main":
            return "main"
        else:
            print_red("Unknown subcategory.")
            time.sleep(2)

def substructure_menu():
    while True:
        clear_screen()
        print_orange("== Substructure Categories ==")
        print("\n- Shields")
        print("- Misc")
        print("- back\n")
        print("Type subcategory name to open it, 'main' to go to main menu, or 'back' to store categories.\n")

        cmd = input("Substructure > ").strip().lower()
        if not cmd:
            continue

        if cmd in ['shields', 'shield']:
            result = open_category("substructure", "shields")
            if result == "main":
                return "main"
        elif cmd in ['misc', 'miscellaneous']:
            result = open_category("substructure", "misc")
            if result == "main":
                return "main"
        elif cmd == "back":
            break
        elif cmd == "main":
            return "main"
        else:
            print_red("Unknown subcategory.")
            time.sleep(2)

def open_category(category, subcategory=None):
    while True:
        clear_screen()
        if subcategory:
            print_orange(f"== Viewing {category.title()} - {subcategory.title()} ==")
            items = store[category][subcategory]
        else:
            print_orange(f"== Viewing {category.title()} ==")
            items = store[category]

        print()
        for item in items:
            print(f"- {item}")
        print("- back\n")
        print("Type 'buy [item name] [hpX (optional)]' to purchase.")
        print("Type item name alone to view details.")
        print("Type 'main' to return to main menu, or 'back' to previous menu.\n")

        cmd = input("Category > ").strip()
        if not cmd:
            continue

        parts = cmd.split()
        command_input = parts[0]

        # Commands we accept here
        possible_commands = ["back", "main", "buy"] + list(items.keys())
        nav_command = match_prefix(command_input, possible_commands)
        if nav_command:
            if nav_command == "back":
                break
            if nav_command == "main":
                return "main"
            if nav_command == "buy":
                buy_item(parts[1:], to_inventory=True)  # Buying inside store adds to inventory
                continue

            # Show item info
            if nav_command in items:
                clear_screen()
                print_orange(f"== {nav_command} Info ==")
                for k, v in items[nav_command].items():
                    print(f"{k.title()}: {v}")
                input("\nPress Enter to continue...")
                continue

        # If no match, try exact (case insensitive)
        item_name_input = cmd.lower()
        found_item = None
        for item in items:
            if item.lower() == item_name_input:
                found_item = item
                break

        if found_item:
            clear_screen()
            print_orange(f"== {found_item} Info ==")
            for k, v in items[found_item].items():
                print(f"{k.title()}: {v}")
            input("\nPress Enter to continue...")
        else:
            print_red("Item not found.")
            time.sleep(2)

if __name__ == "__main__":
    # Check audio files in ShipAssets folder
    check_audio_files()
    
    loading_animation()
    main_menu()
