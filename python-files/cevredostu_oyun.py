import json
import os
from datetime import date, timedelta

# Kategoriler ve puanlar
CATEGORIES = {
    "SU": 10,
    "PLASTIK_ATIK": 8,
    "ULASIM_ENERJI": 7
}

# Görevler
TASKS = [
    ("Diş fırçalarken suyu kapalı tuttum", "SU"),
    ("Duş alırken suyu sabunlanma sırasında kapattım", "SU"),
    ("Elde bulaşık yıkarken musluğu sürekli açık bırakmadım / Bulaşığı makinede yıkadım", "SU"),
    ("Geri dönüştürülebilir atıkları ayrı biriktirdim", "PLASTIK_ATIK"),
    ("Cam/plastik/kâğıt/pil gibi atıkları ilgili kutuya attım", "PLASTIK_ATIK"),
    ("Tek kullanımlık plastik yerine tekrar kullanılabilir şişe kullandım", "PLASTIK_ATIK"),
    ("Bez çanta ile alışveriş yaptım", "PLASTIK_ATIK"),
    ("Plastik pipet yerine metal/bambu pipet kullandım", "PLASTIK_ATIK"),
    ("Bugün yürüyerek ya da bisikletle ulaşımı tercih ettim", "ULASIM_ENERJI"),
    ("Toplu taşıma kullandım, özel araç kullanmadım", "ULASIM_ENERJI"),
    ("Gereksiz yanan ışıkları kapattım", "ULASIM_ENERJI"),
    ("Cihazları prizden çıkardım (stand-by tüketimi önledim)", "ULASIM_ENERJI"),
    ("Enerji tasarruflu ampul kullandım", "ULASIM_ENERJI"),
    ("Asansör yerine merdiven kullandım", "ULASIM_ENERJI"),
]

DATA_FILE = "cevredostu_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"streak": 0, "lastSuccessDate": None, "days": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def main():
    data = load_data()
    streak = data.get("streak", 0)
    last_date = data.get("lastSuccessDate", None)
    days = data.get("days", {})
    today = date.today().isoformat()

    # Bugünün seçili maddeleri
    today_selected = set(days.get(today, []))

    print("Çevre Dostu Günlük Görevleri:")
    print("-" * 40)
    if today_selected:
        print("Bugün daha önce seçtiğiniz maddeler:")
        for i in sorted(today_selected):
            desc, cat = TASKS[i]
            print(f"{i+1}. {desc} (+{CATEGORIES[cat]} puan)")
        print("\nYeni seçimler ekleyebilirsiniz. Daha önce seçtikleriniz tekrar seçilemez.")
    else:
        print("Bugün henüz seçim yapmadınız.")

    group_size = 4
    num_tasks = len(TASKS)
    new_selected = set()

    for start in range(0, num_tasks, group_size):
        end = min(start + group_size, num_tasks)
        print(f"\nGörevler {start+1}-{end}:")
        for idx in range(start, end):
            desc, cat = TASKS[idx]
            already = " (SEÇİLDİ)" if idx in today_selected else ""
            print(f"{idx+1}. {desc} (+{CATEGORIES[cat]} puan){already}")
        print("Yaptığınız yeni görevlerin numaralarını aralarına virgül koyarak girin (ör: 1,3). Daha önce seçtikleriniz tekrar seçilemez:")
        inp = input("Seçiminiz: ")
        try:
            indices = [int(i.strip()) for i in inp.split(",") if i.strip().isdigit()]
        except Exception:
            indices = []
        for i in indices:
            if start < i <= end and (i-1) not in today_selected:
                new_selected.add(i-1)

    # Bugünün tüm seçili maddeleri (öncekiler + yeniler)
    all_selected = today_selected.union(new_selected)
    days[today] = list(all_selected)
    data["days"] = days

    total_point = sum(CATEGORIES[TASKS[i][1]] for i in all_selected)
    print(f"\nBugünkü Toplam Puanınız: {total_point}")

    # Streak ve başarı mesajı
    if total_point >= 25:
        if last_date != today:
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            if last_date == yesterday:
                streak += 1
            else:
                streak = 1
            data["streak"] = streak
            data["lastSuccessDate"] = today
            save_data(data)
            if streak == 1:
                print("Tebrikler! Bugün çevre dostu bir gün geçirdin!")
            elif streak == 2:
                print("Harika! 2 gündür üst üste çevre dostusun!")
            elif streak == 3:
                print("Mükemmel! 3 gündür üst üste çevre dostusun!")
            else:
                print(f"{streak} gündür üst üste çevre dostusun! Böyle devam et!")
        else:
            print("Bugün zaten çevre dostu olarak kaydedildin!")
    else:
        print("25 puana ulaşamadın, gün içinde tekrar seçim yapabilirsin!")

    print(f"Streak (üst üste gün): {data.get('streak', 0)}")
    save_data(data)

if __name__ == "__main__":
    main() 