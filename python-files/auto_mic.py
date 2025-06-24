# Descrição:
# Versão final com cache de perfil e capacidade de re-treinamento.
# 1. Salva o perfil de áudio aprendido em um arquivo de cache.
# 2. Ao iniciar, carrega o perfil do cache, se existir, para operação imediata.
# 3. Se o cache não existir, executa a fase de aprendizagem e cria o cache.
# 4. Permite que o usuário digite "treinar" no terminal a qualquer momento para
#    iniciar uma nova fase de aprendizagem e atualizar o cache.

import sounddevice as sd
import numpy as np
import librosa
import time
import sys
import threading
import queue
import os
from pathlib import Path # << NOVO/MODIFICADO
from enum import Enum, auto

# --- Bloco de Importação Condicional para Controle de Volume (Windows) ---
pycaw_enabled = False
if sys.platform == "win32":
    try:
        from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        pycaw_enabled = True
    except ImportError:
        print("Aviso: A biblioteca 'pycaw' não foi encontrada. O controle de volume não funcionará.")

#Configuração do Cache
CACHE_DIR = Path("C:/auto_mic_cache")
CACHE_FILENAME = "audio_profile.npz"
CACHE_FILE_PATH = CACHE_DIR / CACHE_FILENAME

# --- Configurações Globais ---
SAMPLE_RATE = 44100
WINDOW_SECONDS = 1.0
WINDOW_SAMPLES = int(SAMPLE_RATE * WINDOW_SECONDS)
BLOCK_SIZE = 2048
ENERGY_THRESHOLD = 0.002

# --- Configurações de Detecção ---
LEARNING_DURATION_S = 20.0 
THRESHOLD_STD_DEVS = 4.0
CONFIRMATION_COUNT_TO_ALERT = 4
CONFIRMATION_COUNT_TO_RECOVER = 6

# --- Configurações da Impressão Digital Espectral ---
NUM_FINGERPRINT_BINS = 50
FINGERPRINT_THRESHOLD_STD_DEVS = 2.5

class SystemState(Enum):
    LEARNING = auto()
    OPERATIONAL = auto()

