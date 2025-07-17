{
 "cells": [
  {
   "cell_type": "code",
   "metadata": {
    "ExecuteTime": {
     "end_time": "2025-07-17T06:48:27.852156Z",
     "start_time": "2025-07-17T06:47:42.282954Z"
    }
   },
   "source": [
    "import tkinter as tk\n",
    "from tkinter import messagebox\n",
    "from datetime import datetime\n",
    "from tkcalendar import DateEntry\n",
    "\n",
    "def suggest_class():\n",
    "    dob = dob_entry.get_date()\n",
    "    today = datetime.today()\n",
    "    cutoff = datetime(today.year, 6, 1)  # June 1 of current year\n",
    "\n",
    "    age = cutoff.year - dob.year - ((cutoff.month, cutoff.day) < (dob.month, dob.day))\n",
    "\n",
    "    if age < 3:\n",
    "        suggested = \"Not eligible for admission yet\"\n",
    "    elif 3 <= age < 4:\n",
    "        suggested = \"Nursery\"\n",
    "    elif 4 <= age < 5:\n",
    "        suggested = \"LKG\"\n",
    "    elif 5 <= age < 6:\n",
    "        suggested = \"UKG\"\n",
    "    else:\n",
    "        suggested = f\"{age - 5}th Standard\"\n",
    "\n",
    "    result_label.config(text=f\"Suggested Class: {suggested}\", fg=\"green\")\n",
    "\n",
    "# GUI Setup\n",
    "window = tk.Tk()\n",
    "window.title(\"School Admission Class Finder\")\n",
    "window.geometry(\"400x250\")\n",
    "\n",
    "tk.Label(window, text=\"Select Child's Date of Birth:\", font=(\"Arial\", 12)).pack(pady=10)\n",
    "\n",
    "dob_entry = DateEntry(window, width=20, font=(\"Arial\", 12), date_pattern=\"yyyy-mm-dd\", background='darkblue', foreground='white', borderwidth=2)\n",
    "dob_entry.pack()\n",
    "\n",
    "tk.Button(window, text=\"Check Class\", command=suggest_class, font=(\"Arial\", 12)).pack(pady=15)\n",
    "\n",
    "result_label = tk.Label(window, text=\"\", font=(\"Arial\", 14))\n",
    "result_label.pack()\n",
    "\n",
    "window.mainloop()\n"
   ],
   "outputs": [],
   "execution_count": 2
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
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
   "version": "3.8.10"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
