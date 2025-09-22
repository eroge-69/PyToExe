import json
import os
import sys
import random
import shutil
import subprocess
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import dcg_pb2
import numpy as np
from google.protobuf.json_format import Parse
from numba import njit


def extract_var(name, default=None):
    if name in os.environ:
        return os.environ[name]
    else:
        if default is None:
            raise ValueError(f"Environment variable {name} not set.")
        else:
            return default


def db(x, power=True):
    return (10 if power else 20) * np.log10(np.abs(x))


def quantize_echo(echo, nbits):
    mmax = np.max(np.max(np.abs(echo)))
    echo = echo / mmax
    echo = np.round(echo * (2 ** (nbits - 1) - 1))
    echo = np.clip(echo, -(2 ** (nbits - 1)), 2 ** (nbits - 1) - 1)
    return echo


def get_alpha_index(alpha, alphas):
    # TODO Check if this is correct.
    return 0 if alpha <= np.min(alphas) else np.max(np.where(alphas < alpha)) + 1


def baq_compress_block(x, x_threshold):
    y = np.zeros_like(x)
    x_abs = np.abs(x)
    x_sign = np.sign(x)
    # TODO Check if this is correct.
    y = np.searchsorted(x_threshold, x_abs, side="right") * x_sign
    return y


@njit
def write_value_to_u8_arr(data_u8, value, offset_bits, nbits):
    max_value = (1 << nbits) - 1
    max_negative_value = -(1 << (nbits - 1))
    int_value = int(value)
    if int_value < max_negative_value:
        raise ValueError(f"Value {value} does not fit in {nbits} bits.")
    if int_value > max_value:
        raise ValueError(f"Value {value} does not fit in {nbits} bits.")
    masked_value = int_value & max_value

    # Initial byte and bit offsets
    byte_offset = offset_bits // 8
    bit_offset = offset_bits % 8

    while nbits > 0:
        # Determine how many bits can be written to the current byte
        bits_in_current_byte = min(8 - bit_offset, nbits)

        # Prepare the bits to write
        bits_to_write = (masked_value & ((1 << bits_in_current_byte) - 1)) << bit_offset

        # Write the bits to the current byte
        data_u8[byte_offset] |= bits_to_write

        # Update the value and bit counters
        masked_value >>= bits_in_current_byte
        nbits -= bits_in_current_byte

        # Move to the next byte
        byte_offset += 1
        bit_offset = 0  # From now on, write from the start of each byte


# TODO Test BAQ compression in the same way that in MATLAB/FPGA is tested.
def baq_compress(mat_quantized, npulses, nbins, alphas, lbaq, x_thresholds):
    mat_baq = np.zeros_like(mat_quantized)
    mat_alpha = np.zeros_like(np.real(mat_quantized)).astype(np.float64)
    mat_alpha_index = np.zeros_like(np.real(mat_quantized)).astype(np.int64)
    for i_pulse in range(npulses):
        pulse = mat_quantized[i_pulse]
        for chunk in range(int(np.ceil(nbins / lbaq))):
            chunk_start = chunk * lbaq
            chunk_end = min((chunk + 1) * lbaq, nbins)
            chunk_data = pulse[chunk_start:chunk_end]
            chunk_data_i = np.real(chunk_data)
            chunk_data_q = np.imag(chunk_data)
            alpha_i = np.sum(np.abs(chunk_data_i)) / len(
                chunk_data_i
            )  # TODO LBAQ or len(chunk_data_i)?
            alpha_q = np.sum(np.abs(chunk_data_q)) / len(
                chunk_data_q
            )  # TODO LBAQ or len(chunk_data_q)?
            alpha = int(
                np.round((alpha_i + alpha_q) / 2)
            )  # TODO Is it correct to use a single alpha for both I and Q?
            mat_alpha[i_pulse, chunk_start:chunk_end] = alpha
            alpha_index = get_alpha_index(alpha, alphas)
            mat_alpha_index[i_pulse, chunk_start:chunk_end] = alpha_index
            x_threshold = x_thresholds[alpha_index]
            baq_data_i = baq_compress_block(chunk_data_i, x_threshold)
            baq_data_q = baq_compress_block(chunk_data_q, x_threshold)
            mat_baq[i_pulse, chunk_start:chunk_end] = baq_data_i + 1j * baq_data_q
    return mat_baq, mat_alpha, mat_alpha_index


def get_output_raw_zip_path(
    acquisition_mode, start_datetime, end_datetime, generation_datetime
):
    data_type_id = DICT_ACQUISITION_MODE_TO_CODE[acquisition_mode]
    start_time = start_datetime.strftime("%Y%m%dT%H%M%S")
    end_time = end_datetime.strftime("%Y%m%dT%H%M%S")
    generation_time = generation_datetime.strftime("%Y%m%dT%H%M%S")
    path = (
        OUTPUT_PATH
        / f"ISX01_R_{data_type_id}{POL}_RAW_{start_time}_{end_time}_{generation_time}_00010_ZA02_O_E01.zip"
    )
    return path


def get_max_samples_per_packet(nbaq):
    return PAYLOAD_SIZE * 8 // nbaq  # Samples.


def get_max_complex_samples_per_packet(nbaq):
    return get_max_samples_per_packet(nbaq) // 2  # Complex samples.


