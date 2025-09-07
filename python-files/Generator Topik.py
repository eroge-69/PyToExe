import customtkinter as ctk
import random
import pickle
import os

from PIL import Image, ImageTk

# === Setup Tampilan ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create the app instance
app = ctk.CTk()
app.title("TopiKu")
app.geometry("800x600")
app.resizable(False, False)

# === Top Bar ===
top_frame = ctk.CTkFrame(app, fg_color="transparent")
top_frame.pack(fill="x", padx=10, pady=5)

app_title = ctk.CTkLabel(top_frame, text="TopiKu", font=ctk.CTkFont(size=24, weight="bold"))
app_title.pack(side="left", padx=(10, 0))

# Function to toggle the sidebar visibility
def toggle_history_sidebar():
    if sidebar_frame.winfo_ismapped():
        sidebar_frame.pack_forget()
    else:
        sidebar_frame.pack(side="right", fill="y", padx=0, pady=0)
history_button = ctk.CTkButton(top_frame, text="📚", width=40, height=32, corner_radius=12, command=toggle_history_sidebar)
history_button.pack(side="right")

# === Sidebar History ===
sidebar_frame = ctk.CTkFrame(app, width=260, fg_color="#111111")
sidebar_scrollable = ctk.CTkScrollableFrame(sidebar_frame, width=260, height=600)
sidebar_scrollable.pack(fill="both", expand=True)





