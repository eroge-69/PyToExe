#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New Rhythm Game — A/L + Combos
Main features:
 - Main Menu with custom background image
 - Fake Loading screen (3 seconds) before gameplay
 - Settings screen to adjust music volume (left/right arrows)
 - Difficulty select (Easy / Normal / Hard)
 - Fullscreen toggle (F11 or Alt+Enter) without changing the game's look (uses SCALED)
 - Game uses A = left, L = right, A+L = combo notes
 - Use [ / ] to tweak BPM, - / = to tweak offset, P/ESC to pause, Q to quit
"""

import os
import sys
import pygame
from pygame import Rect

# ---------------- CONFIG --------------------
SONG_PATH = r"/mnt/data/ヒミツのテレパス (feat. 琴葉 茜・葵) by irucaice, 琴葉 茜・葵.mp3"
MENU_BG_PATH = r"/mnt/data/Screenshot 2025-09-04 110746.png"  # provided image
GAME_TITLE = "new rhythm game"

# Gameplay / timing (defaults for Normal; difficulty can override)
BPM = 120.0
START_OFFSET_SEC = 2.0
WINDOW_PERFECT = 50
WINDOW_GOOD    = 100
WINDOW_OK      = 160

# Visual (logical resolution; SCALED keeps the look in fullscreen)
WIDTH, HEIGHT = 900, 600
HIT_LINE_Y = HEIGHT - 120
LANE_W = 180
NOTE_H = 18
NOTE_SPEED = 550
FONT_NAME = None

# Loading screen duration (ms)
FAKE_LOAD_MS = 3000

# ----------------- CLASSES ------------------
class Note:
    def __init__(self, lane, hit_time_ms):
        self.lane = lane  # "L","R","C"
        self.hit_time = hit_time_ms
        self.hit = False
        self.judged = False
        self.result = None
        if lane == "L":
            self.x = WIDTH//2 - LANE_W - 12
            self.w = LANE_W
        elif lane == "R":
            self.x = WIDTH//2 + 12
            self.w = LANE_W
        else:
            self.x = WIDTH//2 - (LANE_W + 12)
            self.w = 2*LANE_W + 24
        self.y = -50

    def screen_y(self, song_ms, note_travel_ms):
        dt = (self.hit_time - song_ms)
        return HIT_LINE_Y - (dt / note_travel_ms) * (HIT_LINE_Y + 100)


class NewRhythmGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception as e:
            print("Warning: mixer init failed:", e)

        # window (use logical size; we can toggle SCALED fullscreen later)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 22)
        self.bigfont = pygame.font.Font(FONT_NAME, 36)

        # colors
        self.BG = (18, 18, 24)
        self.LANE = (40, 40, 60)
        self.HITLINE = (200, 200, 220)
        self.NOTE_L = (120, 180, 255)
        self.NOTE_R = (255, 170, 120)
        self.NOTE_C = (180, 255, 160)
        self.TEXT = (235, 235, 245)

        # game flow states: MENU, LOADING, SETTINGS, GAME, RESULTS
        self.state = "MENU"
        self.menu_options = ["Start Game", "Difficulty", "Settings", "Quit"]
        self.menu_index = 0

        # settings
        self.volume = 0.9  # 0.0 - 1.0
        self.bpm = BPM
        self.global_offset_ms = int(START_OFFSET_SEC * 1000)
        self.beat_interval_ms = 60000.0 / self.bpm
        self.travel_time_ms = int((HIT_LINE_Y + 100) / NOTE_SPEED * 1000)

        # difficulty
        self.difficulties = ["Easy", "Normal", "Hard"]
        self.difficulty_index = 1  # default Normal
        self.apply_difficulty()

        # fullscreen flag
        self.is_fullscreen = False

        # game variables
        self.notes = []
        self.next_beat_index = 0
        self.generated_until_ms = 0

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.last_judgement = ""
        self.last_judge_timer = 0

        self.a_pressed_time = None
        self.l_pressed_time = None

        self.start_ticks = None
        self.started = False
        self.paused = False
        self.finished = False

        # load assets
        self.menu_bg = self.load_menu_bg(MENU_BG_PATH)
        self.song_loaded = self.load_song(SONG_PATH)
        if self.song_loaded:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception:
                pass

    # -------- difficulty / fullscreen ----------
    def apply_difficulty(self):
        """Adjust note speed and timing windows. Keeps visuals identical in style."""
        global WINDOW_PERFECT, WINDOW_GOOD, WINDOW_OK, NOTE_SPEED
        diff = self.difficulties[self.difficulty_index]
        if diff == "Easy":
            WINDOW_PERFECT, WINDOW_GOOD, WINDOW_OK = 80, 140, 220
            NOTE_SPEED = 400
        elif diff == "Normal":
            WINDOW_PERFECT, WINDOW_GOOD, WINDOW_OK = 50, 100, 160
            NOTE_SPEED = 550
        else:  # Hard
            WINDOW_PERFECT, WINDOW_GOOD, WINDOW_OK = 30, 70, 120
            NOTE_SPEED = 700
        # recompute travel time for the new speed
        self.travel_time_ms = int((HIT_LINE_Y + 100) / NOTE_SPEED * 1000)

    def toggle_fullscreen(self):
        """Toggle fullscreen using SCALED to preserve the game's look."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            # SCALED keeps logical (WIDTH x HEIGHT) and scales to screen
            self.screen = pygame.display.set_mode(
                (WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED
            )
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def handle_global_keys(self, ev):
        """Keys that work anywhere (menus, loading, settings, game)."""
        if ev.type == pygame.KEYDOWN:
            alt_enter = (ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER)) and (ev.mod & pygame.KMOD_ALT)
            if ev.key == pygame.K_F11 or alt_enter:
                self.toggle_fullscreen()

    # -------------- loading -------------------
    def load_menu_bg(self, path):
        try:
            if os.path.isfile(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
                return img
            else:
                print("Menu background not found at", path)
                return None
        except Exception as e:
            print("Error loading menu background:", e)
            return None

    def load_song(self, path):
        try:
            if not os.path.isfile(path):
                base = os.path.basename(path)
                alt = os.path.join(os.path.dirname(__file__), base)
                if os.path.isfile(alt):
                    path = alt
                else:
                    print("Song not found:", path)
                    return False
            pygame.mixer.music.load(path)
            return True
        except Exception as e:
            print("Error loading song:", e)
            return False

    # -------- menu / settings --------
    def process_menu_input(self, events):
        for ev in events:
            if ev.type == pygame.QUIT:
                self.quit_game()
            self.handle_global_keys(ev)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                elif ev.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    sel = self.menu_options[self.menu_index]
                    if sel == "Start Game":
                        self.state = "LOADING"
                        self.loading_start = pygame.time.get_ticks()
                    elif sel == "Difficulty":
                        self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulties)
                        self.apply_difficulty()
                    elif sel == "Settings":
                        self.state = "SETTINGS"
                    elif sel == "Quit":
                        self.quit_game()

    def process_settings_input(self, events):
        for ev in events:
            if ev.type == pygame.QUIT:
                self.quit_game()
            self.handle_global_keys(ev)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LEFT:
                    self.volume = max(0.0, round(self.volume - 0.05, 2))
                    try:
                        pygame.mixer.music.set_volume(self.volume)
                    except:
                        pass
                elif ev.key == pygame.K_RIGHT:
                    self.volume = min(1.0, round(self.volume + 0.05, 2))
                    try:
                        pygame.mixer.music.set_volume(self.volume)
                    except:
                        pass
                elif ev.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                elif ev.key == pygame.K_q:
                    self.quit_game()

    # --------- game input (A/L) ---------
    def process_game_input(self, events, song_ms):
        for ev in events:
            if ev.type == pygame.QUIT:
                self.quit_game()
            self.handle_global_keys(ev)
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.paused = not self.paused
                    if self.paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif ev.key == pygame.K_q:
                    self.quit_game()
                elif ev.key == pygame.K_LEFTBRACKET:
                    self.bpm = max(40.0, self.bpm - 1.0)
                    self.beat_interval_ms = 60000.0 / self.bpm
                    self.last_floating_text(f"BPM {self.bpm:.0f}")
                elif ev.key == pygame.K_RIGHTBRACKET:
                    self.bpm = min(240.0, self.bpm + 1.0)
                    self.beat_interval_ms = 60000.0 / self.bpm
                    self.last_floating_text(f"BPM {self.bpm:.0f}")
                elif ev.key == pygame.K_MINUS:
                    self.global_offset_ms -= 10
                    self.last_floating_text(f"Offset {self.global_offset_ms} ms")
                elif ev.key == pygame.K_EQUALS or ev.key == pygame.K_PLUS:
                    self.global_offset_ms += 10
                    self.last_floating_text(f"Offset {self.global_offset_ms} ms")
                elif ev.key == pygame.K_a:
                    self.handle_hit_key('A', song_ms)
                elif ev.key == pygame.K_l:
                    self.handle_hit_key('L', song_ms)

    def handle_hit_key(self, key, song_ms):
        if key == 'A':
            self.a_pressed_time = song_ms
        elif key == 'L':
            self.l_pressed_time = song_ms

        note_idx = self.find_best_note_for_key(key, song_ms)
        if note_idx is not None:
            note = self.notes[note_idx]
            if note.lane == 'C':
                other_time = self.l_pressed_time if key == 'A' else self.a_pressed_time
                if other_time is not None and abs(other_time - song_ms) <= WINDOW_OK:
                    delta_a = abs((self.a_pressed_time or song_ms) - note.hit_time)
                    delta_l = abs((self.l_pressed_time or song_ms) - note.hit_time)
                    worst = max(delta_a, delta_l)
                    hit_result = self.judge_delta(worst)
                    self.apply_judgement(note, hit_result)
                    self.a_pressed_time = None
                    self.l_pressed_time = None
                else:
                    return
            else:
                delta = abs(song_ms - note.hit_time)
                hit_result = self.judge_delta(delta)
                self.apply_judgement(note, hit_result)

    def find_best_note_for_key(self, key, song_ms):
        lanes = ['L', 'C'] if key == 'A' else ['R', 'C']
        best_idx = None
        best_dt = 10**9
        for i, n in enumerate(self.notes):
            if n.judged or n.lane not in lanes:
                continue
            dt = abs(song_ms - n.hit_time)
            if dt < best_dt and dt <= WINDOW_OK:
                best_dt = dt
                best_idx = i
        return best_idx

    def judge_delta(self, delta_ms):
        if delta_ms <= WINDOW_PERFECT:
            return "Perfect"
        elif delta_ms <= WINDOW_GOOD:
            return "Good"
        elif delta_ms <= WINDOW_OK:
            return "Ok"
        else:
            return "Miss"

    def apply_judgement(self, note, judgement):
        note.judged = True
        note.hit = (judgement != "Miss")
        note.result = judgement
        if judgement == "Perfect":
            self.score += 100
            self.combo += 1
        elif judgement == "Good":
            self.score += 70
            self.combo += 1
        elif judgement == "Ok":
            self.score += 40
            self.combo += 1
        else:
            self.combo = 0
            self.health = max(0, self.health - 5)
        self.max_combo = max(self.max_combo, self.combo)
        self.last_judgement = judgement
        self.last_judge_timer = pygame.time.get_ticks()

    # ---------- generate / update ----------
    def generate_notes_until(self, target_ms):
        while True:
            beat_time = self.global_offset_ms + int(self.next_beat_index * self.beat_interval_ms)
            if beat_time > target_ms + 2000:
                break
            lane = "C" if self.next_beat_index % 4 == 3 else ("L" if self.next_beat_index % 2 == 0 else "R")
            self.notes.append(Note(lane, beat_time))
            self.next_beat_index += 1
        self.generated_until_ms = target_ms

    def start_music(self):
        try:
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.volume)
        except Exception as e:
            print("Error starting music:", e)
        self.start_ticks = pygame.time.get_ticks()
        self.started = True

    def song_ms(self):
        if not self.started or self.start_ticks is None:
            return 0
        pos = pygame.mixer.music.get_pos()
        if pos < 0:
            return pygame.time.get_ticks() - self.start_ticks
        return pos

    def update_game(self, dt):
        if not self.started:
            self.start_music()
        if self.paused:
            return
        song_ms = self.song_ms()
        self.generate_notes_until(song_ms + 8000)
        for n in self.notes:
            if not n.judged and song_ms - n.hit_time > WINDOW_OK + 60:
                n.judged = True
                n.hit = False
                n.result = "Miss"
                self.combo = 0
                self.health = max(0, self.health - 5)
                self.last_judgement = "Miss"
                self.last_judge_timer = pygame.time.get_ticks()
        if not pygame.mixer.music.get_busy():
            all_judged = all(n.judged for n in self.notes)
            if all_judged and song_ms > self.global_offset_ms + 1000:
                self.finished = True

    # ---------- draw helpers ----------
    def draw_text_center(self, text, font, color, y=None):
        surf = font.render(text, True, color)
        if y is None:
            y = HEIGHT//2 - surf.get_height()//2
        self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))

    def last_floating_text(self, text):
        self.last_judgement = text
        self.last_judge_timer = pygame.time.get_ticks()

    # ---------- drawings ----------
    def draw_menu(self):
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
            # faded title overlay
            title_surf = self.bigfont.render(GAME_TITLE, True, (245, 245, 245))
            title_bg = pygame.Surface((title_surf.get_width() + 30, title_surf.get_height() + 20), pygame.SRCALPHA)
            title_bg.fill((0, 0, 0, 140))
            self.screen.blit(title_bg, (WIDTH//2 - title_bg.get_width()//2, 40))
            self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))
        else:
            self.screen.fill(self.BG)
            self.draw_text_center(GAME_TITLE, self.bigfont, self.TEXT, 80)

        # menu options
        for i, opt in enumerate(self.menu_options):
            text = opt
            if opt == "Difficulty":
                text += f": {self.difficulties[self.difficulty_index]}"
            color = (255, 255, 200) if i == self.menu_index else (200, 200, 200)
            opt_surf = self.font.render(text, True, color)
            self.screen.blit(opt_surf, (WIDTH//2 - opt_surf.get_width()//2, 240 + i*48))

        # hint
        hint = "↑/↓: move  Enter: select  F11/Alt+Enter: fullscreen"
        self.screen.blit(self.font.render(hint, True, (180, 180, 200)), (WIDTH//2 - 260, HEIGHT - 40))

    def draw_loading(self):
        self.screen.fill((14, 14, 18))
        self.draw_text_center("Loading...", self.bigfont, (240, 240, 240))
        # simple progress based on time elapsed
        elapsed = pygame.time.get_ticks() - self.loading_start
        pct = min(1.0, elapsed / FAKE_LOAD_MS)
        bar_w = 500
        bar_h = 18
        x = WIDTH//2 - bar_w//2
        y = HEIGHT//2 + 60
        pygame.draw.rect(self.screen, (60, 60, 70), (x, y, bar_w, bar_h), border_radius=8)
        pygame.draw.rect(self.screen, (120, 200, 180), (x, y, int(bar_w * pct), bar_h), border_radius=8)

    def draw_settings(self):
        self.screen.fill((12, 12, 16))
        title = self.bigfont.render("Settings", True, self.TEXT)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        vol_line = f"Music Volume: {int(self.volume*100)}%    (← / →)"
        self.screen.blit(self.font.render(vol_line, True, (220, 220, 220)), (WIDTH//2 - 200, HEIGHT//2 - 12))
        hint = "Esc: back  F11/Alt+Enter: fullscreen"
        self.screen.blit(self.font.render(hint, True, (180, 180, 180)), (20, HEIGHT - 40))

    def draw_game(self):
        self.screen.fill(self.BG)
        left_rect = Rect(WIDTH//2 - LANE_W - 12, 0, LANE_W, HEIGHT)
        right_rect = Rect(WIDTH//2 + 12, 0, LANE_W, HEIGHT)
        pygame.draw.rect(self.screen, self.LANE, left_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.LANE, right_rect, border_radius=16)
        pygame.draw.line(self.screen, self.HITLINE, (0, HIT_LINE_Y), (WIDTH, HIT_LINE_Y), 3)

        song_ms = self.song_ms()
        for n in self.notes:
            if n.judged:
                continue
            y = n.screen_y(song_ms, self.travel_time_ms)
            if y > HEIGHT + 30:
                continue
            rect = Rect(n.x, y, n.w, NOTE_H)
            color = self.NOTE_L if n.lane == 'L' else self.NOTE_R if n.lane == 'R' else self.NOTE_C
            pygame.draw.rect(self.screen, color, rect, border_radius=8)

        # HUD
        hud_text = (
            f"Score: {self.score}   Combo: {self.combo}   Max: {self.max_combo}   "
            f"BPM: {self.bpm:.0f}   Offset: {self.global_offset_ms} ms"
        )
        surf = self.font.render(hud_text, True, self.TEXT)
        self.screen.blit(surf, (20, 16))

        bar_w = 260
        bar_h = 16
        x = WIDTH - bar_w - 24
        y = 16
        pygame.draw.rect(self.screen, (70, 70, 90), (x, y, bar_w, bar_h), border_radius=10)
        fill_w = int(bar_w * self.health / 100)
        pygame.draw.rect(self.screen, (120, 220, 160), (x, y, fill_w, bar_h), border_radius=10)

        if self.last_judgement:
            t = pygame.time.get_ticks() - self.last_judge_timer
            if t < 600:
                alpha = max(0, 255 - int(255 * (t / 600)))
                msg = self.bigfont.render(self.last_judgement, True, self.TEXT)
                msg.set_alpha(alpha)
                self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HIT_LINE_Y - 80))

        help_lines = [
            "A: Left  |  L: Right  |  A+L: Combo",
            "[ / ]: BPM  |  - / =: Offset  |  P/ESC: Pause  |  Q: Quit  |  F11/Alt+Enter: Fullscreen",
        ]
        for i, line in enumerate(help_lines):
            s = self.font.render(line, True, (180, 180, 200))
            self.screen.blit(s, (20, HEIGHT - 60 + 20 * i))

        if self.finished:
            self.draw_results()

    def draw_results(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        title = self.bigfont.render("Results", True, self.TEXT)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 140))
        lines = [
            f"Score: {self.score}",
            f"Max Combo: {self.max_combo}",
            "Press Q to quit.",
        ]
        for i, line in enumerate(lines):
            s = self.font.render(line, True, self.TEXT)
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 220 + i * 36))

    # ---------- main loop and state transitions ----------
    def run(self):
        while True:
            dt = self.clock.tick(120)
            events = pygame.event.get()

            if self.state == "MENU":
                self.process_menu_input(events)
                self.draw_menu()

            elif self.state == "LOADING":
                # allow global keys during loading
                for ev in events:
                    if ev.type == pygame.QUIT:
                        self.quit_game()
                    self.handle_global_keys(ev)
                # show fake loading, then switch to GAME
                self.draw_loading()
                if pygame.time.get_ticks() - self.loading_start >= FAKE_LOAD_MS:
                    self.reset_game_state()
                    self.state = "GAME"

            elif self.state == "SETTINGS":
                self.process_settings_input(events)
                self.draw_settings()

            elif self.state == "GAME":
                song_ms = self.song_ms()
                self.process_game_input(events, song_ms)
                self.update_game(dt)
                self.draw_game()

            pygame.display.flip()

    def reset_game_state(self):
        # reset gameplay variables and start music
        self.notes = []
        self.next_beat_index = 0
        self.generated_until_ms = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.last_judgement = ""
        self.last_judge_timer = 0
        self.a_pressed_time = None
        self.l_pressed_time = None
        self.start_ticks = None
        self.started = False
        self.paused = False
        self.finished = False
        # make sure current difficulty speed is applied
        self.apply_difficulty()
        # ensure volume applied
        try:
            pygame.mixer.music.set_volume(self.volume)
        except:
            pass

    def quit_game(self):
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    game = NewRhythmGame()
    game.run()


