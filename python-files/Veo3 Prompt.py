
"""
Universal King • Veo3 Prompt Forge (Visual + Sound)
Version: 1.1

Usage:
    from universal_king_veo3 import generate_prompt

    seed = {
        "concept": "phoenix coronation over desert citadel",
        "genre": "epic_fantasy",
        "emotion_core": ["epic_majesty", "sacred_glow"],
        "time_period": "ancient",
        "setting_hint": "sandstone fortress with banners",
        "subject_focus": "crowned phoenix and ceremonial herald",
        "duration": "8s",
        "aspect_ratio": "16:9",
        "fps": 24,
        "audio_style": "orchestral_epic"
    }

    render = generate_prompt(seed)
    print(json.dumps(render, indent=2))

Notes:
- This is a deterministic string composer (no external APIs).
- It follows the blueprint and assembly rules you provided.
"""

from typing import List, Dict
import random

DEFAULTS = {
    "genre": "epic_fantasy",
    "emotion_core": ["epic_majesty"],
    "time_period": "timeless",
    "setting_hint": "vast open environment",
    "subject_focus": "primary hero figure",
    "duration": "8s",
    "aspect_ratio": "16:9",
    "fps": 24,
    "audio_style": "hybrid_cinematic"
}

PALETTES = {
    "warm_epic": ["gold_ember", "crimson", "smoke_grey"],
    "cool_mystic": ["sapphire_blue", "jade", "smoke_grey"],
    "teal_orange": ["teal", "orange_glow", "graphite"],
    "monochrome_noir": ["charcoal", "silver", "ink_black"]
}

CAMERA_ANGLES = ["low_hero", "high_god", "eye_level", "aerial_orbit", "macro_close"]
CAMERA_MOVES = ["slow_dolly", "steady_orbit", "crane_rise", "push_in", "locked_frame"]
LENSES = ["21mm_anamorphic", "35mm", "50mm_macro", "85mm_portrait"]
DOF = ["deep", "medium", "shallow_bokeh"]

LIGHT_KEYS = ["soft_warm", "hard_rim", "moon_silver", "neon_mix", "divine_glow"]
LIGHT_FILL = ["ambient_bounce", "torch_flicker", "holographic"]
LIGHT_BACK = ["god_rays", "rim_fire", "moon_halo"]
CONTRAST = ["high", "balanced", "filmic"]

MATERIALS = ["silk_thread", "aged_bronze", "wet_stone", "crystal", "holo_mesh"]
MICRO = ["skin_pores", "fabric_weave", "condensation", "hair_strands"]
MACRO = ["sparks", "floating_petals", "rain_sheet", "snow_swirl", "sand_ribbon"]

PHYSICS_BEND = ["frozen_lightning", "floating_waterfalls", "time_echoes", "gravity_bloom"]
DIVINE_SIGNS = ["peacock_feather_aura", "chakra_glow", "constellation_runes"]

NEGATIVES = [
    "no_text_overlays",
    "no_ui_watermarks",
    "no_modern_streetwear_if_historical",
    "no_goofy_faces",
    "no_low_detail_backgrounds",
    "no_overexposure",
    "no_cartoonish_proportions"
]

def choose(seq, n=1):
    seq = list(seq)
    random.shuffle(seq)
    return seq[:n] if n>1 else seq[0]

def _mood_bias_from_genre(genre:str)->str:
    return {
        "epic_fantasy": "warm_epic",
        "mythic": "warm_epic",
        "historical": "warm_epic",
        "sci_fi": "cool_mystic",
        "noir": "monochrome_noir",
        "horror": "cool_mystic",
        "surreal": "teal_orange",
        "romance": "warm_epic"
    }.get(genre, "warm_epic")

def _assemble_description(seed:Dict, picks:Dict)->str:
    # One-flow cinematic paragraph per assembly rules
    environment = (
        f"In the {seed.get('time_period')} era, {seed.get('setting_hint')} unfolds at "
        f"{picks.get('scale','grand')} scale under {picks.get('weather','storm')} skies, "
        f"air alive with {', '.join(picks['atmosphere_particles'])};"
    )
    subject = (
        f" {seed.get('concept')} centers on {seed.get('subject_focus')}, rendered with "
        f"hyper-real textures across {', '.join(picks['materials'])}, micro-details of "
        f"{', '.join(picks['micro'])}, and macro effects like {', '.join(picks['macro'])};"
    )
    story = (
        f" the moment captures {seed.get('genre')} energy as {picks['action']}—"
        f"a beat structure of setup, surge, and {'impact' if seed.get('genre')!='noir' else 'stillness'};"
    )
    camera = (
        f" filmed via {picks['camera_angle']} angle with {picks['camera_movement']} motion, "
        f"{picks['lens']} lens, {picks['dof']} depth-of-field;"
    )
    lighting = (
        f" lit by {picks['light_key']} key, {picks['light_fill']} fill, and {picks['light_back']} backlight "
        f"with volumetric presence and {picks['contrast']} contrast;"
    )
    color = (
        f" color grade leans {picks['mood_bias']} using palette {', '.join(picks['palette'])};"
    )
    magic = (
        f" the world bends with {', '.join(picks['physics_bend'])} and bears signs of "
        f"{', '.join(picks['divine_signs'])};"
    )
    performance = (
        f" performance tempo is {picks['tempo']} with an energy curve of rise–hold–resolve, "
        f"loop-friendly composition;"
    )
    quality = (
        " final image is hyper-cinematic, ultra-detailed, photoreal yet poetically surreal, HDR with subtle film grain and precision grading."
    )
    return (environment + subject + story + camera + lighting + color + magic + performance + quality).strip()

