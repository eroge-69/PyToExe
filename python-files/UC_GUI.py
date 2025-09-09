#!/usr/bin/env python
# coding: utf-8

import math
import logging
import tkinter as tk

try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError as e:
    print("Missing a required package. Please run:")
    print("    pip install numpy matplotlib")
    raise

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger().setLevel(logging.INFO)

# ---------------- Units ----------------
Weights = ["tonne", "kg", "g", "st", "lb", "oz"]
Distances = ["km", "m", "cm", "mm", "mi", "yd", "ft", "in"]
Volumes = ["m3", "l", "cc", "ml", "yd3", "ft3", "in3", "gal", "qt", "pt", "c", "floz", "tbsp", "tsp"]
Units = [Weights, Distances, Volumes]
Unittypes = ["Weights", "Distances", "Volumes"]
Weightsconv = [1000.0, 1000.0, 0.0001574730901, 14.0, 16.0]
Distancesconv = [1000.0, 100.0, 10.0, 0.0000006213711922, 1760.0, 3.0, 12.0]
Volumesconv = [1000.0, 1000.0, 1.0, 0.000001307950619, 27.0, 1728.0, 0.004329004329, 4.0, 2.0, 2.0, 8.0, 2.0, 3.0]
Conversions = [Weightsconv, Distancesconv, Volumesconv]

# ---------------- Functions ----------------
def sigfigs_str(string):
    if "." in string:
        digits = string.replace(".", "").lstrip("0")
    else:
        digits = string.lstrip("0")
    if not digits:
        return 0
    return len(digits)

def round_sf(x, sf):
    if x == 0:
        return 0
    return round(x, sf - int(math.floor(math.log10(abs(x))) + 1))

def floatconv(instr):
    decimal_seen = False
    for char in instr:
        if char.isdigit():
            continue
        elif char == '.':
            if decimal_seen:
                raise ValueError(f"Error: too many decimals in input '{instr}'")
            decimal_seen = True
        else:
            raise ValueError(f"Error: non-numerical character '{char}' in input '{instr}'")
    return float(instr)

def find(array, target, path=None, top=True):
    if path is None:
        path = []
    for i, item in enumerate(array):
        if isinstance(item, list):
            result = find(item, target, path + [i], top=False)
            if result is not None:
                return result
        elif item == target:
            path += [i]
            return path
    if top:
        return None  # return None instead of raising IndexError
    return None

def convert(invalstr, inunit, outunit):
    def cal(inval, inunitpos, outunitpos):
        fac = 1.0
        x = 0
        while x < abs(outunitpos[1] - inunitpos[1]):
            array = Conversions[inunitpos[0]]
            if inunitpos[1] < outunitpos[1]:
                fac *= array[inunitpos[1] + x]
            elif inunitpos[1] > outunitpos[1]:
                fac /= array[outunitpos[1] + x]
            x += 1
        return inval * fac

    inval = floatconv(invalstr)
    sigfig = max(sigfigs_str(invalstr), 3)
    inunitpos = find(Units, inunit)
    outunitpos = find(Units, outunit)

    if inunitpos is None or outunitpos is None:
        raise ValueError(f"Unit not found: '{inunit}' or '{outunit}'")
    if inunitpos[0] != outunitpos[0]:
        raise KeyError(f"Error: incompatible units '{inunit}' and '{outunit}'")
    elif inunitpos == outunitpos:
        outval = inval
    else:
        outval = round_sf(cal(inval, inunitpos, outunitpos), sigfig)

    return outval, sigfig

# ---------------- Main GUI ----------------
def main():
    root = tk.Tk()
    root.title("Unit Converter")
    root.resizable(False, False)

    # StringVars without traces initially
    unittypestr = tk.StringVar(value="Distances")
    inunitstr = tk.StringVar(value="m")
    outunitstr = tk.StringVar(value="ft")

    # Functions that rely on StringVars and menus
    def updateoptions(menu, string, options):
        menu = menu["menu"]
        menu.delete(0, "end")
        for option in options:
            menu.add_command(label=option, command=tk._setit(string, option))

    def typeonselection(*args):
        unittypepos = find(Unittypes, unittypestr.get())
        if unittypepos is None:
            return
        inoptions = Units[unittypepos[0]].copy()
        updateoptions(inmenu, inunitstr, inoptions)
        inunitstr.set(inoptions[0])
        outoptions = Units[unittypepos[0]].copy()
        updateoptions(outmenu, outunitstr, outoptions)
        outunitstr.set(outoptions[1])

    def inmenuonselection(*args):
        if inunitstr.get() == outunitstr.get():
            unittypepos = find(Unittypes, unittypestr.get())
            if unittypepos is None:
                return
            inoptions = Units[unittypepos[0]].copy()
            outoptions = Units[unittypepos[0]].copy()
            if find(inoptions, inunitstr.get())[0] == 0:
                outunitstr.set(outoptions[1])
            else:
                outunitstr.set(outoptions[0])

    def outmenuonselection(*args):
        if inunitstr.get() == outunitstr.get():
            unittypepos = find(Unittypes, unittypestr.get())
            if unittypepos is None:
                return
            inoptions = Units[unittypepos[0]].copy()
            outoptions = Units[unittypepos[0]].copy()
            if find(outoptions, outunitstr.get())[0] == 0:
                inunitstr.set(inoptions[1])
            else:
                inunitstr.set(inoptions[0])

    def calculate():
        invalstr = invalbox.get()
        inunit = inunitstr.get()
        outunit = outunitstr.get()
        try:
            newtxt, sigfig = convert(invalstr, inunit, outunit)
            outlabel.config(text=newtxt)
            sigfigval.config(text=sigfig)
        except Exception as e:
            outlabel.config(text=f"Error: {e}")
            sigfigval.config(text="-")

    # Widgets
    unittypelabel = tk.Label(root, text="Unit type:")
    unittypelabel.grid(row=0, column=0)
    unittypemenu = tk.OptionMenu(root, unittypestr, *Unittypes)
    unittypemenu.grid(row=0, column=1)

    invallabel = tk.Label(root, text="Value:")
    invallabel.grid(row=1, column=0)
    invalbox = tk.Entry(root)
    invalbox.grid(row=1, column=1)

    inmenulabel = tk.Label(root, text="From unit:")
    inmenulabel.grid(row=2, column=0)
    inmenu = tk.OptionMenu(root, inunitstr, *Distances)
    inmenu.grid(row=2, column=1)

    outmenulabel = tk.Label(root, text="To unit:")
    outmenulabel.grid(row=3, column=0)
    outmenu = tk.OptionMenu(root, outunitstr, *Distances)
    outmenu.grid(row=3, column=1)

    calcbutton = tk.Button(root, text="Calculate", command=calculate)
    calcbutton.grid(row=4, column=0)
    outlabel = tk.Label(root, text="")
    outlabel.grid(row=4, column=1)

    sigfigtxt = tk.Label(root, text="Significant figures round to:")
    sigfigtxt.grid(row=5, column=0)
    sigfigval = tk.Label(root, text="")
    sigfigval.grid(row=5, column=1)

    for widget in (unittypelabel, unittypemenu, invallabel, invalbox,
                   inmenulabel, inmenu, outmenulabel, outmenu,
                   calcbutton, outlabel, sigfigtxt, sigfigval):
        widget.grid_configure(padx=20, pady=20)

    # Attach trace callbacks AFTER menus and variables are fully initialized
    unittypestr.trace_add("write", typeonselection)
    inunitstr.trace_add("write", inmenuonselection)
    outunitstr.trace_add("write", outmenuonselection)

    root.mainloop()

if __name__ == "__main__":
    main()
