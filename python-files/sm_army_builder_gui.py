
# sm_army_builder_gui.py
# Space Marines Army Builder — desktop GUI (PyQt5)
# Follows the rules from "armybuilder.doc" and uses the JSON data file
# "units_codex_with_cursed_extras (1).json" by default (same folder).
#
# Convert to EXE (example):
#   pip install pyinstaller pyqt5
#   pyinstaller --onefile --windowed sm_army_builder_gui.py
#
# Notes:
# - Left: units list with tabs (Codex, Heroes, Deathwatch, Cursed, Damned)
# - Right: roster, grouped by category, with model +/- and transport radios
# - Top bar: points total and category counters; Reset and Export .txt
# - Implements key constraints:
#     * HQ 1–2, Troops 2–6, Elite 0–3, Fast 0–3, Heavy 0–3
#     * 0–1 limits: Emperor's Champion, Land Raider Crusader, Assassin, Inquisitor,
#                  Legion of the Damned, Deathwatch Kill Team
#     * Command Squad: does NOT consume an HQ slot; max one per qualifying HQ;
#                      qualifying HQ excludes Emperor's Champion
#     * Cursed picks: You may take up to as many cursed units as you have non‑cursed
#                     Troop selections. BUT if any Troop from Cursed is taken,
#                     total Cursed allowance becomes exactly 1 and is consumed.
#     * Exclusions: Grey Knights ↔ Deathwatch and non‑LotD Cursed are mutually exclusive.
#                   (Legion of the Damned does not trigger the exclusion.)
# - UI approximates the provided HTML screenshot styling.
#
# Known gaps (MVP):
# - Detailed weapon/option groups (beyond transports and model count) are not fully
#   interactive for every unit; the infrastructure exists to extend it.
# - Detachments UI exists only to set points cap; it does not split roster by detachment.
# - If your JSON differs in structure, adjust FIELD MAPS near load_data().
#
# © 2025 — for personal use.
from __future__ import annotations
import json, os, sys, math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# ---- PyQt5 import (fallback to PySide6 if needed) ----
QT_LIB = "PyQt5"
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except Exception:
    QT_LIB = "PySide6"
    from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore

APP_TITLE = "SM Army Builder"
POINTS_CAP_DEFAULT = 2000

# --- Domain model ------------------------------------------------------------
SECTIONS_ORDER = ["HQ", "Elite", "Troop", "Fast", "Heavy"]

# Custom doc-specified sort order per section (selection panel).
CUSTOM_ORDER = {
    "HQ": [
        "Force Commander", "Commander", "Leader", "Emperor's Champion",
        "Chaplain", "Librarian", "Command Squad"
    ],
    "Elite": [
        "Dreadnought", "Terminator Squad", "Terminator Assault Squad", "Space Marine Veteran Squad",
    ],
    "Troop": [
        "Space Marine Tactical Squad", "Scout Squad"
    ],
    "Fast": [
        "Assault Squad", "Bike Squad", "Attack Bike Squad", "Scout Bike Squad",
        "Land Speeder Squad", "Land Speeder Tornado", "Land Speeder Typhoon"
    ],
    "Heavy": [
        "Devastator Squad", # others (tanks) arbitrary
        "Predator Annihilator", "Predator Destructor", "Vindicator", "Whirlwind",
        "Land Raider", "Land Raider Crusader"
    ],
}

# Doc-mandated 0-1 (global) identifiers by display name pattern
ZERO_ONE_NAMES = {
    "Emperor's Champion",
    "Land Raider Crusader",
    "Assassin",
    "Inquisitor",
    "Legion of the Damned",
    "Deathwatch Kill Team",
    # From doc (Cursed category has its own 0-1 per certain units handled below)
}

# Cursed chapters grid (2x3). If your JSON has different names, you can edit here.
CURSED_CHAPTERS = [
    "Minotaurs",
    "Lamenters",
    "Flame Falcons",
    "Sons of Antaeus",
    "Legion of the Damned",
    "Black Dragons",
]

# Allowed units in the Cursed tab (and which of them are 0-1 there)
CURSED_ALLOWED = {
    # HQ
    "Force Commander": False,
    "Commander": False,
    "Leader": False,
    "Librarian": False,
    "Chaplain": False,
    "Command Squad": False,
    # Elite
    "Dreadnought": False,
    "Terminator Squad": True,   # 0-1
    # Troop
    "Space Marine Tactical Squad": False,
    # Fast
    "Assault Squad": True,      # 0-1
    "Bike Squad": True,         # 0-1
    # Heavy
    "Devastator Squad": False,
    "Predator Annihilator": True,
    "Predator Destructor": True,
    "Vindicator": True,
    "Whirlwind": True,
    "Land Raider": True,
}

