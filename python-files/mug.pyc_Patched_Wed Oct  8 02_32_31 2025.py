# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: mug.py
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import pygame
import sys
import os
import math
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import threading
import time
from fractions import Fraction
pygame.init()
pygame.mixer.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
JUDGE_LINE_Y = int(SCREEN_HEIGHT * 0.8)
TRACK_WIDTH = 120
TRACK_COUNT = 4
TRACK_START_X = (SCREEN_WIDTH - TRACK_WIDTH * TRACK_COUNT) // 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)
KEY_MAP = {pygame.K_d: 0, pygame.K_f: 1, pygame.K_j: 2, pygame.K_k: 3}

class NoteType(Enum):
    TAP = 1
    HOLD = 2
    SLIDE = 3

class JudgeType(Enum):
    PERFECT = 1
    GREAT = 2
    GOOD = 3
    MISS = 4

@dataclass
class Note:
    track: int
    time: float
    note_type: NoteType
    end_time: float = 0.0
    hit: bool = False
    judge: Optional[JudgeType] = None
    processed: bool = False
    hold_start_judge: Optional[JudgeType] = None
    show_judge: bool = False

class GameState(Enum):
    MENU = 1
    SONG_SELECT = 2
    PLAYING = 3
    RESULT = 4
    CREDITS = 5

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Meteor Nuker')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.state = GameState.MENU
        self.running = True
        self.song_title = 'Ultimate Shot - To Cosmos'
        self.difficulties = ['Easy', 'Present', 'Expert', 'Glitch', 'Meteor Shower']
        self.selected_difficulty = 0
        self.notes = []
        self.current_time = 0.0
        self.song_length = 120000
        self.offset = 1000
        self.bpm = 120
        self.music_file = None
        self.music_loaded = False
        self.music_volume = 0.7
        self.music_start_delay = 1000
        self.keys_pressed = [False] * 4
        self.keys_just_pressed = [False] * 4
        self.stats = {'tap': {'perfect': 0, 'great': 0, 'good': 0, 'miss': 0}, 'hold': {'perfect': 0, 'great': 0, 'good': 0, 'miss': 0}, 'slide': {'perfect': 0, 'great': 0, 'good': 0, 'miss': 0}}
        self.score = 0.0
        self.total_notes = 0
        self.note_weights = {'tap': 4, 'hold': 8, 'slide': 1}
        self.hit_effects = []
        self.judge_text = ''
        self.judge_timer = 0
        self.music_playing = False
        self.game_start_time = 0
        self.music_started = False
        self.load_credits()
        self.load_music_files()

    def load_music_files(self):
        """加载可用的音乐文件"""  # inserted
        music_extensions = ['.mp3', '.wav', '.ogg']
        self.available_music = []
        for ext in music_extensions:
            for filename in ['song' + ext, 'music' + ext, 'bgm' + ext]:
                if os.path.exists(filename):
                    pass  # postinserted
                else:  # inserted
                    self.available_music.append(filename)
        if self.available_music:
            self.music_file = self.available_music[0]
            print(f'Music file found: {self.music_file}')
        return None

    def load_music(self):
        """加载并准备音乐播放"""  # inserted
        if self.music_file and os.path.exists(self.music_file):
            try:
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.set_volume(self.music_volume)
                self.music_loaded = True
                print(f'Music loaded successfully: {self.music_file}')
                return None
            except pygame.error as e:
                print(f'Music loading failed: {e}')
                self.music_loaded = False
                return None

    def start_music(self):
        """开始音乐播放"""  # inserted
        if self.music_loaded:
            try:
                pygame.mixer.music.play((-1))
                self.music_started = True
                print('Music playback started')
                return None
            except pygame.error as e:
                print(f'Music start failed: {e}')
                self.music_started = False

    def stop_music(self):
        """停止音乐播放"""  # inserted
        if self.music_started:
            pygame.mixer.music.stop()
            self.music_started = False
            print('Music playback stopped')
        return None

    def pause_music(self):
        """暂停音乐播放"""  # inserted
        if self.music_started:
            pygame.mixer.music.pause()
        return None

    def resume_music(self):
        """恢复音乐播放"""  # inserted
        if self.music_started:
            pygame.mixer.music.unpause()
        return None

    def load_credits(self):
        """从文件加载制作人员表"""  # inserted
        self.credits = ['Development Team', '', 'Game Developer: Developer', 'Music Producer: Musician', 'Chart Creator: Charter', '', 'Thanks for playing!']
        try:
            if os.path.exists('credits.txt'):
                with open('credits.txt', 'r', encoding='utf-8') as f:
                    self.credits = [line.strip() for line in f.readlines()]
            return
        except:
            pass  # postinserted
        return None

    def beats_to_milliseconds(self, beats):
        """将拍数转换为毫秒"""  # inserted
        beat_duration = 60000 / self.bpm
        return beats * beat_duration

    def parse_beat_notation(self, beat_str):
        """解析拍数表示法，支持带分数格式\n\n格式说明：\n- 整数：如 \"4\" 表示第4拍\n- 带分数：如 \"4+1/2\" 表示第4拍半\n- 纯分数：如 \"1/4\" 表示四分之一拍\n"""  # inserted
        beat_str = beat_str.strip()
        if '+' in beat_str:
            parts = beat_str.split('+')
            whole_part = int(parts[0])
            fraction_part = Fraction(parts[1])
            return whole_part + fraction_part

    def load_chart_for_difficulty(self):
        """根据选择的难度加载谱面"""  # inserted
        difficulty_names = ['easy', 'present', 'expert', 'glitch', 'meteorshower']
        filename = f'chart_{difficulty_names[self.selected_difficulty]}.txt'
        if os.path.exists(filename):
            self.load_chart_from_file(filename)
        return None

    def load_chart_from_file(self, filename):
        """从txt文件加载谱面\n\n新的谱面文件格式说明:\n# 第一行必须是BPM设置: BPM:120\n# 注释行以#开头，会被忽略\n# 音符格式: 音轨,拍数,音符类型,结束拍数(仅HOLD音符需要)\n# 音轨: 0-3 (对应D,F,J,K键)\n# 拍数: 支持整数、分数、带分数格式\n#   - 整数: 4 (第4拍)\n#   - 分数: 1/4 (四分之一拍)  \n#   - 带分数: 4+1/2 (第4拍半)\n# 音符类型: 1=TAP(点击音符), 2=HOLD(长按音符), 3=SLIDE(滑动音符)\n# 示例:\n# BPM:120\n# 0,1,1           # 音轨0, 第1拍, TAP音符\n# 1,1+1/2,2,2+1/2 # 音轨1, 1.5拍到2.5拍, HOLD音符\n# 2,2+3/4,3       # 音轨2, 第2又3/4拍, SLIDE音符\n"""  # inserted
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    self.notes = []
                    self.bpm = 120
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if line.upper().startswith('BPM:'):
                                self.bpm = float(line[4:])
                                print(f'BPM set to: {self.bpm}')
                                continue
                        else:  # inserted
                            parts = line.split(',')
                            if len(parts) >= 3:
                                pass  # postinserted
                            else:  # inserted
                                    track = int(parts[0])
                                    beat_time = self.parse_beat_notation(parts[1])
                                    note_type_num = int(parts[2])
                                    if track < 0 or track >= TRACK_COUNT:
                                        print(f'Invalid track {track} in line {line_num}')
                                        continue
                                    time_ms = self.beats_to_milliseconds(beat_time)
                                    if note_type_num == 1:
                                        note_type = NoteType.TAP
                                    end_time = 0.0
                                    if len(parts) >= 4 and note_type == NoteType.HOLD:
                                        end_beat = self.parse_beat_notation(parts[3])
                                        end_time = self.beats_to_milliseconds(end_beat)
                                    self.notes.append(Note(track, time_ms, note_type, end_time))
                    else:  # inserted
                        self.total_notes = len(self.notes)
                        self.notes.sort(key=lambda note: note.time)
                        if self.notes:
                            last_note_time = max((note.end_time if note.end_time > 0 else note.time for note in self.notes))
                            self.song_length = last_note_time + 2000
                        print(f'Loaded {self.total_notes} notes from {filename} (BPM: {self.bpm})')
        except Exception as e:
            print(f'Failed to load chart file: {e}')
            self.notes = []
            self.total_notes = 0
            self.bpm = 120

    def handle_events(self):
        """处理事件"""  # inserted
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_music()
                self.running = False
            else:  # inserted
                if event.type == pygame.KEYDOWN:
                    if self.state == GameState.MENU:
                        if event.key == pygame.K_RETURN:
                            self.state = GameState.SONG_SELECT
                        else:  # inserted
                            if event.key == pygame.K_c:
                                self.state = GameState.CREDITS
                    else:  # inserted
                        if self.state == GameState.SONG_SELECT:
                            if event.key == pygame.K_UP:
                                self.selected_difficulty = (self.selected_difficulty - 1) % len(self.difficulties)
                            else:  # inserted
                                if event.key == pygame.K_DOWN:
                                    self.selected_difficulty = (self.selected_difficulty + 1) % len(self.difficulties)
                                else:  # inserted
                                    if event.key == pygame.K_RETURN:
                                        self.start_game()
                                    else:  # inserted
                                        if event.key == pygame.K_ESCAPE:
                                            self.state = GameState.MENU
                        else:  # inserted
                            if self.state == GameState.PLAYING:
                                if event.key in KEY_MAP:
                                    track = KEY_MAP[event.key]
                                    self.keys_pressed[track] = True
                                    self.keys_just_pressed[track] = True
                                    self.check_note_hit(track)
                                else:  # inserted
                                    if event.key == pygame.K_ESCAPE:
                                        self.end_game()
                            else:  # inserted
                                if self.state == GameState.RESULT:
                                    if event.key == pygame.K_RETURN:
                                        self.state = GameState.MENU
                                else:  # inserted
                                    if self.state == GameState.CREDITS:
                                        if event.key == pygame.K_ESCAPE:
                                            self.state = GameState.MENU
                else:  # inserted
                    if event.type == pygame.KEYUP:
                        pass  # postinserted
                    else:  # inserted
                        if self.state == GameState.PLAYING:
                            pass  # postinserted
                        else:  # inserted
                            if event.key in KEY_MAP:
                                pass  # postinserted
                            else:  # inserted
                                track = KEY_MAP[event.key]
                                self.keys_pressed[track] = False

    def start_game(self):
        """开始游戏"""  # inserted
        self.state = GameState.PLAYING
        self.load_chart_for_difficulty()
        self.current_time = 0
        self.stats = {'tap': {'perfect': 0, 'great': 0, 'good': 0, 'miss': 0}, 'hold': {'perfect': 0, 'great': 0, 'good': 0, 'miss': 0}, 'slide': {'perfect': 0, 'great': 0, 'good': 0, 'miss': 0}}
        self.score = 0.0
        self.hit_effects = []
        self.keys_pressed = [False] * 4
        for note in self.notes:
            note.hit = False
            note.judge = None
            note.processed = False
        self.game_start_time = pygame.time.get_ticks()
        self.music_playing = True
        self.music_started = False
        self.load_music()

    def end_game(self):
        """结束游戏"""  # inserted
        self.state = GameState.RESULT
        self.music_playing = False
        self.stop_music()
        self.calculate_final_score()

    def check_note_hit(self, track):
        """检查音符命中"""  # inserted
        current_time = self.current_time
        closest_note = None
        closest_time_diff = float('inf')
        for note in self.notes:
            if note.hit or note.track!= track:
                continue
            time_diff = current_time - note.time
            abs_diff = abs(time_diff)
            if abs_diff <= 120:
                pass  # postinserted
            else:  # inserted
                if abs_diff < abs(closest_time_diff):
                    pass  # postinserted
                else:  # inserted
                    closest_note = note
                    closest_time_diff = time_diff
        if closest_note:
            if closest_note.note_type == NoteType.TAP:
                judge = self.get_judge_type(closest_time_diff)
                closest_note.hit = True
                closest_note.judge = judge
                closest_note.processed = True
                closest_note.show_judge = True
                self.add_hit_effect(track, judge)
                self.update_stats('tap', judge)
            return None

    def get_judge_type(self, time_diff):
        """根据时间差获得判定类型"""  # inserted
        abs_diff = abs(time_diff)
        return JudgeType.PERFECT #if abs_diff <= 60 else JudgeType.GREAT if abs_diff <= 80 else JudgeType.GOOD if abs_diff <= 120 else JudgeType.MISS

    def add_hit_effect(self, track, judge):
        """添加命中效果"""  # inserted
        x = TRACK_START_X + track * TRACK_WIDTH + TRACK_WIDTH // 2
        color = {JudgeType.PERFECT: YELLOW, JudgeType.GREAT: GREEN, JudgeType.GOOD: BLUE, JudgeType.MISS: RED}[judge]
        self.hit_effects.append({'x': x, 'y': JUDGE_LINE_Y, 'color': color, 'timer': 30, 'judge': judge})
        self.judge_text = judge.name
        self.judge_timer = 60

    def update_stats(self, note_type, judge):
        """更新统计数据"""  # inserted
        judge_name = judge.name.lower()
        self.stats[note_type][judge_name] += 1

    def calculate_final_score(self):
        """计算最终得分"""  # inserted
        total_weight = 0
        weighted_score = 0
        for note_type, counts in self.stats.items():
            weight = self.note_weights[note_type]
            type_total = sum(counts.values())
            total_weight += weight * type_total
            type_score = (counts['perfect'] * 1.0 + counts['great'] * 0.75 + counts['good'] * 0.25) * weight
            weighted_score += type_score
        if total_weight > 0:
            self.score = weighted_score / total_weight * 100
        return None

    def update(self):
        """更新游戏状态"""  # inserted
        if self.state == GameState.PLAYING:
            if self.music_playing:
                self.current_time = pygame.time.get_ticks() - self.game_start_time + self.offset
                if not self.music_started and self.current_time >= self.music_start_delay:
                    self.start_music()
            self.check_missed_notes()
            self.check_hold_notes()
            self.end_game() if self.current_time >= self.song_length else None
            self.hit_effects = [effect for effect in self.hit_effects if self.update_effect(effect)]
            if self.judge_timer > 0:
                self.judge_timer -= 1
            self.keys_just_pressed = [False] * 4
        return None

    def check_missed_notes(self):
        """检查应该标记为错过的音符"""  # inserted
        current_time = self.current_time
        for note in self.notes:
            if note.processed or note.hit:
                continue
            time_diff = current_time - note.time
            if time_diff > 120:
                pass  # postinserted
            else:  # inserted
                note.hit = True
                note.judge = JudgeType.MISS
                note.processed = True
                note.show_judge = True
                note_type_name = note.note_type.name.lower()
                if note_type_name == 'tap':
                    self.add_hit_effect(note.track, JudgeType.MISS)
                    self.update_stats('tap', JudgeType.MISS)
                else:  # inserted
                    if note_type_name == 'hold':
                        self.add_hit_effect(note.track, JudgeType.MISS)
                        self.update_stats('hold', JudgeType.MISS)
                    else:  # inserted
                        if note_type_name == 'slide':
                            pass  # postinserted
                        else:  # inserted
                            self.add_hit_effect(note.track, JudgeType.MISS)
                            self.update_stats('slide', JudgeType.MISS)

    def check_hold_notes(self):
        """检查Hold音符的持续状态"""  # inserted
        current_time = self.current_time
        for note in self.notes:
            if note.note_type == NoteType.HOLD and note.hit and (not note.processed):
                pass  # postinserted
            else:  # inserted
                if not self.keys_pressed[note.track]:
                    if current_time < note.end_time - 80:
                        note.judge = JudgeType.MISS
                        note.show_judge = True
                        self.add_hit_effect(note.track, JudgeType.MISS)
                        self.update_stats('hold', JudgeType.MISS)
                        note.processed = True
                else:  # inserted
                    if current_time >= note.end_time:
                        pass  # postinserted
                    else:  # inserted
                        if note.hold_start_judge and note.hold_start_judge!= JudgeType.MISS:
                            note.judge = note.hold_start_judge
                            note.show_judge = True
                            self.add_hit_effect(note.track, note.judge)
                            self.update_stats('hold', note.judge)
                        note.processed = True

    def update_effect(self, effect):
        """更新效果"""  # inserted
        effect['timer'] -= 1
        effect['y'] -= 2
        return effect['timer'] > 0

    def draw(self):
        """绘制游戏界面"""  # inserted
        self.screen.fill(BLACK)
        if self.state == GameState.MENU:
            self.draw_menu()
        pygame.display.flip()

    def draw_menu(self):
        """绘制主菜单"""  # inserted
        title = self.large_font.render('Meteor Nuker', True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        start_text = self.font.render('Press ENTER to Start', True, WHITE)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        credits_text = self.font.render('Press C for Credits', True, WHITE)
        self.screen.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, 350))
        if self.music_file:
            music_text = self.small_font.render(f'Music: {os.path.basename(self.music_file)}', True, GREEN)
        self.screen.blit(music_text, (10, SCREEN_HEIGHT - 30))

    def draw_song_select(self):
        """绘制歌曲选择界面"""  # inserted
        title = self.large_font.render(self.song_title, True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        for i, difficulty in enumerate(self.difficulties):
            if i == self.selected_difficulty:
                if difficulty == 'Meteor Shower':
                    color = PURPLE
            diff_text = self.font.render(difficulty, True, color)
            y = 200 + i * 40
            self.screen.blit(diff_text, (SCREEN_WIDTH // 2 - diff_text.get_width() // 2, y))
        instruction = self.small_font.render('UP/DOWN: Select, ENTER: Confirm, ESC: Back', True, WHITE)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 450))

    def draw_game(self):
        """绘制游戏界面"""  # inserted
        for i in range(TRACK_COUNT):
            x = TRACK_START_X + i * TRACK_WIDTH
            pygame.draw.rect(self.screen, DARK_GRAY, (x, 0, TRACK_WIDTH, SCREEN_HEIGHT), 2)
            if self.keys_pressed[i]:
                pass  # postinserted
            else:  # inserted
                pygame.draw.rect(self.screen, GRAY, (x + 2, 0, TRACK_WIDTH - 4, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, WHITE, (TRACK_START_X, JUDGE_LINE_Y), (TRACK_START_X + TRACK_WIDTH * TRACK_COUNT, JUDGE_LINE_Y), 3)
        self.draw_notes()
        for effect in self.hit_effects:
            pygame.draw.circle(self.screen, effect['color'], (effect['x'], effect['y']), 10)
        if self.judge_timer > 0:
            judge_surface = self.font.render(self.judge_text, True, YELLOW)
            self.screen.blit(judge_surface, (SCREEN_WIDTH // 2 - judge_surface.get_width() // 2, JUDGE_LINE_Y - 100))
        self.draw_game_ui()

    def draw_notes(self):
        """绘制音符"""  # inserted
        current_time = self.current_time
        for note in self.notes:
            time_to_judge = note.time - current_time
            note_y = JUDGE_LINE_Y - time_to_judge / 1000.0 * 800
            if note_y < (-50) and note.note_type!= NoteType.HOLD:
                continue
            if note_y > SCREEN_HEIGHT + 50:
                continue
            x = TRACK_START_X + note.track * TRACK_WIDTH + TRACK_WIDTH // 2
            if note.note_type == NoteType.TAP:
                if not note.hit:
                    pygame.draw.circle(self.screen, WHITE, (x, int(note_y)), 20, 3)
            else:  # inserted
                if note.note_type == NoteType.SLIDE:
                    if not note.hit:
                        pygame.draw.polygon(self.screen, YELLOW, [(x - 15, int(note_y) - 15), (x + 15, int(note_y) - 15), (x + 15, int(note_y) + 15), (x - 15, int(note_y) + 15)], 3)
                else:  # inserted
                    if note.note_type == NoteType.HOLD:
                        pass  # postinserted
                    else:  # inserted
                        if not note.hit:
                            pygame.draw.circle(self.screen, GREEN, (x, int(note_y)), 20, 3)
                        if note.end_time > 0:
                            pass  # postinserted
                        else:  # inserted
                            end_time_to_judge = note.end_time - current_time
                            end_y = JUDGE_LINE_Y - end_time_to_judge / 1000.0 * 800
                            if note.hit and current_time >= note.time:
                                start_y = JUDGE_LINE_Y
                            if end_y < JUDGE_LINE_Y:
                                pass  # postinserted
                            else:  # inserted
                                pygame.draw.line(self.screen, GREEN, (x, int(start_y)), (x, int(end_y)), 8)

    def draw_game_ui(self):
        """绘制游戏UI信息"""  # inserted
        temp_score = self.calculate_current_score()
        score_text = self.font.render(f'Score: {temp_score:.2f}%', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        bpm_text = self.small_font.render(f'BPM: {self.bpm}', True, WHITE)
        self.screen.blit(bpm_text, (10, 50))
        current_beat = self.current_time / 1000.0 * (self.bpm / 60.0)
        beat_text = self.small_font.render(f'Beat: {current_beat:.2f}', True, WHITE)
        self.screen.blit(beat_text, (10, 70))
        time_text = self.small_font.render(f'Time: {self.current_time // 1000:.1f}s', True, WHITE)
        self.screen.blit(time_text, (10, 90))
        key_labels = ['D', 'F', 'J', 'K']
        for i, label in enumerate(key_labels):
            x = TRACK_START_X + i * TRACK_WIDTH + TRACK_WIDTH // 2
            color = YELLOW if self.keys_pressed[i] else WHITE
            key_text = self.font.render(label, True, color)
            self.screen.blit(key_text, (x - key_text.get_width() // 2, JUDGE_LINE_Y + 30))
        if self.music_loaded:
            if self.music_started and pygame.mixer.music.get_busy():
                music_status = 'Music: Playing'
                status_color = GREEN
        music_text = self.small_font.render(music_status, True, status_color)
        self.screen.blit(music_text, (SCREEN_WIDTH - music_text.get_width() - 10, 10))

    def calculate_current_score(self):
        """计算当前得分"""  # inserted
        total_weight = 0
        weighted_score = 0
        for note_type, counts in self.stats.items():
            weight = self.note_weights[note_type]
            type_total = sum(counts.values())
            total_weight += weight * type_total
            type_score = (counts['perfect'] * 1.0 + counts['great'] * 0.75 + counts['good'] * 0.25) * weight
            weighted_score += type_score
        return weighted_score / total_weight * 100 if total_weight > 0 else weighted_score

    def draw_result(self):
        """绘制结果界面"""  # inserted
        title = self.large_font.render('Game Result', True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        song_info = self.font.render(f'{self.song_title} - {self.difficulties[self.selected_difficulty]}', True, WHITE)
        self.screen.blit(song_info, (SCREEN_WIDTH // 2 - song_info.get_width() // 2, 100))
        bpm_info = self.small_font.render(f'BPM: {self.bpm}', True, WHITE)
        self.screen.blit(bpm_info, (SCREEN_WIDTH // 2 - bpm_info.get_width() // 2, 120))
        score_text = self.font.render(f'Final Score: {self.score:.2f}%', True, YELLOW)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 145))
        self.draw_stats_table()
        return_text = self.small_font.render('Press ENTER', True, WHITE)
        self.screen.blit(return_text, (SCREEN_WIDTH // 2 - return_text.get_width() // 2, 550))

    def draw_stats_table(self):
        """绘制统计表格"""  # inserted
        start_y = 180
        row_height = 30
        col_width = 100
        headers = ['', 'Perfect', 'Great', 'Good', 'Miss', 'Total']
        for i, header in enumerate(headers):
            x = 50 + i * col_width
            text = self.small_font.render(header, True, WHITE)
            self.screen.blit(text, (x, start_y))
        rows = ['Tap', 'Hold', 'Slide', 'Total']
        for i, row_name in enumerate(rows):
            y = start_y + (i + 1) * row_height
            label = self.small_font.render(row_name, True, WHITE)
            self.screen.blit(label, (50, y))
            if row_name == 'Total':
                totals = [0, 0, 0, 0, 0]
                for note_type in ['tap', 'hold', 'slide']:
                    counts = self.stats[note_type]
                    totals[0] += counts['perfect']
                    totals[1] += counts['great']
                    totals[2] += counts['good']
                    totals[3] += counts['miss']
                    totals[4] += sum(counts.values())
                for j, total in enumerate(totals):
                    x = 50 + (j + 1) * col_width
                    text = self.small_font.render(str(total), True, YELLOW)
                    self.screen.blit(text, (x, y))
            else:  # inserted
                note_type_map = {'Tap': 'tap', 'Hold': 'hold', 'Slide': 'slide'}
                note_type = note_type_map[row_name]
                counts = self.stats[note_type]
                values = [counts['perfect'], counts['great'], counts['good'], counts['miss'], sum(counts.values())]
                for j, value in enumerate(values):
                    x = 50 + (j + 1) * col_width
                    text = self.small_font.render(str(value), True, WHITE)
                    self.screen.blit(text, (x, y))

    def draw_credits(self):
        """绘制制作人员表"""  # inserted
        start_y = 100
        for i, line in enumerate(self.credits):
            text = self.font.render(line, True, WHITE)
            y = start_y + i * 40
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        back_text = self.small_font.render('Press ESC to Go Back', True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 550))

    def run(self):
        """主游戏循环"""  # inserted
        if self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.stop_music()
        pygame.quit()
        sys.exit()
if __name__ == '__main__':
    game = Game()
    game.run()