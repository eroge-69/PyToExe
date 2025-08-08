"""
Pygame Rich Text Editor — Images + Editable Tables + Reset

Features added in this version:
- Fixed Button rendering (labels drawn on button surface)
- Reset button: clears document and defaults
- Insert Table dialog: choose rows x cols when inserting
- Editable table cells: click a cell or navigate with TAB/Arrows to edit text in cells
- Table cell text is stored in span['rows'] and saved/loaded via JSON
- Image support and paste (as in previous version)

Run: python easyedit_v4_tables_images.py
Requires: pygame (Pillow optional for clipboard images), pyperclip optional
"""

import pygame
import json
import os
import copy
import time

# optional Pillow for clipboard images
try:
    from PIL import Image, ImageGrab
    _HAS_PIL = True
except Exception:
    Image = None
    ImageGrab = None
    _HAS_PIL = False

# optional system clipboard for text
try:
    import pyperclip
    _HAS_PYPERCLIP = True
except Exception:
    pyperclip = None
    _HAS_PYPERCLIP = False

# --------------------- Config ---------------------
WIDTH, HEIGHT = 1000, 640
SIDEBAR_W = 220
BG_COLOR = (245, 245, 250)
FONT_PATH = None  # e.g. r"C:/Windows/Fonts/segoeui.ttf"
DEFAULT_FONT_NAME = "Segoe UI"
DEFAULT_FONT_SIZE = 20
DEFAULT_COLOR = (10, 10, 10)
SAVE_FILE = 'document.json'
IMAGE_DIR = 'images'

os.makedirs(IMAGE_DIR, exist_ok=True)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pygame Rich Text Editor (v4)")
clock = pygame.time.Clock()

# --------------------- Helpers ---------------------

def make_font(size=20, bold=False, italic=False, underline=False):
    if FONT_PATH and os.path.isfile(FONT_PATH):
        f = pygame.font.Font(FONT_PATH, size)
    else:
        # fall back to default system font; if not available pygame uses a default
        try:
            f = pygame.font.SysFont(DEFAULT_FONT_NAME, size)
        except Exception:
            f = pygame.font.Font(None, size)
    f.set_bold(bold)
    f.set_italic(italic)
    f.set_underline(underline)
    return f


def draw_gradient_rect(surface, rect, color1, color2):
    x, y, w, h = rect
    for i in range(w):  # horizontal statt vertikal
        t = i / max(w - 1, 1)
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + h))


# --------------------- Span helpers ---------------------
# Text spans: {'text': str, 'bold':bool, 'italic':bool, 'underline':bool, 'color':(r,g,b), 'size':int}
# Image spans: {'type':'image', 'path': str, 'width':int, 'height':int, 'border':bool}
# Table spans: {'type':'table', 'rows': [[str,...], ...], 'col_widths': [int,...], 'border':bool}


def merge_adjacent_spans(spans):
    if not spans:
        return []
    merged = [spans[0].copy()]
    for s in spans[1:]:
        prev = merged[-1]
        if ('text' in prev) and ('text' in s) and all(prev.get(k) == s.get(k) for k in ('bold', 'italic', 'underline', 'color', 'size')):
            prev['text'] += s['text']
        else:
            merged.append(s.copy())
    return merged


def flatten_text(spans):
    out = []
    for s in spans:
        if 'text' in s:
            out.append(s['text'])
        else:
            out.append('\uFFFC')
    return ''.join(out)


def text_length(spans):
    total = 0
    for s in spans:
        if 'text' in s:
            total += len(s['text'])
        else:
            total += 1
    return total

