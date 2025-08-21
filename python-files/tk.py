import tkinter as tk
from tkinter import ttk
import os, shutil

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Сортировка фалов")
        self.root.geometry("600x500")

        self.running = False
        self.counter = 0

        self.setup_ui()

    def setup_ui(self):
        # === Путь 1 ===
        tk.Label(self.root, text="Путь 1 (источник):").pack(pady=(10, 0), anchor="w", padx=10)
        self.path1_entry = tk.Entry(self.root, width=70)
        self.path1_entry.pack(pady=5, padx=10, fill=tk.X)

        # === Путь 2 ===
        tk.Label(self.root, text="Путь 2 (назначение):").pack(pady=(10, 0), anchor="w", padx=10)
        self.path2_entry = tk.Entry(self.root, width=70)
        self.path2_entry.pack(pady=5, padx=10, fill=tk.X)

        # Кнопка обновить список файлов для Пути 2
        self.refresh_button = tk.Button(self.root, text="Обновить список файлов", command=self.update_file_list)
        self.refresh_button.pack(pady=5)

        # === Список файлов Пути 2 ===
        tk.Label(self.root, text="Файлы в Пути 2:").pack(pady=(10, 0), anchor="w", padx=10)
        self.file_listbox = tk.Listbox(self.root, height=12)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        self.file_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        scrollbar.pack(pady=5, padx=(0, 10), side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.place(in_=self.root, relx=0.05, rely=0.4, relwidth=0.85, relheight=0.45)
        scrollbar.place(in_=self.root, relx=0.9, rely=0.4, relheight=0.45)

        # === Кнопки управления ===
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.start_button = tk.Button(button_frame, text="Запустить", width=10, command=self.start)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(button_frame, text="Стоп", width=10, command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.exit_button = tk.Button(button_frame, text="Выход", width=10, command=self.root.quit)
        self.exit_button.grid(row=0, column=2, padx=5)

        # === Статус ===
        self.status_label = tk.Label(self.root, text="Готов", fg="gray")
        self.status_label.pack(pady=5)

    def start(self):
        path1 = self.path1_entry.get().strip()
        path2 = self.path2_entry.get().strip()

        if not os.path.isdir(path1):
            self.status_label.config(text="Ошибка: Путь 1 не существует", fg="red")
            return
        if not os.path.isdir(path2):
            self.status_label.config(text="Ошибка: Путь 2 не существует", fg="red")
            return

        if not self.running:
            self.running = True
            self.status_label.config(text="Работает...", fg="green")
            self.run_background_task()

    def stop(self):
        self.running = False
        self.status_label.config(text="Остановлено", fg="orange")

    def run_background_task(self):
        formate = ["$#!", "_crypt", "1212", "501", "a2r", "aao",
                   "aas", "acidssa", "acl", "aco", "aes", "aex",
                   "afa", "afp", "afs3", "ant", "aos", "asc",
                   "axx", "bfa", "bfe", "bfw", "bmpenx", "bn2",
                   "bnc", "cae", "can", "ccf", "ccp", "cef", "cfd",
                   "cfe", "cgp", "ch", "cha", "chi", "cif",
                   "cip", "clu", "clx", "cmg", "cod", "code",
                   "cpt", "cpx", "cr", "crf", "cri", "crp",
                   "cry", "crypted", "cryptomit", "cry[tra",
                   "cryptx", "csnmsg", "csvenx", "ctx", "cxv",
                   "cyp", "dlc", "daz", "dcd", "dcf", "dco",
                   "dcv", "dez", "docenx", "docmenx", "docxenx",
                   "dotmenx", "dotxenx", "dpd", "drc", "dst", "dvdfabhdd",
                   "dwl", "ebak", "ecc", "ecr", "ecs", "edf",
                   "eea", "eee", "efa", "efc", "efl", "eggd",
                   "egisenc", "egl", "egs", "eid", "emc", "enc",
                   "encr", "encrypt", "encrypted", "enf", "enp",
                   "eoc", "epm", "etff", "etxt", "fca", "fen",
                   "fke", "fold", "fsh", "gifenx", "gmd", "gpg", "grd",
                   "hbe", "hcs", "hne", "hpg", "hse", "hsf",
                   "htmenx", "htmlenx", "hwp", "ica", "iccp", "icd",
                   "icp", "img3", "ism", "jbc", "jpegenx", "jrl",
                   "key", "kgd", "kme", "kmz", "kry", "kum", "lce",
                   "lhn", "lhz", "locked", "lok", "lp4", "lrs", "lxv",
                   "m2o", "m2m", "m2f", "max", "maxa", "mcr", "mef",
                   "mhtenx", "mhtmlenx", "ml256", "nle", "n2e", "n3e",
                   "n4e", "nsx", "nhh", "nic", "ocf", "oef", "otp",
                   "p12", "p7m", "pad", "pae", "pfenx", "pea", "pei",
                   "pf", "pfx", "pgp", "pgs", "pi2", "pie", "pigg",
                   "pkd", "ple", "pms", "potmenx", "pptxenx", "ppamenx",
                   "ppenc", "ppsenx", "ppsmenx", "ppsxenx", "pptenx",
                   "pptmenx", "pptxenx", "puf", "qce", "qsa", "r64",
                   "rarenx", "raw", "rbb", "rgf", "rhs", "rif", "rip",
                   "rng", "rpz", "rsakey", "rtfenx", "rxf", "rzx",
                   "sal", "sa5", "saa", "saf", "safe", "sai", "sbak",
                   "sbox", "sbx", "sda", "sdd", "sde", "sea", "see",
                   "sef", "sema", "set", "seu", "shy", "sit", "sitw", "skd",
                   "slg", "sme", "spd", "spk", "sst", "switch", "tc", "teneta",
                   "tgs", "tifenx", "tiffenx", "tlg", "tmm", "tsc", "tsig", "txtenx",
                   "ue2", "ueed", "ueef", "uenc", "uti", "vde", "vf3", "vmdf",
                   "vme", "vsf", "wbe", "wbs", "wmg", "wna", "wtc", "xcs", "xcz",
                   "xdc", "xea", "xfi", "xfl", "xg", "xia", "xis", "xlamenx",
                   "xlsbenx", "xlsenx", "xlsmenx", "xlsxenx", "xltmenx", "xltxenx",
                   "xpa", "xpo", "ypt", "zl7", "zbd", "zed", "zipenx", "zix", "zxn"]
        direkt = self.path1_entry.get().strip()
        dest = self.path2_entry.get().strip()
        if self.running:
            for root, path, file in os.walk(direkt):
                for fil in file:
                    destination = dest
                    otbor = fil.split('.')
                    otbor.append(' ')
                    dist_sputnik = (root.replace(direkt, "")[1:]).split('\\')
                    if len(dist_sputnik) > 1:
                        destination = os.fspath(os.path.join(destination, dist_sputnik[0] + '\\' + dist_sputnik[1]))
                    if otbor[1] in formate:
                        if os.path.exists(destination[:(destination.index('\\' + dist_sputnik[1]))]) == False:
                            os.mkdir(destination[:(destination.index('\\' + dist_sputnik[1]))])
                        if os.path.exists(destination) == False:
                            os.mkdir(destination)
                        if os.path.exists(os.path.join(destination, otbor[1])) == False:
                            os.mkdir(os.path.join(destination, otbor[1]))
                        shutil.move(os.path.join(root, fil), os.path.join(destination, otbor[1] + '\\' + fil))
                        self.update_file_list()

            # Повтор через 1000 мс
            self.root.after(1000, self.run_background_task)

    def update_file_list(self):
        """Обновляет список файлов из Пути 2"""
        self.file_listbox.delete(0, tk.END)  # Очищаем список
        path2 = self.path2_entry.get().strip()

        if not path2:
            self.status_label.config(text="Путь пуст", fg="red")
            return

        if not os.path.exists(path2):
            self.status_label.config(text="Путь не существует", fg="red")
            return

        if not os.path.isdir(path2):
            self.status_label.config(text="Путь не папка", fg="red")
            return

        try:
            files = os.listdir(path2)
            if files:
                for f in sorted(files):
                    self.file_listbox.insert(tk.END, f)
            else:
                self.file_listbox.insert(tk.END, "(папка пуста)")
            self.status_label.config(text=f"Файлы обновлены: {len(files)} элементов", fg="blue")
        except PermissionError:
            self.file_listbox.insert(tk.END, "Ошибка доступа")
            self.status_label.config(text="Ошибка доступа к папке", fg="red")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()