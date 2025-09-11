{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0b639313-9272-49f3-b8ed-fd13421f9c8c",
   "metadata": {},
   "outputs": [],
   "source": [
    "import tkinter as tk\n",
    "\n",
    "# Создаём главное окно\n",
    "root = tk.Tk()\n",
    "root.title(\"Баннер\")\n",
    "root.geometry(\"400x200+500+300\")  # Размер и позиция окна\n",
    "root.configure(bg=\"lightblue\")\n",
    "\n",
    "# Убираем рамку и системные кнопки\n",
    "root.overrideredirect(True)\n",
    "\n",
    "# Делаем окно всегда поверх других\n",
    "root.attributes(\"-topmost\", True)\n",
    "\n",
    "# Добавляем текст или изображение\n",
    "label = tk.Label(root, text=\"ВАЖНЫЙ БАННЕР\", font=(\"Arial\", 20), bg=\"lightblue\")\n",
    "label.pack(expand=True)\n",
    "\n",
    "# Отключаем закрытие по клавишам (Alt+F4, Esc)\n",
    "def disable_event():\n",
    "    pass\n",
    "\n",
    "root.protocol(\"WM_DELETE_WINDOW\", disable_event)\n",
    "root.bind(\"<Escape>\", lambda e: None)\n",
    "\n",
    "# Запускаем окно\n",
    "root.mainloop()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b0460aa4-0aef-40bb-886a-e3397cfd5fc1",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
