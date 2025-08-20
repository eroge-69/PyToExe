import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import sys
import threading


model = Model("vosk-model-small-pl-0.22")
rec = KaldiRecognizer(model, 16000)


NUM_MAP = {
    "jeden": "1", "dwa": "2", "trzy": "3", "cztery": "4",
    "pięć": "5", "piec": "5", "sześć": "6", "szesc": "6",
    "siedem": "7", "osiem": "8", "dziewięć": "9", "dziewiec": "9", "dupa" : "champion"
}

q = queue.Queue()  

def callback(indata, frames, time, status):
    try:
        if status:
            print(status, file=sys.stderr, flush=True)
        data_bytes = memoryview(indata).tobytes()

        if rec.AcceptWaveform(data_bytes):
            result = rec.Result()
            text = json.loads(result).get("text", "").lower()
            tokens = text.split()
            for t in tokens:
                if t in NUM_MAP:
                    q.put(NUM_MAP[t])
        else:
            pass

    except Exception as e:
        print("Callback exception:", e, file=sys.stderr, flush=True)

def main():
    try:
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                               channels=1, callback=callback):
            while True:
                try:
                    num = q.get(timeout=0.1)  
                    print(num, flush=True)
                except queue.Empty:
                    continue
    except KeyboardInterrupt:
        print("\nPrzerwane")
    except Exception as e:
        print("Bład uruchomienia:", e, file=sys.stderr)
    finally:
        pass

if __name__ == "__main__":
    main()
