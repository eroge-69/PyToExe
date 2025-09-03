from pydoc import text
from pygame import mixer
from GDI_effects.GDI import *
mixer.init()
mixer.music.load("C:\KOOL1.wav")
mixer.music.play(1)
Effects.glitch_screen(repeat=900)
mixer.music.load("C:\KOOL2.wav")
mixer.music.play(1)
Effects.rainbow_blink(repeat=900)
mixer.music.load("C:\KOOL3.wav")
mixer.music.play(1)
Effects.rotate_screen(repeat=900)
mixer.music.load("C:\KOOL4.wav")
mixer.music.play(1)
Effects.rotate_screen(repeat=900)
mixer.music.load("C:\KOOL5.wav")
mixer.music.play(-1)
Effects.void_screen
Effects.flip_screen_upside_down
Effects.invert_screen
Effects.error_screen
Effects.bw_screen
