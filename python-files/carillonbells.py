import argparse
from datetime import date
from pathlib import Path
from random import choice
from time import sleep

import schedule
from playsound import playsound

# The hymns and chimes
ALL_HYMNS = list(Path("Hymns").resolve().glob("*.WAV"))
NINE_AM_CHIME_FILE = "tolls/WestminsterWithNine.wav"
TWELVE_PM_CHIME_FILE = "tolls/WestminsterWithTwelve.wav"
FIVE_PM_CHIME_FILE = "tolls/WestminsterWithFive.wav"
SINGLE_CHIME_FILE = "tolls/SingleChime.wav"


def play_9am():
    print(f"9am begin on {date.today().isoformat()}")

    # Play the 9am chimes
    playsound(NINE_AM_CHIME_FILE)
    print("9am Done!")


def play_12pm():
    print(f"Noon begin on {date.today().isoformat()}")

    # Play the Noon chimes
    playsound(TWELVE_PM_CHIME_FILE)

    # Randonly select a Hymn and play it
    playsound(choice(ALL_HYMNS).as_posix())
    print("Noon Done!")


def play_5pm():
    print(f"5pm begin on {date.today().isoformat()}")

    # Play the 5pm chimes
    playsound(FIVE_PM_CHIME_FILE)
    print("5pm Done!")


def play_single_chime():
    """Play a single chime."""
    playsound(SINGLE_CHIME_FILE)


def main():
    """Program entypoint."""
    # Set up an argument to allow us to play a single chime to test the system
    print("Carillon Program Open!")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Play a chime to ensure the system is working properly.",
    )
    args = parser.parse_args()

    # If the test argument was provided, play the test chime
    if args.test:
        play_single_chime()

    # Schedule the playback events using the schedule module
    else:
        print("Start scheduled chimes")
        schedule.every().day.at("09:00").do(play_9am)
        schedule.every().day.at("12:00").do(play_12pm)
        schedule.every().day.at("17:00").do(play_5pm)

        # Loop indefinitely to run the scheduled events
        while True:
            schedule.run_pending()
            sleep(1)


if __name__ == "__main__":
    main()
