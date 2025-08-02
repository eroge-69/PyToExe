import os
import shutil
import zipfile
import json
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import subprocess
import platform

SETTINGS_FILE = "settings.json"

class ModpackManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Modpack Manager")

        self.minecraft_path = ""
        self.modpacks_path = ""

        self.load_settings()

        # Меню
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Выбрать папку Minecraft", command=self.select_minecraft_path)
        file_menu.add_command(label="Открыть папку Minecraft", command=self.open_minecraft_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Выбрать папку модпаков", command=self.select_modpacks_path)
        file_menu.add_command(label="Открыть папку модпаков", command=self.open_modpacks_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить сборку", command=self.save_modpack)
        file_menu.add_command(label="Экспорт сборки", command=self.export_modpack)
        file_menu.add_command(label="Удалить сборку", command=self.delete_modpack)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Переименовать сборку", command=self.rename_modpack)
        edit_menu.add_command(label="Изменить описание сборки", command=self.edit_description)

        self.menu_bar.add_cascade(label="Файл", menu=file_menu)
        self.menu_bar.add_cascade(label="Редактировать", menu=edit_menu)

        # Главное окно
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Справа — список сборок и поиск
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right_frame, text="Список сборок").pack()

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_search)
        search_entry = tk.Entry(right_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=3)

        self.listbox = tk.Listbox(right_frame, width=30)
        self.listbox.pack(fill=tk.Y, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_modpack_select)

        # Слева — описание и моды
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Описание
        tk.Label(left_frame, text="Описание сборки").pack()
        self.desc_text = tk.Text(left_frame, height=5, width=50)
        self.desc_text.pack(fill=tk.X, pady=5)
        self.desc_text.config(state=tk.DISABLED)

        # Моды
        tk.Label(left_frame, text="Моды в сборке").pack()
        self.mods_text = tk.Text(left_frame, height=15, width=50)
        self.mods_text.pack(fill=tk.BOTH, expand=True)

        self.refresh_listbox()

    # --- Загрузка и сохранение настроек ---
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.minecraft_path = data.get("minecraft_path", "")
                    self.modpacks_path = data.get("modpacks_path", "")
            except Exception:
                pass

    def save_settings(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "minecraft_path": self.minecraft_path,
                "modpacks_path": self.modpacks_path
            }, f, indent=4, ensure_ascii=False)

    # --- Папки ---
    def select_minecraft_path(self):
        path = filedialog.askdirectory(title="Выберите папку Minecraft")
        if path:
            self.minecraft_path = path
            self.save_settings()
            self.refresh_listbox()

    def select_modpacks_path(self):
        path = filedialog.askdirectory(title="Выберите папку с модпаками")
        if path:
            self.modpacks_path = path
            self.save_settings()
            self.refresh_listbox()

    def open_folder(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def open_minecraft_folder(self):
        if self.minecraft_path:
            self.open_folder(self.minecraft_path)

    def open_modpacks_folder(self):
        if self.modpacks_path:
            self.open_folder(self.modpacks_path)

    # --- Работа со списком сборок ---
    def refresh_listbox(self):
        self.all_modpacks = []
        self.listbox.delete(0, tk.END)
        if os.path.isdir(self.modpacks_path):
            self.all_modpacks = sorted(
                [f for f in os.listdir(self.modpacks_path) if os.path.isdir(os.path.join(self.modpacks_path, f))],
                key=str.lower
            )
            self.update_search()

    def update_search(self, *args):
        query = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for modpack in self.all_modpacks:
            if query in modpack.lower():
                self.listbox.insert(tk.END, modpack)

    def on_modpack_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            self.mods_text.delete("1.0", tk.END)
            self.desc_text.config(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.config(state=tk.DISABLED)
            return

        selected = self.listbox.get(selection[0])
        self.load_description(selected)
        self.display_mods_in_modpack(selected)

    # --- Описание сборки ---
    def load_description(self, modpack_name):
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete("1.0", tk.END)
        desc_path = os.path.join(self.modpacks_path, modpack_name, "description.json")
        if os.path.isfile(desc_path):
            try:
                with open(desc_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    description = data.get("description", "")
                    self.desc_text.insert(tk.END, description)
            except Exception:
                pass
        self.desc_text.config(state=tk.DISABLED)

    def edit_description(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите сборку для редактирования описания.")
            return

        modpack_name = self.listbox.get(selection[0])
        desc_path = os.path.join(self.modpacks_path, modpack_name, "description.json")

        current_desc = ""
        if os.path.isfile(desc_path):
            try:
                with open(desc_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    current_desc = data.get("description", "")
            except Exception:
                pass

        # Открываем простое окно для редактирования
        desc = simpledialog.askstring("Изменить описание сборки",
                                      "Введите новое описание:",
                                      initialvalue=current_desc,
                                      parent=self.root)
        if desc is not None:
            try:
                with open(desc_path, "w", encoding="utf-8") as f:
                    json.dump({"description": desc}, f, ensure_ascii=False, indent=4)
                self.load_description(modpack_name)
                messagebox.showinfo("Готово", "Описание сборки сохранено.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить описание:\n{e}")

    # --- Моды в сборке ---
    def display_mods_in_modpack(self, modpack_name):
        modpack_mods = os.path.join(self.modpacks_path, modpack_name, "mods")
        mods_list = []

        if os.path.isdir(modpack_mods):
            for file in os.listdir(modpack_mods):
                if file.endswith(".jar"):
                    jar_path = os.path.join(modpack_mods, file)
                    mod_name = self.extract_mod_name(jar_path)
                    mods_list.append(mod_name or f"[Неизвестно] {file}")

        self.mods_text.delete("1.0", tk.END)
        self.mods_text.insert(tk.END, "\n".join(mods_list))

    def extract_mod_name(self, jar_path):
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                if "mcmod.info" in jar.namelist():
                    with jar.open("mcmod.info") as info_file:
                        data = json.load(info_file)
                        if isinstance(data, list) and "name" in data[0]:
                            return data[0]["name"]
        except Exception:
            return None
        return None

    # --- Сохранение текущей сборки ---
    def clear_folder(self, folder_path):
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")

    def save_modpack(self):
        if not self.minecraft_path or not self.modpacks_path:
            messagebox.showerror("Ошибка", "Сначала выберите обе папки!")
            return

        name = simpledialog.askstring("Имя сборки", "Введите название сборки:")
        if not name:
            return

        target_path = os.path.join(self.modpacks_path, name)
        os.makedirs(os.path.join(target_path, "mods"), exist_ok=True)
        os.makedirs(os.path.join(target_path, "config"), exist_ok=True)

        try:
            shutil.copytree(os.path.join(self.minecraft_path, "mods"), os.path.join(target_path, "mods"), dirs_exist_ok=True)
            shutil.copytree(os.path.join(self.minecraft_path, "config"), os.path.join(target_path, "config"), dirs_exist_ok=True)

            self.clear_folder(os.path.join(self.minecraft_path, "mods"))
            self.clear_folder(os.path.join(self.minecraft_path, "config"))

            messagebox.showinfo("Успешно", f"Сборка '{name}' сохранена и Minecraft очищен.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        self.refresh_listbox()

    # --- Экспорт сборки ---
    def export_modpack(self):
        if not self.minecraft_path or not self.modpacks_path:
            messagebox.showerror("Ошибка", "Сначала выберите обе папки!")
            return

        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите сборку для экспорта.")
            return

        selected = self.listbox.get(selection[0])
        source_path = os.path.join(self.modpacks_path, selected)

        try:
            shutil.copytree(os.path.join(source_path, "mods"), os.path.join(self.minecraft_path, "mods"), dirs_exist_ok=True)
            shutil.copytree(os.path.join(source_path, "config"), os.path.join(self.minecraft_path, "config"), dirs_exist_ok=True)
            messagebox.showinfo("Успешно", f"Сборка '{selected}' экспортирована в Minecraft.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- Удаление сборки ---
    def delete_modpack(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите сборку для удаления.")
            return

        selected = self.listbox.get(selection[0])
        path = os.path.join(self.modpacks_path, selected)

        confirm = messagebox.askyesno("Подтверждение", f"Удалить сборку '{selected}'?")
        if confirm:
            try:
                shutil.rmtree(path)
                self.refresh_listbox()
                self.mods_text.delete("1.0", tk.END)
                self.desc_text.config(state=tk.NORMAL)
                self.desc_text.delete("1.0", tk.END)
                self.desc_text.config(state=tk.DISABLED)
                messagebox.showinfo("Удалено", f"Сборка '{selected}' удалена.")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    # --- Переименование сборки ---
    def rename_modpack(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите сборку для переименования.")
            return

        old_name = self.listbox.get(selection[0])
        new_name = simpledialog.askstring("Переименовать сборку", f"Новое имя для '{old_name}':")
        if not new_name or new_name == old_name:
            return

        old_path = os.path.join(self.modpacks_path, old_name)
        new_path = os.path.join(self.modpacks_path, new_name)

        if os.path.exists(new_path):
            messagebox.showerror("Ошибка", "Сборка с таким именем уже существует.")
            return

        try:
            os.rename(old_path, new_path)
            self.refresh_listbox()
            messagebox.showinfo("Готово", f"Сборка '{old_name}' переименована в '{new_name}'.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать сборку:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModpackManager(root)
    root.mainloop()
