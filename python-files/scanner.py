import os
import hashlib

# ---- רשימת Hashes (SHA1) ----
hashes_to_check = {
    "321684ad00246673cedb70ac06d07a06a7be8bf4": "Susano",
    "c981e506dd06d254c456b64fb01de3e5a73ee178": "Eulen",
    "37da86fbc31ec590c77c8dcce3db79dae14bef47": "Gosth",
    "430ef7824759dc2295eb6cc5591bf2558c71e350": "Xino",
    "ac374bd498c4e9e146a8ea90d581b8083b785ec5": "Free Cheat",
    "98839054af71f795961fbffacd43f75b16344fda": "Generic Bypass",
    "da418ec66cc71f19dbb7fd35cbfe09696965af04": "Super Bypass",
    "fb85802b658d983db159726f1ac7b29ef72fab2f": "USB Oblivion",
    "9ea1ebdf39b90a6f75c878c4026c33afbde8dfd1": "Core Bypass",
    "5610ada1f4f867b284a28a23e1f37143c4dbd114": "Grin Bypass",
    "c1796c2ffbf2d60afeb2b4d08170af606c3ab143": "Spotless Private",
    "8add953588e96af356df103abb0adab6f18a0ea0": "Sacred Bypass",
    "fd5d690ab282dcb622b4b6f31a226e3e880b88a3": "Spotless Private",
    "98f189dc7075461d1899e7952d6f455e1b95c66f": "420 solutions",
    "0867a3489caa0d187590a7c3f456a1cae56e67d8": "9z cleaner",
    "eff91ebe94a423f03edb2633b3f83c7ce35bd419": "7even Store Bypass",
    "e7affcd1d9d8ff71ad56b80d038803ed6687acdf": "RavenX Spoofer",
    "ae54939d8736c38d2e9660b59e4110441d9c4f20": "ProjectX",
    "ec25f05ee99ecf12338abdd006682b4d0e4b8a39": "Unload Lite",
    "935dd75420ea520f5cf64c0569cd90bd8e98ef8a": "Unload Full",
    "d6b1a7609d93eb43d77502a9eac986040d0d54d1": "Sinister Bypass",
    "478bfe1fd30a7382709216f72d5d6b70a8407b6f": "Sactioned Bypass",
    "28edc3dd6ade4ad97a9d051c3fac4a0798a52cce": "9zx Cheat",
    "09197795d759e56477765ee37a7b11511d9fa427": "9z Bypass",
    "1699b594612cb29084c10117dc17762ee94c2f78": "Generic Cheat Executable",
    "dec3798931c574fdff3782b6dc8b893cebd843e6": "Fenix",
    "a563ed92a0507bd1877bc751e671ad443870d1d4": "Void Mod Menu",
    "3c8a822bb32e837dffe2033a8a07e62316138c17": "MinKernel",
    "b27c9ced6419575d18e0be9a79985a1937a0e8c9": "TD Premium",
    "7fb5cbdaa3f42594480b56ef4d81363a9fa07f57": "Flyside",
    "2f60e2956284937d7b36ff7c928ea123accb391c": "Eulen",
    "53d8b9f50743045ae3bb417edd8ee62481d5ec10": "Gosth",
    "13eb0c6b9a6c2df19bb8e0e1fb0c1c32ba0c0cd7": "DC Free",
    "9686a67ba28d96ad494d40f81719a877058d94be": "Free Cheat",
    "2103baf8c8690905951d4ba10f30b29fa8cc5508": "UnAttendGC/Everest",
    "919e2ed42808f89052f6f7d56075606a28a48a2a": "Miguel Cheat",
    "ce625dcc2a50d5ca393cddb4133038aed26b2842": "Stopped Bypass Advanced",
    "742d0eefd055f4838da19ca42b7f62592f1c9aa2": "Stopped Bypass Basic",
    "0fdfed6e59e24dc2c22a263a40f385ccd89b8922": "Woofer Perma Spoofer",
    "b06dbd74c822220a9a2393e589702afb4516604a": "Perma Spoofer",
    "c2b58573750bc7c403af092d630e671f50b034ff": "Superino Bypass",
    "6019455241951d24859045fbc3fd1adb08d58234": "216 Pure Mode Bypass",
    "db65a7b1f2d283c31aebb5a7f98a1c5d64c4bed6": "Macho Cheat",
    "771b9f851570314be28a6abfa5aa3c44af247573": "Keyser",
    "a71533d382d8a99ed8b410bdbff268808505a12a": "KO Free Cheat",
    "301551834bee86fb32b6015f90a224ca93cc2406": "NK External Cheat",
    "317252aa51d966bf573c4fd3600521ebe107d295": "Skript",
    "5b94e0649ec13b06c48974533f0f6de0b5b2c357": "XRC Bypass",
    "e9901da1c370a8d11f915de86b24282161d13744": "VDA Cheat",
    "e64104326b9de4863e66128988d9561dea50fe8d": "Quanta Bypass",
    "6dadff8ce0ca1faec18135a7489ad6ce25062e6b": "TZX",
    "03584814d4a2a8bbb51b1ab37cccb06944857f1b": "Interface Cleaner",
    "509be5b4344e2891dba8f88102bb34a69169e357": "Vanish Bypass",
    "877faf64fcd2a6a4231903d726cfa4398a20351d": "Susano",
    "59af915b7a50c668365677287537a9edacf09bca": "Stopped Private Cheat",
    "c38c64ef5805f46af2d1e1ea6453d9f6530de80a": "NoVida.rpf",
    "a5733d03c9125968a23761ccbd055861af50a7eb": "Susano",
    "a207f61c1affb9fe2cdbc10a97b12278c5632719": "TZ Cheats",
    "0c82361e84264b677261895d627fe992a28b892b": "TZX",
    "49b2e3a1b5e1f45db206aecc4719507b9e027545": "TZX",
    "4de0f90074d21a8378b7eec791f919a473175cb1": "TZX",
    "c84ea53bf974d43f9d691774d5fb6d22aab3fd4c": "Krysha Private Cheat",
    "bfb08901001f3c901496fcb34f6c56bc1d7ca75e": "Stopped Bypass",
    "487c99e9347f8c5e1ce3a525a1817e6b153aeadb": "XRC Bypass",
    "1575e62652693bf22190b714416207d59e702d28": "Fresh Bypass",
    "d43ba22cf0f4bdd7d126cf0878d241e3aab20289": "Venacy Cheat",
    "facd169e5d3d393330636322cc65ea7502268617": "Venacy Cheat",
    "04e6d9ea037494b4b9e7de48db28a4eb0f5efc80": "TZ Internal Testing Version",
    "874ce0252e8b5866f429bd726a65add81b62aa87": "TZ Internal Stable Version",
    "47d61dd07b78cc306f94c672372c9171beca4917": "Mix Code Bypass",
    "9d966de30148dfb5cce0005c3740680f4cde3d43": "Solutions Bypass",
    "cab8832f04351dc44b1cec6ac9db195ea8f8c310": "Quantity Cheat",
    "abdb905a02891177cff96f27eef0bcbef96362ac": "Weed Bypass",
    "4e5189a3b6121276ef0ce40eb74ecdf5e8201016": "EZ Project Cheat",
    "85275138d9ac8900193f3a4496b610da6ff20c12": "Fresh Bypass",
    "3904ba9b4797f4258204abac96ac30e6fb932979": "Lavender Cheat",
    "6b41360dbb2330cf23d0d4cc67f8fad7c9c321cd": "FLK FiveM Cheat",
    "cd355e04fc63e0fad828d5f0c5c2b7aaff62cbb7": "FLK FiveM Bypass",
    "c43c7ef674fe31bfcdbe3abed7c93631f2717c32": "FLK FiveM Spoofer",
    "d07949bfe15ec7dabb44b1af7bf93b52372c953d": "Unity Bypass",
    "053f4689876beec507d93635ca999686bce66549": "Wraith Solutions",
    "0f16fe39586ee496386c627617dedee84b6e9ceb": "Unique Bypass",
    "a1341b644fc7f50a5f403cec33ec480c12a1c8f6": "Atlantis Solutions",
    "6288b3bbd8c656f40f1826b29fac88645741bc67": "FLK FiveM External",
    "a9be0ea551912472059d627c53e9c4b64680aa91": "FLK Bypass",
    "c7b82aabfffac51a4a9f25ba77e3db2872cd3862": "Skript.gg",
}