# Category slot caps
SLOT_LIMITS = {
    "HQ": (1, 2),
    "Troop": (2, 6),
    "Elite": (0, 3),
    "Fast": (0, 3),
    "Heavy": (0, 3),
}

@dataclass
class OptionChoice:
    id: str
    label: str
    points: int = 0
    max_models: Optional[int] = None

@dataclass
class OptionGroup:
    id: str
    label: str
    type: str                 # 'exclusive'|'multi'|'multi_per_model'|'count_limit'|'toggle'
    items: List[OptionChoice] = field(default_factory=list)
    limit_total: Optional[int] = None
    requires: Optional[str] = None
    points: Optional[int] = None           # for toggle

@dataclass
class UnitDef:
    name: str
    faction: str
    section: str
    base_min: int = 1
    base_max: int = 1
    per_model: Optional[int] = None        # points per model
    fixed_points: Optional[int] = None     # fixed (vehicles etc.); if set, per_model ignored
    limit_0_1: bool = False
    consumes_slot: bool = True
    requires_qualifying_hq: bool = False
    hq_exclusions: List[str] = field(default_factory=list)  # names that do NOT grant command squad
    option_groups: List[OptionGroup] = field(default_factory=list)
    cursed_extra_points: Dict[str,int] = field(default_factory=dict)

@dataclass
class RosterItem:
    unit: UnitDef
    models: int
    faction: str
    cursed_chapter: Optional[str] = None
    selected_options: Dict[str, Any] = field(default_factory=dict)  # group_id -> payload

    def display_name(self) -> str:
        if self.cursed_chapter:
            return f"{self.cursed_chapter} — {self.unit.name}"
        return self.unit.name

    def base_points(self) -> int:
        if self.unit.fixed_points is not None:
            p = self.unit.fixed_points
        else:
            p = self.models * (self.unit.per_model or 0)
        # Cursed chapter surcharges/discounts
        if self.cursed_chapter:
            p += self.unit.cursed_extra_points.get(self.cursed_chapter, 0)
        return p

    def options_points(self) -> int:
        total = 0
        for gid, sel in self.selected_options.items():
            if isinstance(sel, dict) and sel.get("type") == "exclusive":
                choice = sel.get("choice")
                if choice:
                    total += int(choice.get("points") or 0)
            elif isinstance(sel, dict) and sel.get("type") == "toggle":
                if sel.get("on"):
                    total += int(sel.get("points") or 0)
            elif isinstance(sel, dict) and sel.get("type") == "multi":
                for choice in sel.get("choices", []):
                    total += int(choice.get("points") or 0)
            elif isinstance(sel, dict) and sel.get("type") == "multi_per_model":
                ppm = int(sel.get("points_per_model") or 0)
                total += ppm * self.models
            elif isinstance(sel, dict) and sel.get("type") == "count_limit":
                # sel has 'choices': list of {points}
                for choice in sel.get("choices", []):
                    total += int(choice.get("points") or 0)
        return total

    def total_points(self) -> int:
        return self.base_points() + self.options_points()

# --- Data loading ------------------------------------------------------------
def load_json_from_default_locations() -> Dict[str, Any]:
    # Try to find the json in the script folder with common names
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    candidates = [
        "units_codex_with_cursed_extras.json",
        "units_codex_with_cursed_extras (1).json",
        "units.json",
    ]
    for c in candidates:
        p = os.path.join(script_dir, c)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

    # If not found, prompt for a file
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Select units JSON", script_dir, "JSON files (*.json)")
    if not path:
        QtWidgets.QMessageBox.critical(None, APP_TITLE, "No JSON file selected.")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_units(data: Dict[str,Any]) -> List[UnitDef]:
    units: List[UnitDef] = []
    for obj in data.get("units", []):
        name = obj.get("name","").strip()
        faction = obj.get("faction", "codex").lower()
        section = obj.get("section","").strip()
        base = obj.get("base", {})
        base_min = int(base.get("min", 1))
        base_max = int(base.get("max", 1))
        per_model = base.get("per_model_points")
        per_model = int(per_model) if per_model is not None else None
        fixed_points = base.get("fixed_points")
        fixed_points = int(fixed_points) if fixed_points is not None else None

        consumes_slot = bool(obj.get("consumes_slot", True))
        requires_qualifying_hq = bool(obj.get("requires_qualifying_hq", False))
        hq_exclusions = obj.get("hq_exclusions", [])

        # 0-1 logic: either explicit, or known names/patterns, or "limit":"0-1"
        limit_0_1 = False
        if obj.get("limit_fixed") and str(obj.get("limit")).startswith("0-1"):
            limit_0_1 = True
        if name in ZERO_ONE_NAMES:
            limit_0_1 = True
        if name == "Land Raider Crusader":
            limit_0_1 = True

        # Option groups (we only fully wire 'transport' and 'toggle' for MVP)
        groups: List[OptionGroup] = []
        for g in obj.get("groups", []):
            gid = g.get("id")
            gtype = g.get("type")
            glabel = g.get("label", gid)
            og = OptionGroup(id=gid, label=glabel, type=gtype, limit_total=g.get("limit_total"), requires=g.get("requires"))
            if gtype == "toggle":
                og.points = int(g.get("points", 0)) if g.get("points") is not None else None
            items = []
            for it in g.get("items", []):
                items.append(OptionChoice(
                    id=str(it.get("id")),
                    label=str(it.get("label")),
                    points=int(it.get("points", 0)) if it.get("points") not in (None, "") else 0,
                    max_models=it.get("max_models"),
                ))
            og.items = items
            groups.append(og)

        units.append(UnitDef(
            name=name,
            faction=faction,
            section=section,
            base_min=base_min,
            base_max=base_max,
            per_model=per_model,
            fixed_points=fixed_points,
            limit_0_1=limit_0_1,
            consumes_slot=consumes_slot,
            requires_qualifying_hq=requires_qualifying_hq,
            hq_exclusions=hq_exclusions,
            option_groups=groups,
            cursed_extra_points=obj.get("cursed_extra_points", {}),
        ))
    return units

