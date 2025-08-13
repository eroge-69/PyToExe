import numpy as np
import sounddevice as sd
import argparse
import threading

# Simple one-pole low-pass filter (focus on low frequencies where "ANC" is most feasible)
class OnePoleLP:
    def __init__(self, cutoff=800.0, fs=48000.0):
        self.fs = fs
        self.z = 0.0
        self.set_cutoff(cutoff)
    def set_cutoff(self, cutoff):
        cutoff = float(np.clip(cutoff, 10.0, self.fs/2 - 100.0))
        self.cutoff = cutoff
        self.alpha = np.exp(-2.0 * np.pi * cutoff / self.fs)
        self.one_minus_alpha = 1.0 - self.alpha
    def process(self, x):
        y = np.empty_like(x)
        z = self.z
        a = self.alpha
        oma = self.one_minus_alpha
        for i in range(len(x)):
            z = oma * x[i] + a * z
            y[i] = z
        self.z = z
        return y

def list_devices():
    print(sd.query_devices())

def main():
    p = argparse.ArgumentParser(description="Naive ANC: invert mic and play it to headphones in real-time.")
    p.add_argument("--list", action="store_true", help="List audio devices and exit")
    p.add_argument("--in", dest="in_dev", type=int, default=None, help="Input device index (mic)")
    p.add_argument("--out", dest="out_dev", type=int, default=None, help="Output device index (headphones)")
    p.add_argument("--sr", type=int, default=48000, help="Sample rate (try 48000)")
    p.add_argument("--block", type=int, default=128, help="Block size (64–256, smaller = lower latency)")
    p.add_argument("--gain", type=float, default=0.5, help="Anti-noise gain (0.0–1.0 to start)")
    p.add_argument("--lp", type=float, default=800.0, help="Low-pass cutoff Hz for anti-noise (200–1200 works)")
    p.add_argument("--channels", type=int, default=1, help="Channels to use (1 or 2, 1 recommended)")
    args = p.parse_args()

    if args.list:
        list_devices()
        return

    fs = args.sr
    block = args.block
    gain = float(np.clip(args.gain, 0.0, 1.5))
    channels = 1 if args.channels not in (1, 2) else args.channels

    lp = OnePoleLP(args.lp, fs)
    limiter_ceiling = 0.9  # soft safety limit

    print("Starting. Keep your volume LOW first. Ctrl+C to stop.")
    print(f"Sample rate: {fs} Hz | Blocksize: {block} | Est. per-block latency: ~{1000*block/fs:.2f} ms")

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status, flush=True)
        # Collapse input to mono (average channels if more than one)
        x = indata.mean(axis=1) if indata.shape[1] > 1 else indata[:, 0]
        # Focus on lows (steady noise)
        x = lp.process(x)
        # Invert and scale
        y = -gain * x
        # Simple peak limiter to avoid nasty surprises
        peak = np.max(np.abs(y))
        if peak > limiter_ceiling:
            y *= (limiter_ceiling / max(peak, 1e-6))
        # Copy to output channels
        if channels == 1:
            outdata[:, 0] = y
        else:
            outdata[:, 0] = y
            outdata[:, 1] = y

    # Duplex stream (mic -> process -> headphones)
    stream = sd.Stream(
        device=(args.in_dev, args.out_dev),
        samplerate=fs,
        blocksize=block,
        dtype="float32",
        latency="low",
        channels=channels,
        callback=callback
    )

    with stream:
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            print("\nExiting. Bye!")

if __name__ == "__main__":
    main()