topics = {
    "Persahabatan": [
        "Apa kenangan paling lucu yang kamu miliki bersama teman-teman?",
        "Apa yang menurutmu membuat persahabatan itu langgeng?",
        "Apa yang kamu cari dalam diri seorang teman?",
        "Apakah ada teman lama yang ingin kamu temui lagi? Kenapa?",
        "Pernahkah kamu merasa kesepian meskipun dikelilingi teman-temanmu?",
        "Apa arti sebuah persahabatan yang sejati bagimu?",
        "Bagaimana cara kamu mengatasi konflik dengan teman tanpa merusak hubungan?",
        "Apa hal paling keren yang pernah dilakukan temanmu untukmu?",
        "Apakah kamu pernah merasa dibenci oleh teman? Bagaimana kamu menghadapinya?",
        "Apa yang membuat kamu merasa nyaman saat bersama teman-temanmu?",
        "Bagaimana cara kamu menjaga hubungan baik dengan teman meskipun sudah jarang bertemu?",
        "Apa yang kamu lakukan saat temanmu sedang merasa down?",
        "Apa yang menurutmu membuat seorang teman sangat bisa dipercaya?",
        "Apa pengalaman paling berkesan yang kamu miliki bersama sahabatmu?",
        "Apakah kamu percaya bahwa sahabat bisa menjadi lebih dari sekadar teman? Kenapa?",
        "Apa yang menurutmu menjadi tantangan terbesar dalam menjaga persahabatan?",
        "Seperti apa cara kamu memilih teman yang baik dan dapat dipercaya?",
        "Pernahkah kamu merasa bahwa hubungan persahabatanmu mengubah hidupmu? Bagaimana?",
        "Apa yang harus dilakukan seorang teman jika teman lainnya sedang berada dalam hubungan yang toxic?",
        "Bagaimana menurutmu peran persahabatan dalam kehidupan sehari-hari?",
        "Apa yang kamu lakukan saat merasa persahabatanmu mulai renggang?",
        "Apakah kamu lebih suka memiliki teman yang satu geng atau lebih banyak teman dengan minat yang beragam?",
        "Apa yang menurutmu bisa membuat sebuah persahabatan lebih kuat dari waktu ke waktu?",
        "Bagaimana cara menjaga hubungan persahabatan yang sehat saat kalian sudah menikah atau punya pasangan?",
        "Apa hal yang menurutmu sering disalahpahami dalam persahabatan?",
        "Apakah kamu percaya bahwa teman bisa saling berubah seiring waktu?",
        "Bagaimana cara kamu membantu teman yang sedang menghadapi masalah besar?",
        "Apa kenangan paling lucu yang kamu miliki bersama teman?",
        "Apa hal yang paling kamu hargai dari sahabatmu?",
        "Apa perbedaan antara teman dekat dan teman biasa menurutmu?",
        "Apakah kamu merasa lebih nyaman berbagi masalah pribadi dengan teman atau keluarga?",
        "Apa yang bisa dilakukan untuk memperbaiki hubungan persahabatan yang telah rusak?",
        "Bagaimana kamu mengatasi rasa cemburu dalam persahabatan?",
        "Apakah menurutmu seorang sahabat harus selalu memberi dukungan tanpa syarat?",
        "Apa yang membuat kamu merasa sahabatmu adalah orang yang benar-benar bisa diandalkan?",
        "Bagaimana cara menjaga persahabatan agar tetap kuat meskipun ada perbedaan?",
        "Apakah kamu lebih suka persahabatan yang santai atau yang lebih mendalam?",
        "Apa yang menurutmu menjadi indikator bahwa sebuah persahabatan sudah tidak sehat lagi?",
        "Seperti apa cara sahabatmu menunjukkan perhatian padamu yang paling berkesan?",
        "Bagaimana cara kamu memberi ruang pribadi pada teman tanpa merusak hubungan?",
        "Apa yang akan kamu lakukan jika sahabatmu membuat keputusan yang kamu anggap salah?",
        "Bagaimana caramu mendukung teman yang sedang berjuang dengan masalah mental?",
        "Apa hal yang paling membuat kamu merasa dihargai oleh teman-temanmu?",
        "Apakah kamu pernah merasa bahwa hubungan persahabatanmu harus ada batasan? Mengapa?",
        "Apa yang harus dilakukan jika sahabatmu mulai menjauh?",
        "Bagaimana kamu bisa membangun kembali kepercayaan setelah dikhianati oleh teman?",
        "Apa yang membuat kamu merasa lebih dekat dengan teman yang berbeda latar belakangnya?",
        "Apa peran humor dalam persahabatan menurutmu?",
        "Apakah kamu percaya bahwa persahabatan bisa bertahan meskipun ada jarak fisik yang jauh?",
        "Apa yang menurutmu membuat persahabatan antar gender lebih rumit?",
        "Apakah kamu pernah merasa bahwa seorang teman lebih seperti keluarga bagimu?",
        "Apa hal yang paling kamu nikmati saat menghabiskan waktu bersama teman-teman?",
        "Bagaimana kamu mengatasi perasaan kesepian meskipun dikelilingi teman-teman?",
        "Apa yang menurutmu menjadi alasan seseorang merasa nyaman untuk bercerita kepada teman?",
        "Bagaimana cara kamu menghargai waktu yang kamu habiskan bersama teman-temanmu?"
    ],
    "Pendidikan": [
        "Apa alasan kamu memilih jurusan yang kamu ambil saat ini?",
        "Bagaimana cara kamu mengatasi tantangan belajar yang sulit?",
        "Apa metode belajar yang menurutmu paling efektif?",
        "Apakah ada mata pelajaran yang dulu sangat kamu benci, tapi sekarang kamu suka?",
        "Menurutmu, apa yang paling penting untuk dilakukan agar sukses di sekolah atau universitas?",
        "Apa alasan kamu memilih jurusan yang kamu ambil saat ini?",
        "Bagaimana cara kamu mengatasi tantangan belajar yang sulit?",
        "Apa metode belajar yang menurutmu paling efektif?",
        "Apakah ada mata pelajaran yang dulu sangat kamu benci, tapi sekarang kamu suka?",
        "Menurutmu, apa yang paling penting untuk dilakukan agar sukses di sekolah atau universitas?",
        "Apa pendapatmu tentang ujian berbasis online?",
        "Apa yang kamu harapkan dari pengalaman belajar di luar negeri?",
        "Apa pendapatmu tentang sistem pendidikan di Indonesia?",
        "Siapa guru atau dosen yang paling menginspirasi kamu dan mengapa?",
        "Apa yang akan kamu lakukan jika sistem pendidikan di dunia ini berubah drastis?",
        "Apa pendapatmu tentang pendidikan jarak jauh atau daring?",
        "Bagaimana teknologi mempengaruhi cara kita belajar?",
        "Apa peran kreativitas dalam pendidikan menurutmu?",
        "Apakah kamu setuju bahwa pendidikan lebih penting daripada pengalaman kerja? Mengapa?",
        "Apa yang kamu pikirkan tentang pelajaran yang tidak sesuai dengan minat atau bakat?",
        "Apa yang menurutmu bisa dilakukan untuk meningkatkan kualitas pendidikan di Indonesia?",
        "Apa yang lebih penting: teori atau praktik? Mengapa?",
        "Seperti apa guru atau dosen yang ideal menurutmu?",
        "Bagaimana cara kamu memotivasi diri untuk belajar ketika merasa malas?",
        "Apa pengalaman pendidikan terbaik yang pernah kamu miliki?",
        "Apakah kamu pernah merasa tidak dihargai dalam lingkungan pendidikan? Ceritakan.",
        "Apa tantangan terbesar yang kamu hadapi dalam pendidikan formal?",
        "Bagaimana cara mengatasi rasa takut atau stres sebelum ujian?",
        "Apa pendapatmu tentang sistem grading atau penilaian di sekolah?",
        "Bagaimana pendidikan bisa lebih inklusif bagi semua lapisan masyarakat?",
        "Apakah kamu lebih suka belajar secara individu atau dalam kelompok? Mengapa?",
        "Bagaimana cara mengajarkan mata pelajaran yang sulit agar lebih menarik?",
        "Apa yang menurutmu penting dalam membangun lingkungan belajar yang sehat?",
        "Apakah kamu lebih suka menggunakan buku teks atau sumber digital dalam belajar?",
        "Apa yang harus dilakukan oleh seorang guru untuk membuat pelajaran menjadi menyenangkan?",
        "Apa peran sekolah dalam mempersiapkan siswa untuk dunia kerja?",
        "Apa yang bisa dilakukan agar siswa lebih tertarik dengan pelajaran matematika?",
        "Bagaimana cara mengajarkan keterampilan sosial dalam pendidikan?",
        "Apa pendapatmu tentang ujian yang sering kali menilai hanya berdasarkan hafalan?",
        "Apa yang menurutmu penting dalam pembelajaran bahasa asing?",
        "Apa peran sekolah dalam mengembangkan bakat dan minat siswa?",
        "Apa yang membuatmu tertarik mengikuti kuliah atau pelatihan di luar negeri?",
        "Apakah menurutmu pendidikan seni cukup penting dalam sistem pendidikan formal?",
        "Bagaimana cara menyikapi perbedaan kemampuan belajar antar siswa?",
        "Bagaimana cara sekolah atau universitas dapat meningkatkan keterampilan praktis siswa?",
        "Apa pendapatmu tentang penekanan pada nilai akademik yang tinggi dalam pendidikan?",
        "Seperti apa program pendidikan yang ideal untuk masa depan?",
        "Apa yang kamu harapkan dari teman sekelas atau kelompok belajar saat bekerja sama?",
        "Apakah kamu merasa bahwa ujian standar terlalu membebani siswa?",
        "Apa yang menurutmu bisa dilakukan untuk mengurangi kecemasan akademik di kalangan siswa?",
        "Bagaimana cara meningkatkan kerjasama antara orang tua dan sekolah dalam pendidikan?",
        "Apakah pendidikan karakter sama pentingnya dengan pendidikan akademis? Mengapa?",
        "Apa yang harus dilakukan untuk memperbaiki kualitas pendidikan di daerah terpencil?",
        "Apa harapanmu terhadap sistem pendidikan yang mengutamakan keberagaman dan inklusivitas?",
        "Apa yang bisa dilakukan untuk mengatasi kekurangan fasilitas pendidikan di beberapa daerah?",
        "Bagaimana cara meningkatkan motivasi belajar di kalangan siswa yang kurang tertarik pada pelajaran?",
        "Apakah pendidikan di luar negeri lebih baik dibandingkan di dalam negeri? Mengapa?",
        "Apa peran media sosial dalam proses pembelajaran modern?"
    ],
    "Percintaan": [
        "Apa hal pertama yang membuat kamu tertarik pada seseorang?",
        "Menurutmu, apa yang membuat hubungan cinta bertahan lama?",
        "Apa tantangan terbesar yang pernah kamu hadapi dalam hubungan asmara?",
        "Apa yang menurutmu penting dalam komunikasi antar pasangan?",
        "Apakah kamu percaya pada cinta pada pandangan pertama?",
        "Apa hal pertama yang membuat kamu tertarik pada seseorang?",
        "Menurutmu, apa yang membuat hubungan cinta bertahan lama?",
        "Apa tantangan terbesar yang pernah kamu hadapi dalam hubungan asmara?",
        "Apa yang menurutmu penting dalam komunikasi antar pasangan?",
        "Apakah kamu percaya pada cinta pada pandangan pertama?",
        "Apa yang paling romantis yang pernah kamu lakukan untuk pasanganmu?",
        "Apa hal yang paling kamu sukai dari pasanganmu?",
        "Bagaimana cara kamu mengatasi perbedaan pendapat dalam hubungan?",
        "Apa yang menurutmu membuat hubungan cinta menjadi sehat?",
        "Apa pendapatmu tentang hubungan jarak jauh?",
        "Apa yang kamu lakukan jika pasanganmu merasa tidak nyaman dalam hubungan?",
        "Bagaimana cara kamu menjaga kebahagiaan dalam hubungan asmara?",
        "Apa yang menurutmu paling penting dalam menjaga kepercayaan dalam hubungan?",
        "Apakah menurutmu pasangan seharusnya memiliki ruang pribadi? Kenapa?",
        "Apa hal yang kamu lakukan untuk menjaga hubungan tetap romantis?",
        "Bagaimana cara kamu menangani konflik dengan pasangan?",
        "Apakah kamu percaya bahwa pasangan harus selalu satu visi dan misi?",
        "Apa pendapatmu tentang perbedaan usia dalam hubungan cinta?",
        "Bagaimana cara menjaga hubungan tetap kuat saat ada masalah?",
        "Apa hal terpenting yang perlu dipertimbangkan sebelum memutuskan untuk berkomitmen?",
        "Apa yang paling kamu hargai dalam diri pasanganmu?",
        "Bagaimana cara kamu menunjukkan perhatian kepada pasanganmu?",
        "Apa yang menurutmu membuat pasangan lebih dekat dan lebih intim?",
        "Apa yang kamu lakukan saat merasa hubunganmu mulai renggang?",
        "Apakah kamu lebih memilih hubungan yang penuh kebebasan atau lebih terikat?",
        "Apa yang menurutmu bisa membuat pasanganmu merasa lebih dihargai?",
        "Bagaimana cara kamu menangani rasa cemburu dalam hubungan?",
        "Apa yang menurutmu penting untuk dipertahankan dalam hubungan asmara?",
        "Apakah kamu percaya bahwa setiap pasangan bisa berubah seiring waktu?",
        "Apa yang menurutmu membuat hubungan percintaan dengan pasangan terasa spesial?",
        "Apa hal terpenting yang harus dibicarakan dalam sebuah hubungan?",
        "Bagaimana cara menghadapi perbedaan nilai atau prinsip dalam hubungan?",
        "Apakah kamu lebih suka hubungan yang santai atau yang lebih serius?",
        "Apa pendapatmu tentang mengungkapkan perasaan melalui kata-kata atau tindakan?",
        "Bagaimana cara menjaga komunikasi yang baik dalam hubungan jarak jauh?",
        "Apa yang membuat kamu merasa nyaman dan aman dalam hubungan asmara?",
        "Apa perbedaan antara cinta sejati dan ketertarikan fisik menurutmu?",
        "Apa yang menurutmu lebih penting dalam hubungan, cinta atau kepercayaan?",
        "Bagaimana cara kamu menjaga keseimbangan antara hubungan dan kehidupan pribadi?",
        "Apa yang membuat kamu merasa dihargai dalam sebuah hubungan cinta?",
        "Bagaimana cara menjaga hubungan tetap bahagia meskipun menghadapi tantangan hidup?",
        "Apa yang menurutmu harus dilakukan agar hubungan tetap menyenangkan dan tidak monoton?",
        "Apa yang kamu harapkan dari pasanganmu dalam hubungan asmara?",
        "Bagaimana cara kamu menghadapi ketakutan dalam hubungan, seperti takut kehilangan pasangan?",
        "Apa hal yang paling berkesan yang pernah dilakukan pasanganmu untuk kamu?",
        "Apa yang menurutmu dapat memperkuat ikatan emosional antara pasangan?",
        "Bagaimana cara kamu mengatasi perasaan kesepian dalam hubungan yang sudah lama?",
        "Apa pendapatmu tentang pasangan yang sering berdebat dalam hubungan?",
        "Apa yang menurutmu membuat hubungan percintaan lebih bermakna dan berkesan?",
        "Apa yang akan kamu lakukan jika pasanganmu membuat keputusan yang kamu anggap salah?"
    ],
    "Personal": [
        "Apa yang paling kamu hargai dalam hidup?",
        "Bagaimana cara kamu menjaga keseimbangan antara pekerjaan dan kehidupan pribadi?",
        "Apa kegiatan yang paling kamu nikmati di waktu senggang?",
        "Apa cita-cita besar yang ingin kamu capai dalam hidup?",
        "Bagaimana kamu mengatasi stres dan tekanan dalam hidup sehari-hari?",
        "Apa kenangan masa kecil yang paling berkesan bagi kamu?",
        "Siapa orang yang paling berpengaruh dalam hidup kamu dan mengapa?",
        "Apa nilai atau prinsip hidup yang paling kamu pegang teguh?",
        "Bagaimana kamu menggambarkan diri kamu dalam tiga kata?",
        "Apa pencapaian pribadi yang paling kamu banggakan?",
        "Kapan terakhir kali kamu merasa benar-benar bahagia dan kenapa?",
        "Apa hal kecil yang bisa membuat hari kamu jadi lebih baik?",
        "Bagaimana kamu menghadapi perubahan besar dalam hidup?",
        "Apa yang kamu lakukan saat merasa kehilangan arah?",
        "Apa arti kesuksesan menurut kamu?",
        "Jika kamu bisa memberi nasihat ke diri sendiri di masa lalu, apa yang akan kamu katakan?",
        "Bagaimana kamu mengelola waktu dan prioritas dalam kehidupan sehari-hari?",
        "Apa impian masa kecil kamu dan apakah masih ingin kamu wujudkan?",
        "Apa yang kamu pelajari dari kegagalan terbesar dalam hidup kamu?",
        "Bagaimana kamu menjaga hubungan dengan orang-orang terdekat?",
        "Apa ketakutan terbesar kamu dan bagaimana kamu menghadapinya?",
        "Apa peran spiritualitas atau keyakinan dalam hidup kamu?",
        "Bagaimana kamu membangun kepercayaan diri?",
        "Apa arti ‘rumah’ bagi kamu?",
        "Kapan terakhir kali kamu keluar dari zona nyaman dan apa hasilnya?",
        "Bagaimana kamu menangani konflik dalam kehidupan pribadi?",
        "Apa hal yang paling kamu syukuri hari ini?",
        "Apa kegiatan sederhana yang bisa membuat kamu merasa tenang?",
        "Bagaimana kamu menilai kualitas diri kamu sebagai teman?",
        "Apa satu hal yang ingin kamu ubah dari masa lalu?",
        "Apa motivasi utama kamu dalam menjalani hidup?",
        "Bagaimana cara kamu merayakan pencapaian pribadi?",
        "Apa keputusan paling berani yang pernah kamu ambil?",
        "Apa hal paling penting yang kamu pelajari dari orang tua kamu?",
        "Bagaimana kamu menggambarkan versi terbaik dari diri kamu?",
        "Apa arti kebebasan bagi kamu?",
        "Apa hal yang paling kamu rindukan dari masa lalu?",
        "Bagaimana kamu menghadapi rasa takut akan kegagalan?",
        "Apa rutinitas pagi kamu dan mengapa itu penting?",
        "Apa yang membuat kamu merasa dicintai dan dihargai?",
        "Apa hubungan antara pekerjaan dan passion menurut kamu?",
        "Bagaimana kamu menjaga kesehatan mental dan emosional?",
        "Apa peran teknologi dalam kehidupan pribadi kamu?",
        "Apa mimpi kamu yang belum terwujud?",
        "Bagaimana kamu mengatur keuangan pribadi?",
        "Apa buku atau film yang paling menginspirasi kamu?",
        "Apa pelajaran hidup terbesar yang kamu temukan sejauh ini?",
        "Bagaimana kamu ingin dikenang oleh orang lain?",
        "Apa perbedaan kamu yang dulu dan kamu yang sekarang?",
        "Apa tantangan terbesar dalam membangun kehidupan yang seimbang?"
    ]
}