# --- Utility: sorting and section maps --------------------------------------
def sort_key_for_unit(u: UnitDef) -> Tuple[int,int,int,str]:
    sec_ord = SECTIONS_ORDER.index(u.section) if u.section in SECTIONS_ORDER else 99
    custom = CUSTOM_ORDER.get(u.section, [])
    try:
        pos = custom.index(u.name)
    except ValueError:
        pos = 1000
        # Fine-tune tank order in Heavy if not specified
        if u.section == "Heavy":
            if u.name == "Land Raider": pos = 900
            if u.name == "Land Raider Crusader": pos = 999
    # Units with 0-1 mark should appear after their peers (except Emperor's Champion which is specified)
    penalty = 5 if u.limit_0_1 and u.name not in ("Emperor's Champion",) else 0
    return (sec_ord, pos, penalty, u.name)

def points_label_for_unit(u: UnitDef) -> str:
    if u.fixed_points is not None:
        return f"{u.fixed_points} pts"
    if u.per_model is not None:
        base = u.base_min * u.per_model
        return f"{base}/{u.per_model}"
    return "—"

# --- Roster / Rules engine ---------------------------------------------------
class RosterState:
    def __init__(self) -> None:
        self.items: List[RosterItem] = []
        self.points_cap = POINTS_CAP_DEFAULT
        self.detachments = 1

    # Counts including "consumes_slot" only.
    def slots_used(self) -> Dict[str,int]:
        out = {s:0 for s in SECTIONS_ORDER}
        for it in self.items:
            if it.unit.consumes_slot:
                out[it.unit.section] += 1
        return out

    def qualifying_hq_count(self) -> int:
        # HQ used that grant Command Squad (i.e., not Emperor's Champion)
        count = 0
        for it in self.items:
            if it.unit.section == "HQ" and it.unit.consumes_slot:
                if it.unit.name not in ("Emperor's Champion", "Command Squad"):
                    count += 1
        return count

    def command_squad_count(self) -> int:
        return sum(1 for it in self.items if it.unit.name == "Command Squad")

    def zero_one_present(self, name: str) -> bool:
        return any(it.unit.name == name for it in self.items)

    def has_grey_knight(self) -> bool:
        return any(it.faction == "heroes" and it.unit.name.lower().startswith("grey") for it in self.items)

    def has_deathwatch(self) -> bool:
        return any(it.faction == "deathwatch" for it in self.items)

    def has_non_lotd_cursed(self) -> bool:
        for it in self.items:
            if it.faction == "cursed" and (it.cursed_chapter or "") != "Legion of the Damned":
                return True
        return False

    def cursed_allowed_max(self) -> int:
        # Doc rule:
        # Each non‑cursed Troop selection enables 1 cursed selection.
        # But if any Troop from Cursed is present → allowance = 1 (and likely consumed).
        troop_non_cursed = sum(1 for it in self.items if it.unit.section=="Troop" and it.faction!="cursed" and it.unit.consumes_slot)
        any_cursed_troop = any(it.unit.section=="Troop" and it.faction=="cursed" for it in self.items)
        if any_cursed_troop:
            return 1
        return troop_non_cursed

    def cursed_used(self) -> int:
        return sum(1 for it in self.items if it.faction=="cursed")

    def total_points(self) -> int:
        return sum(it.total_points() for it in self.items)

    def can_add(self, u: UnitDef, faction: str, cursed_chapter: Optional[str]) -> Tuple[bool,str]:
        # Exclusions
        if faction == "heroes":
            # GK exclude Deathwatch & non‑LotD Cursed
            if self.has_deathwatch() or self.has_non_lotd_cursed():
                return False, "Grey Knights exclude Deathwatch and Cursed (except Legion of the Damned)."
        if faction == "deathwatch":
            if self.has_grey_knight() or self.has_non_lotd_cursed():
                return False, "Deathwatch exclude Grey Knights and non‑LotD Cursed."
        if faction == "cursed":
            # If non‑LotD while GK or Deathwatch present → block
            if (cursed_chapter or "") != "Legion of the Damned":
                if self.has_grey_knight() or self.has_deathwatch():
                    return False, "Cursed (non‑LotD) exclude Grey Knights and Deathwatch."

            # Only allow specific units
            if u.name not in CURSED_ALLOWED:
                return False, "This unit is not available in Cursed."
            if CURSED_ALLOWED[u.name] and self.zero_one_present(u.name) and any(it.faction=="cursed" and it.unit.name==u.name for it in self.items):
                return False, "0–1 in Cursed."

            # Allowance
            max_cursed = self.cursed_allowed_max()
            if self.cursed_used() >= max_cursed:
                return False, f"Cursed limit reached ({self.cursed_used()}/{max_cursed})."

        # Zero‑one checks
        if u.limit_0_1 and self.zero_one_present(u.name):
            return False, "0–1 unit already selected."

        # Command Squad gating
        if u.name == "Command Squad":
            if self.qualifying_hq_count() == 0:
                return False, "Requires a qualifying HQ (not Emperor's Champion)."
            # One CS per qualifying HQ
            if self.command_squad_count() >= self.qualifying_hq_count():
                return False, "Max one Command Squad per qualifying HQ."

        # Category slot caps
        used = self.slots_used()
        lo, hi = SLOT_LIMITS.get(u.section, (0,99))
        add = 1 if u.consumes_slot else 0
        if used[u.section] + add > hi:
            return False, f"{u.section} cap exceeded."
        # Enforce minimums at export, not add-time.

        # Points cap (soft): allow adding but warn if exceeding.
        if self.total_points() + (u.fixed_points or (u.per_model or 0)*u.base_min) > self.points_cap + 400:
            # hard stop if too crazy over cap
            return False, "Points would exceed cap too much."

        return True, ""