def zip_folder(folder_path, zip_path, compression_level):
    # Remove existing zip file.
    zip_path.unlink(missing_ok=True)

    # Create tarball.
    p = subprocess.run(
        [
            "zip",
            "-r",
            f"-{compression_level}",
            zip_path.name,
            ".",
        ],
        capture_output=True,
        cwd=folder_path,
    )

    # Print zip creation output.
    if p.returncode != 0:
        print("Error creating zip.")
        print(p.stdout.decode("utf-8"))
        print(p.stderr.decode("utf-8"))
        raise RuntimeError("Error creating zip.")
    else:
        print("zip created successfully.")
        print(p.stdout.decode("utf-8"))
        print(p.stderr.decode("utf-8"))

    # Move the zip file to the output directory.
    (folder_path / zip_path.name).rename(zip_path)


def extract_info(beam):
    with open(ECHO_JSON_PATHS[beam]) as fp:
        _echo_d = json.load(fp)
    _echo_fc = _echo_d["swath_info"]["fc_Hz"]
    _echo_npulses = _echo_d["raster_info"]["raster_list"][0]["lines"]
    _echo_dt = _echo_d["raster_info"]["raster_list"][0]["lines_start"]
    _echo_samples_spacing = _echo_d["raster_info"]["raster_list"][0]["samples_step"]
    _echo_adc_fs = 1 / _echo_samples_spacing
    _range_decimation = (16 * FREF / 2) / _echo_adc_fs
    if (int(_range_decimation) != _range_decimation) or (_range_decimation < 1):
        print("WARNING - Invalid range decimation.")
    _range_decimation = int(_range_decimation)
    _echo_swst = _echo_d["raster_info"]["raster_list"][0]["samples_start"]
    _nbins = _echo_d["raster_info"]["raster_list"][0]["samples"]
    _echo_swet = _echo_swst + _echo_samples_spacing * (_nbins - 1)
    _echo_swet_idx = int(np.floor(_echo_swet * _echo_adc_fs))
    _echo_swst_idx = int(np.floor(_echo_swst * _echo_adc_fs))
    _echo_swl_idx = _echo_swet_idx - _echo_swst_idx + 1
    _echo_pri = _echo_d["raster_info"]["raster_list"][0]["lines_step"]
    _echo_prf = 1 / _echo_pri
    _timestamp = _echo_d["dataset_info"]["acquisition_start_utc"] + "Z"
    _beam = _echo_d["swath_info"]["beam"]
    if _beam != beam:
        raise ValueError("Beam mismatch.")
    _az_steering_deg = _echo_d["burst_info"]["az_steering_deg_pol"]
    return {
        "fc": _echo_fc,
        "npulses": _echo_npulses,
        "dt": _echo_dt,
        "adc_fs": _echo_adc_fs,
        "range_decimation": _range_decimation,
        "swst": _echo_swst,
        "nbins": _nbins,
        "swet": _echo_swet,
        "swet_idx": _echo_swet_idx,
        "swst_idx": _echo_swst_idx,
        "swl_idx": _echo_swl_idx,
        "pri": _echo_pri,
        "prf": _echo_prf,
        "timestamp": _timestamp,
        "beam": _beam,
        "az_steering_deg": _az_steering_deg,
        "lines_start": {
            burst_index: _echo_d["raster_info"]["raster_list"][burst_index][
                "lines_start"
            ]
            for burst_index in BURST_INDEXES
        },
    }


# Set-up Logging Library
LOG_FORMAT  = '%(asctime)s [%(levelname)s] %(message)s'
logging.basicConfig(
    format=LOG_FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)


# ------------------ Parsing input arguments --------------------------------- #
# call like:
#
# python3 sim-to-raw.py DATA_DIR BEAM_NAME_1 ... BEAM_NAME_N BURST_NUMBERS
#
################################################################################

if len(sys.argv) < 3:
    raise ValueError("Needs at least two argument")
elif len(sys.argv) > 7:
    raise ValueError("Too many argument. Maximum 6 arguments")

DATA_DIR = sys.argv[1]
beam_name = sys.argv[2]
beams_names = []
numbers_of_bursts = 0
if len(sys.argv) > 3:
    beams_names = sys.argv[2:-1]
    numbers_of_bursts = sys.argv[-1]


# ------------------ Directories ---------------------------- #
logging.info("Directories Definitions: start")
# DATA_DIR = extract_var("MY_DATA_DIR", "scan_1")
# print(f"DATA_DIR: {DATA_DIR}")
# Base input paths.
BASE_INPUT_PATH = Path(f"outputDir").resolve(strict=True)

# Input parameters.
if "strip" in DATA_DIR:
    BEAMS = [beam_name]
    ACQ_ID = "001"
    POL_TYPE = "SP"  # Dual-pol, doesn't affect the simulation.
    POL = "VV"
    ACQUISITION_MODE = dcg_pb2.EnumAcquisitionMode.STRIPMAP  # Mode.
    UUID = "4AFFC4C432E24FC50E80B00A871DAFE7"  # UUID generated internally by the FOS. No specific meaning.
    BURST_INDEXES = [0]
    NOISE_BURST_INDEX = 0
    ICAL_BURST_INDEX = 0
    GENERATION_DATETIME = datetime(2024, 9, 17, 10, 55, 16, tzinfo=timezone.utc)  # UTC.
elif "spot" in DATA_DIR:
    BEAMS = [beam_name]
    ACQ_ID = "001"
    POL_TYPE = "SP"  # Single-pol, doesn't affect the simulation.
    POL = "VV"
    ACQUISITION_MODE = dcg_pb2.EnumAcquisitionMode.SPOTLIGHT  # Mode.
    UUID = "88888888888888888888888888888888"  # UUID generated internally by the FOS. No specific meaning.
    BURST_INDEXES = [0]
    NOISE_BURST_INDEX = 0
    ICAL_BURST_INDEX = 0
    GENERATION_DATETIME = datetime(2024, 9, 17, 11, 56, 17, tzinfo=timezone.utc)  # UTC.
