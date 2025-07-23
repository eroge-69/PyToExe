""" 
rwl_ai_app.py - Real-time Voice Conversion (RVC) Application  
This script performs real-time voice conversion using RVC models via microphone and speaker.  
It allows the user to select input/output audio devices and a voice model, then converts the live audio in real-time.  
"""
import sys
import os
import numpy as np
import torch
import sounddevice as sd
import threading
import queue
import time

# Ensure the real RVC code is accessible by adding the RVC directory to sys.path
rvc_dir = os.path.abspath('./RVC')
if rvc_dir not in sys.path:
    sys.path.append(rvc_dir)

# Import the RVC voice conversion pipeline and necessary model classes
try:
    from vc_infer_pipeline import VC
except ImportError as e:
    print("Error: Could not import VC from vc_infer_pipeline. Make sure the RVC folder is correctly placed.", file=sys.stderr)
    sys.exit(1)

try:
    from lib.infer_pack.models import SynthesizerTrnMs256NSFsid, SynthesizerTrnMs256NSFsid_nono
except ImportError as e:
    print("Error: Could not import RVC model classes. Ensure that the RVC folder contains the 'lib/infer_pack/models.py' file.", file=sys.stderr)
    sys.exit(1)

# Import fairseq for loading the content encoding model (Hubert)
try:
    from fairseq import checkpoint_utils
except ImportError as e:
    print("Error: fairseq library not found. Please install fairseq to load the Hubert model.", file=sys.stderr)
    sys.exit(1)

# List and select audio input and output devices
print("Available input devices:")
input_devices = []
for idx, dev in enumerate(sd.query_devices()):
    if dev['max_input_channels'] > 0:
        input_devices.append(idx)
        print(f"{idx}: {dev['name']} (Input channels: {dev['max_input_channels']})")
print("\nAvailable output devices:")
output_devices = []
for idx, dev in enumerate(sd.query_devices()):
    if dev['max_output_channels'] > 0:
        output_devices.append(idx)
        print(f"{idx}: {dev['name']} (Output channels: {dev['max_output_channels']})")

# Prompt user to choose devices
in_device = None
out_device = None
while in_device is None:
    try:
        in_idx = int(input("\nEnter the device index for the microphone input: ").strip())
    except:
        print("Please enter a valid number for input device index.")
        continue
    if in_idx in input_devices:
        in_device = in_idx
    else:
        print("Invalid input device index. Please select from the list above.")
while out_device is None:
    try:
        out_idx = int(input("Enter the device index for the speaker output: ").strip())
    except:
        print("Please enter a valid number for output device index.")
        continue
    if out_idx in output_devices:
        out_device = out_idx
    else:
        print("Invalid output device index. Please select from the list above.")

# List available voice conversion models from the 'models' directory
models_dir = "models"
if not os.path.isdir(models_dir):
    print(f"Error: Models directory '{models_dir}' not found.", file=sys.stderr)
    sys.exit(1)