# --- Qt Widgets --------------------------------------------------------------
class TopBar(QtWidgets.QWidget):
    resetRequested = QtCore.pyqtSignal()
    exportRequested = QtCore.pyqtSignal()
    settingsRequested = QtCore.pyqtSignal()

    def __init__(self, roster: RosterState):
        super().__init__()
        self.roster = roster
        self.setObjectName("TopBar")
        self.brand = QtWidgets.QLabel("SM Army Builder")
        self.brand.setObjectName("Brand")

        self.lblTotal = QtWidgets.QLabel()
        self.pills = {
            "HQ": QtWidgets.QLabel(),
            "Elite": QtWidgets.QLabel(),
            "Troop": QtWidgets.QLabel(),
            "Fast": QtWidgets.QLabel(),
            "Heavy": QtWidgets.QLabel(),
            "Cursed": QtWidgets.QLabel(),
        }
        pillBox = QtWidgets.QHBoxLayout()
        pillBox.setSpacing(6)
        pillBox.addWidget(self.lblTotal)
        for k in ["HQ","Elite","Troop","Fast","Heavy","Cursed"]:
            pillBox.addWidget(self.pills[k])
        pillBox.addStretch(1)

        self.btnSettings = QtWidgets.QPushButton("Settings")
        self.btnReset = QtWidgets.QPushButton("Reset")
        self.btnExport = QtWidgets.QPushButton("Export .txt")
        self.btnReset.clicked.connect(self.resetRequested.emit)
        self.btnExport.clicked.connect(self.exportRequested.emit)
        self.btnSettings.clicked.connect(self.settingsRequested.emit)

        row = QtWidgets.QHBoxLayout(self)
        row.addWidget(self.brand)
        row.addLayout(pillBox, 1)
        row.addWidget(self.btnSettings)
        row.addWidget(self.btnReset)
        row.addWidget(self.btnExport)
        self.update_pills()

    def update_pills(self):
        used = self.roster.slots_used()
        def fmt(k):
            lo, hi = SLOT_LIMITS[k]
            return f"{k}  <b>{used[k]}/{hi}</b>"
        self.lblTotal.setText(f"<span class='pill total'><b>{self.roster.total_points()}/{self.roster.points_cap}</b></span>")
        for k in ["HQ","Elite","Troop","Fast","Heavy"]:
            self.pills[k].setText(f"<span class='pill'>{fmt(k)}</span>")
        # Cursed uses dynamic allowance
        cmax = self.roster.cursed_allowed_max()
        self.pills["Cursed"].setText(f"<span class='pill'>Cursed <b>{self.roster.cursed_used()}/{cmax}</b></span>")