# --------------------- Editor logic ---------------------
class Editor:
    def __init__(self):
        self.reset_document()
        self.default = {'bold': False, 'italic': False, 'underline': False, 'color': DEFAULT_COLOR, 'size': DEFAULT_FONT_SIZE}
        self.cursor = 0
        self.select_anchor = None
        self.scroll = 0
        self.blink = 0
        self.undo_stack = []
        self.redo_stack = []
        self.internal_clipboard = ''
        self._image_cache = {}
        # when editing inside a table cell, store (span_idx, row, col) or None
        self.editing_table = None

    def reset_document(self):
        self.spans = [
            {'text': '', 'bold': False, 'italic': False, 'underline': False, 'color': DEFAULT_COLOR, 'size': DEFAULT_FONT_SIZE}
        ]
        self.default = {'bold': False, 'italic': False, 'underline': False, 'color': DEFAULT_COLOR, 'size': DEFAULT_FONT_SIZE}
        self.cursor = 0
        self.select_anchor = None
        self.editing_table = None
        self.undo_stack = []
        self.redo_stack = []

    def snapshot(self):
        return json.dumps({'spans': self.spans, 'cursor': self.cursor, 'select_anchor': self.select_anchor, 'default': self.default}, ensure_ascii=False)

    def push_undo(self):
        self.undo_stack.append(self.snapshot())
        if len(self.undo_stack) > 200:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self.snapshot())
        data = json.loads(self.undo_stack.pop())
        self._restore_snapshot(data)

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self.snapshot())
        data = json.loads(self.redo_stack.pop())
        self._restore_snapshot(data)

    def _restore_snapshot(self, data):
        self.spans = data['spans']
        self.cursor = data['cursor']
        self.select_anchor = data.get('select_anchor')
        self.default = data.get('default', self.default)
        self.editing_table = None

    def get_word_char_counts(self):
        text = flatten_text(self.spans)
        words = len([w for w in text.split() if w.strip() != ''])
        chars = len(text)
        return words, chars

    # helper to convert absolute char position to span index + offset inside span
    def pos_to_span_index(self, pos):
        if not self.spans:  # create empty text span if none
            self.spans.append({'text': '', 'bold': False, 'italic': False, 'underline': False, 'color': (255, 255, 255)})
            return 0, 0

        total = 0
        for i, s in enumerate(self.spans):
            length = len(s.get('text', '')) if 'text' in s else 1
            if total + length >= pos:
                return i, pos - total
            total += length
        # cursor at end
        last_span = len(self.spans) - 1
        if 'text' in self.spans[last_span]:
            return last_span, len(self.spans[last_span]['text'])
        else:
            return last_span, 1

    def has_selection(self):
        return self.select_anchor is not None and self.select_anchor != self.cursor

    def get_selection_range(self):
        if not self.has_selection():
            return None
        a, b = self.select_anchor, self.cursor
        return (a, b) if a <= b else (b, a)

    def delete_selection(self):
        rng = self.get_selection_range()
        if not rng:
            return
        a, b = rng
        self.push_undo()
        new_spans = []
        abs_pos = 0
        for s in self.spans:
            span_len = len(s['text']) if 'text' in s else 1
            s_start = abs_pos
            s_end = abs_pos + span_len
            if s_end <= a or s_start >= b:
                new_spans.append(s.copy())
            else:
                if 'text' in s:
                    left = ''
                    right = ''
                    if a > s_start:
                        left = s['text'][:(a - s_start)]
                    if b < s_end:
                        right = s['text'][(b - s_start):]
                    if left:
                        ns = s.copy(); ns['text'] = left; new_spans.append(ns)
                    if right:
                        ns = s.copy(); ns['text'] = right; new_spans.append(ns)
                else:
                    # object fully deleted if inside selection
                    pass
            abs_pos += span_len
        self.spans = merge_adjacent_spans(new_spans)
        self.cursor = a
        self.select_anchor = None
        self.editing_table = None

    def insert_text(self, text):
        if text == '':
            return
        # if editing a table cell, insert there
        if self.editing_table is not None:
            si, r, c = self.editing_table
            try:
                tspan = self.spans[si]
                if tspan.get('type') == 'table':
                    self.push_undo()
                    tspan['rows'][r][c] += text
                    return
            except Exception:
                pass
        self.push_undo()
        if self.has_selection():
            self.delete_selection()
        si, off = self.pos_to_span_index(self.cursor)
        s = self.spans[si]
        if 'text' not in s:
            insert_at = si if off == 0 else si + 1
            new_middle = self.default.copy(); new_middle['text'] = text
            self.spans = self.spans[:insert_at] + [new_middle] + self.spans[insert_at:]
            self.cursor += len(text)
        else:
            before = s['text'][:off]
            after = s['text'][off:]
            same_style = all(s.get(k) == self.default.get(k) for k in ('bold', 'italic', 'underline', 'color', 'size'))
            if same_style:
                s['text'] = before + text + after
                self.cursor += len(text)
            else:
                new_middle = self.default.copy(); new_middle['text'] = text
                new_left = s.copy(); new_left['text'] = before
                new_right = s.copy(); new_right['text'] = after
                new_list = []
                if new_left['text']:
                    new_list.append(new_left)
                new_list.append(new_middle)
                if new_right['text']:
                    new_list.append(new_right)
                self.spans = self.spans[:si] + new_list + self.spans[si+1:]
                self.cursor += len(text)
        self.spans = merge_adjacent_spans(self.spans)

    def insert_object_span(self, span):
        self.push_undo()
        if self.has_selection():
            self.delete_selection()
        si, off = self.pos_to_span_index(self.cursor)
        if 'text' in self.spans[si]:
            s = self.spans[si]
            before = s['text'][:off]
            after = s['text'][off:]
            new_list = []
            if before:
                new_list.append({**s, 'text': before})
            new_list.append(span.copy())
            if after:
                new_list.append({**s, 'text': after})
            self.spans = self.spans[:si] + new_list + self.spans[si+1:]
        else:
            if off == 0:
                self.spans = self.spans[:si] + [span.copy()] + self.spans[si:]
            else:
                self.spans = self.spans[:si+1] + [span.copy()] + self.spans[si+1:]
        self.cursor += 1
        self.editing_table = None
        self.spans = merge_adjacent_spans(self.spans)

    def delete_back(self):
        if self.editing_table is not None:
            si, r, c = self.editing_table
            try:
                tspan = self.spans[si]
                if tspan.get('type') == 'table':
                    if tspan['rows'][r][c]:
                        self.push_undo()
                        tspan['rows'][r][c] = tspan['rows'][r][c][:-1]
                        return
            except Exception:
                pass
        if self.has_selection():
            self.push_undo(); self.delete_selection(); return
        if self.cursor == 0: return
        self.push_undo()
        si, off = self.pos_to_span_index(self.cursor)
        if 'text' in self.spans[si]:
            if off > 0:
                s = self.spans[si]
                s['text'] = s['text'][:off - 1] + s['text'][off:]
                self.cursor -= 1
            else:
                if si > 0:
                    prev = self.spans[si - 1]
                    if 'text' in prev and len(prev['text']) > 0:
                        prev['text'] = prev['text'][:-1]
                        self.cursor -= 1
                    else:
                        del self.spans[si - 1]
                        self.cursor -= 1
        else:
            if off == 1:
                del self.spans[si]
                self.cursor -= 1
            else:
                if si > 0:
                    prev = self.spans[si - 1]
                    if 'text' in prev and len(prev['text']) > 0:
                        prev['text'] = prev['text'][:-1]
                        self.cursor -= 1
                    else:
                        del self.spans[si - 1]
                        self.cursor -= 1
        self.spans = merge_adjacent_spans(self.spans)

    def delete_forward(self):
        if self.editing_table is not None:
            si, r, c = self.editing_table
            try:
                tspan = self.spans[si]
                if tspan.get('type') == 'table':
                    if tspan['rows'][r][c]:
                        self.push_undo()
                        tspan['rows'][r][c] = tspan['rows'][r][c][1:]
                        return
            except Exception:
                pass
        if self.has_selection():
            self.push_undo(); self.delete_selection(); return
        total = text_length(self.spans)
        if self.cursor >= total: return
        self.push_undo()
        si, off = self.pos_to_span_index(self.cursor)
        s = self.spans[si]
        if 'text' in s:
            if off < len(s['text']):
                s['text'] = s['text'][:off] + s['text'][off + 1:]
            else:
                if si + 1 < len(self.spans):
                    del self.spans[si + 1]
        else:
            del self.spans[si]
        self.spans = merge_adjacent_spans(self.spans)

    def delete_word_back(self):
        if self.has_selection():
            self.push_undo(); self.delete_selection(); return
        if self.cursor == 0: return
        self.push_undo()
        text = flatten_text(self.spans)
        i = self.cursor - 1
        while i >= 0 and text[i].isspace():
            i -= 1
        while i >= 0 and not text[i].isspace():
            i -= 1
        new_cursor = max(i + 1, 0)
        a, b = new_cursor, self.cursor
        self.select_anchor = a
        self.cursor = b
        self.delete_selection()

    def apply_style_to_selection(self, style_changes):
        rng = self.get_selection_range()
        if rng is None:
            for k, v in style_changes.items():
                if isinstance(v, bool):
                    self.default[k] = not self.default.get(k, False)
                else:
                    self.default[k] = v
            return
        a, b = rng
        bool_toggles = {}
        for k, v in style_changes.items():
            if isinstance(v, bool):
                all_true = True
                abs_pos = 0
                for s in self.spans:
                    span_len = len(s['text']) if 'text' in s else 1
                    if 'text' in s:
                        for ch in s['text']:
                            if abs_pos >= a and abs_pos < b:
                                if not s.get(k, False):
                                    all_true = False; break
                            abs_pos += 1
                        if not all_true:
                            break
                    else:
                        abs_pos += 1
                bool_toggles[k] = not all_true
        self.push_undo()
        left_idx, left_off = self.pos_to_span_index(a)
        right_idx, right_off = self.pos_to_span_index(b)
        new_spans = []
        left_span = self.spans[left_idx]
        if 'text' in left_span and left_off > 0:
            s = left_span.copy(); s['text'] = left_span['text'][:left_off]; new_spans.append(s)
        sel_text_spans = []
        abs_pos = 0
        for i, si_span in enumerate(self.spans):
            span_len = len(si_span['text']) if 'text' in si_span else 1
            s_start = abs_pos
            s_end = abs_pos + span_len
            if s_end <= a or s_start >= b:
                pass
            else:
                if 'text' in si_span:
                    start = max(0, a - s_start)
                    end = min(span_len, b - s_start)
                    txt = si_span['text'][start:end]
                    if txt:
                        new_s = si_span.copy(); new_s['text'] = txt
                        sel_text_spans.append(new_s)
                else:
                    if a <= s_start and s_end <= b:
                        sel_text_spans.append(si_span.copy())
            abs_pos += span_len
        merged_sel = []
        buf = None
        for s in sel_text_spans:
            if 'text' in s:
                if buf is None:
                    buf = s.copy()
                else:
                    buf['text'] += s['text']
            else:
                if buf is not None:
                    merged_sel.append(buf); buf = None
                merged_sel.append(s)
        if buf is not None:
            merged_sel.append(buf)
        for s in merged_sel:
            if 'text' in s:
                for k, newval in bool_toggles.items():
                    s[k] = newval
                for k, v in style_changes.items():
                    if not isinstance(v, bool):
                        s[k] = v
                new_spans.append(s)
            else:
                new_spans.append(s)
        right_span = self.spans[right_idx]
        if 'text' in right_span and right_off < len(right_span['text']):
            s = right_span.copy(); s['text'] = right_span['text'][right_off:]; new_spans.append(s)
        self.spans = self.spans[:left_idx] + new_spans + self.spans[right_idx + 1:]
        self.select_anchor = None
        self.spans = merge_adjacent_spans(self.spans)

    def set_default(self, style_dict):
        self.default.update(style_dict)

    def save(self, filename=SAVE_FILE):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'spans': self.spans, 'default': self.default}, f, ensure_ascii=False, indent=2)

    def load(self, filename=SAVE_FILE):
        if not os.path.isfile(filename):
            return
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.spans = data.get('spans', self.spans)
        self.default = data.get('default', self.default)
        self.spans = merge_adjacent_spans(self.spans)
        self.cursor = 0
        self.select_anchor = None
        self.editing_table = None

    def copy_selection(self):
        rng = self.get_selection_range()
        if not rng:
            return
        a, b = rng
        abs_pos = 0
        copied_text = ''
        copied_object = None
        for s in self.spans:
            span_len = len(s['text']) if 'text' in s else 1
            s_start = abs_pos
            s_end = abs_pos + span_len
            if s_end <= a or s_start >= b:
                pass
            else:
                if 'text' in s:
                    start = max(0, a - s_start)
                    end = min(span_len, b - s_start)
                    copied_text += s['text'][start:end]
                else:
                    if a <= s_start and s_end <= b:
                        if s.get('type') == 'image':
                            copied_object = f'[[IMAGE:{s.get("path")}]]'
                        elif s.get('type') == 'table':
                            copied_object = f'[[TABLE:{json.dumps(s, ensure_ascii=False)}]]'
            abs_pos += span_len
        if copied_object:
            self.internal_clipboard = copied_object
            if _HAS_PYPERCLIP:
                pyperclip.copy(copied_object)
        else:
            self.internal_clipboard = copied_text
            if _HAS_PYPERCLIP:
                pyperclip.copy(copied_text)

    def paste_clipboard(self):
        txt = ''
        if _HAS_PYPERCLIP:
            try:
                txt = pyperclip.paste()
            except Exception:
                txt = ''
        else:
            txt = self.internal_clipboard
        if isinstance(txt, str) and txt.startswith('[[IMAGE:') and txt.endswith(']]'):
            path = txt[len('[[IMAGE:'):-2]
            if os.path.isfile(path):
                try:
                    img = pygame.image.load(path)
                    w, h = img.get_size()
                    max_w = 400
                    if w > max_w:
                        scale = max_w / w
                        w = int(w * scale); h = int(h * scale)
                    span = {'type': 'image', 'path': path, 'width': w, 'height': h, 'border': True}
                    self.insert_object_span(span)
                    return
                except Exception:
                    pass
        elif isinstance(txt, str) and txt.startswith('[[TABLE:') and txt.endswith(']]'):
            body = txt[len('[[TABLE:'):-2]
            try:
                tspan = json.loads(body)
                self.insert_object_span(tspan)
                return
            except Exception:
                pass
        if _HAS_PIL:
            try:
                clip = ImageGrab.grabclipboard()
                if isinstance(clip, Image.Image):
                    ts = int(time.time()*1000)
                    fname = os.path.join(IMAGE_DIR, f'clip_{ts}.png')
                    clip.save(fname, 'PNG')
                    w, h = clip.size
                    max_w = 400
                    if w > max_w:
                        scale = max_w / w
                        w = int(w * scale); h = int(h * scale)
                    span = {'type': 'image', 'path': fname, 'width': w, 'height': h, 'border': True}
                    self.insert_object_span(span)
                    return
            except Exception:
                pass
        if isinstance(txt, str) and os.path.isfile(txt):
            try:
                img = pygame.image.load(txt)
                w, h = img.get_size()
                max_w = 400
                if w > max_w:
                    scale = max_w / w
                    w = int(w * scale); h = int(h * scale)
                span = {'type': 'image', 'path': txt, 'width': w, 'height': h, 'border': True}
                self.insert_object_span(span)
                return
            except Exception:
                pass
        if txt:
            self.insert_text(txt)

    # --- Ergänzte Hilfsmethoden, damit der restliche Code funktioniert ---
    def move_cursor(self, delta):
        total = text_length(self.spans)
        self.cursor = max(0, min(total, self.cursor + delta))
        # when moving out of a table editing cell, stop editing
        self.editing_table = None

    def get_total_length(self):
        return text_length(self.spans)

    # aliasen die im alten Code verwendet wurden:
    def delete_char(self):
        # mappe auf delete_back
        self.delete_back()

    def insert_table(self, rows, cols):
        rows = max(1, int(rows))
        cols = max(1, int(cols))
        grid = [["" for _ in range(cols)] for _ in range(rows)]
        col_ws = [120 for _ in range(cols)]
        span = {'type': 'table', 'rows': grid, 'col_widths': col_ws, 'border': True}
        self.insert_object_span(span)

    def insert_image(self, path):
        try:
            img = pygame.image.load(path)
            w, h = img.get_size()
            max_w = 400
            if w > max_w:
                scale = max_w / w
                w = int(w * scale); h = int(h * scale)
            span = {'type': 'image', 'path': path, 'width': w, 'height': h, 'border': True}
            self.insert_object_span(span)
        except Exception:
            pass

