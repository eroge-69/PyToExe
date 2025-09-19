import math
import sys
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

G = 9.81

def trace_func(time: np.ndarray, velocity: float, alpha: float) -> Tuple[np.ndarray, np.ndarray]:
    v_0x = velocity * math.cos(alpha)
    v_0y = velocity * math.sin(alpha)
    x = v_0x * time
    y = v_0y * time - G * time ** 2 / 2.0
    return x, y


def seen_by_rls(x: float, y: float, x_rls: float) -> bool:
    dx = x - x_rls
    rho = math.hypot(dx, y)
    if rho == 0:
        return False
    gamma = math.atan2(y, abs(dx))
    return math.radians(5.0) <= gamma <= math.radians(40.0)


def split_segments(x_arr: np.ndarray, y_arr: np.ndarray, mask: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
    segments: List[Tuple[np.ndarray, np.ndarray]] = []
    start = None
    n = len(mask)
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        is_last = (i == n - 1)
        if (not m or is_last) and start is not None:
            end = i + 1 if (m and is_last) else i
            if end - start >= 2:
                segments.append((x_arr[start:end], y_arr[start:end]))
            start = None
    return segments


def compute_launch_params(height: float, velocity: float, beta_rad: float) -> Tuple[float, float, float, float, float]:
    v_y = velocity * math.sin(beta_rad)
    v_0x = velocity * math.cos(beta_rad)
    h_max_relative = (velocity ** 2) * (math.sin(beta_rad) ** 2) / (2.0 * G)
    h_max = h_max_relative + height
    v_0y = math.sqrt(max(h_max * 2.0 * G, 0.0))
    v0 = math.hypot(v_0x, v_0y)
    alpha = math.atan2(v_0y, v_0x)
    t_max = 2.0 * v_0y / G if G > 0 else 0.0
    return v0, alpha, v_0x, v_y, t_max


def plot_with_sliders() -> None:
    # Defaults
    init_height = 3500.0
    init_velocity = 200.0
    init_angle_deg = 66.0
    init_x_rls = 6000.0

    # Figure and axes layout
    fig, ax = plt.subplots(figsize=(13, 8))
    plt.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.22)

    # Slider axes
    ax_height = plt.axes([0.08, 0.14, 0.40, 0.03])
    ax_velocity = plt.axes([0.08, 0.10, 0.40, 0.03])
    ax_angle = plt.axes([0.08, 0.06, 0.40, 0.03])
    ax_xrls = plt.axes([0.58, 0.14, 0.34, 0.03])
    ax_time = plt.axes([0.58, 0.10, 0.34, 0.03])

    # Sliders
    s_height = Slider(ax_height, 'Высота, м', 0.0, 10000.0, valinit=init_height, valstep=50.0)
    s_velocity = Slider(ax_velocity, 'Скорость, м/с', 10.0, 2000.0, valinit=init_velocity, valstep=5.0)
    s_angle = Slider(ax_angle, 'Угол, °', 1.0, 89.0, valinit=init_angle_deg, valstep=1.0)
    s_xrls = Slider(ax_xrls, 'РЛС x, м', 0.0, 20000.0, valinit=init_x_rls, valstep=50.0)
    s_time = Slider(ax_time, 't, с', 0.0, 1.0, valinit=0.0, valstep=0.01)

    # Artists containers
    green_lines: List[any] = []
    red_lines: List[any] = []
    rls_lines: List[any] = []
    rls_point = None
    impact_point = None
    current_point = None

    def recompute_and_draw(_=None):
        nonlocal rls_point, impact_point, current_point
        # Read values
        height = float(s_height.val)
        velocity = float(s_velocity.val)
        beta = math.radians(float(s_angle.val))
        x_rls = float(s_xrls.val)

        # Compute trajectory
        v0, alpha, v_0x, v_y, t_max = compute_launch_params(height, velocity, beta)
        # Update time slider max/step
        new_max = max(t_max, 0.01)
        if abs(s_time.valmax - new_max) > 1e-9:
            s_time.valmax = new_max
            s_time.ax.set_xlim(s_time.valmin, s_time.valmax)
        s_time.valstep = max(new_max / 200.0, 0.01)
        if s_time.val > s_time.valmax:
            s_time.set_val(s_time.valmax)

        t = np.linspace(0.0, max(t_max, 1e-6), 1000)
        X, Y = trace_func(t, v0, alpha)

        # Masks and segments
        mask_in = np.array([seen_by_rls(float(xi), float(yi), x_rls) for xi, yi in zip(X, Y)], dtype=bool)
        mask_out = ~mask_in
        green_segments = split_segments(X, Y, mask_in)
        red_segments = split_segments(X, Y, mask_out)

        # Clear old artists
        for ln in green_lines:
            ln.remove()
        green_lines.clear()
        for ln in red_lines:
            ln.remove()
        red_lines.clear()
        for ln in rls_lines:
            ln.remove()
        rls_lines.clear()
        if rls_point is not None:
            rls_point.remove()
            rls_point = None
        if impact_point is not None:
            impact_point.remove()
            impact_point = None
        if current_point is not None:
            current_point.remove()
            current_point = None

        # Draw segments
        for xs, ys in green_segments:
            (ln,) = ax.plot(xs, ys, color="green", linewidth=3, label="обнаружение РЛС")
            green_lines.append(ln)
        for xs, ys in red_segments:
            (ln,) = ax.plot(xs, ys, color="red", linewidth=1.5, label="вне сектора")
            red_lines.append(ln)

        # Impact point
        x_impact = (v0 * math.cos(alpha)) * t_max
        impact_in_sector = seen_by_rls(float(x_impact), 0.0, x_rls)
        impact_point = ax.scatter([x_impact], [0.0], color=("green" if impact_in_sector else "red"), s=80, marker="x", zorder=5, label="точка падения")

        # Current point at s_time
        t_cur = float(s_time.val)
        x_cur, y_cur = trace_func(np.array([t_cur]), v0, alpha)
        x_cur, y_cur = float(x_cur[0]), float(y_cur[0])
        current_point = ax.scatter([x_cur], [y_cur], color="blue", s=60, marker="o", facecolors='none', linewidths=2, zorder=6, label="БР (текущая)")

        # RLS point
        rls_point = ax.scatter([x_rls], [0.0], color="black", s=70, marker="^", zorder=6, label="РЛС")

        # RLS sector boundary lines
        max_x = float(np.max(X)) if X.size else 1.0
        max_y = float(np.max(Y)) if Y.size else 1.0
        extent = max(max_x - x_rls, x_rls - float(np.min(X)) if X.size else 0.0, max_y)
        for sign in (-1, 1):
            for ang in (5.0, 40.0):
                theta = math.radians(ang)
                dx = sign * extent
                x_line = np.array([x_rls, x_rls + dx])
                y_line = np.array([0.0, math.tan(theta) * abs(dx)])
                (ln,) = ax.plot(x_line, y_line, linestyle=":", color=(0, 0, 0, 0.5))
                rls_lines.append(ln)

        # Axes, limits, legend
        ax.set_title("Траектория полёта и сектор РЛС")
        ax.set_xlabel("Дальность (x), м")
        ax.set_ylabel("Высота (y), м")
        ax.grid(True, alpha=0.3)
        # Compute right x limit automatically
        x_limit = max(float(np.max(X)) if X.size else 1000.0, x_rls + extent)
        ax.set_xlim(0.0, x_limit * 1.02)
        # Adjust Y if needed
        ymin, ymax = ax.get_ylim()
        if ymax < max_y * 1.05:
            ax.set_ylim(ymin, max_y * 1.05)

        # Deduplicate legend
        handles, labels = ax.get_legend_handles_labels()
        uniq = {}
        for h, l in zip(handles, labels):
            if l not in uniq:
                uniq[l] = h
        if uniq:
            ax.legend(uniq.values(), uniq.keys(), loc="upper right")

        fig.canvas.draw_idle()

    # Bind updates
    s_height.on_changed(recompute_and_draw)
    s_velocity.on_changed(recompute_and_draw)
    s_angle.on_changed(recompute_and_draw)
    s_xrls.on_changed(recompute_and_draw)
    s_time.on_changed(recompute_and_draw)

    # Initial draw
    recompute_and_draw()
    plt.show()


def read_float(prompt: str, default: float) -> float:
    # Сохранено для обратной совместимости, не используется в режимe со слайдерами
    return default


def main() -> None:
    try:
        plot_with_sliders()
    except Exception as exc:
        print("Ошибка отрисовки:", exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