class UnitRow(QtWidgets.QFrame):
    addRequested = QtCore.pyqtSignal(object, str)  # UnitDef, faction

    def __init__(self, unit: UnitDef, faction: str, show_zero_one: bool):
        super().__init__()
        self.unit = unit
        self.faction = faction
        self.setObjectName("UnitRow")
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(10,8,10,8)

        left = QtWidgets.QVBoxLayout()
        name = QtWidgets.QLabel(unit.name)
        name.setObjectName("UnitName")
        sub = QtWidgets.QLabel(self._sub_label(show_zero_one))
        sub.setObjectName("UnitSub")
        left.addWidget(name)
        left.addWidget(sub)

        right = QtWidgets.QHBoxLayout()
        pts = QtWidgets.QLabel(points_label_for_unit(unit))
        pts.setObjectName("Badge")
        self.btn = QtWidgets.QPushButton("+")
        self.btn.setObjectName("AddOK")
        self.btn.clicked.connect(lambda: self.addRequested.emit(unit, faction))
        right.addWidget(pts)
        right.addWidget(self.btn)

        lay.addLayout(left, 1)
        lay.addLayout(right)

    def _sub_label(self, show_zero_one: bool) -> str:
        s = self.unit.section
        if show_zero_one and self.unit.limit_0_1:
            s += " 0–1"
        return s

    def setDisabledAdd(self, disabled: bool, reason: str = ""):
        self.btn.setDisabled(disabled)
        if disabled:
            self.btn.setObjectName("AddNO")
            self.setToolTip(reason or "Not allowed.")
        else:
            self.btn.setObjectName("AddOK")
            self.setToolTip("")

class RosterItemWidget(QtWidgets.QFrame):
    removeRequested = QtCore.pyqtSignal(object)  # RosterItem
    totalsChanged = QtCore.pyqtSignal()

    def __init__(self, item: RosterItem):
        super().__init__()
        self.item = item
        self.setObjectName("RosterItem")
        lay = QtWidgets.QVBoxLayout(self)
        head = QtWidgets.QHBoxLayout()

        self.btnCollapse = QtWidgets.QToolButton()
        self.btnCollapse.setText("▾")
        self.btnCollapse.setCheckable(True)
        self.btnCollapse.setChecked(True)

        title = QtWidgets.QLabel(self.item.display_name())
        title.setObjectName("RiTitle")
        sub = QtWidgets.QLabel(f"{self.item.total_points()} pts")
        sub.setObjectName("RiSub")

        head_left = QtWidgets.QHBoxLayout()
        head_left.addWidget(self.btnCollapse)
        head_left.addWidget(title)
        head_left.addStretch(1)

        head_right = QtWidgets.QHBoxLayout()
        head_right.addWidget(sub)
        self.lblSub = sub

        btnX = QtWidgets.QPushButton("×")
        btnX.setObjectName("RemoveX")
        btnX.clicked.connect(lambda: self.removeRequested.emit(self.item))
        head_right.addWidget(btnX)

        head.addLayout(head_left, 1)
        head.addLayout(head_right)
        lay.addLayout(head)

        # Body (collapsible)
        self.body = QtWidgets.QWidget()
        bodyLay = QtWidgets.QVBoxLayout(self.body)

        # Model qty (if variable)
        if self.item.unit.fixed_points is None and self.item.unit.per_model is not None and self.item.unit.base_max>self.item.unit.base_min:
            qtyRow = QtWidgets.QHBoxLayout()
            qtyRow.addWidget(QtWidgets.QLabel("Models:"))
            self.btnMinus = QtWidgets.QPushButton("−")
            self.btnPlus = QtWidgets.QPushButton("+")
            self.lblQty = QtWidgets.QLabel(str(self.item.models))
            self.btnMinus.clicked.connect(self.dec_models)
            self.btnPlus.clicked.connect(self.inc_models)
            qtyRow.addWidget(self.btnMinus)
            qtyRow.addWidget(self.lblQty)
            qtyRow.addWidget(self.btnPlus)
            qtyRow.addStretch(1)
            bodyLay.addLayout(qtyRow)

        # Transport group (exclusive radios)
        for g in self.item.unit.option_groups:
            if g.id == "transport" and g.type == "exclusive" and g.items:
                bodyLay.addWidget(QtWidgets.QLabel("Transport:"))
                self.transportGroup = QtWidgets.QButtonGroup(self)
                row = QtWidgets.QHBoxLayout()
                for opt in g.items:
                    rb = QtWidgets.QRadioButton(f"{opt.label} (+{opt.points})" if opt.points else opt.label)
                    rb.toggled.connect(self.tweak_transport_points)
                    self.transportGroup.addButton(rb)
                    self.transportGroup.setId(rb, g.items.index(opt))
                    row.addWidget(rb)
                bodyLay.addLayout(row)
                break

        lay.addWidget(self.body)
        self.btnCollapse.toggled.connect(lambda on: self.body.setVisible(on))

    def dec_models(self):
        if self.item.models > self.item.unit.base_min:
            self.item.models -= 1
            self.lblQty.setText(str(self.item.models))
            self.totalsChanged.emit()
            self.refresh_sub()

    def inc_models(self):
        if self.item.models < self.item.unit.base_max:
            self.item.models += 1
            self.lblQty.setText(str(self.item.models))
            self.totalsChanged.emit()
            self.refresh_sub()

    def tweak_transport_points(self):
        # Update selected transport choice and recompute points
        group_def = next((g for g in self.item.unit.option_groups if g.id=="transport"), None)
        if not group_def: return
        idx = self.sender().parent().parent()  # not reliable across layouts; instead traverse
        # Re-read buttons
        for btn in self.transportGroup.buttons():
            if btn.isChecked():
                i = self.transportGroup.id(btn)
                choice = group_def.items[i]
                self.item.selected_options["transport"] = {"type":"exclusive","choice":{"id":choice.id,"points":choice.points,"label":choice.label}}
                break
        self.totalsChanged.emit()
        self.refresh_sub()

    def refresh_sub(self):
        self.lblSub.setText(f"{self.item.total_points()} pts")