elif "scan" in DATA_DIR:
    # Input data lines start order is W5, W1, W2, W3, W4.
    BEAMS = beams_names  # ScanSAR-3.
    ACQ_ID = "001"
    POL_TYPE = "SP"  # Single-pol, doesn't affect the simulation.
    POL = "VV"
    ACQUISITION_MODE = dcg_pb2.EnumAcquisitionMode.SCANSAR3  # Mode.
    UUID = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"  # UUID generated internally by the FOS. No specific meaning.
    BURST_INDEXES = range(numbers_of_bursts)
    NOISE_BURST_INDEX = 0
    ICAL_BURST_INDEX = 0
    GENERATION_DATETIME = datetime(2024, 9, 17, 12, 56, 17, tzinfo=timezone.utc)  # UTC.
else:
    raise ValueError("Invalid data path.")

USE_DIRECT_SIM = True  # Use direct simulation.

# Input paths.
ECHO_JSON_PATHS = dict()
RAW_ECHO_PATHS = dict()
RAW_NOISE_PATHS = dict()
CHIRP_PATHS = dict()
for beam in BEAMS:
    ECHO_JSON_PATHS[beam] = (
        BASE_INPUT_PATH / f"l0_acqId{ACQ_ID}_{beam}{POL_TYPE}_{POL}_ECHO.json"
    ).resolve(strict=True)
    RAW_ECHO_PATHS[beam] = dict()
    RAW_NOISE_PATHS[beam] = dict()
    CHIRP_PATHS[beam] = dict()
    for burst_index in BURST_INDEXES:
        RAW_ECHO_PATHS[beam][burst_index] = (
            BASE_INPUT_PATH
            / "out"
            / beam
            / str(burst_index)
            / ("rawEcho.bin" if USE_DIRECT_SIM else "rngCompRawEcho.bin")
        ).resolve(strict=True)
        RAW_NOISE_PATHS[beam][burst_index] = (
            BASE_INPUT_PATH / "out" / beam / str(burst_index) / "rawNoise.bin"
        ).resolve(strict=True)
        CHIRP_PATHS[beam][burst_index] = (
            BASE_INPUT_PATH / "out" / beam / str(burst_index) / "chirp.bin"
        ).resolve(strict=True)
SVATT_JSON_PATH = (BASE_INPUT_PATH / f"l0_acqId{ACQ_ID}_SVATT.json").resolve(
    strict=True
)

SVORB_JSON_PATH = (BASE_INPUT_PATH / f"l0_acqId{ACQ_ID}_SVORB.json").resolve(
    strict=True
)

# Constants.
DICT_ACQUISITION_MODE_TO_CODE = {
    dcg_pb2.EnumAcquisitionMode.STRIPMAP: "ST",
    dcg_pb2.EnumAcquisitionMode.SPOTLIGHT: "SP",
    dcg_pb2.EnumAcquisitionMode.SCANSAR2: "SC",
    dcg_pb2.EnumAcquisitionMode.SCANSAR3: "SC",
}
RAW_ECHO_NBITS = 14  # Bits.
BAQ_BYPASS = True  # Bypass BAQ.
BAQ_BYPASS_NBITS = 16  # Bits.
NBAQ = 6  # Bits.
LBAQ = 512  # Samples.
PRIMARY_HEADER_SIZE = 6  # Bytes.
SECONDARY_HEADER_SIZE = 362 + 16  # Bytes.
HEADER_SIZE = PRIMARY_HEADER_SIZE + SECONDARY_HEADER_SIZE  # Bytes.
PAYLOAD_SIZE = 15360  # Bytes.
STREAMS = 4  # Streams.
PADDED_PACKET_SIZE = 16384  # Bytes.
FREF = 184.32e6  # Hz.
DTF_ZIP_COMPRESSION_LEVEL = 9  # Level.
RAW_ZIP_COMPRESSION_LEVEL = 0  # Level.
MAX_AZIMUTH_BEAMS_PER_SECOND = 20  # Hz.
N_NOISE_PULSES = 100  # Number of noise pulses.
N_ICAL_PULSES = 300  # Number of ICAL pulses.
SIGNAL_TYPE_ECHO = 0
SIGNAL_TYPE_NOISE = 1
SIGNAL_TYPE_ICAL = 8  # TODO What about signal type 9?
SIGNAL_DESCRIPTIONS = {
    SIGNAL_TYPE_ECHO: "ECHO",
    SIGNAL_TYPE_NOISE: "NOISE",
    SIGNAL_TYPE_ICAL: "ICAL"
}
SSX_FC = 9.65e9  # Hz.

# Other input paths.
AI_TEMPLATE_JSON_PATH = Path("raw_compressor/input/ai_template.json").resolve(strict=True)
DC_TEMPLATE_JSON_PATH = Path("raw_compressor/input/dc_template.json").resolve(strict=True)
SSX_ASWD_CONF_JSON_TEMPLATE_PATH = Path("raw_compressor/input/ssx-aswd-conf_template.json").resolve(
    strict=True
)
BAQ_LUT_PATH = Path(
    f"raw_compressor/BAQ-LUT/thresholds_inBits{RAW_ECHO_NBITS}_BAQ{NBAQ}.txt"
).resolve(strict=True)

# RAW zip naming convention.
# ABBCC_DDEEEEEEEE_<start_time>_<end_time>_<generation_time>_<group_id>_<environment>_<version>.<extension>
# (e.g.  ISX01_R_STVV_RAW_20250912T102502_20250912T102558_20250912T105516_00010_ZA02_O_E01.zip)

