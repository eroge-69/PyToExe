import os
import numpy as np
import librosa
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

def list_audio_files(audio_dir):
    files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    return files

def print_menu(files):
    print("Proszę wybrać plik audio do rozpoznania wieku:")
    for i, fname in enumerate(files, 1):
        print(f"[{i}] {fname}")
    print(f"[{len(files)+1}] Zamknij")

def extract_features(file_path, n_mfcc=13):
    try:
        y, sr = librosa.load(file_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        delta = librosa.feature.delta(mfcc)
        delta2 = librosa.feature.delta(mfcc, order=2)
        features = np.concatenate([mfcc, delta, delta2], axis=0)
        mean = np.mean(features, axis=1)
        var = np.var(features, axis=1)
        feature_vector = np.concatenate([mean, var])
        return feature_vector.reshape(1, -1)
    except Exception as e:
        print(f"Nie udało się przetworzyć {file_path}: {e}")
        return None

def recognize_age(file_path, X_train, y_train, k=5):
    features = extract_features(file_path)
    if features is None:
        return "Błąd ekstrakcji cech – nie rozpoznano wieku."
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    pred = knn.predict(features)[0]
    label_map = {
        1: "Młodzież (do 19 lat)",
        2: "Młodzi dorośli (20-39)",
        3: "Starsi dorośli (40-59)",
        4: "Seniorzy (60+)"
    }
    return label_map.get(pred, f"Nieznana klasa ({pred})")

def test_classifier_per_class(X_train, y_train, X_test, y_test, k=5):
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\nSkuteczność ogólna kNN (k={k}): {acc*100:.2f}%")

    cm = confusion_matrix(y_test, y_pred, labels=[1, 2, 3, 4])
    print("\nMacierz pomyłek:")
    print(cm)

    print("\nSkuteczność dla każdej klasy:")
    class_names = {
        1: "Młodzież (do 19 lat)",
        2: "Młodzi dorośli (20-39)",
        3: "Starsi dorośli (40-59)",
        4: "Seniorzy (60+)"
    }

    for i, class_id in enumerate([1, 2, 3, 4]):
        true_positives = cm[i, i]
        total_actual = cm[i, :].sum()
        acc_class = true_positives / total_actual if total_actual > 0 else 0
        print(f" - {class_names[class_id]}: {acc_class*100:.2f}% ({true_positives}/{total_actual})")

def main():
    audio_dir = "audio"
    X_train = np.load("data/X_train.npy")
    y_train = np.load("data/y_train.npy")

    if os.path.exists("data/X_test.npy") and os.path.exists("data/y_test.npy"):
        X_test = np.load("data/X_test.npy")
        y_test = np.load("data/y_test.npy")
        test_classifier_per_class(X_train, y_train, X_test, y_test, k=5)
    else:
        print("Brak danych testowych (X_test.npy, y_test.npy).")

    while True:
        files = list_audio_files(audio_dir)
        if not files:
            print("Brak plików .wav w katalogu 'audio/'. Dodaj nagrania i spróbuj ponownie.")
            break
        print_menu(files)
        try:
            choice = int(input("Proszę podać numer pliku i wcisnąć Enter: "))
            if choice == len(files) + 1:
                print("Zamykam program.")
                break
            elif 1 <= choice <= len(files):
                file_path = os.path.join(audio_dir, files[choice - 1])
                print(f"Wybrano plik: {file_path}")
                wynik = recognize_age(file_path, X_train, y_train, k=5)
                print(f"\nWynik klasyfikacji: {wynik}\n")
                input("Proszę nacisnąć Enter, aby wrócić do menu.")
            else:
                print("Niepoprawny wybór.")
        except ValueError:
            print("Proszę podać liczbę.")

if __name__ == "__main__":
    main()