class BackgroundSoundMonitor:
    def __init__(self):
        print("--- Inicializando Detector Robusto v5 (com Cache) ---")
        self._initialize_state()
        self._initialize_mic_volume_control()
        self._load_profile_from_cache_or_learn() 

    def _initialize_state(self):
        self.state = SystemState.LEARNING # Estado inicial padrão
        self.processing_queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()
        self.passthrough_active = threading.Event()
        self.audio_buffer = np.zeros(WINDOW_SAMPLES, dtype=np.float32)
        
        self.learning_features_mfcc = []
        self.learning_features_stft = []
        self.learning_start_time = 0
        
        self.profile_mean = None
        self.profile_std_dev = None
        self.fan_fingerprint_indices = None
        self.fan_energy_lower_bound = None
        
        self.absent_counter = 0
        self.present_counter = 0
        self.mic_volume_interface = None

    def _initialize_mic_volume_control(self):
        if not pycaw_enabled: return
        try:
            CoInitialize()
            devices = AudioUtilities.GetMicrophone()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.mic_volume_interface = interface.QueryInterface(IAudioEndpointVolume)
            self.mic_volume_interface.SetMasterVolumeLevelScalar(1.0, None)
            current_vol = self.mic_volume_interface.GetMasterVolumeLevelScalar()
            print(f"✅ Controle de volume iniciado. Volume: {current_vol*100:.0f}%.")
        except Exception as e:
            self.mic_volume_interface = None
            print(f"⚠️ AVISO: Não foi possível inicializar o controle de volume. Erro: {e}")
            if 'CoInitialize' in str(e): CoUninitialize()

    # << NOVO/MODIFICADO >>: Lógica de Carregamento do Cache
    def _load_profile_from_cache_or_learn(self):
        if CACHE_FILE_PATH.exists():
            print(f"\n[CACHE] Encontrado arquivo de perfil em: {CACHE_FILE_PATH}")
            try:
                with np.load(CACHE_FILE_PATH) as data:
                    self.profile_mean = data['mean']
                    self.profile_std_dev = data['std']
                    self.fan_fingerprint_indices = data['indices']
                    self.fan_energy_lower_bound = data['bound']
                
                self.state = SystemState.OPERATIONAL
                print("✅ [OPERACIONAL] Perfil carregado do cache. Monitoramento ativo.")
                print('   -> Para re-treinar, digite "treinar" e pressione Enter.')
                return
            except Exception as e:
                print(f"⚠️ AVISO: Falha ao carregar o cache ({e}). Iniciando nova aprendizagem.")
        
        # Se o cache não existe ou falhou ao carregar, inicia a aprendizagem
        self._setup_learning_phase()

    # << NOVO/MODIFICADO >>: Lógica de Salvamento no Cache
    def _save_profile_to_cache(self):
        if self.profile_mean is None: return
        print(f"\n[CACHE] Salvando novo perfil em: {CACHE_FILE_PATH}")
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            np.savez(CACHE_FILE_PATH, 
                     mean=self.profile_mean, 
                     std=self.profile_std_dev,
                     indices=self.fan_fingerprint_indices,
                     bound=self.fan_energy_lower_bound)
            print("💾 Perfil salvo com sucesso.")
        except Exception as e:
            print(f"❌ ERRO: Não foi possível salvar o arquivo de cache. Erro: {e}")
            print("   -> Verifique as permissões de escrita na pasta C:/auto_mic_cache/")

    # << NOVO/MODIFICADO >>: Inicia a fase de aprendizagem
    def _setup_learning_phase(self):
        self.state = SystemState.LEARNING
        self.learning_features_mfcc.clear()
        self.learning_features_stft.clear()
        self.learning_start_time = time.time()
        self.passthrough_active.set()
        
        print(f"\n[APRENDIZAGEM] Construindo perfil por {int(LEARNING_DURATION_S)} segundos.")
        print("   -> MODO PASSTHROUGH ATIVO: Você ouvirá o som do microfone.")
        print("   -> Mantenha apenas o som de fundo normal (ventilador).")

    def _check_and_reset_mic_volume(self):
        # (código sem alteração)
        if self.mic_volume_interface is None: return
        try:
            current_vol = self.mic_volume_interface.GetMasterVolumeLevelScalar()
            if current_vol < 0.99:
                self.mic_volume_interface.SetMasterVolumeLevelScalar(1.0, None)
                print(f"🔊 Volume do microfone redefinido para 100% (estava em {current_vol*100:.0f}%).")
        except Exception as e:
            print(f"Erro ao verificar/definir volume do microfone: {e}")
            self.mic_volume_interface = None

    def _extract_features(self, audio):
        # (código sem alteração)
        if np.sqrt(np.mean(audio**2)) < ENERGY_THRESHOLD: return None, None
        if len(audio) < 2048: return None, None
        mfccs = np.mean(librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=20, n_fft=2048).T, axis=0)
        stft = np.abs(librosa.stft(audio, n_fft=2048))
        if np.isnan(mfccs).any() or not np.isfinite(mfccs).all(): return None, None
        return mfccs, stft

    def _build_profile(self):
        if not self.learning_features_mfcc:
            print("\n❌ ERRO: Nenhum som detectado. Verifique o microfone.")
            # Em vez de recursão, apenas reinicia a fase e retorna
            self._setup_learning_phase() # Tenta aprender de novo
            return

        feature_matrix = np.array(self.learning_features_mfcc)
        self.profile_mean = np.mean(feature_matrix, axis=0)
        self.profile_std_dev = np.std(feature_matrix, axis=0)
        self.profile_std_dev[self.profile_std_dev < 1e-5] = 1e-5
        
        mean_spectrogram = np.mean(np.array(self.learning_features_stft), axis=0)
        mean_energy_per_bin = np.mean(mean_spectrogram, axis=1)
        self.fan_fingerprint_indices = np.argsort(mean_energy_per_bin)[-NUM_FINGERPRINT_BINS:]
        
        fingerprint_energies = [np.sum(stft[self.fan_fingerprint_indices,:]) for stft in self.learning_features_stft]
        fan_fingerprint_energy_mean = np.mean(fingerprint_energies)
        fan_fingerprint_energy_std = np.std(fingerprint_energies)
        self.fan_energy_lower_bound = fan_fingerprint_energy_mean - (FINGERPRINT_THRESHOLD_STD_DEVS * fan_fingerprint_energy_std)

        # Limpa listas de aprendizagem para liberar memória
        self.learning_features_mfcc.clear()
        self.learning_features_stft.clear()
        del feature_matrix, mean_spectrogram, mean_energy_per_bin, fingerprint_energies
        
        self.passthrough_active.clear() 
        self.state = SystemState.OPERATIONAL
        self._save_profile_to_cache() 
        print("\n✅ [OPERACIONAL] Perfil concluído. Monitoramento ativo.")
        print('   -> Para re-treinar, digite "treinar" e pressione Enter.')

    def audio_callback(self, indata, outdata, frames, time_info, status):
        # (código sem alteração)
        if self.passthrough_active.is_set(): outdata[:] = indata
        else: outdata.fill(0)
        try:
            self.processing_queue.put_nowait(indata.copy())
        except queue.Full:
            try:
                # Descarta o item mais antigo para evitar bloqueio/memória
                self.processing_queue.get_nowait()
                self.processing_queue.put_nowait(indata.copy())
            except queue.Empty:
                pass

    def _processing_thread(self):
        # (código com pequenas alterações)
        last_volume_check = 0
        while not self.stop_event.is_set():
            try:
                chunk = self.processing_queue.get(timeout=0.5)
                self.audio_buffer = np.roll(self.audio_buffer, -len(chunk))
                self.audio_buffer[-len(chunk):] = chunk.flatten()
            except queue.Empty: continue
            
            if time.time() - last_volume_check > 2.0:
                self._check_and_reset_mic_volume()
                last_volume_check = time.time()
                
            if self.state == SystemState.LEARNING:
                # Usa o start_time do objeto
                if time.time() - self.learning_start_time > LEARNING_DURATION_S: 
                    self._build_profile()
                    continue
                mfccs, stft = self._extract_features(self.audio_buffer)
                if mfccs is not None:
                    self.learning_features_mfcc.append(mfccs)
                    self.learning_features_stft.append(stft)
            
            elif self.state == SystemState.OPERATIONAL:
                current_mfccs, current_stft = self._extract_features(self.audio_buffer)
                is_background_absent = True
                if current_mfccs is not None:
                    anomaly_score = np.mean(np.abs((current_mfccs - self.profile_mean) / self.profile_std_dev))
                    is_texture_different = anomaly_score > THRESHOLD_STD_DEVS
                    if not is_texture_different: is_background_absent = False
                    else:
                        current_fingerprint_energy = np.sum(current_stft[self.fan_fingerprint_indices,:])
                        is_fan_present_in_spectrum = current_fingerprint_energy > self.fan_energy_lower_bound
                        if is_fan_present_in_spectrum: is_background_absent = False

                if is_background_absent: self.present_counter = 0; self.absent_counter += 1
                else: self.absent_counter = 0; self.present_counter += 1
                
                if not self.passthrough_active.is_set() and self.absent_counter >= CONFIRMATION_COUNT_TO_ALERT:
                    self.passthrough_active.set()
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print(f"\n{'!'*60}\n🔇 [{timestamp}] ALERTA: O som de fundo desapareceu.\n   -> Ativando modo de diagnóstico.\n{'!'*60}\n")
                
                elif self.passthrough_active.is_set() and self.present_counter >= CONFIRMATION_COUNT_TO_RECOVER:
                    self.passthrough_active.clear()
                    self.absent_counter = 0; self.present_counter = 0
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print(f"{'='*60}\n✅ [{timestamp}] RECUPERAÇÃO: Som de fundo detectado novamente.\n{'='*60}")

    # Thread para input do usuário
    def _user_input_thread(self):
        while not self.stop_event.is_set():
            try:
                command = input() # Isso irá bloquear até que o usuário pressione Enter
                if command.strip().lower() == 'treinar':
                    print("\n[COMANDO] Recebido comando para re-treinar o perfil.")
                    self._setup_learning_phase()
            except (EOFError, KeyboardInterrupt):
                # Ocorre quando o programa está sendo fechado
                break

    def run(self):
        # Inicia as duas threads
        self.processor_thread = threading.Thread(target=self._processing_thread, daemon=True)
        self.input_thread = threading.Thread(target=self._user_input_thread, daemon=True)
        
        self.processor_thread.start()
        self.input_thread.start()

        try:
            with sd.Stream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, channels=1, dtype='float32', callback=self.audio_callback):
                self.processor_thread.join() # O programa principal espera aqui
                self.input_thread.join()
        except Exception as e:
            print(f"\n❌ Ocorreu um erro fatal durante o stream: {e}", file=sys.stderr)
        finally:
            self.cleanup()

    def cleanup(self):
        if not self.stop_event.is_set():
            print("\n👋 Encerrando o monitor...")
            self.stop_event.set()
        # Aguarda threads terminarem
        if hasattr(self, 'processor_thread') and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=2)
        if hasattr(self, 'input_thread') and self.input_thread.is_alive():
            # Não há como "desbloquear" input() facilmente, mas join para garantir
            self.input_thread.join(timeout=2)
        # Libera recursos COM apenas se inicializado
        if pycaw_enabled and self.mic_volume_interface is not None:
            try:
                CoUninitialize()
            except Exception:
                pass
        print("Programa encerrado.")

def main():
    monitor = BackgroundSoundMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        monitor.cleanup()

if __name__ == "__main__":
    main()