OUTPUT_PATH = Path("raw_compressor/output").resolve(strict=True) / DATA_DIR
if not OUTPUT_PATH.exists():
    OUTPUT_PATH.mkdir()
OUTPUT_RAW_PATH = (
    OUTPUT_PATH / "RAW"
)  # Folder. To be renamed according to the naming convention and zipped without compression in *.zip.
OUTPUT_AIF_PATH = OUTPUT_RAW_PATH / f"LRSAIF_uuid{UUID}.binpb"
OUTPUT_DCF_PATH = OUTPUT_RAW_PATH / f"LRSDCF_uuid{UUID}.binpb"
OUTPUT_DTF_PATH = (
    OUTPUT_RAW_PATH / f"LRSDTF_uuid{UUID}"
)  # Folder. To be zipped in *.zip.
OUTPUT_IRD_PATH = OUTPUT_DTF_PATH / f"LRSIRD_uuid{UUID}.bin"
OUTPUT_ITM_PATH = OUTPUT_DTF_PATH / f"LRSITM_uuid{UUID}.bin"
OUTPUT_SVATT_PATH = OUTPUT_DTF_PATH / f"LRSATT_uuid{UUID}.json"
OUTPUT_SVORB_PATH = OUTPUT_DTF_PATH / f"LRSORB_uuid{UUID}.json"

shutil.rmtree(OUTPUT_RAW_PATH, ignore_errors=True)
if not OUTPUT_RAW_PATH.exists():
    OUTPUT_RAW_PATH.mkdir()
if not OUTPUT_DTF_PATH.exists():
    OUTPUT_DTF_PATH.mkdir()
logging.info("Directories Definitions: end")

# ---------------- Load Simulation Data ------------------------ #
logging.info("Load Simulated Data: start")
echo_info = dict()
for beam in BEAMS:
    echo_info[beam] = extract_info(beam)

for burst_index in BURST_INDEXES:
    for beam in BEAMS:
        if beam != BEAMS[0]:
            previous_beam = BEAMS[BEAMS.index(beam) - 1]
            if (
                echo_info[beam]["lines_start"][burst_index]
                < echo_info[previous_beam]["lines_start"][burst_index]
            ):
                raise ValueError("Lines start mismatch.")


max_pri = max([echo_info[beam]["pri"] for beam in BEAMS])

# Load ECHO binary data.
for beam in BEAMS:
    for burst_index in BURST_INDEXES:
        _raw_echo_coup = np.fromfile(RAW_ECHO_PATHS[beam][burst_index], dtype=np.float32)
        # the matlab function fwrite writes along the columns, so you need to read according to
        # that direction and then tranpose to reconstruct the original matrix
        _raw_echo_coup = np.reshape(_raw_echo_coup, (echo_info[beam]["swl_idx"], 2*echo_info[beam]["npulses"]))
        _raw_echo_coup = np.transpose(_raw_echo_coup)

        _raw_echo = np.zeros((echo_info[beam]["npulses"], echo_info[beam]["swl_idx"]), dtype=np.complex64)
        for i in range(echo_info[beam]["npulses"]):
            _raw_echo[i, :] = _raw_echo_coup[2*i, :] +1J*_raw_echo_coup[2*i+1, :]

        echo_info[beam][f"raw_echo_{burst_index}"] = _raw_echo

logging.info("Load Simulated Data: end")

# ---------------- Quantize ECHO Data ----------------------- #
logging.info("Quantize Simulated Data: start")

for beam in BEAMS:
    for burst_index in BURST_INDEXES:
        _raw_echo = echo_info[beam][f"raw_echo_{burst_index}"]
        _raw_echo_quantized = quantize_echo(_raw_echo, RAW_ECHO_NBITS)
        echo_info[beam][f"raw_echo_quantized_{burst_index}"] = _raw_echo_quantized
logging.info("Quantize Simulated Data: end")

# ---------------- BAQ Compression ------------------------- #
logging.info("BAQ Compression: start")

with open(BAQ_LUT_PATH, "r") as f:
    lines = f.readlines()
lines = [line.strip() for line in lines]

alphas = np.array([int(x) for x in lines[0][1:-1].split(", ")])
n_alphas = len(alphas)

x_thresholds = np.array(
    [
        [
            int(x)
            for x in line[line.find("(") + 1 : line.find(")")].split(", ")  # noqa E203
        ]
        for line in lines[2 : 2 + n_alphas + 1]  # noqa E203
    ]
)

y_centroids = np.array(
    [
        [int(x) for x in line[line.find("(") + 1 : line.find(")")].split(", ")]
        for line in lines[2 + n_alphas + 2 : 2 + 2 * n_alphas + 3]
    ]
)

for beam in BEAMS:
    for burst_index in BURST_INDEXES:
        _raw_echo_baq, _raw_echo_alpha, _raw_echo_alpha_index = baq_compress(
            mat_quantized=echo_info[beam][f"raw_echo_quantized_{burst_index}"],
            npulses=echo_info[beam]["npulses"],
            nbins=echo_info[beam]["nbins"],
            alphas=alphas,
            lbaq=LBAQ,
            x_thresholds=x_thresholds,
        )

        echo_info[beam][f"raw_echo_baq_{burst_index}"] = _raw_echo_baq
        # echo_info[beam][f"raw_echo_alpha_{burst_index}"] = _raw_echo_alpha
        echo_info[beam][f"raw_echo_alpha_index_{burst_index}"] = _raw_echo_alpha_index