class RosterPanel(QtWidgets.QScrollArea):
    def __init__(self, roster: RosterState, topbar: TopBar):
        super().__init__()
        self.roster = roster
        self.topbar = topbar
        self.setWidgetResizable(True)
        self.content = QtWidgets.QWidget()
        self.setWidget(self.content)
        self.vbox = QtWidgets.QVBoxLayout(self.content)
        self.vbox.setContentsMargins(10,10,10,10)
        self.refresh()

    def refresh(self):
        # clear
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            w = item.widget()
            if w: w.setParent(None)

        # group by section
        groups: Dict[str, List[RosterItem]] = {s:[] for s in SECTIONS_ORDER}
        for it in self.roster.items:
            groups[it.unit.section].append(it)

        for sec in SECTIONS_ORDER:
            items = groups[sec]
            if not items: continue
            header = QtWidgets.QLabel(f"{sec} — {len(items)} selected")
            header.setObjectName("CatHead")
            self.vbox.addWidget(header)
            for rit in items:
                w = RosterItemWidget(rit)
                w.removeRequested.connect(self.remove_item)
                w.totalsChanged.connect(self.topbar.update_pills)
                w.totalsChanged.connect(self.refresh)  # update totals / points
                self.vbox.addWidget(w)

        if not any(groups.values()):
            empty = QtWidgets.QLabel("— empty —")
            empty.setAlignment(QtCore.Qt.AlignCenter)
            self.vbox.addWidget(empty)

        self.topbar.update_pills()

    def remove_item(self, item: RosterItem):
        self.roster.items.remove(item)
        self.refresh()