# --------------------- UI Components ---------------------
class Button:
    def __init__(self, rect, text, action=None, toggled=False, bg_color=(255, 255, 255), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.hover = False
        self.toggled = toggled
        self.bg_color = bg_color
        self.text_color = text_color


    def draw(self, surf):
        alpha = 110 if self.toggled else (70 if self.hover else 40)
        s = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        s.fill((255, 255, 255, alpha))
        txt = make_font(16).render(self.text, True, (0, 0, 0))
        txt_x = 10
        txt_y = (self.rect.height - txt.get_height()) // 2
        s.blit(txt, (txt_x, txt_y))
        surf.blit(s, self.rect.topleft)

    def handle_event(self, ev, offset=(0,0)):
        # offset: position of the surface the button lives on (useful if sidebar not at 0,0)
        if ev.type == pygame.MOUSEMOTION:
            local = (ev.pos[0] - offset[0], ev.pos[1] - offset[1])
            self.hover = self.rect.collidepoint(local)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            local = (ev.pos[0] - offset[0], ev.pos[1] - offset[1])
            if self.rect.collidepoint(local):
                if self.action:
                    self.action()

# Simple dialog to ask rows/cols for a new table
class TableDialog:
    def __init__(self):
        self.visible = False
        self.rows = 2
        self.cols = 2
        self.rect = pygame.Rect(SIDEBAR_W + 120, 120, 280, 160)
        self.active_field = 'rows'  # 'rows' or 'cols'

    def open(self):
        self.visible = True
        self.rows = 2
        self.cols = 2
        self.active_field = 'rows'

    def close(self):
        self.visible = False

    def handle_event(self, ev, apply_fn=None):
        if not self.visible:
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.close(); return
            if ev.key == pygame.K_TAB:
                self.active_field = 'cols' if self.active_field == 'rows' else 'rows'
            if ev.key == pygame.K_RETURN:
                if apply_fn:
                    apply_fn(self.rows, self.cols)
                self.close(); return
            if ev.key == pygame.K_BACKSPACE:
                if self.active_field == 'rows':
                    s = str(self.rows)
                    self.rows = int(s[:-1]) if len(s) > 1 else 0
                else:
                    s = str(self.cols)
                    self.cols = int(s[:-1]) if len(s) > 1 else 0
            else:
                if ev.unicode.isdigit():
                    if self.active_field == 'rows':
                        self.rows = int(str(self.rows) + ev.unicode)
                    else:
                        self.cols = int(str(self.cols) + ev.unicode)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            # click inside dialog toggles focus roughly
            mx, my = ev.pos
            if not self.rect.collidepoint(ev.pos):
                return

    def draw(self, surf):
        if not self.visible: return
        s = pygame.Surface(self.rect.size)
        s.fill((250,250,250))
        pygame.draw.rect(s, (100,100,100), s.get_rect(), 2)
        title = make_font(18, bold=True).render('Insert Table', True, (10,10,10))
        s.blit(title, (12,8))
        rtxt = make_font(16).render(f'Rows: {self.rows}', True, (0,0,0))
        ctxt = make_font(16).render(f'Cols: {self.cols}', True, (0,0,0))
        s.blit(rtxt, (12,48))
        s.blit(ctxt, (12,84))
        hint = make_font(12).render('Enter to insert — Tab to switch field', True, (80,80,80))
        s.blit(hint, (12,120))
        surf.blit(s, self.rect.topleft)

# --------------------- Editor + UI Setup ---------------------
editor = Editor()

PALETTE = []
for r in (30, 80, 140, 200):
    for g in (30, 80, 140, 200):
        for b in (30, 80, 140, 200):
            PALETTE.append((r, g, b))
PALETTE = PALETTE[:64]

buttons = []
btn_h = 38
pad = 10
x = 12
start_y = 6 + 50


def make_button_grid(cfg_list):
    bs = []
    y = start_y
    for t, a in cfg_list:
        bs.append(Button((x, y, SIDEBAR_W - 24, btn_h), t, action=a))
        y += btn_h + 8
    return bs

# actions

def action_bold():
    editor.apply_style_to_selection({'bold': True})

def action_italic():
    editor.apply_style_to_selection({'italic': True})

def action_underline():
    editor.apply_style_to_selection({'underline': True})

color_picker = None  # not needed now

def action_size_inc():
    sel = editor.get_selection_range()
    if sel:
        editor.apply_style_to_selection({'size': min(72, editor.default['size'] + 2)})
    else:
        editor.set_default({'size': min(72, editor.default['size'] + 2)})


def action_size_dec():
    sel = editor.get_selection_range()
    if sel:
        editor.apply_style_to_selection({'size': max(8, editor.default['size'] - 2)})
    else:
        editor.set_default({'size': max(8, editor.default['size'] - 2)})


def action_reset():
    editor.reset_document()


def action_save():
    editor.save(); print('Saved')


def action_load():
    editor.load(); print('Loaded')

# table dialog and action
TABLE_DIALOG = TableDialog()

def action_insert_table_click():
    TABLE_DIALOG.open()


def action_insert_table(rows, cols):
    rows = max(1, int(rows))
    cols = max(1, int(cols))
    grid = [["" for _ in range(cols)] for _ in range(rows)]
    col_ws = [max(80, min(240, 120)) for _ in range(cols)]
    span = {'type': 'table', 'rows': grid, 'col_widths': col_ws, 'border': True}
    editor.insert_object_span(span)

btns_cfg = [
    ("Bold", action_bold),
    ("Italic", action_italic),
    ("Underline", action_underline),
    ("Size +", action_size_inc),
    ("Size -", action_size_dec),
    ("Insert Table", action_insert_table_click),
    ("Reset", action_reset),
    ("Save", action_save),
    ("Load", action_load),
]

buttons = make_button_grid(btns_cfg)

# text area
text_rect = pygame.Rect(SIDEBAR_W + 20, 20, WIDTH - SIDEBAR_W - 40, HEIGHT - 60)
mouse_down_in_text = False

# prepare a default FONT and LINE_HEIGHT used by some legacy UI parts
FONT = make_font(DEFAULT_FONT_SIZE)
LINE_HEIGHT = FONT.get_linesize()

# --------------------- Rendering ---------------------

def render_text_area(spans, rect, cursor_pos, selection_range=None, scroll=0, editing_table=None):
    surf = pygame.Surface(rect.size)
    surf.fill((255,255,255))
    padding = 8
    x = padding
    y = padding - scroll
    line_height = 0
    caret_pixel_pos = None
    sel_boxes = []
    abs_pos = 0
    for idx, s in enumerate(spans):
        # image
        if 'text' not in s and s.get('type') == 'image':
            w = s.get('width', 120)
            h = s.get('height', 80)
            if x + w > rect.width - padding:
                x = padding
                y += max(1, line_height)
                line_height = 0
            if abs_pos == cursor_pos:
                caret_pixel_pos = (x, y)
            if selection_range:
                a, b = selection_range
                if a <= abs_pos < b:
                    sel_boxes.append(pygame.Rect(x, y, w, h))
            try:
                img = editor._image_cache.get(s['path'])
                if img is None:
                    loaded = pygame.image.load(s['path']).convert_alpha()
                    img = pygame.transform.smoothscale(loaded, (w, h))
                    editor._image_cache[s['path']] = img
                surf.blit(img, (x, y))
            except Exception:
                pygame.draw.rect(surf, (220,220,220), (x, y, w, h))
                txt = make_font(14).render('Image', True, (120,120,120))
                surf.blit(txt, (x + 6, y + 6))
            if s.get('border'):
                pygame.draw.rect(surf, (0,0,0), (x, y, w, h), 2)
            x += w + 8
            line_height = max(line_height, h)
            abs_pos += 1
            continue
        # table
        if 'text' not in s and s.get('type') == 'table':
            col_ws = s.get('col_widths', [120]* (len(s.get('rows', [[]])[0]) if s.get('rows') else 1))
            rows = s.get('rows', [])
            font = make_font(16)
            cell_h = font.get_linesize() + 8
            table_w = sum(col_ws)
            table_h = len(rows) * cell_h
            if x + table_w > rect.width - padding:
                x = padding
                y += max(1, line_height)
                line_height = 0
            if abs_pos == cursor_pos:
                caret_pixel_pos = (x, y)
            if selection_range:
                a, b = selection_range
                if a <= abs_pos < b:
                    sel_boxes.append(pygame.Rect(x, y, table_w, table_h))
            cx = x
            cy = y
            for r_i, row in enumerate(rows):
                cx = x
                for ci, cell in enumerate(row):
                    w = col_ws[ci] if ci < len(col_ws) else 120
                    rect_cell = pygame.Rect(cx, cy, w, cell_h)
                    pygame.draw.rect(surf, (255,255,255), rect_cell)
                    if s.get('border'):
                        pygame.draw.rect(surf, (0,0,0), rect_cell, 1)
                    # highlight if editing
                    if editing_table is not None and editing_table[0] == idx and editing_table[1] == r_i and editing_table[2] == ci:
                        pygame.draw.rect(surf, (0,120,215), rect_cell, 2)
                    txt = make_font(14).render(str(cell), True, (0,0,0))
                    surf.blit(txt, (cx + 4, cy + 4))
                    cx += w
                cy += cell_h
            x += table_w + 8
            line_height = max(line_height, table_h)
            abs_pos += 1
            continue
        # text
        font = make_font(s.get('size', DEFAULT_FONT_SIZE), bold=s.get('bold', False), italic=s.get('italic', False), underline=s.get('underline', False))
        color = s.get('color', DEFAULT_COLOR)
        for ch in s['text']:
            if ch == '\n':
                x = padding
                y += font.get_linesize()
                line_height = 0
                if abs_pos == cursor_pos:
                    caret_pixel_pos = (x, y)
                abs_pos += 1
                continue
            ch_surf = font.render(ch, True, color)
            ch_w, ch_h = ch_surf.get_size()
            if x + ch_w > rect.width - padding:
                x = padding
                y += font.get_linesize()
                line_height = 0
            if abs_pos == cursor_pos:
                caret_pixel_pos = (x, y)
            if selection_range:
                a, b = selection_range
                if a <= abs_pos < b:
                    sel_boxes.append(pygame.Rect(x, y, ch_w, font.get_linesize()))
            surf.blit(ch_surf, (x, y))
            x += ch_w
            line_height = max(line_height, font.get_linesize())
            abs_pos += 1
    if caret_pixel_pos is None and cursor_pos == abs_pos:
        caret_pixel_pos = (x, y)
    content_height = y + line_height + padding
    for b in sel_boxes:
        s = pygame.Surface((b.width, b.height), pygame.SRCALPHA)
        s.fill((100,150,240,120))
        surf.blit(s, (b.x, b.y))
    return surf, caret_pixel_pos, content_height


def pixel_to_pos(spans, rect, relx, rely, scroll=0):
    padding = 8
    x = padding
    y = padding - scroll
    abs_pos = 0
    for s in spans:
        if 'text' not in s and s.get('type') == 'image':
            w = s.get('width', 120)
            h = s.get('height', 80)
            if x + w > rect.width - padding:
                x = padding
                y += h if h>0 else DEFAULT_FONT_SIZE
            if rely >= y and rely < y + h:
                if relx <= x + w / 2:
                    return abs_pos
                else:
                    return abs_pos + 1
            x += w + 8
            abs_pos += 1
            continue
        if 'text' not in s and s.get('type') == 'table':
            col_ws = s.get('col_widths', [120]* (len(s.get('rows', [[]])[0]) if s.get('rows') else 1))
            rows = s.get('rows', [])
            font = make_font(16)
            cell_h = font.get_linesize() + 8
            table_w = sum(col_ws)
            table_h = len(rows) * cell_h
            if x + table_w > rect.width - padding:
                x = padding
                y += table_h
            if rely >= y and rely < y + table_h:
                # determine clicked cell
                cx = x
                cy = y
                for r_i in range(len(rows)):
                    cx = x
                    for ci in range(len(rows[0])):
                        w = col_ws[ci] if ci < len(col_ws) else 120
                        if relx >= cx and relx < cx + w and rely >= cy and rely < cy + cell_h:
                            # return position at object start (abs_pos) and also provide cell index via special tuple handled by caller
                            return abs_pos, (r_i, ci)
                        cx += w
                    cy += cell_h
                # fallback
                if relx <= x + table_w/2:
                    return abs_pos
                else:
                    return abs_pos + 1
            x += table_w + 8
            abs_pos += 1
            continue
        font = make_font(s.get('size', DEFAULT_FONT_SIZE), bold=s.get('bold', False), italic=s.get('italic', False), underline=s.get('underline', False))
        for ch in s['text']:
            if ch == '\n':
                if rely < y + font.get_linesize():
                    return abs_pos
                x = padding
                y += font.get_linesize()
                abs_pos += 1
                continue
            ch_w, ch_h = font.size(ch)
            if x + ch_w > rect.width - padding:
                x = padding
                y += font.get_linesize()
            if rely >= y and rely < y + font.get_linesize():
                if relx <= x + ch_w / 2:
                    return abs_pos
            x += ch_w
            abs_pos += 1
    return abs_pos

# --------------------- Main loop ---------------------
running = True
scroll_offset = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # give all buttons a chance to update hover / clicks
        for b in buttons:
            b.handle_event(event, offset=(0,0))

        # table dialog has priority when visible
        if TABLE_DIALOG.visible:
            TABLE_DIALOG.handle_event(event, apply_fn=action_insert_table)
            # still allow ESC/closing handled in dialog
            if event.type == pygame.KEYDOWN:
                # swallow keys for dialog only
                pass
            # don't process further edits when dialog open
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                # when dialog visible, skip editor interactions below
                continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # wheel up
                scroll_offset = max(0, scroll_offset - LINE_HEIGHT)
            elif event.button == 5:  # wheel down
                scroll_offset += LINE_HEIGHT
            elif event.button == 1:
                mx, my = event.pos
                if mx > SIDEBAR_W:
                    # map click to text area relative coords
                    relx = mx - text_rect.x
                    rely = my - text_rect.y
                    pos = pixel_to_pos(editor.spans, text_rect, relx, rely, scroll=scroll_offset)
                    # pixel_to_pos can return (pos, (r,c)) for table cell clicks
                    if isinstance(pos, tuple) and len(pos) == 2 and isinstance(pos[1], tuple):
                        obj_pos, (r_i, c_i) = pos
                        # find span index at obj_pos
                        si, _ = editor.pos_to_span_index(obj_pos)
                        # set cursor at object start and enter table-edit mode
                        editor.cursor = obj_pos
                        editor.editing_table = (si, r_i, c_i)
                    else:
                        # normal position (int)
                        if isinstance(pos, tuple):
                            # sometimes returns (int,) - flatten
                            pos = pos[0]
                        editor.cursor = pos
                        editor.select_anchor = None
                        editor.editing_table = None
                else:
                    # click on sidebar -> buttons already handled by Button.handle_event
                    pass

        elif event.type == pygame.MOUSEMOTION:
            # possible drag selection (simple behaviour)
            if pygame.mouse.get_pressed()[0]:
                mx, my = event.pos
                if mx > SIDEBAR_W:
                    relx = mx - text_rect.x
                    rely = my - text_rect.y
                    pos = pixel_to_pos(editor.spans, text_rect, relx, rely, scroll=scroll_offset)
                    if isinstance(pos, tuple) and len(pos) == 2 and isinstance(pos[1], tuple):
                        editor.cursor = pos[0]
                    else:
                        if isinstance(pos, tuple):
                            pos = pos[0]
                        editor.cursor = pos

        elif event.type == pygame.MOUSEBUTTONUP:
            pass

        elif event.type == pygame.KEYDOWN:
            # if editing a table cell and ESC -> exit
            if editor.editing_table is not None:
                if event.key == pygame.K_ESCAPE:
                    editor.editing_table = None
                elif event.key == pygame.K_BACKSPACE:
                    editor.delete_back()
                elif event.key == pygame.K_RETURN:
                    # when in table cell, Enter moves to next row same column (or creates new row)
                    si, r, c = editor.editing_table
                    tspan = editor.spans[si]
                    if r + 1 < len(tspan['rows']):
                        editor.editing_table = (si, r + 1, c)
                    else:
                        # add a new row
                        newrow = ["" for _ in range(len(tspan['rows'][0]))]
                        editor.push_undo()
                        tspan['rows'].append(newrow)
                        editor.editing_table = (si, r + 1, c)
                elif event.key == pygame.K_TAB:
                    # move to next cell
                    si, r, c = editor.editing_table
                    tspan = editor.spans[si]
                    rows = len(tspan['rows'])
                    cols = len(tspan['rows'][0]) if rows>0 else 0
                    nc = c + 1
                    nr = r
                    if nc >= cols:
                        nc = 0
                        nr = (r + 1) % max(1, rows)
                    editor.editing_table = (si, nr, nc)
                elif event.key == pygame.K_LEFT:
                    editor.move_cursor(-1)
                elif event.key == pygame.K_RIGHT:
                    editor.move_cursor(1)
                elif event.key == pygame.K_UP:
                    editor.move_cursor(-80)
                elif event.key == pygame.K_DOWN:
                    editor.move_cursor(80)
                else:
                    if event.unicode:
                        editor.insert_text(event.unicode)
                continue  # skip normal editor actions when editing table

            # regular editor key handling
            if event.key == pygame.K_BACKSPACE:
                editor.delete_char()
            elif event.key == pygame.K_RETURN:
                editor.insert_text("\n")
            elif event.key == pygame.K_LEFT:
                editor.move_cursor(-1)
            elif event.key == pygame.K_RIGHT:
                editor.move_cursor(1)
            elif event.key == pygame.K_UP:
                editor.move_cursor(-80)
            elif event.key == pygame.K_DOWN:
                editor.move_cursor(80)
            elif event.key == pygame.K_TAB:
                # insert a tab character
                editor.insert_text("    ")
            elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                editor.save()
            elif event.key == pygame.K_o and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                editor.load()
            else:
                if event.unicode:
                    editor.insert_text(event.unicode)

    # --- Rendering ---
    screen.fill((200, 200, 200))
    screen_height = screen.get_height()

   # Sidebar mit Farbverlauf zeichnen (blau → lila)
    for y in range(SIDEBAR_W):
        t = y / SIDEBAR_W
        r = int(100 + (186 - 100) * t)
        g = int(149 + (85 - 149) * t)
        b = int(237 + (211 - 237) * t)
        pygame.draw.line(screen, (r, g, b), (y, 0), (y, screen_height))

    # Buttons zeichnen mit größerer, fetter Schrift
    big_font = pygame.font.SysFont('Arial', 22, bold=True)
    for btn in buttons:
        pygame.draw.rect(screen, btn.bg_color, btn.rect, border_radius=8)
        pygame.draw.rect(screen, (55, 0, 125), btn.rect, 2, border_radius=8)
    
        text_surface = big_font.render(btn.text, True, btn.text_color)
        text_rect = text_surface.get_rect(center=btn.rect.center)
        screen.blit(text_surface, text_rect)
        
   # Funktion zum Rendern mit Outline
    def render_text_with_outline(text, font, text_color, outline_color, outline_width=2):
        base = font.render(text, True, text_color)
        outline = font.render(text, True, outline_color)
    
        w, h = base.get_size()
        surf = pygame.Surface((w + outline_width * 2, h + outline_width * 2), pygame.SRCALPHA)

        # Outline in alle Richtungen zeichnen
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    surf.blit(outline, (dx + outline_width, dy + outline_width))

        # Haupttext in die Mitte setzen
        surf.blit(base, (outline_width, outline_width))
        return surf

    # Überschrift-Schrift festlegen
    title_font = pygame.font.SysFont('Segoe UI', 32, bold=True)

    # Text mit Outline rendern
    title_surface = render_text_with_outline("TOOLS", title_font, (255, 255, 255), (0, 0, 0), outline_width=2)
    title_rect = title_surface.get_rect(topleft=(50, 10))

    # Text aufs screen zeichnen
    screen.blit(title_surface, title_rect)



    # text area rect: update to current window size
    w, h = screen.get_size()
    text_rect = pygame.Rect(SIDEBAR_W + 20, 20, w - SIDEBAR_W - 40, h - 60)

    # render document into a surface
    selection_range = editor.get_selection_range()
    surface, caret_pos, content_h = render_text_area(editor.spans, text_rect, editor.cursor, selection_range, scroll=scroll_offset, editing_table=editor.editing_table)

    # blit area background
    screen.blit(surface, text_rect.topleft)

    # draw caret if visible
    if caret_pos:
        cx, cy = caret_pos
        # caret_pos is relative to text_rect top-left
        caret_x = text_rect.x + cx
        caret_y = text_rect.y + cy
        if pygame.time.get_ticks() // 500 % 2 == 0:
            pygame.draw.line(screen, (0, 0, 0), (caret_x, caret_y), (caret_x, caret_y + make_font(DEFAULT_FONT_SIZE).get_linesize()))

    # draw table dialog if open (on top)
    if TABLE_DIALOG.visible:
        TABLE_DIALOG.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
