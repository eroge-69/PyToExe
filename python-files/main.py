import logging
from argparse import ArgumentParser
from math import ceil
from pathlib import Path
from sys import stdout, stderr

from mido import MidiFile

parser = ArgumentParser(description="Turns a MIDI file into a lot of "
                                    "TypeScript code for MakeCode Arcade!")
parser.add_argument("path", type=Path,
                    help="The path to the MIDI file. ")
parser.add_argument("--output_path", "-p", type=Path,
                    default=None, help="The path to write the code to.")
parser.add_argument("--stdout", "-s", action="store_true",
                    help="Whether to output everything to standard output "
                         "instead of writing to a file. ")
parser.add_argument("--debug", "-d", action="store_true",
                    help="Whether to log debug messages or not. ")
args = parser.parse_args()

in_path = args.path.expanduser().resolve()
out_path = args.output_path
debug = args.debug
to_stdout = args.stdout
if out_path is None:
    # Put output file in the same directory as input file with same name
    # but with different extension
    out_path = in_path.parent / (in_path.stem + ".txt")


def create_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    A simple function to create a logger. You would typically put this right
    under all the other modules you imported.
    And then call `logger.debug()`, `logger.info()`, `logger.warning()`,
    `logger.error()`, `logger.critical()`, and
    `logger.exception` everywhere in that module.
    :param name: A string with the logger name.
    :param level: A integer with the logger level. Defaults to logging.DEBUG.
    :return: A logging.Logger which you can use as a regular logger.
    """
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)
    logger.propagate = False

    console_formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                          "%(levelname)s - %(message)s")

    # https://stackoverflow.com/a/16066513/10291933
    stdout_handler = logging.StreamHandler(stream=stdout)
    stdout_handler.setLevel(level=level)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    stdout_handler.setFormatter(fmt=console_formatter)
    if stdout_handler not in logger.handlers:
        logger.addHandler(hdlr=stdout_handler)

    stderr_handler = logging.StreamHandler(stream=stderr)
    stderr_handler.setLevel(level=logging.WARNING)
    stderr_handler.setFormatter(fmt=console_formatter)
    if stderr_handler not in logger.handlers:
        logger.addHandler(hdlr=stderr_handler)

    logger.debug(f"Created logger named {repr(name)} with level {repr(level)}")
    logger.debug(f"Handlers for {repr(name)}: {repr(logger.handlers)}")
    return logger


if to_stdout:
    level = logging.WARNING
elif debug:
    level = logging.DEBUG
else:
    level = logging.INFO
logger = create_logger(__name__, level=level)

logger.info(f"Parsing {in_path}")
midi = MidiFile(in_path)

if midi.type not in (0, 1):
    raise ValueError(f"MIDI file not type 0 or type 1!")

logger.debug(f"MIDI file type: {midi.type}")

# Generate all MIDI messages in playback order
# This will squish all tracks together
msgs = tuple(midi)


def note_num_to_name(num: int) -> str:
    # https://stackoverflow.com/a/54546263/10291933
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    octave = ceil(num / 12)
    name = notes[num % 12]
    return name + str(octave)


# https://gist.github.com/CGrassin/26a1fdf4fc5de788da9b376ff717516e
# MIT License
# Python to convert a string note (eg. "A4") to a frequency (eg. 440).
# Inspired by https://gist.github.com/stuartmemo/3766449
def get_frequency(note: str, A4: int = 440) -> float:
    """
    Get the frequency from a note name.

    :param note: A note name, ex. "A4"
    :param A4: The frequency of note A4. Defaults to 440. (hz)
    :return: A float of the frequency.
    """
    notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    octave = int(note[2]) if len(note) == 3 else int(note[1])
    key_number = notes.index(note[0:-1])
    if key_number < 3:
        key_number = key_number + 12 + ((octave - 1) * 12) + 1
    else:
        key_number = key_number + ((octave - 1) * 12) + 1
    return A4 * 2 ** ((key_number - 49) / 12)


def format_hex(num: int, min_len: int = 0) -> str:
    raw_hex = hex(num)[2:]
    return ("0" * (min_len - len(raw_hex))) + raw_hex


def format_col(time: int, velocity: int, notes: list[int]) -> str:
    """
    Formats a column.

    :param time: The time, in milliseconds.
    :param velocity: Velocity.
    :param notes: A list of MIDI note to press.
    :return: A string.
    """
    col = format_hex(time, 8)
    col += format_hex(velocity, 2)
    note_list = ["0"] * (88 + 21)
    for note in notes:
        note_list[note] = "f" if "#" in note_num_to_name(note - 21) else "1"
    col += "".join(note_list)
    col += "0"
    return col


def secs_to_ms(t: float) -> int:
    """
    Convert seconds to milliseconds.

    :param t: The time, in seconds.
    :return: The time, in milliseconds, rounded.
    """
    return round(t * 1000)


logger.info("Generating images")

image = []
width_count = 0

i = 0
while msgs[i].type != "note_on":
    i += 1

last_time = secs_to_ms(msgs[i].time)
last_velocity = msgs[i].velocity
last_notes = [msgs[i].note]

while i < len(msgs):
    msg = msgs[i]
    next_msg = msgs[i + 1] if i + 1 < len(msgs) else None

    if msg.type == "note_on":
        logger.debug(f"Note message: {msg}")

        if width_count == 0:
            image.append(("1" * (8 + 2 + (88 + 21))) + "0")
            image.append(("3" * 8) + ("2" * 2) + ("1" * (88 + 21)) + "0")
            width_count = 2

        msg_time = secs_to_ms(msg.time)

        if last_time != msg_time or last_velocity != msg.velocity:
            logger.debug("Inserting new chord")

            image.append(format_col(last_time, last_velocity, last_notes))
            width_count += 1

            last_time = msg_time
            last_velocity = msg.velocity
            last_notes = [msg.note]
        else:
            logger.debug("Appending to last chord")

            last_notes.append(msg.note)

        if width_count == 512:
            width_count = 0
    else:
        logger.debug(f"Meta message: {msg}")
    i += 1


def format_cols_to_img(cols: list[str], pre_pad: str = "",
                       start_at: int = 0) -> str:
    """
    Flips an array sideways and makes it a string or something like that.

    :param cols: A list of strs.
    :param pre_pad: A string of what you want to pre_pad each line with.
     Defaults to "".
    :param start_at: Start at some point along the strings.
    :return: A string.
    """
    grid = ""
    for y in range(len(cols[0])):
        grid += f"{pre_pad}"
        for x in range(start_at, min(len(cols), start_at + 512)):
            grid += f"{cols[x][y]} "
        grid += "\n"
    return f"{pre_pad}{grid.strip()}\n"


images_code = ""

img_count = 0

for i in range(0, len(image), 512 * 4):
    images_code += "img`\n"
    j = i
    while j < i + (512 * 4):
        images_code += format_cols_to_img(image, start_at=j)
        j += 512
    images_code += "`\n\n\n"
    img_count += 1


logger.info(f"Generated {img_count} image(s)")

if to_stdout:
    print(images_code)
else:
    logger.info(f"Writing to {out_path}")
    out_path.write_text(images_code)
