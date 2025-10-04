#!/usr/bin/env python3
"""
Comet — small demo CLI tool with an ASCII comet animation, menu, and logging.
Intended to be built into an executable (e.g. comet.exe).
"""

import sys
import time
import argparse
import logging
from datetime import datetime
from shutil import get_terminal_size

__version__ = "1.0.0"
LOGFILE = "comet.log"


def setup_logging():
    logging.basicConfig(
        filename=LOGFILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def ascii_comet(duration=6.0, fps=20):
    """
    Draw a simple moving comet animation in the terminal for `duration` seconds.
    """
    cols = get_terminal_size((80, 20)).columns
    comet = "☄"
    tail = "~~~"
    total_frames = int(duration * fps)
    for frame in range(total_frames):
        t = frame / total_frames
        pos = int(t * max(0, cols - len(tail) - 4)) + 2
        line = " " * pos + comet + tail
        print("\r" + line[:cols], end="", flush=True)
        time.sleep(1.0 / fps)
    print()


def interactive_menu():
    print("Comet — small demo utility")
    print("=========================")
    print("1) Show comet animation")
    print("2) Version info")
    print("3) Show last 10 log lines")
    print("4) Quit")
    while True:
        choice = input("Choose 1-4: ").strip()
        if choice == "1":
            logging.info("User selected animation")
            ascii_comet()
        elif choice == "2":
            print(f"Comet version {__version__}")
            logging.info("Displayed version")
        elif choice == "3":
            show_last_logs(10)
        elif choice == "4":
            logging.info("Exiting from interactive menu")
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")


def show_last_logs(n=10):
    try:
        with open(LOGFILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("No log file found.")
        return
    print("--- last log lines ---")
    for line in lines[-n:]:
        print(line.rstrip())
    print("----------------------")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="comet", description="Comet — demo executable utility")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--animate", action="store_true", help="Run the comet animation and exit")
    parser.add_argument("--duration", type=float, default=6.0, help="Animation duration in seconds")
    parser.add_argument("--quiet", action="store_true", help="Minimize terminal output (still logs to file)")
    args = parser.parse_args(argv)

    setup_logging()
    logging.info("Comet started (pid=%d)", os_getpid_safe())

    if args.version:
        print(f"Comet version {__version__}")
        logging.info("Printed version and exited")
        return 0

    if args.animate:
        if args.quiet:
            ascii_comet(duration=args.duration, fps=25)
        else:
            ascii_comet(duration=args.duration)
        logging.info("Animation finished (duration=%s)", args.duration)
        return 0

    try:
        interactive_menu()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted — exiting.")
        logging.info("Interrupted by user")
    return 0


def os_getpid_safe():
    try:
        import os
        return os.getpid()
    except Exception:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