# --- Selection panel ---------------------------------------------------------
class SelectorPanel(QtWidgets.QScrollArea):
    def __init__(self, units: List[UnitDef], roster: RosterState, topbar: TopBar):
        super().__init__()
        self.all_units = units
        self.roster = roster
        self.topbar = topbar
        self.setWidgetResizable(True)
        self.content = QtWidgets.QWidget()
        self.setWidget(self.content)
        self.vbox = QtWidgets.QVBoxLayout(self.content)
        self.vbox.setContentsMargins(10,10,10,10)

    def show_tab(self, faction: str):
        # clear
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            w = item.widget()
            if w: w.setParent(None)

        # Filter units by faction
        units = [u for u in self.all_units if u.faction == faction]

        # Cursed: limit to allowed list
        show_zero_one = True
        if faction == "cursed":
            units = [u for u in units if u.name in CURSED_ALLOWED]
            show_zero_one = True

        # Sort by section and custom order
        units.sort(key=sort_key_for_unit)

        # Build grouped UI
        last_sec = None
        for u in units:
            if u.section != last_sec:
                head = QtWidgets.QLabel(f"{u.section}")
                head.setObjectName("CatHead")
                self.vbox.addWidget(head)
                last_sec = u.section
            row = UnitRow(u, faction, show_zero_one=True)
            row.addRequested.connect(self.try_add_unit)
            self.vbox.addWidget(row)

        # After constructing, evaluate which are disallowed (to grey out +)
        self.update_disabled_states()

    def update_disabled_states(self):
        for i in range(self.vbox.count()):
            w = self.vbox.itemAt(i).widget()
            if isinstance(w, UnitRow):
                ok, reason = self.roster.can_add(w.unit, w.faction, None)
                # For cursed, we cannot fully check until chapter is chosen; but we pre-check with None
                w.setDisabledAdd(not ok, reason)

    def try_add_unit(self, unit: UnitDef, faction: str):
        cursed_chapter = None
        if faction == "cursed":
            # Ask for chapter in a simple dialog (2x3 grid)
            cursed_chapter = self.pick_cursed_chapter()
            if not cursed_chapter:
                return

        ok, reason = self.roster.can_add(unit, faction, cursed_chapter)
        if not ok:
            QtWidgets.QMessageBox.information(self, "Cannot add", reason)
            return

        models = unit.base_min if unit.per_model is not None else 1
        item = RosterItem(unit=unit, models=models, faction=faction, cursed_chapter=cursed_chapter)
        self.roster.items.append(item)
        self.topbar.update_pills()
        self.update_disabled_states()

    def pick_cursed_chapter(self) -> Optional[str]:
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Choose Cursed Chapter")
        grid = QtWidgets.QGridLayout(dlg)
        grid.setContentsMargins(10,10,10,10)
        selected = {"name": None}

        def choose(name):
            selected["name"] = name
            dlg.accept()

        # 2x3 matrix
        for idx, name in enumerate(CURSED_CHAPTERS):
            btn = QtWidgets.QPushButton(name)
            btn.clicked.connect(lambda _=False, n=name: choose(n))
            r = idx // 3; c = idx % 3
            grid.addWidget(btn, r, c)

        btnCancel = QtWidgets.QPushButton("Cancel")
        btnCancel.clicked.connect(dlg.reject)
        grid.addWidget(btnCancel, 2, 0, 1, 3)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            return selected["name"]
        return None

# --- Settings dialog ---------------------------------------------------------
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, roster: RosterState):
        super().__init__()
        self.roster = roster
        self.setWindowTitle("Settings")
        form = QtWidgets.QFormLayout(self)
        self.spinCap = QtWidgets.QSpinBox()
        self.spinCap.setRange(0, 99999)
        self.spinCap.setSingleStep(50)
        self.spinCap.setValue(self.roster.points_cap)
        form.addRow("Army Points Limit:", self.spinCap)

        self.spinDet = QtWidgets.QSpinBox()
        self.spinDet.setRange(1, 3)
        self.spinDet.setValue(self.roster.detachments)
        form.addRow("Detachments:", self.spinDet)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)

    def accept(self):
        self.roster.points_cap = int(self.spinCap.value())
        self.roster.detachments = int(self.spinDet.value())
        super().accept()

