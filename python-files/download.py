import json
import random
from typing import Dict, List, Set
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class SchoolScheduleApp:
    def __init__(self, root):
        self.root = root
        self.style = tb.Style(theme="minty")  