history_file = "history.pkl"

def load_history():
    if os.path.exists(history_file):
        with open(history_file, "rb") as file:
            return pickle.load(file)
    return []

def save_history(history):
    with open(history_file, "wb") as file:
        pickle.dump(history, file)

history = load_history()

def generate_topic(category):
    available_topics = [topic for topic in topics[category] if topic not in history]
    if available_topics:
        topic = random.choice(available_topics)
        history.append(topic)
        save_history(history)
        return f'✨ "{topic}" ✨'
    else:
        return "🚫 Semua topik sudah dipilih! Klik Reset untuk memulai ulang."

def reset_history():
    global history
    history = []
    save_history(history)
    topic_label.configure(text="✅ History direset. Yuk mulai lagi!")

def on_generate():
    category = category_var.get()
    if not category:
        topic_label.configure(text="⚠️ Silakan pilih kategori terlebih dahulu.")
        return

    # Hapus tombol generate awal
    if hasattr(on_generate, "first") and on_generate.first:
        generate_button_initial.pack_forget()
        button_wrapper.pack(pady=(20, 10))
        on_generate.first = False

    topic = generate_topic(category)
    topic_label.configure(text=topic)

on_generate.first = True

def toggle_history_sidebar():
    if sidebar_frame.winfo_ismapped():
        sidebar_frame.pack_forget()
    else:
        sidebar_frame.pack(side="right", fill="y", padx=0, pady=0)

    refresh_history_sidebar()