# --- Main window -------------------------------------------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data: Dict[str,Any]):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 720)

        self.units = build_units(data)
        self.roster = RosterState()

        # Top bar
        self.top = TopBar(self.roster)
        self.top.resetRequested.connect(self.reset_all)
        self.top.exportRequested.connect(self.export_txt)
        self.top.settingsRequested.connect(self.open_settings)
        topWrap = QtWidgets.QWidget()
        topLay = QtWidgets.QVBoxLayout(topWrap)
        topLay.addWidget(self.top)

        # Tabs + selectors
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.North)
        # Order of tabs
        self.selector = SelectorPanel(self.units, self.roster, self.top)
        self.tabs.addTab(self.selector, "Codex")
        self.selector_heroes = SelectorPanel(self.units, self.roster, self.top)
        self.tabs.addTab(self.selector_heroes, "Heroes")
        self.selector_dw = SelectorPanel(self.units, self.roster, self.top)
        self.tabs.addTab(self.selector_dw, "Deathwatch")
        self.selector_cursed = SelectorPanel(self.units, self.roster, self.top)
        self.tabs.addTab(self.selector_cursed, "Cursed")
        self.selector_damned = SelectorPanel(self.units, self.roster, self.top)
        self.tabs.addTab(self.selector_damned, "Damned")
        self.tabs.currentChanged.connect(self.refresh_tab)

        left = QtWidgets.QWidget()
        leftLay = QtWidgets.QVBoxLayout(left)
        leftLay.addWidget(self.tabs)

        # Roster panel (right)
        self.rosterPanel = RosterPanel(self.roster, self.top)

        # Split
        split = QtWidgets.QSplitter()
        split.setOrientation(QtCore.Qt.Horizontal)
        split.addWidget(left)
        split.addWidget(self.rosterPanel)
        split.setStretchFactor(0, 1)  # left 1
        split.setStretchFactor(1, 2)  # right 2

        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)
        v.addWidget(topWrap)
        v.addWidget(split, 1)
        self.setCentralWidget(central)

        # Initial tab views
        self.selector.show_tab("codex")
        self.selector_heroes.show_tab("heroes")
        self.selector_dw.show_tab("deathwatch")
        self.selector_cursed.show_tab("cursed")
        self.selector_damned.show_tab("damned")

        # Style
        self.setStyleSheet(self._qss())

    def refresh_tab(self, idx: int):
        # re-evaluate disabled "+" buttons on tab switch
        w = self.tabs.widget(idx)
        if isinstance(w, SelectorPanel):
            w.update_disabled_states()
        self.rosterPanel.refresh()

    def reset_all(self):
        self.roster.items.clear()
        self.rosterPanel.refresh()
        for w in (self.selector, self.selector_heroes, self.selector_dw, self.selector_cursed, self.selector_damned):
            w.update_disabled_states()

    def export_txt(self):
        # Ensure minimums
        used = self.roster.slots_used()
        mins_ok = all(used[k] >= SLOT_LIMITS[k][0] for k in SLOT_LIMITS)
        if not mins_ok:
            QtWidgets.QMessageBox.information(self, "Invalid army", "Minimum slot requirements not met.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export roster", "roster.txt", "Text files (*.txt)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.render_roster_text())
        QtWidgets.QMessageBox.information(self, "Exported", f"Saved to:\n{path}")

    def render_roster_text(self) -> str:
        lines = [f"{APP_TITLE} — {self.roster.total_points()} pts (cap {self.roster.points_cap})", ""]
        groups: Dict[str,List[RosterItem]] = {s:[] for s in SECTIONS_ORDER}
        for it in self.roster.items:
            groups[it.unit.section].append(it)
        for sec in SECTIONS_ORDER:
            items = groups[sec]
            if not items: continue
            lines.append(f"{sec}:")
            for it in items:
                lines.append(f"  - {it.display_name()} — {it.total_points()} pts (models {it.models})")
            lines.append("")
        return "\n".join(lines)

    def open_settings(self):
        dlg = SettingsDialog(self.roster)
        if dlg.exec_():
            self.top.update_pills()

    def _qss(self) -> str:
        # Dark style roughly matching the screenshot / HTML
        return """
        QWidget { background: #0e1116; color: #e6ebf2; font-family: Segoe UI, Roboto, Arial; }
        #TopBar { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #151a23F7, stop:1 #151a23E6); border-bottom: 1px solid #29303b; padding: 8px; }
        #Brand { font-weight: 800; }
        QLabel { font-size: 13px; }
        QTabBar::tab { padding: 8px 12px; background: #111624; color: #a7afbc; border-right: 1px solid #29303b; font-weight: 800; }
        QTabBar::tab:selected { background: #0f1421; color: #e6ebf2; }
        QSplitter::handle { background: #151a23; width: 6px; }
        QPushButton { background: #111522; color: #fff; border: 1px solid #29303b; border-radius: 6px; padding: 6px 10px; font-weight: 600; }
        QPushButton:hover { border-color: #3a4252; }
        QPushButton#RemoveX { background: rgba(220,53,69,.15); border-color: rgba(220,53,69,.45); color: #f6b2b9; font-size: 16px; width: 32px; height: 32px; border-radius: 16px; }
        QPushButton#AddOK { background: rgba(46,160,67,.15); border-color: rgba(46,160,67,.35); color: #90e6a8; font-weight: 900; font-size: 18px; width: 40px; height: 40px; border-radius: 20px; }
        QPushButton#AddNO { background: rgba(220,53,69,.15); border-color: rgba(220,53,69,.45); color: #f6b2b9; font-weight: 900; font-size: 18px; width: 40px; height: 40px; border-radius: 20px; }
        #CatHead { background: #0f1421; border: 1px solid #29303b; border-radius: 6px; padding: 6px 8px; color: #cfd6e6; font-weight: 700; margin: 6px 0 4px 0; }
        QFrame#UnitRow { background: #121826; border: 1px solid #29303b; border-radius: 9px; margin: 6px 0; }
        QLabel#UnitName { font-weight: 800; }
        QLabel#UnitSub { color: #a7afbc; }
        QLabel#Badge { background: #0e1422; border: 1px solid #29303b; padding: 4px 10px; border-radius: 999px; color: #cfe4ff; font-weight: 700; }
        QFrame#RosterItem { background: #111725; border: 1px solid #29303b; border-radius: 9px; padding: 6px 8px; }
        QLabel#RiTitle { font-weight: 800; }
        QLabel#RiSub { color: #cfe4ff; font-weight: 700; }
        """

# --- App bootstrap -----------------------------------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    data = load_json_from_default_locations()
    win = MainWindow(data)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