def _assemble_sound(seed:Dict, picks:Dict)->str:
    core = seed.get("audio_style", DEFAULTS["audio_style"])
    elements = [
        "deep_sub_bass_rumble",
        "ethereal_choir_layer",
        picks["signature_instrument"],
        picks["ambient_fx"],
        picks["percussive_hit"]
    ]
    return (f"{core} score with layered elements: {', '.join(elements)}; "
            f"tempo synced to {picks['tempo']} visual pacing; "
            f"spatial mix is cinematic surround with foreground clarity; "
            f"emotional bias reflects {', '.join(seed.get('emotion_core', DEFAULTS['emotion_core']))}.")

def generate_prompt(seed:Dict)->Dict:
    # Merge defaults
    s = {**DEFAULTS, **seed}
    # Picks
    picks = {
        "scale": choose(["intimate","medium","grand","cosmic"]),
        "weather": choose(["clear","fog","storm","snow","sandstorm","cosmic_dust"]),
        "atmosphere_particles": choose(["dust_motes","embers","mist","pollen","sparkles"], n=3),
        "materials": choose(MATERIALS, n=3),
        "micro": choose(MICRO, n=2),
        "macro": choose(MACRO, n=2),
        "action": f"a decisive action unfolds around {s.get('concept')}",
        "camera_angle": choose(CAMERA_ANGLES),
        "camera_movement": choose(CAMERA_MOVES),
        "lens": choose(LENSES),
        "dof": choose(DOF),
        "light_key": choose(LIGHT_KEYS),
        "light_fill": choose(LIGHT_FILL),
        "light_back": choose(LIGHT_BACK),
        "contrast": choose(CONTRAST),
        "mood_bias": _mood_bias_from_genre(s.get("genre")),
        "palette": PALETTES.get(_mood_bias_from_genre(s.get("genre")), PALETTES["warm_epic"]),
        "physics_bend": choose(PHYSICS_BEND, n=2),
        "divine_signs": choose(DIVINE_SIGNS, n=1),
        "tempo": choose(["slow_majestic","meditative","kinetic"]),
        "signature_instrument": choose([
            "taiko_drums","sarod","veena","erhu","duduk","glass_harmonica",
            "modular_synth_lead","choir_solo_soprano","war_horns"
        ]),
        "ambient_fx": choose(["nebula_wind","ocean_whispers","temple_echo","rain_hiss","electro_hum"]),
        "percussive_hit": choose(["impact_braaam","granular_riser_hit","gong_strike","knife_sweep_cymbal"])
    }

    description = _assemble_description(s, picks)
    sound = _assemble_sound(s, picks)

    render = {
        "description": description,
        "camera": f"{picks['camera_angle']} {picks['camera_movement']} {picks['lens']} {picks['dof']}",
        "lighting": f"{picks['light_key']} {picks['light_fill']} {picks['light_back']} true {picks['contrast']}",
        "style": "hyper-cinematic, ultra-detailed, realistic textures with poetic surreal accents",
        "color": f"palette: {', '.join(picks['palette'])}; mood: {picks['mood_bias']}",
        "effects": f"{', '.join(picks['macro'])}; micro: {', '.join(picks['micro'])}; physics: {', '.join(picks['physics_bend'])}; signs: {', '.join([picks['divine_signs']] if isinstance(picks['divine_signs'], str) else picks['divine_signs'])}",
        "sound": sound,
        "duration": s.get("duration"),
        "aspect_ratio": s.get("aspect_ratio"),
        "resolution": "4K",
        "fps": s.get("fps"),
        "negatives": ", ".join(NEGATIVES)
    }
    return render

if __name__ == "__main__":
    # Simple CLI demo
    demo_seed = {
        "concept": "phoenix coronation over desert citadel",
        "genre": "epic_fantasy",
        "emotion_core": ["epic_majesty", "sacred_glow"],
        "time_period": "ancient",
        "setting_hint": "polished sandstone fortress under banners",
        "subject_focus": "crowned phoenix ascending; herald on ramparts",
        "duration": "8s",
        "aspect_ratio": "16:9",
        "fps": 24,
        "audio_style": "orchestral_epic"
    }
    print(json.dumps(generate_prompt(demo_seed), indent=2))
