from transformers import AutoModelForSpeechSeq2Seq, AutoModelForCTC, AutoProcessor, pipeline
import torch
import soundfile as sf


def init_pipeline(path, model_type):
    if model_type == "whisper":
        model = AutoModelForSpeechSeq2Seq.from_pretrained(path,
                                                          use_safetensors=True, )
    else:
        model = AutoModelForCTC.from_pretrained(path,
                                                use_safetensors=True, )

    if torch.cuda.is_available():
        torch_dtype = torch.float16
        device = "cuda"
    else:
        torch_dtype = torch.float32
        device = "cpu"
    model.eval()
    processor = AutoProcessor.from_pretrained(path)

    try:
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            decoder=processor.decoder,
            torch_dtype=torch_dtype,
            device=device,
        )
    except:
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )

    return pipe


def inference(pipe, model_type, audio_file):
    if model_type == "whisper":
        generate_kwargs = {"language": "de"}
        result = pipe(audio_file, generate_kwargs=generate_kwargs)
    else:
        result = pipe(audio_file)
    return result["text"]


path = "C:/Users/theti/.cache/huggingface/hub/models--sharrnah--wav2vec2-bert-CV16-de" # path_to_model_folder
# time execution
import time

start_time = time.time()
print(f"Start Pipeline initialization")
pipe = init_pipeline(path, "bert")
end_time = time.time()
print(f"Pipeline initialized in {end_time - start_time} seconds")

audio_path = "C:/Users/theti/Desktop/recording_20250715_111635.wav"
audio, sample_rate = sf.read(audio_path)
# resample to 16000 Hz if necessary
if sample_rate != 16000:
    import librosa

    audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
    sample_rate = 16000
# Perform inference
start_time = time.time()
print(f"Start Inference")
text = inference(pipe, "bert", audio)
end_time = time.time()
print(f"Inference result: {text}")
print(f"Inference completed in {end_time - start_time} seconds")