logging.info("BAQ Compression: end")
# ------------------------ Load, Quantize and Compress NOISE Data ------------------- #
logging.info("Load, Quantize and Compress NOISE: start")
for beam in BEAMS:
    _raw_noise_coup = np.fromfile(RAW_NOISE_PATHS[beam][NOISE_BURST_INDEX], dtype=np.float32)
    # the matlab function fwrite writes along the columns, so you need to read according to
    # that direction and then tranpose to reconstruct the original matrix
    _raw_noise_coup = np.reshape(_raw_noise_coup, (echo_info[beam]["swl_idx"], 2*N_NOISE_PULSES))
    _raw_noise_coup = np.transpose(_raw_noise_coup)
    _raw_noise = np.zeros((N_NOISE_PULSES, echo_info[beam]["swl_idx"]), dtype=np.complex64)
    for i in range(N_NOISE_PULSES):
        _raw_noise[i, :] = _raw_noise_coup[2*i, :] +1J*_raw_noise_coup[2*i+1, :]

    echo_info[beam][f"raw_noise_{NOISE_BURST_INDEX}"] = _raw_noise

    _raw_noise_quantized = quantize_echo(_raw_noise, RAW_ECHO_NBITS)
    echo_info[beam][f"raw_noise_quantized_{NOISE_BURST_INDEX}"] = _raw_noise_quantized

    # BAQ compress NOISE data.
    _raw_noise_baq, _raw_noise_alpha, _raw_noise_alpha_index = baq_compress(
        mat_quantized=_raw_noise_quantized,
        npulses=N_NOISE_PULSES,
        nbins=echo_info[beam]["nbins"],
        alphas=alphas,
        lbaq=LBAQ,
        x_thresholds=x_thresholds,
    )

    echo_info[beam][f"raw_noise_baq_{NOISE_BURST_INDEX}"] = _raw_noise_baq
    # echo_info[beam][f"raw_noise_alpha_{NOISE_BURST_INDEX}"] = _raw_noise_alpha
    echo_info[beam][
        f"raw_noise_alpha_index_{NOISE_BURST_INDEX}"
    ] = _raw_noise_alpha_index

logging.info("Load, Quantize and Compress NOISE: end")
# --------------- Load and Quantize ICAL Chirp Data -------------------------------- #
logging.info("Load, Quantize ICAL: start")
for beam in BEAMS:
    _raw_chirp = np.fromfile(CHIRP_PATHS[beam][ICAL_BURST_INDEX], dtype=np.complex64)
    echo_info[beam][f"raw_chirp_{ICAL_BURST_INDEX}"] = _raw_chirp
    _raw_chirp_quantized = quantize_echo(_raw_chirp, RAW_ECHO_NBITS)
    echo_info[beam][f"raw_chirp_quantized_{ICAL_BURST_INDEX}"] = _raw_chirp_quantized

logging.info("Load, Quantize ICAL: end")
# ------------------------- Packetize Data ---------------------------------------- #
logging.info("Packetize Data: start")
signal_comp = []  # NOISE ICAL ECHO ICAL NOISE.

# NOISE.
t0 = 0
for beam in BEAMS:
    signal_comp.append(
        (
            SIGNAL_TYPE_NOISE,
            0,
            N_NOISE_PULSES // (2 * len(BEAMS)),
            beam,
            NOISE_BURST_INDEX,
            t0,
        )
    )
    t0 += N_NOISE_PULSES // (2 * len(BEAMS)) * echo_info[beam]["pri"]
# ICAL.
for beam in BEAMS:
    signal_comp.append(
        (
            SIGNAL_TYPE_ICAL,
            0,
            N_ICAL_PULSES // (2 * len(BEAMS)),
            beam,
            ICAL_BURST_INDEX,
            t0,
        )
    ),
    t0 += N_ICAL_PULSES // (2 * len(BEAMS)) * echo_info[beam]["pri"]

if t0 > echo_info[BEAMS[0]]["lines_start"][BURST_INDEXES[0]]:
    raise ValueError("Time overlap.")

# ECHO.
for burst_index in BURST_INDEXES:
    for beam in BEAMS:
        t0 = echo_info[beam]["lines_start"][burst_index]
        signal_comp.append(
            (SIGNAL_TYPE_ECHO, 0, echo_info[beam]["npulses"], beam, burst_index, t0)
        )
# ICAL.
for beam in BEAMS:
    signal_comp.append(
        (
            SIGNAL_TYPE_ICAL,
            N_ICAL_PULSES // (2 * len(BEAMS)),
            N_ICAL_PULSES // (2 * len(BEAMS)),
            beam,
            ICAL_BURST_INDEX,
            t0,
        )
    )
    t0 += N_ICAL_PULSES // (2 * len(BEAMS)) * echo_info[beam]["pri"]
# NOISE.
for beam in BEAMS:
    signal_comp.append(
        (
            SIGNAL_TYPE_NOISE,
            N_NOISE_PULSES // (2 * len(BEAMS)),
            N_NOISE_PULSES // (2 * len(BEAMS)),
            beam,
            NOISE_BURST_INDEX,
            t0,
        )
    )
    t0 += N_NOISE_PULSES // (2 * len(BEAMS)) * echo_info[beam]["pri"]

i_pulse_off = 0
i_packet_off = 0

