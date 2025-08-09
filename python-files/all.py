# -------------------------
# Sound generators
# -------------------------
def sine(frequency, length_secs, amp=1.0):
    t = np.linspace(0, length_secs, int(SAMPLE_RATE * length_secs), False)
    return amp * np.sin(2 * np.pi * frequency * t)


def exponential_decay_envelope(length_samples, attack=0.001, decay=0.5):
    # quick attack then exponential decay
    env = np.ones(length_samples)
    attack_samples = max(1, int(attack * SAMPLE_RATE))
    env[:attack_samples] = np.linspace(0, 1, attack_samples)
    tail = np.arange(length_samples - attack_samples)
    # normalize tail to start at 1 and decay to near 0
    env[attack_samples:] = np.exp(-tail / (decay * SAMPLE_RATE))
    return env


def kick(length_secs=0.25):
    # Kick: pitch drop sine + envelope
    length = length_secs
    n = int(SAMPLE_RATE * length)
    t = np.linspace(0, length, n, False)
    # pitch falls from about 120Hz to 40Hz
    freqs = np.linspace(120, 40, n)
    wave_data = np.sin(2 * np.pi * freqs * t)
    env = exponential_decay_envelope(n, attack=0.001, decay=0.08)
    return (wave_data * env * 1.0).astype(np.float32)


def snare(length_secs=0.18):
    # Snare: noisy + short oscillator
    n = int(SAMPLE_RATE * length_secs)
    noise = np.random.normal(0, 1, n)
    tone = sine(1800, length_secs, amp=0.2)
    env = exponential_decay_envelope(n, attack=0.001, decay=0.06)
    out = (noise * 0.6 + tone * 0.6) * env
    # small highpass-ish by subtracting moving average
    kernel = 3
    out = out - np.convolve(out, np.ones(kernel) / kernel, mode='same')
    return out.astype(np.float32)


def hihat(length_secs=0.06):
    n = int(SAMPLE_RATE * length_secs)
    noise = np.random.normal(0, 1, n)
    env = exponential_decay_envelope(n, attack=0.0005, decay=0.02)
    # bright thin sound
    out = noise * env * 0.6
    # quick highpass effect
    out = out - np.convolve(out, np.ones(2) / 2, mode='same')
    return out.astype(np.float32)
