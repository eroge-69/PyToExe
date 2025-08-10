from pynput.keyboard import Controller
import time

# NOTE sequence ដែលអ្នកផ្ដល់
notes = """
t r w t r w t r w t y u 
[4o] p s g f d 5 a s d s 
[1o] u i o 
[6a] s 
[4o] p s g f a 5 h g f 
[1s] s s d d d 
[6f] f f a a a 4 t p o 
[5p] o u i 
[1o] i u t 
[6t] 4 p o o t 
[5u] y t y 
[1o] i u i 
[6u] y t 
[4u] o u y t 
[5u] o u u o 
[1p] o u y 
[6t] t y 
[4u] o u p o 
[5y] u y u 
[8t] 
[6t] t 
[4h] s s p p a s 
[5d] o o f d 
[1of] d d s 
[6p] p a s 
[4h] s s p a s 
[5d] o o f d 
[1f] d 
[Oad] s 
[6p] o u o 
[4p] o i 
[5u] y t 
[1tu] o 
[Wry] u 
[6et] p o 
[4t] p 
[5o] i u 
[8t] r w 
[8t] r w 
[6t] r w 
[6t] y 
[6u] 
[4o] p s g f d 5 a s d s 
[1o] u i o 
[6a] s 
[4o] p s g f a 5 h g f 
[1s] s s d d d 
[6f] f f a a a 
[4o] p s g f d 5 a s d s 
[1o] u i o 
[6a] s 
[4f] h f s p 
[5a] o a s d 
[1s] 
[6a] s s 
[qa] p 
[qp] o 
[wp] 
[wy] u 8 8 
[6et] 
[6y] u 
[4tp] o 
[4o] u 
[5p] o u 
[5y] t 
[8p] o u 
[8y] t 
[6et] 6 a 
[qs] a 
[qp] o 
[7u] o 7 u 
[8p] o u 
[8y] u o 
[6u] 
[6t] y u 
[4p] o 
[4o] u 
[5o] u 
[5o] u y 
[8t] 8 6 6 
[qh] s s p 
[ep] a s 
[wd] 
[ro] f d 
[tf] d 
[td] s 
[ep] p a s 
[qh] s s 
[ep] a s 
[wd] 
[ro] f d 
[tf] d 
[Wd] s 
[ep] o u o 
[qp] o i 
[wu] y t 
[wu] o 
[W0y] u 
[et] p o 
[qt] p 
[wo] i u 
[8t] r w 
[8t] r 
[8w] 
[6t] r w 
[6t] y u 
[4o] p s 
[4g] f d 5 a 
[5s] d s 
[8o] 
[8u] i o 
[6a] 
[6s] 
[4o] p s 
[4g] f a 5 
[5h] g f 
[8s] s s 
[8d] d d 
[6f] f f 
[6a] a a 
[4o] p s 
[4g] f d 5 a 
[5s] d s 
[8o] 
[8u] i o 
[6a] 
[6s] 
[4f] h f 
[4s] p 
[5a] o 
[5a] s d 
[8s] 
[8s] 
[6a] 
[6s] 
[ih] j l c x z o k l z l 
[sh] f g h 
[psk] l 
[ix] v x l j 
[ok] h k l z 
[sl]
"""

# Settings
tempo = 0.25  # ចន្លោះពេលចុច key (លឿន / យឺត)
keyboard = Controller()

def play_notes(note_string):
    for token in note_string.split():
        # Remove square brackets from chords
        chord = token.strip("[]")
        # ចុចច្រើន key ប្រសិនបើជាកូដ chord
        for char in chord:
            keyboard.press(char.lower())
        for char in chord:
            keyboard.release(char.lower())
        time.sleep(tempo)

if __name__ == "__main__":
    print("Switch to Roblox piano within 5 seconds...")
    time.sleep(5)
    play_notes(notes)
    print("Finished!")