# ---- רשימת סטרינגים ----
strings_to_check = [
    "exloader.net", "taskthow.exe", "loader.exe", "loader_prod.exe", "launcher.exe", "supernatueal.exe",
    "public.zip", "memory_aim_temp", "password_is_eulen.rar", "loader.cfg", "settings.cock", "taceless",
    "grin bypass", "spotless", "password_is_eulen (1).rar", "password_is_eulen (2).rar", "password_is_eulen (3).rar",
    "loader.exe", "tzx.zip", "tzx (1).zip", "tzx (2).zip", "tzx (3).zip", "public (1).zip", "public (2).zip",
    "public (3).zip", "password_is_eulen", "tdpremium.zip", "free cheats", "tdpremium (1).zip", "tdpremium.rar",
    "hack", "bypass", "usbdeview", "loader_prod", "NoLess.exe", "modmenu", "keyauth", "susano", "eulen",
    "redengine", "cutiehook", "Wexize Revamp", "gosth", "supernatural", "tdpremium", "9z cleaner", "9z",
    "taskthow", "ts3clietnt_win64.dll", "ts3clietnt_win64/.dll", "ts3client_win64.exe", "xino"
]skip_dirs = [
    "C:\\Windows"
    "C:\\ProgramData"
]

# ---- מגבלת גודל קובץ (בבתים, כאן 100MB) ----
MAX_FILE_SIZE = 100 * 1024 * 1024

def get_file_hash(path, algo="sha1"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_directory(root_path):
    for root, dirs, files in os.walk(root_path):
        # דילוג על תיקיות מערכת
        if any(root.startswith(sd) for sd in skip_dirs):
            continue

        for file in files:
            file_path = os.path.join(root, file)

            # בודק סיומת
            if not file.lower().endswith((".exe", ".dll", ".bat")):
                continue

            # בודק גודל קובץ
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue
            except:
                continue

            try:
                # בדיקה לפי Hash
                file_hash = get_file_hash(file_path, "sha1")
                if file_hash in hashes_to_check:
                    print(f"[HASH] נמצא: {file_path} → {hashes_to_check[file_hash]}")

                # בדיקה לפי שם
                for s in strings_to_check:
                    if s.lower() in file.lower():
                        print(f"[STRING] נמצא: {file_path} → מכיל '{s}'")

            except Exception as e:
                print(f"שגיאה בקריאת {file_path}: {e}")

if __name__ == "__main__":
    print("מתחיל סריקה על כל המחשב...")
    scan_directory("C:\\")
    print("סריקה הסתיימה.")