def refresh_history_sidebar():
    for widget in sidebar_scrollable.winfo_children():
        widget.destroy()

    if not history:
        ctk.CTkLabel(sidebar_scrollable, text="(Belum ada topik)", anchor="w").pack(anchor="w", padx=10, pady=10)
        return

    for i, item in enumerate(history[::-1], 1):
        lbl = ctk.CTkLabel(sidebar_scrollable, text=f"{i}. {item}", anchor="w", wraplength=240, justify="left")
        lbl.pack(anchor="w", padx=10, pady=5)

# === Setup Tampilan ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("TopiKu")
app.geometry("800x600")
app.resizable(False, False)

# === Background Hiasan ===
bg_label = ctk.CTkLabel(app, text="TopiKu", font=ctk.CTkFont(size=80, weight="bold"), text_color="#333333")
bg_label.place(relx=0.5, rely=0.5, anchor="center")

# === Top Bar ===
top_frame = ctk.CTkFrame(app, fg_color="transparent")
top_frame.pack(fill="x", padx=10, pady=5)

app_title = ctk.CTkLabel(top_frame, text="TopiKu", font=ctk.CTkFont(size=24, weight="bold"))
app_title.pack(side="left", padx=(10, 0))

history_button = ctk.CTkButton(top_frame, text="📚", width=40, height=32, corner_radius=12, command=toggle_history_sidebar)
history_button.pack(side="right")

