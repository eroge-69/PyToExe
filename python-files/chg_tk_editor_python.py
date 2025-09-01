#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHG Editor — Tk (Windows-friendly) UI

Features
- Open/inspect .CHG files (binary format inferred from provided C# reader)
- Edit objects (types: 9 GameObject, 4 Sound, 6 Particle, 2 Light)
- Insert new objects of supported types; delete selected
- Preserve unknown/extra data (desc blocks, scripts, links) for safe round‑trip
- Save/Export back to .CHG; optional JSON import/export for objects

Notes
- Strings are encoded as Windows-1251 (Encoding.Default in C# on RU locales).
- Quaternion in file is stored as [-w, x, y, z]. UI shows (x,y,z,w).
- Description (200) blocks and Script(500) area are preserved as raw bytes.
- Link(400) blocks parsed minimally and also preserved on write.

Tested on Python 3.10+. Requires only Tkinter (bundled with CPython on Windows).
"""
from __future__ import annotations
import io
import os
import struct
import sys
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Union

# ------------------------------ Binary helpers ------------------------------
LE = "<"  # little endian

def read(fmt: str, f: io.BufferedReader):
    size = struct.calcsize(fmt)
    data = f.read(size)
    if len(data) != size:
        raise EOFError("Unexpected EOF while reading")
    return struct.unpack(fmt, data)

def write(fmt: str, f: io.BufferedWriter, *values):
    f.write(struct.pack(fmt, *values))

# ------------------------------ CHG primitives ------------------------------

def decode_bytes(bs: bytes) -> str:
    # C# BinaryReader with Encoding.Default – commonly cp1251 on Windows RU
    for enc in ("cp1251", "utf-8", "latin1"):
        try:
            return bs.decode(enc)
        except Exception:
            continue
    return bs.decode("latin1", errors="replace")


def encode_str(s: str) -> bytes:
    for enc in ("cp1251", "utf-8", "latin1"):
        try:
            return s.encode(enc)
        except Exception:
            continue
    return s.encode("latin1", errors="replace")

@dataclass
class CHGString:
    text: str = ""

    @classmethod
    def read(cls, f: io.BufferedReader) -> "CHGString":
        (size,) = read(LE + "I", f)
        data = f.read(size)
        if len(data) != size:
            raise EOFError("Unexpected EOF in CHGString")
        txt = decode_bytes(data)
        return cls(txt)

    def to_bytes(self) -> bytes:
        b = encode_str(self.text)
        return struct.pack(LE + "I", len(b)) + b

@dataclass
class Vector3:
    x: float
    y: float
    z: float

    @classmethod
    def read(cls, f: io.BufferedReader) -> "Vector3":
        x, y, z = read(LE + "fff", f)
        return cls(x, y, z)

    def to_bytes(self) -> bytes:
        return struct.pack(LE + "fff", self.x, self.y, self.z)

@dataclass
class Quaternion:
    x: float
    y: float
    z: float
    w: float  # UI stores true w; file stores -w first

    @classmethod
    def read(cls, f: io.BufferedReader) -> "Quaternion":
        (w_neg,) = read(LE + "f", f)
        x, y, z = read(LE + "fff", f)
        return cls(x, y, z, -w_neg)

    def to_bytes(self) -> bytes:
        return struct.pack(LE + "f", -self.w) + struct.pack(LE + "fff", self.x, self.y, self.z)

# ------------------------------ Blocks ------------------------------

OBJ_SIGN = 100
DESC_SIGN = 200
UNK300_SIGN = 300
LINK_SIGN = 400
SCRIPT_SIGN = 500

@dataclass
class DescriptionBlock:
    # Entire raw block, including header (sign,len,type,...)
    sign: int
    length: int
    btype: int
    payload: bytes

    @classmethod
    def read(cls, f: io.BufferedReader) -> "DescriptionBlock":
        (sign,) = read(LE + "h", f)
        (length,) = read(LE + "I", f)
        (btype,) = read(LE + "I", f)
        to_read = length - 10
        payload = f.read(to_read)
        if len(payload) != to_read:
            raise EOFError("EOF in DescriptionBlock")
        return cls(sign, length, btype, payload)

    def to_bytes(self) -> bytes:
        return struct.pack(LE + "hII", self.sign, self.length, self.btype) + self.payload

@dataclass
class LinkBlock:
    sign: int
    size: int
    name: CHGString
    unk: int

    @classmethod
    def read(cls, f: io.BufferedReader) -> "LinkBlock":
        (sign,) = read(LE + "H", f)
        (size,) = read(LE + "I", f)
        name = CHGString.read(f)
        (unk,) = read(LE + "I", f)
        return cls(sign, size, name, unk)

    def to_bytes(self) -> bytes:
        payload = self.name.to_bytes() + struct.pack(LE + "I", self.unk)
        size = 2 + 4 + len(payload)  # entire block size including header
        return struct.pack(LE + "H", self.sign) + struct.pack(LE + "I", size) + payload

@dataclass
class BaseObject:
    block_sign: int = OBJ_SIGN
    block_type: int = 0
    position: Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    size: Vector3 = field(default_factory=lambda: Vector3(1, 1, 1))
    rotation: Quaternion = field(default_factory=lambda: Quaternion(0, 0, 0, 1))
    name: CHGString = field(default_factory=lambda: CHGString("Object"))
    parent_name: CHGString = field(default_factory=lambda: CHGString(""))
    desc: Optional[DescriptionBlock] = None

    # raw preservation (for unknown types)
    raw_unknown: Optional[bytes] = None  # bytes after header/type (length-10)

    @property
    def display_name(self) -> str:
        base = self.name.text.split("\n")[0]
        return base or f"Type{self.block_type}"

    @classmethod
    def read_from(cls, f: io.BufferedReader) -> "BaseObject":
        start = f.tell()
        (sign,) = read(LE + "h", f)
        (blen,) = read(LE + "I", f)
        (btype,) = read(LE + "I", f)
        if btype not in (9, 4, 6, 2):
            # Unknown type; read raw and keep it
            raw = f.read(blen - 10)
            obj = BaseObject(block_sign=sign, block_type=btype)
            obj.raw_unknown = raw
            return obj
        pos = Vector3.read(f)
        scale = Vector3.read(f)
        rot = Quaternion.read(f)
        name = CHGString.read(f)
        parent = CHGString.read(f)
        if btype == 9:
            file_name = CHGString.read(f)
            obj = GameObject(block_type=9, position=pos, size=scale, rotation=rot,
                             name=name, parent_name=parent, file_name=file_name)
            return obj
        if btype == 6:
            return Particle(block_type=6, position=pos, size=scale, rotation=rot,
                            name=name, parent_name=parent)
        if btype == 4:
            file_name = CHGString.read(f)
            (sound_sign,) = read(LE + "B", f)
            (unk_u32,) = read(LE + "I", f)
            flt = list(read(LE + "ffffffff", f))
            (unk_b2,) = read(LE + "B", f)
            (flt9,) = read(LE + "f", f)
            return Sound(block_type=4, position=pos, size=scale, rotation=rot,
                         name=name, parent_name=parent, file_name=file_name,
                         sound_sign=sound_sign, unk=unk_u32,
                         floats=flt + [flt9], unk_b2=unk_b2)
        if btype == 2:
            (light_sign,) = read(LE + "I", f)
            flt1, flt2, flt3 = read(LE + "fff", f)
            (flt4,) = read(LE + "f", f)
            (unk_byte,) = read(LE + "B", f)
            flt5, flt6, flt7, flt8 = read(LE + "ffff", f)
            (unk1,) = read(LE + "I", f)
            (unk2,) = read(LE + "I", f)
            unk_str2 = CHGString.read(f)
            (unkanother,) = read(LE + "B", f)
            return Light(block_type=2, position=pos, size=scale, rotation=rot,
                         name=name, parent_name=parent,
                         light_block_sign=light_sign,
                         flt1=flt1, flt2=flt2, flt3=flt3, flt4=flt4, unk=unk_byte,
                         flt5=flt5, flt6=flt6, flt7=flt7, flt8=flt8, unk1=unk1, unk2=unk2,
                         unk_string2=unk_str2, unkanother=unkanother)
        raise AssertionError("Unhandled type")

    def _common_payload(self) -> bytes:
        return (
            self.position.to_bytes()
            + self.size.to_bytes()
            + self.rotation.to_bytes()
            + self.name.to_bytes()
            + self.parent_name.to_bytes()
        )

    def _header(self, payload_len: int) -> bytes:
        # 2 + 4 + 4 == 10 bytes header
        return struct.pack(LE + "hII", self.block_sign, 10 + payload_len, self.block_type)

    def to_bytes(self) -> bytes:
        if self.raw_unknown is not None:
            return struct.pack(LE + "hII", self.block_sign, 10 + len(self.raw_unknown), self.block_type) + self.raw_unknown
        raise NotImplementedError

@dataclass
class GameObject(BaseObject):
    file_name: CHGString = field(default_factory=lambda: CHGString(""))

    def to_bytes(self) -> bytes:
        self.block_type = 9
        payload = self._common_payload() + self.file_name.to_bytes()
        return self._header(len(payload)) + payload

@dataclass
class Particle(BaseObject):
    def to_bytes(self) -> bytes:
        self.block_type = 6
        payload = self._common_payload()
        return self._header(len(payload)) + payload

@dataclass
class Sound(BaseObject):
    file_name: CHGString = field(default_factory=lambda: CHGString(""))
    sound_sign: int = 0
    unk: int = 0
    floats: List[float] = field(default_factory=lambda: [0.0] * 9)  # 9 floats
    unk_b2: int = 0

    def to_bytes(self) -> bytes:
        self.block_type = 4
        payload = self._common_payload()
        payload += self.file_name.to_bytes()
        payload += struct.pack(LE + "B", self.sound_sign)
        payload += struct.pack(LE + "I", self.unk)
        if len(self.floats) < 9:
            self.floats = (self.floats + [0.0] * 9)[:9]
        payload += struct.pack(LE + "ffffffff", *self.floats[:8])
        payload += struct.pack(LE + "B", self.unk_b2)
        payload += struct.pack(LE + "f", self.floats[8])
        return self._header(len(payload)) + payload

@dataclass
class Light(BaseObject):
    light_block_sign: int = 0
    flt1: float = 0.0
    flt2: float = 0.0
    flt3: float = 0.0
    flt4: float = 0.0
    unk: int = 0  # byte
    flt5: float = 0.0
    flt6: float = 0.0
    flt7: float = 0.0
    flt8: float = 0.0
    unk1: int = 0
    unk2: int = 0
    unk_string2: CHGString = field(default_factory=lambda: CHGString(""))
    unkanother: int = 0  # byte

    def to_bytes(self) -> bytes:
        self.block_type = 2
        payload = self._common_payload()
        payload += struct.pack(LE + "I", self.light_block_sign)
        payload += struct.pack(LE + "fff", self.flt1, self.flt2, self.flt3)
        payload += struct.pack(LE + "f", self.flt4)
        payload += struct.pack(LE + "B", self.unk)
        payload += struct.pack(LE + "ffff", self.flt5, self.flt6, self.flt7, self.flt8)
        payload += struct.pack(LE + "I", self.unk1)
        payload += struct.pack(LE + "I", self.unk2)
        payload += self.unk_string2.to_bytes()
        payload += struct.pack(LE + "B", self.unkanother)
        return self._header(len(payload)) + payload

# ------------------------------ CHG file ------------------------------

@dataclass
class CHGFile:
    file_sign: int = 1234  # short
    file_length: int = 0   # int
    objects: List[BaseObject] = field(default_factory=list)
    desc_blocks: List[DescriptionBlock] = field(default_factory=list)
    link_blocks: List[LinkBlock] = field(default_factory=list)
    scripts_raw: bytes = b""  # preserved tail starting at 0x500 sign (if present)

    @classmethod
    def parse(cls, data: bytes) -> "CHGFile":
        f = io.BytesIO(data)
        (file_sign,) = read(LE + "h", f)
        (file_len,) = read(LE + "I", f)
        out = CHGFile(file_sign=file_sign, file_length=file_len)
        try:
            while True:
                here = f.tell()
                next2 = f.read(2)
                if not next2 or len(next2) < 2:
                    break
                sign = struct.unpack(LE + "h", next2)[0]
                f.seek(here)
                if sign == OBJ_SIGN:  # 100
                    obj = BaseObject.read_from(f)
                    out.objects.append(obj)
                elif sign == DESC_SIGN:  # 200
                    desc = DescriptionBlock.read(f)
                    out.desc_blocks.append(desc)
                    if out.objects:
                        out.objects[-1].desc = desc
                elif sign == UNK300_SIGN:  # 300 — early exit like C#
                    # Consume and stop
                    f.read(2)
                    break
                elif sign == LINK_SIGN:  # 400
                    lb = LinkBlock.read(f)
                    out.link_blocks.append(lb)
                elif sign == SCRIPT_SIGN:  # 500
                    # Preserve everything from here to EOF
                    tail = f.read()
                    out.scripts_raw = struct.pack(LE + "h", SCRIPT_SIGN) + tail
                    break
                else:
                    # Unknown block; try to bail to avoid infinite loop
                    raise ValueError(f"Unknown block sign {sign} at offset {here}")
        except EOFError:
            pass
        return out

    def to_bytes(self) -> bytes:
        # Build body (everything after header)
        body = io.BytesIO()
        for obj in self.objects:
            body.write(obj.to_bytes())
            if obj.desc is not None:
                # Re-emit associated desc immediately after, like source reader expects
                body.write(obj.desc.to_bytes())
        for lb in self.link_blocks:
            body.write(lb.to_bytes())
        if self.scripts_raw:
            body.write(self.scripts_raw)
        body_bytes = body.getvalue()
        header = struct.pack(LE + "hI", self.file_sign, len(body_bytes))
        return header + body_bytes

    # --------------- JSON (objects) ---------------
    def objects_to_json(self) -> str:
        def obj_to_dict(o: BaseObject):
            d = {
                "type": o.block_type,
                "position": asdict(o.position),
                "size": asdict(o.size),
                "rotation": asdict(o.rotation),
                "name": o.name.text,
                "parent": o.parent_name.text,
            }
            if isinstance(o, GameObject):
                d["file_name"] = o.file_name.text
            if isinstance(o, Sound):
                d["file_name"] = o.file_name.text
                d["sound_sign"] = o.sound_sign
                d["unk"] = o.unk
                d["floats"] = o.floats
                d["unk_b2"] = o.unk_b2
            if isinstance(o, Light):
                d.update({
                    "light_block_sign": o.light_block_sign,
                    "flt1": o.flt1, "flt2": o.flt2, "flt3": o.flt3, "flt4": o.flt4,
                    "unk": o.unk, "flt5": o.flt5, "flt6": o.flt6, "flt7": o.flt7, "flt8": o.flt8,
                    "unk1": o.unk1, "unk2": o.unk2, "unk_string2": o.unk_string2.text,
                    "unkanother": o.unkanother,
                })
            return d
        data = [obj_to_dict(o) for o in self.objects if o.raw_unknown is None]
        return json.dumps(data, ensure_ascii=False, indent=2)

    def load_objects_from_json(self, s: str):
        arr = json.loads(s)
        new_objs: List[BaseObject] = []
        for d in arr:
            t = int(d.get("type", 9))
            base_kwargs = dict(
                position=Vector3(**d.get("position", {"x": 0, "y": 0, "z": 0})),
                size=Vector3(**d.get("size", {"x": 1, "y": 1, "z": 1})),
                rotation=Quaternion(**d.get("rotation", {"x": 0, "y": 0, "z": 0, "w": 1})),
                name=CHGString(d.get("name", "Object")),
                parent_name=CHGString(d.get("parent", "")),
            )
            if t == 9:
                new_objs.append(GameObject(**base_kwargs, file_name=CHGString(d.get("file_name", ""))))
            elif t == 6:
                new_objs.append(Particle(**base_kwargs))
            elif t == 4:
                new_objs.append(Sound(**base_kwargs,
                                      file_name=CHGString(d.get("file_name", "")),
                                      sound_sign=int(d.get("sound_sign", 0)),
                                      unk=int(d.get("unk", 0)),
                                      floats=list(d.get("floats", [0]*9))[:9],
                                      unk_b2=int(d.get("unk_b2", 0))))
            elif t == 2:
                new_objs.append(Light(**base_kwargs,
                                      light_block_sign=int(d.get("light_block_sign", 0)),
                                      flt1=float(d.get("flt1", 0)), flt2=float(d.get("flt2", 0)), flt3=float(d.get("flt3", 0)), flt4=float(d.get("flt4", 0)),
                                      unk=int(d.get("unk", 0)),
                                      flt5=float(d.get("flt5", 0)), flt6=float(d.get("flt6", 0)), flt7=float(d.get("flt7", 0)), flt8=float(d.get("flt8", 0)),
                                      unk1=int(d.get("unk1", 0)), unk2=int(d.get("unk2", 0)),
                                      unk_string2=CHGString(d.get("unk_string2", "")),
                                      unkanother=int(d.get("unkanother", 0))))
            else:
                # Unknown — skip to avoid data loss
                continue
        self.objects = new_objs

# ------------------------------ Tk UI ------------------------------

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHG Editor (Tk)")
        self.geometry("1100x650")
        self.chg: Optional[CHGFile] = None
        self.current_path: Optional[str] = None

        self._build_menu()
        self._build_ui()

    # --- UI construction ---
    def _build_menu(self):
        m = tk.Menu(self)
        fm = tk.Menu(m, tearoff=0)
        fm.add_command(label="Open…", command=self.cmd_open)
        fm.add_command(label="Save", command=self.cmd_save)
        fm.add_command(label="Save As…", command=self.cmd_save_as)
        fm.add_separator()
        fm.add_command(label="Export Objects to JSON…", command=self.cmd_export_json)
        fm.add_command(label="Import Objects from JSON…", command=self.cmd_import_json)
        fm.add_separator()
        fm.add_command(label="Exit", command=self.destroy)
        m.add_cascade(label="File", menu=fm)

        em = tk.Menu(m, tearoff=0)
        em.add_command(label="Add GameObject (9)", command=lambda: self.add_object(9))
        em.add_command(label="Add Sound (4)", command=lambda: self.add_object(4))
        em.add_command(label="Add Particle (6)", command=lambda: self.add_object(6))
        em.add_command(label="Add Light (2)", command=lambda: self.add_object(2))
        em.add_separator()
        em.add_command(label="Delete Selected", command=self.delete_selected)
        m.add_cascade(label="Edit", menu=em)

        self.config(menu=m)

    def _build_ui(self):
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)

        # Tree (left)
        left = ttk.Frame(root)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols = ("idx", "type", "name", "parent")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, w in zip(cols, (60, 70, 280, 200)):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=w, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Buttons under tree
        tb = ttk.Frame(left)
        tb.pack(fill=tk.X)
        ttk.Button(tb, text="+ GameObject", command=lambda: self.add_object(9)).pack(side=tk.LEFT)
        ttk.Button(tb, text="+ Sound", command=lambda: self.add_object(4)).pack(side=tk.LEFT)
        ttk.Button(tb, text="+ Particle", command=lambda: self.add_object(6)).pack(side=tk.LEFT)
        ttk.Button(tb, text="+ Light", command=lambda: self.add_object(2)).pack(side=tk.LEFT)
        ttk.Button(tb, text="Delete", command=self.delete_selected).pack(side=tk.LEFT)

        # Details (right)
        right = ttk.Frame(root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.detail = right
        self.detail_widgets: dict[str, tk.Widget] = {}

        self._build_detail_panel()

        # Status
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill=tk.X, side=tk.BOTTOM)

    def _build_detail_panel(self):
        for w in self.detail.winfo_children():
            w.destroy()
        grid = ttk.Frame(self.detail)
        grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        self._add_entry(grid, "Name", row=0)
        self._add_entry(grid, "Parent", row=1)
        for i, axis in enumerate(["x", "y", "z"]):
            self._add_entry(grid, f"Pos.{axis}", row=2, col=i)
            self._add_entry(grid, f"Scale.{axis}", row=3, col=i)
        for i, axis in enumerate(["x", "y", "z", "w"]):
            self._add_entry(grid, f"Rot.{axis}", row=4 + (i // 2), col=(i % 2))
        # Type-specific area
        ttk.Separator(grid, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=6, sticky="ew", pady=8)
        self.type_area = ttk.Frame(grid)
        self.type_area.grid(row=7, column=0, columnspan=6, sticky="nsew")
        grid.columnconfigure(0, weight=1)

        # Action buttons
        btns = ttk.Frame(self.detail)
        btns.pack(fill=tk.X, padx=12, pady=(0, 12))
        ttk.Button(btns, text="Apply Changes", command=self.apply_changes).pack(side=tk.LEFT)
        ttk.Button(btns, text="Save", command=self.cmd_save).pack(side=tk.LEFT, padx=6)

    def _add_entry(self, parent, label, row, col=0):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="ew", padx=4, pady=2)
        ttk.Label(frame, text=label, width=10).pack(side=tk.LEFT)
        var = tk.StringVar()
        ent = ttk.Entry(frame, textvariable=var)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.detail_widgets[label] = ent

    # --- Commands ---
    def cmd_open(self):
        path = filedialog.askopenfilename(title="Open CHG", filetypes=[("CHG files", "*.chg"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "rb") as fh:
            data = fh.read()
        self.chg = CHGFile.parse(data)
        self.current_path = path
        self.refresh_tree()
        self.status.set(f"Loaded {os.path.basename(path)}: {len(self.chg.objects)} objects, {len(self.chg.link_blocks)} links")

    def cmd_save(self):
        if not self.chg:
            return
        if not self.current_path:
            return self.cmd_save_as()
        data = self.chg.to_bytes()
        with open(self.current_path, "wb") as fh:
            fh.write(data)
        self.status.set(f"Saved {os.path.basename(self.current_path)} ({len(data)} bytes)")

    def cmd_save_as(self):
        if not self.chg:
            return
        path = filedialog.asksaveasfilename(title="Save CHG As", defaultextension=".chg",
                                            filetypes=[("CHG files", "*.chg"), ("All files", "*.*")])
        if not path:
            return
        self.current_path = path
        self.cmd_save()

    def cmd_export_json(self):
        if not self.chg:
            return
        path = filedialog.asksaveasfilename(title="Export Objects JSON", defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.chg.objects_to_json())
        self.status.set(f"Exported JSON → {os.path.basename(path)}")

    def cmd_import_json(self):
        if not self.chg:
            return
        path = filedialog.askopenfilename(title="Import Objects JSON", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as fh:
            s = fh.read()
        self.chg.load_objects_from_json(s)
        self.refresh_tree()
        self.status.set(f"Imported objects from JSON: {len(self.chg.objects)} items")

    def add_object(self, t: int):
        if not self.chg:
            self.chg = CHGFile()
        base = dict(
            position=Vector3(0, 0, 0), size=Vector3(1, 1, 1), rotation=Quaternion(0, 0, 0, 1),
            name=CHGString(f"New{t}"), parent_name=CHGString("")
        )
        if t == 9:
            obj = GameObject(**base, file_name=CHGString(""))
        elif t == 4:
            obj = Sound(**base, file_name=CHGString("sound.wav"), floats=[0.0]*9)
        elif t == 6:
            obj = Particle(**base)
        elif t == 2:
            obj = Light(**base)
        else:
            messagebox.showwarning("Unknown", f"Unsupported type {t}")
            return
        self.chg.objects.append(obj)
        self.refresh_tree()
        self.status.set(f"Inserted object type {t}")

    def delete_selected(self):
        if not self.chg:
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "values")[0])
        if 0 <= idx < len(self.chg.objects):
            del self.chg.objects[idx]
            self.refresh_tree()
            self._build_detail_panel()

    def on_select(self, event=None):
        if not self.chg:
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "values")[0])
        if not (0 <= idx < len(self.chg.objects)):
            return
        obj = self.chg.objects[idx]
        self.populate_detail(obj)

    def populate_detail(self, obj: BaseObject):
        # common
        self.detail_widgets["Name"].delete(0, tk.END)
        self.detail_widgets["Name"].insert(0, obj.name.text)
        self.detail_widgets["Parent"].delete(0, tk.END)
        self.detail_widgets["Parent"].insert(0, obj.parent_name.text)
        # pos
        for axis, v in zip(["x", "y", "z"], (obj.position.x, obj.position.y, obj.position.z)):
            w = self.detail_widgets[f"Pos.{axis}"]
            w.delete(0, tk.END); w.insert(0, str(v))
        # scale
        for axis, v in zip(["x", "y", "z"], (obj.size.x, obj.size.y, obj.size.z)):
            w = self.detail_widgets[f"Scale.{axis}"]
            w.delete(0, tk.END); w.insert(0, str(v))
        # rot
        for axis, v in zip(["x", "y", "z", "w"], (obj.rotation.x, obj.rotation.y, obj.rotation.z, obj.rotation.w)):
            key = f"Rot.{axis}"
            if key in self.detail_widgets:
                w = self.detail_widgets[key]
                w.delete(0, tk.END); w.insert(0, str(v))
        # type-specific
        for w in self.type_area.winfo_children():
            w.destroy()
        if isinstance(obj, GameObject):
            self._add_type_entry(self.type_area, "file_name", obj.file_name.text)
        elif isinstance(obj, Particle):
            ttk.Label(self.type_area, text="Particle (no extra fields)").pack(anchor="w")
        elif isinstance(obj, Sound):
            self._add_type_entry(self.type_area, "file_name", obj.file_name.text)
            self._add_type_entry(self.type_area, "sound_sign", str(obj.sound_sign))
            self._add_type_entry(self.type_area, "unk", str(obj.unk))
            for i, val in enumerate(obj.floats[:9]):
                self._add_type_entry(self.type_area, f"f{i+1}", str(val))
            self._add_type_entry(self.type_area, "unk_b2", str(obj.unk_b2))
        elif isinstance(obj, Light):
            fields = {
                "light_block_sign": obj.light_block_sign,
                "flt1": obj.flt1, "flt2": obj.flt2, "flt3": obj.flt3, "flt4": obj.flt4,
                "unk": obj.unk,
                "flt5": obj.flt5, "flt6": obj.flt6, "flt7": obj.flt7, "flt8": obj.flt8,
                "unk1": obj.unk1, "unk2": obj.unk2, "unk_string2": obj.unk_string2.text,
                "unkanother": obj.unkanother,
            }
            for k, v in fields.items():
                self._add_type_entry(self.type_area, k, str(v))
        else:
            ttk.Label(self.type_area, text=f"Unknown type {obj.block_type} (raw preserved)").pack(anchor="w")

    def _add_type_entry(self, parent, key, value):
        f = ttk.Frame(parent); f.pack(fill=tk.X, pady=1)
        ttk.Label(f, text=key, width=18).pack(side=tk.LEFT)
        e = ttk.Entry(f)
        e.insert(0, value)
        e.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.detail_widgets[f"type:{key}"] = e

    def apply_changes(self):
        if not self.chg:
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(self.tree.item(sel[0], "values")[0])
        obj = self.chg.objects[idx]
        try:
            obj.name.text = self.detail_widgets["Name"].get()
            obj.parent_name.text = self.detail_widgets["Parent"].get()
            # pos
            obj.position.x = float(self.detail_widgets["Pos.x"].get())
            obj.position.y = float(self.detail_widgets["Pos.y"].get())
            obj.position.z = float(self.detail_widgets["Pos.z"].get())
            # scale
            obj.size.x = float(self.detail_widgets["Scale.x"].get())
            obj.size.y = float(self.detail_widgets["Scale.y"].get())
            obj.size.z = float(self.detail_widgets["Scale.z"].get())
            # rot
            obj.rotation.x = float(self.detail_widgets["Rot.x"].get())
            obj.rotation.y = float(self.detail_widgets["Rot.y"].get())
            obj.rotation.z = float(self.detail_widgets["Rot.z"].get())
            obj.rotation.w = float(self.detail_widgets["Rot.w"].get())

            # type specifics
            if isinstance(obj, GameObject):
                obj.file_name.text = self.detail_widgets.get("type:file_name").get()
            elif isinstance(obj, Sound):
                obj.file_name.text = self.detail_widgets.get("type:file_name").get()
                obj.sound_sign = int(float(self.detail_widgets.get("type:sound_sign").get()))
                obj.unk = int(float(self.detail_widgets.get("type:unk").get()))
                floats = []
                for i in range(1, 10):
                    floats.append(float(self.detail_widgets.get(f"type:f{i}").get()))
                obj.floats = floats
                obj.unk_b2 = int(float(self.detail_widgets.get("type:unk_b2").get()))
            elif isinstance(obj, Light):
                def gv(k): return self.detail_widgets.get(f"type:{k}").get()
                obj.light_block_sign = int(float(gv("light_block_sign")))
                obj.flt1 = float(gv("flt1")); obj.flt2 = float(gv("flt2")); obj.flt3 = float(gv("flt3")); obj.flt4 = float(gv("flt4"))
                obj.unk = int(float(gv("unk")))
                obj.flt5 = float(gv("flt5")); obj.flt6 = float(gv("flt6")); obj.flt7 = float(gv("flt7")); obj.flt8 = float(gv("flt8"))
                obj.unk1 = int(float(gv("unk1"))); obj.unk2 = int(float(gv("unk2")))
                obj.unk_string2.text = gv("unk_string2")
                obj.unkanother = int(float(gv("unkanother")))
            # Unknown types: nothing to apply
        except Exception as e:
            messagebox.showerror("Invalid value", str(e))
            return
        self.refresh_tree(select_idx=idx)
        self.status.set("Changes applied")

    def refresh_tree(self, select_idx: Optional[int] = None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not self.chg:
            return
        for i, obj in enumerate(self.chg.objects):
            typ = obj.block_type
            nm = obj.display_name
            parent = obj.parent_name.text.split("\n")[0]
            self.tree.insert("", "end", values=(i, typ, nm, parent))
        if select_idx is not None and 0 <= select_idx < len(self.chg.objects):
            iid = self.tree.get_children()[select_idx]
            self.tree.selection_set(iid)
            self.tree.see(iid)

# ------------------------------ Entry point ------------------------------

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
