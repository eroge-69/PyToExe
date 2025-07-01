#!/usr/bin/env python3
from __future__ import annotations

import sys
import pathlib
from typing import List, Tuple, Dict, Iterable

import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.backends.backend_pdf

Coord = Tuple[float, float]

# ───────────────────────────── constants ───────────────────────────
BASE_LINEWIDTH = 0.10  # thickness for LINE_WIDTH index 1
DEFAULT_COLOR = (0.0, 0.0, 0.0)

# ───────────────────────────── parsing ──────────────────────────────
class CGMState:
    def __init__(self):
        self.colour_table: Dict[int, Tuple[float, float, float]] = {0: DEFAULT_COLOR}
        self.current_colour_idx: int = 0
        self.current_lw_idx: int = 1

    def colour(self) -> Tuple[float, float, float]:
        return self.colour_table.get(self.current_colour_idx, DEFAULT_COLOR)

    def linewidth(self) -> float:
        return BASE_LINEWIDTH * max(self.current_lw_idx, 1)


def _read_params(it: Iterable[str], n: int) -> List[str]:
    out: List[str] = []
    while len(out) < n:
        try:
            out.extend(next(it).split())
        except StopIteration:
            break
    return out


def read_elements(path: pathlib.Path):
    """Yield (coords, colour, linewidth)."""
    st = CGMState()
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        lines = iter(fh)
        for line in lines:
            header = line.split()
            if len(header) != 5 or not all(tok.lstrip("-+").isdigit() for tok in header):
                continue
            cls, ident, n_int, n_real, n_str = map(int, header)
            params = _read_params(lines, n_int + n_real + n_str)

            # ---- attributes ----
            if cls == 2 and ident == 11:  # LINE_COLOUR
                if n_int >= 1:
                    try:
                        st.current_colour_idx = int(params[0])
                    except ValueError:
                        pass
                if n_real >= 3:
                    try:
                        r, g, b = map(float, params[n_int : n_int + 3])
                        st.colour_table[st.current_colour_idx] = (r, g, b)
                    except ValueError:
                        pass
                continue
            if cls == 2 and ident == 6:  # LINE_WIDTH
                if n_int >= 1:
                    try:
                        st.current_lw_idx = max(1, int(params[0]))
                    except ValueError:
                        pass
                continue

            # ---- polyline ----
            if cls == 1 and ident == 1 and n_real % 2 == 0 and n_real >= 2:
                real_params = params[n_int : n_int + n_real]
                coords: List[Coord] = []
                try:
                    for i in range(0, n_real, 2):
                        x = float(real_params[i])
                        y = float(real_params[i + 1])
                        coords.append((x, y))
                except ValueError:
                    continue
                if len(coords) >= 2:
                    yield coords, st.colour(), st.linewidth()
                continue
            # else: ignore other record types


# ─────────────────────────── rendering to PDF ───────────────────────

def draw_to_pdf(elements, pdf_path: pathlib.Path):
    if not elements:
        print("[WARN] Nessuna polilinea da disegnare.", file=sys.stderr)
	plt.style.use('grayscale')
    fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 portrait (approx.)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    # plot
    for coords, colour, lw in elements:
        xs, ys = zip(*coords)
        ax.plot(xs, ys, linewidth=lw, color=colour)

    # framing
    if elements:
        xs_all = [x for coords, *_ in elements for x, _ in coords]
        ys_all = [y for coords, *_ in elements for _, y in coords]
        margin_x = 0.05 * (max(xs_all) - min(xs_all)) or 0.01
        margin_y = 0.05 * (max(ys_all) - min(ys_all)) or 0.01
        ax.set_xlim(min(xs_all) - margin_x, max(xs_all) + margin_x)
        ax.set_ylim(min(ys_all) - margin_y, max(ys_all) + margin_y)

    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", transparent=True)
    plt.close(fig)


# ───────────────────────── entry‑point CLI ──────────────────────────

def usage():
    print("Uso: python cgm2pdf.py <input.txt> <output.pdf>")
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        usage()
    in_path = pathlib.Path(sys.argv[1]).expanduser()
    out_path = pathlib.Path(sys.argv[2]).expanduser()

    if not in_path.exists():
        print(f"[ERRORE] File non trovato: {in_path}", file=sys.stderr)
        sys.exit(2)

    elements = list(read_elements(in_path))
    draw_to_pdf(elements, out_path)
    print(f"✔️  Salvato PDF in {out_path}")


if __name__ == "__main__":
    main()