# === Dropdown Pilihan Kategori ===
category_var = ctk.StringVar()
category_label = ctk.CTkLabel(app, text="Pilih Kategori:")
category_label.pack()

category_menu = ctk.CTkOptionMenu(app, variable=category_var, values=list(topics.keys()))
category_menu.pack(pady=5)

# === Tombol Generate Awal ===
generate_button_initial = ctk.CTkButton(app, text="🎲 Generate Topik", width=200, height=42, command=on_generate, corner_radius=20)
generate_button_initial.pack(pady=(50, 10))

# === Wrapper untuk Tombol di Bawah (setelah generate) ===
button_wrapper = ctk.CTkFrame(app, fg_color="transparent")

generate_button_final = ctk.CTkButton(button_wrapper, text="🎲 Generate Lagi", width=180, height=42, command=on_generate, corner_radius=20)
generate_button_final.grid(row=0, column=0, padx=10)

reset_button = ctk.CTkButton(button_wrapper, text="🔄", width=40, height=40, corner_radius=20, fg_color="#333", hover_color="#555", command=reset_history)
reset_button.grid(row=0, column=1)

# === Label Hasil Topik ===
topic_label = ctk.CTkLabel(app, text="Pilih kategori dan klik Generate", wraplength=620, justify="center", font=ctk.CTkFont(size=15))
topic_label.pack(pady=30)

# === Sidebar History ===
sidebar_frame = ctk.CTkFrame(app, width=260, fg_color="#111111")
sidebar_scrollable = ctk.CTkScrollableFrame(sidebar_frame, width=260, height=600)
sidebar_scrollable.pack(fill="both", expand=True)

app.mainloop()