with open(OUTPUT_IRD_PATH, "wb") as fp:
    for signal_type, i_start, n_pulses, beam, burst_index, t0 in signal_comp:
        logging.info("Packetize Data: Elaborating " + SIGNAL_DESCRIPTIONS[signal_type])
        if signal_type == SIGNAL_TYPE_ECHO:
            mat_baq = (
                echo_info[beam][f"raw_echo_baq_{burst_index}"]
                if not BAQ_BYPASS
                else echo_info[beam][f"raw_echo_quantized_{burst_index}"]
            )
            mat_alpha_index = (
                echo_info[beam][f"raw_echo_alpha_index_{burst_index}"]
                if not BAQ_BYPASS
                else np.zeros_like(np.real(mat_baq)).astype(np.int64)
            )
            nbaq = NBAQ if not BAQ_BYPASS else BAQ_BYPASS_NBITS
            nbins = mat_baq.shape[1]
        elif signal_type == SIGNAL_TYPE_NOISE:
            mat_baq = (
                echo_info[beam][f"raw_noise_baq_{burst_index}"]
                if not BAQ_BYPASS
                else echo_info[beam][f"raw_noise_quantized_{burst_index}"]
            )
            nbaq = NBAQ if not BAQ_BYPASS else BAQ_BYPASS_NBITS
            mat_alpha_index = (
                echo_info[beam][f"raw_noise_alpha_index_{burst_index}"]
                if not BAQ_BYPASS
                else np.zeros_like(np.real(mat_baq)).astype(np.int64)
            )
        elif signal_type == SIGNAL_TYPE_ICAL:
            mat_baq = np.broadcast_to(
                echo_info[beam][f"raw_chirp_quantized_{burst_index}"],
                (
                    N_ICAL_PULSES,
                    *echo_info[beam][f"raw_chirp_quantized_{burst_index}"].shape,
                ),
            )
            nbaq = BAQ_BYPASS_NBITS
            mat_alpha_index = np.zeros_like(np.real(mat_baq)).astype(np.int64)
        else:
            raise ValueError("Invalid signal type")
        npulses = mat_baq.shape[0]
        nbins = mat_baq.shape[1]
        max_complex_samples_per_packet = get_max_complex_samples_per_packet(nbaq)
        packets_per_pulse = int(np.ceil(nbins / max_complex_samples_per_packet))
        for i_pulse in range(n_pulses):
            for i_packet in range(packets_per_pulse):
                packet_start = i_packet * max_complex_samples_per_packet
                packet_end = min((i_packet + 1) * max_complex_samples_per_packet, nbins)
                baq_data = mat_baq[
                    (i_pulse + i_start) % npulses, packet_start:packet_end
                ]
                alpha_indices = mat_alpha_index[
                    (i_pulse + i_start) % npulses, packet_start:packet_end
                ][::LBAQ]
                ii = np.real(baq_data).astype(np.int64)
                qq = np.imag(baq_data).astype(np.int64)
                ii_e = ii[0::2]
                ii_o = ii[1::2]
                qq_e = qq[0::2]
                qq_o = qq[1::2]

                # Create packet.
                packet = np.zeros(PADDED_PACKET_SIZE, dtype=np.uint8)

                # Compute acquisition pulse index.
                acq_pulse_idx = i_pulse + i_pulse_off

                # Compute acquisition packet index.
                acq_packet_idx = i_packet + i_packet_off

                # Compute azimuth beam index.
                az_beam_idx = 0
                if (
                    ACQUISITION_MODE == dcg_pb2.EnumAcquisitionMode.SPOTLIGHT
                    and signal_type == SIGNAL_TYPE_ECHO
                ):
                    # TODO Improve if there are interleaved NOISE or ICAL.
                    t = i_pulse * echo_info[beam]["pri"]
                    az_beam_idx = int(np.floor(t * MAX_AZIMUTH_BEAMS_PER_SECOND))

                # Compute the elevation beam index.
                el_beam_idx = 0
                if ACQUISITION_MODE == dcg_pb2.EnumAcquisitionMode.SCANSAR3:
                    el_beam_idx = BEAMS.index(beam)

                # Compute the time.
                t0 = echo_info[beam]["lines_start"][burst_index]

                # Populate header.
                header = [
                    ("version", 1, 0, 3),
                    ("type", 1, 3, 1),
                    ("secondaryHeaderFlag", 1, 4, 1),
                    ("apid", 1, 5, 11),
                    ("sequenceFlags", 0, 16, 2),
                    (
                        "packetSequenceCount",
                        acq_packet_idx % (2**14),
                        18,
                        14,
                    ),
                    ("packetDataLength", HEADER_SIZE + (len(ii_e) * nbaq) // 8, 32, 16),
                    (
                        "coarseTime",
                        np.floor(t0 + echo_info[beam]["pri"] * i_pulse),
                        6 * 8,
                        16,
                    ),
                    (
                        "fineTime",
                        np.floor(
                            (
                                t0
                                + echo_info[beam]["pri"] * i_pulse
                                - np.floor(t0 + echo_info[beam]["pri"] * i_pulse)
                            )
                            * FREF
                        ),
                        8 * 8,
                        32,
                    ),
                    ("syncMarker", 0xDEADBEEF, 12 * 8, 32),
                    ("uuid_0", 0xDEADBEEF, 16 * 8, 32),
                    ("uuid_1", 0xCAFEBABE, 20 * 8, 32),
                    ("uuid_2", 0xBADDCAFE, 24 * 8, 32),
                    ("uuid_3", 0xBAADF00D, 28 * 8, 32),
                    ("rxGain", 0, 32 * 8, 8),
                    # TODO Correctly populate the header.
                    ("rxChannelId", 0, 33 * 8, 4),
                    ("subSwathQuantity", 0, 33 * 8 + 4, 4),
                    ("testMode", 0, 34 * 8 + 4, 4),
                    ("eccNumber", 0, 35 * 8, 8),
                    ("dataTakeLength", 1, 36 * 8, 16),
                    ("elevationBeamRank", 0, 38 * 8, 4),
                    ("azimuthBeamRank", 0, 38 * 8 + 4, 4),
                    ("txGuard1", 0, 39 * 8, 12),
                    ("txGuard2", 0, 40 * 8 + 4, 12),
                    ("calPulseTxStart", 0, 42 * 8, 12),
                    ("calSamplingWake", 0, 43 * 8 + 4, 12),
                    ("txCalEnable", 0, 45 * 8, 8),
                    ("rxCalEnable", 0, 46 * 8, 8),
                    ("ceCalEnable", 0, 47 * 8, 8),
                    ("txGain", 0, 48 * 8, 8),
                    ("spacePacketCount", acq_packet_idx, 56 * 8, 32),
                    ("priCount", acq_pulse_idx, 60 * 8, 32),
                    # TODO Check counters for stripmap.
                    (
                        "indexStrobeCount",
                        0,
                        64 * 8,
                        16,
                    ),
                    # TODO Check counters for stripmap.
                    ("swathCount", 0, 66 * 8, 16),
                    # TODO Check counters for stripmap.
                    (
                        "elevationBeamCount",
                        el_beam_idx,
                        68 * 8 + 1,
                        3,
                    ),
                    ("azimuthBeamCount", az_beam_idx, 68 * 8 + 4, 12),
                    # TODO Check counters for stripmap.
                    (
                        "imageBurstCount",
                        0,
                        71 * 8,
                        16,
                    ),
                    # TODO Check counters for stripmap.
                    (
                        "imageBurstPriCount",
                        0,
                        73 * 8,
                        24,
                    ),
                    ("error", 0, 80 * 8, 1),
                    # nbaq is 4 bits, 16 = bypass is encoded as 0.
                    (
                        "baqMode",
                        0 if nbaq == 16 else nbaq,
                        80 * 8 + 4,
                        4,
                    ),
                    ("baqBlockLength", LBAQ / 128, 81 * 8 + 4, 4),
                    # TODO Correctly populate the header.
                    (
                        "rangeDecimation",
                        echo_info[beam]["range_decimation"],
                        82 * 8,
                        8,
                    ),
                    # TODO Correctly populate the header.
                    (
                        "txPulseLength",
                        0,
                        83 * 8,
                        24,
                    ),
                    ("txPulseId", 0, 86 * 8, 32),
                    (
                        "rank",
                        np.floor(echo_info[beam]["swst"] / echo_info[beam]["pri"]),
                        90 * 8 + 2,
                        6,
                    ),
                    ("signalType", signal_type, 91 * 8, 4),
                    ("swap", 0, 91 * 8 + 7, 1),
                    ("pri", np.floor(echo_info[beam]["pri"] * FREF), 93 * 8, 24),
                    (
                        "samplingWindowStart",
                        np.floor(
                            (
                                echo_info[beam]["swst"]
                                - np.floor(
                                    echo_info[beam]["swst"] / echo_info[beam]["pri"]
                                )
                                * echo_info[beam]["pri"]
                            )
                            * FREF
                        ),
                        96 * 8,
                        24,
                    ),
                    (
                        "samplingWindowLength",
                        np.floor(
                            echo_info[beam]["swl_idx"]
                            / echo_info[beam]["adc_fs"]
                            * FREF
                        ),
                        99 * 8,
                        24,
                    ),
                    # TODO Correctly populate the header.
                    (
                        "elevationBeamLength",
                        0,
                        102 * 8 + 4,
                        12,
                    ),
                    # TODO Correctly populate the header.
                    (
                        "azimuthBeamLength",
                        0,
                        105 * 8,
                        16,
                    ),
                    # TODO Correctly populate the header.
                    (
                        "imageBurstLength",
                        echo_info[beam]["npulses"],
                        107 * 8,
                        24,
                    ),
                    ("ssbFlag", 0, 110 * 8, 1),
                    # TODO Correctly populate the header.
                    (
                        "polarization",
                        0,
                        110 * 8 + 1,
                        3,
                    ),
                    ("sasTest", 0, 111 * 8, 1),
                    ("calibrationType", 0, 111 * 8 + 1, 3),
                    ("rxOverRangeCount", 0, 112 * 8, 16),
                    ("numberOfQuads", len(ii_e), 120 * 8, 16),
                    ("endOfHeaderMarkers[0]", 0xDEADBEEF, 368 * 8, 32),
                    ("endOfHeaderMarkers[1]", 0xDEADBEEF, 372 * 8, 32),
                    ("endOfHeaderMarkers[2]", 0xDEADBEEF, 376 * 8, 32),
                    ("endOfHeaderMarkers[3]", 0xDEADBEEF, 380 * 8, 32),
                ]

                for key, value, offset_bits, nbits in header:
                    write_value_to_u8_arr(packet, value, offset_bits, nbits)

                for i, alpha_index in enumerate(alpha_indices):
                    packet[128 + i] = alpha_index & 0xFF

                # Populate payload.
                stream_size_bits = len(ii_e) * nbaq
                stream_size_bits = np.ceil(stream_size_bits / 128) * 128
                stream_size_bytes = int(stream_size_bits / 8)
                for i, xx in enumerate([ii_e, ii_o, qq_e, qq_o]):
                    off = HEADER_SIZE + stream_size_bytes * i
                    WRITE_COUNTER = False
                    if WRITE_COUNTER:
                        jj = 0
                        if i == 1 or i == 3:
                            jj += 1
                        for j, vv in enumerate(xx):
                            write_value_to_u8_arr(packet, jj, off * 8 + j * nbaq, nbaq)
                            jj += 2
                            if jj > 2 ** (nbaq - 1) - 1:
                                jj = -(2 ** (nbaq - 1))
                                if i == 1 or i == 3:
                                    jj += 1
                                    if jj > 2 ** (nbaq - 1) - 1:
                                        raise ValueError("Overflow")
                    else:
                        for j, vv in enumerate(xx):
                            write_value_to_u8_arr(packet, vv, off * 8 + j * nbaq, nbaq)

                # Save packet.
                fp.write(packet.tobytes())
            i_packet_off += packets_per_pulse
        i_pulse_off += n_pulses

logging.info("Packetize Data: end")
# -------------------- Create AUX Files ---------------- #
logging.info("Creation of AUX Files: start")
ai = dcg_pb2.AcquisitionInput()

# Load ai template from json.
with open(AI_TEMPLATE_JSON_PATH) as fp:
    Parse(fp.read(), ai)

ai.acquisition_mode = ACQUISITION_MODE

timestamp = None
for beam in BEAMS:
    if timestamp is None:
        timestamp = echo_info[beam]["timestamp"]
    elif timestamp != echo_info[beam]["timestamp"]:
        raise ValueError("Timestamp mismatch.")

dt_object = datetime.fromisoformat(timestamp)
dt_after_echo = 0

before_echo = True
for signal_type, i_start, n_pulses, beam, burst_index, t0 in signal_comp:
    if not before_echo and (
        signal_type == SIGNAL_TYPE_NOISE or signal_type == SIGNAL_TYPE_ICAL
    ):
        dt_after_echo += n_pulses * echo_info[beam]["pri"]
    elif signal_type == SIGNAL_TYPE_ECHO:
        before_echo = False

imaging_duration = (
    echo_info[BEAMS[-1]]["lines_start"][BURST_INDEXES[-1]]
    + echo_info[BEAMS[-1]]["pri"] * echo_info[BEAMS[-1]]["npulses"]
    - echo_info[BEAMS[0]]["lines_start"][BURST_INDEXES[0]]
)

dc = dcg_pb2.DatatakeConfiguration()

# Load dc template from json.
with open(DC_TEMPLATE_JSON_PATH) as fp:
    Parse(fp.read(), dc)


dc.acquisition_start_time.FromDatetime(dt_object)

# Load config json template.
with open(SSX_ASWD_CONF_JSON_TEMPLATE_PATH) as fp:
    config_json = json.load(fp)
config_json["beamNames"] = BEAMS
config_json["beamAzSteeringDegPols"] = [
    echo_info[beam]["az_steering_deg"] for beam in BEAMS
]

for i in range(len(BEAMS)):
    config_json["chirps"][i]["fc"] = echo_info[BEAMS[i]]["fc"] - SSX_FC

dc.file_data = json.dumps(config_json).encode("utf-8")

# TODO Use msgpack instead of json.
# import msgpack
# dc.file_data = msgpack.dumps(config_json)

dc.arming_duration.FromTimedelta(timedelta(seconds=2))
dc.preamble_duration.FromTimedelta(
    timedelta(seconds=echo_info[BEAMS[0]]["lines_start"][BURST_INDEXES[0]])
)
dc.imaging_duration.FromTimedelta(timedelta(seconds=imaging_duration))
dc.postamble_duration.FromTimedelta(timedelta(seconds=dt_after_echo))
dc.disabling_duration.FromTimedelta(timedelta(seconds=1))

# Write ai protobuf to binpb file.
with open(OUTPUT_AIF_PATH, "wb") as fp:
    fp.write(ai.SerializeToString())

# Write dc protobuf to binpb file.
with open(OUTPUT_DCF_PATH, "wb") as fp:
    fp.write(dc.SerializeToString())

# Copy the SVATT and SVORB files in the output directory.
if shutil.copyfile(SVATT_JSON_PATH, OUTPUT_SVATT_PATH) != OUTPUT_SVATT_PATH:
    raise ValueError("Failed to copy SVATT file")
if shutil.copyfile(SVORB_JSON_PATH, OUTPUT_SVORB_PATH) != OUTPUT_SVORB_PATH:
    raise ValueError("Failed to copy SVORB file")

# Write a random sequence of bytes to the OUTPUT_ITM_PATH file.
random.seed(42)

with open(OUTPUT_ITM_PATH, "wb") as fp:
    # One byte per pulse. Totally arbitrary.
    for _ in range(echo_info[BEAMS[0]]["npulses"] * len(BURST_INDEXES)):
        fp.write(random.getrandbits(8).to_bytes(1, "little"))

logging.info("Creation of AUX Files: end")
logging.info("Zipping Folders: start")
# Compute the output raw zip file path.
output_raw_zip_path = get_output_raw_zip_path(
    acquisition_mode=ACQUISITION_MODE,
    start_datetime=dt_object,
    end_datetime=dt_object
    + dc.preamble_duration.ToTimedelta()
    + dc.imaging_duration.ToTimedelta()
    + dc.postamble_duration.ToTimedelta(),
    generation_datetime=GENERATION_DATETIME,
)

shutil.make_archive(OUTPUT_DTF_PATH, "zip", OUTPUT_DTF_PATH)
shutil.rmtree(OUTPUT_DTF_PATH)
shutil.make_archive(str(output_raw_zip_path).split(".")[0], "zip", OUTPUT_RAW_PATH)
shutil.rmtree(OUTPUT_RAW_PATH)
logging.info("Zipping Folders: end")