model_folders = [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
if not model_folders:
    print(f"No model subdirectories found in '{models_dir}'.", file=sys.stderr)
    sys.exit(1)
print("\nAvailable voice conversion models:")
for i, m in enumerate(model_folders):
    print(f"{i}: {m}")
# Prompt user to choose a model
model_choice = None
while model_choice is None:
    try:
        choice = int(input("Enter the number of the model to use: ").strip())
    except:
        print("Please enter a valid number for model choice.")
        continue
    if 0 <= choice < len(model_folders):
        model_choice = model_folders[choice]
    else:
        print("Invalid choice. Please select a number from the list above.")

model_dir_path = os.path.join(models_dir, model_choice)
model_path = None
# Find a .pth file in the chosen model folder
for file_name in os.listdir(model_dir_path):
    if file_name.lower().endswith(".pth"):
        model_path = os.path.join(model_dir_path, file_name)
        break
if model_path is None:
    print(f"Error: No .pth model file found in '{model_dir_path}'.", file=sys.stderr)
    sys.exit(1)
print(f"\nLoading voice conversion model: {model_choice}")

# Determine device (GPU/CPU/MPS) and whether to use half precision
if torch.cuda.is_available():
    device = "cuda"
    gpu_name = torch.cuda.get_device_name(0).lower()
    # Disable half precision on some GPUs with limited half support
    if ("16" in gpu_name and "v100" not in gpu_name) or "1060" in gpu_name or "1070" in gpu_name or "1080" in gpu_name or "p40" in gpu_name:
        use_half = False
    else:
        use_half = True
elif torch.backends.mps.is_available():
    device = "mps"
    use_half = False  # half precision not reliably supported on MPS
else:
    device = "cpu"
    use_half = False

# Load the RVC model weights
cpt = torch.load(model_path, map_location="cpu")
tgt_sr = cpt["config"][-1]  # target sampling rate of the model
# Adjust config for number of speakers (for multi-speaker models)
if "emb_g.weight" in cpt["weight"]:
    cpt["config"][-3] = cpt["weight"]["emb_g.weight"].shape[0]
if_f0 = cpt.get("f0", 1)  # whether model uses pitch input
# Instantiate model architecture
if if_f0 == 1:
    net_g = SynthesizerTrnMs256NSFsid(*cpt["config"], is_half=use_half)
else:
    net_g = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
# Remove unnecessary training modules and load weights
if hasattr(net_g, "enc_q"):
    del net_g.enc_q
net_g.load_state_dict(cpt["weight"], strict=False)
net_g.eval().to(device)
net_g = net_g.half() if use_half else net_g.float()

# Load the content encoder (Hubert model for content features)
print("Loading content encoder (Hubert model)...")
models, saved_cfg, task = checkpoint_utils.load_model_ensemble_and_task(["hubert_base.pt"], suffix="")
hubert_model = models[0]
hubert_model.to(device)
hubert_model = hubert_model.half() if use_half else hubert_model.float()
hubert_model.eval()

# Initialize the voice conversion pipeline
try:
    vc = VC(tgt_sr, device, use_half)
except TypeError:
    class _VCConfig:
        def __init__(self, dev, half):
            self.device = dev
            self.is_half = half
    vc = VC(tgt_sr, _VCConfig(device, use_half))

# Configure conversion settings
sid = 0  # speaker ID (for multi-speaker models, adjust as needed)
f0_up_key = 0  # no pitch shift
f0_method = "harvest"  # f0 extraction method: "harvest" or "pm"
# Check for any index file for retrieval-based voice conversion in the model folder
index_file = ""
index_rate = 0.0
for file_name in os.listdir(model_dir_path):
    if file_name.lower().endswith(".index"):
        index_file = os.path.join(model_dir_path, file_name)
        index_rate = 1.0  # use full retrieval feature (adjust if needed)
        break

# Setup queues for audio data communication between threads
input_queue = queue.Queue(maxsize=8)
output_queue = queue.Queue(maxsize=8)
running = True

# Audio processing thread: reads from input_queue, processes audio, writes to output_queue
def audio_processing_thread():
    while running:
        try:
            audio_chunk = input_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        # Resample input chunk to 16000 Hz for the content model if needed
        if tgt_sr != 16000:
            orig_len = len(audio_chunk)
            new_len = int(np.rint(orig_len * 16000 / tgt_sr))
            new_len = new_len if new_len > 0 else 1
            audio_chunk_16k = np.interp(
                np.linspace(0, orig_len, new_len, endpoint=False),
                np.arange(orig_len),
                audio_chunk
            ).astype(np.float32)
        else:
            audio_chunk_16k = audio_chunk.astype(np.float32)
        # Ensure mono
        if audio_chunk_16k.ndim > 1:
            audio_chunk_16k = audio_chunk_16k.mean(axis=1)
        # Prepare arguments for pipeline
        f0_file = None
        times = [0, 0, 0]
        try:
            if index_file:
                audio_output = vc.pipeline(hubert_model, net_g, sid, audio_chunk_16k, times, f0_up_key, f0_method, index_file, index_rate, if_f0, f0_file=f0_file)
            else:
                audio_output = vc.pipeline(hubert_model, net_g, sid, audio_chunk_16k, times, f0_up_key, f0_method, "", 0.0, if_f0, f0_file=f0_file)
        except Exception as e:
            print(f"Error during voice conversion: {e}", file=sys.stderr)
            audio_output = None
        if audio_output is not None:
            if not isinstance(audio_output, np.ndarray):
                audio_output = np.array(audio_output)
            # Convert to float32 [-1,1]
            if np.issubdtype(audio_output.dtype, np.integer):
                audio_float = audio_output.astype(np.float32) / 32768.0
            else:
                audio_float = audio_output.astype(np.float32)
            audio_float = np.clip(audio_float, -1.0, 1.0)
            expected_frames = block_size
            if len(audio_float) < expected_frames:
                audio_float = np.pad(audio_float, (0, expected_frames - len(audio_float)), mode='constant')
            elif len(audio_float) > expected_frames:
                audio_float = audio_float[:expected_frames]
            output_queue.put(audio_float)
        else:
            output_queue.put(np.zeros(block_size, dtype=np.float32))

# Determine input/output channel counts
input_channels = 1
out_dev_info = sd.query_devices(out_device)
output_channels = 2 if out_dev_info['max_output_channels'] >= 2 else 1

# Use 0.5 second audio blocks for processing
block_size = int(0.5 * tgt_sr)

# Start the processing thread
thread = threading.Thread(target=audio_processing_thread, daemon=True)
thread.start()

# SoundDevice callback function
def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        print(f"Audio callback status: {status}", file=sys.stderr)
    # Copy and down-mix input to mono
    data = indata.copy()
    mono_data = data[:, 0]
    # Send input to processing thread (drop if queue is full to avoid lag)
    try:
        input_queue.put_nowait(mono_data)
    except queue.Full:
        pass
    # Retrieve audio from processing thread if available
    if not output_queue.empty():
        processed = output_queue.get_nowait()
        if output_channels == 2:
            # Duplicate mono to stereo
            if processed.ndim == 1:
                outdata[:, 0] = processed
                outdata[:, 1] = processed
            else:
                outdata[:] = processed
        else:
            # Mono output
            if processed.ndim == 1:
                outdata[:, 0] = processed
            else:
                outdata[:, 0] = processed[:, 0]
    else:
        outdata.fill(0)

# Start audio stream
print("\nStarting real-time voice conversion... Press Ctrl+C to stop.")
try:
    with sd.Stream(device=(in_device, out_device),
                   samplerate=tgt_sr,
                   blocksize=block_size,
                   dtype='float32',
                   channels=(input_channels, output_channels),
                   callback=audio_callback):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopping voice conversion.")
finally:
    # Stop the processing thread
    running = False
    thread.join(timeout=1.0)
    sys.exit(0)
