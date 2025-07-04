
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
class EventLogAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Event Log Analyzer")
        self.df = None
        self.file_path = None
        self.canvas = None

        self.create_widgets()

    def create_widgets(self):
        # Top frame for file loading
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill='x', padx=5, pady=5)

        self.btn_load = tk.Button(top_frame, text="Load Log File", command=self.load_file)
        self.btn_load.pack(side='left')

        self.label_file = tk.Label(top_frame, text="No file loaded", bg='lightgray', width=80, anchor='w')
        self.label_file.pack(side='left', padx=5)

        # Time range inputs
        time_frame = tk.Frame(self.root)
        time_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(time_frame, text="Start Time:").pack(side='left')
        self.entry_start = tk.Entry(time_frame, width=25)
        self.entry_start.pack(side='left', padx=5)

        tk.Label(time_frame, text="End Time:").pack(side='left')
        self.entry_end = tk.Entry(time_frame, width=25)
        self.entry_end.pack(side='left', padx=5)

        self.btn_refresh = tk.Button(time_frame, text="Refresh", command=self.update_ranking)
        self.btn_refresh.pack(side='left', padx=10)
        
        self.btn_refresh = tk.Button(time_frame, text="Reset", command=self.reset)
        self.btn_refresh.pack(side='left', padx=10)
        
        self.btn_query = tk.Button(time_frame, text="Show Unique Events and IDs", command=self.show_unique_events)
        self.btn_query.pack(pady=10)

        # Ranking radio buttons
        rank_frame = tk.Frame(self.root)
        rank_frame.pack(fill='x', padx=5, pady=5)

        self.rank_type = tk.StringVar(value='single_on')
        tk.Radiobutton(rank_frame, text="Longest Single ON", variable=self.rank_type, value='single_on', command=self.update_ranking).pack(side='left')
        tk.Radiobutton(rank_frame, text="Total ON Duration", variable=self.rank_type, value='total_on', command=self.update_ranking).pack(side='left')
        tk.Radiobutton(rank_frame, text="Most ON Counts", variable=self.rank_type, value='count_on', command=self.update_ranking).pack(side='left')

        # Ranking table
        self.tree = ttk.Treeview(self.root, columns=('Name', 'ID', 'Info'), show='headings', height=10)
        self.tree.heading('Name', text='Event Name')
        self.tree.heading('ID', text='Event ID')
        self.tree.heading('Info', text='Details')
        self.tree.pack(fill='both', padx=5, pady=5, expand=True)
        self.tree.bind("<Double-1>", self.on_event_selected)
        
        # plot single event
        plotEvent_frame = tk.Frame(self.root)
        plotEvent_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(plotEvent_frame, text="Plot single event by given ID:").pack(side='left')
        self.entry_plot = tk.Entry(plotEvent_frame, width=50)
        self.entry_plot.pack(side='left', padx=5)

        self.btn_plot = tk.Button(plotEvent_frame, text="Plot single event", command=self.plot_single_event)
        self.btn_plot.pack(side='left', padx=10)
        
        # Event comparison
        compare_frame = tk.Frame(self.root)
        compare_frame.pack(fill='x', padx=5, pady=5)

        tk.Label(compare_frame, text="Compare Event IDs (Max 8, comma separated):").pack(side='left')
        self.entry_compare = tk.Entry(compare_frame, width=50)
        self.entry_compare.pack(side='left', padx=5)

        self.btn_compare = tk.Button(compare_frame, text="Compare in Gantt", command=self.plot_gantt)
        self.btn_compare.pack(side='left', padx=10)

        # Plot frame
        # self.plot_frame = tk.Frame(self.root)
        # self.plot_frame.pack(fill='both', expand=True)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not path:
            return
        try:
            df = pd.read_csv(path, sep='\t', parse_dates=["Date/Time"])
            assert all(col in df.columns for col in ["Date/Time", "Id", "Name", "Status"])
            df = df.sort_values("Date/Time").reset_index(drop=True)
            self.df = df
            self.file_path = path
            self.label_file.config(text=path, bg='lightgreen')
            self.original_start_time = self.df["Date/Time"].min()
            self.original_end_time = self.df["Date/Time"].max()
            messagebox.showinfo("Success", "File loaded successfully")

            # Set start and end time inputs
            self.entry_start.delete(0, tk.END)
            self.entry_end.delete(0, tk.END)
            self.entry_start.insert(0, self.original_start_time)
            self.entry_end.insert(0,  self.original_end_time)

            self.update_ranking()
        except Exception as e:
            self.df = None
            self.label_file.config(text="Failed to load file", bg='red')
            messagebox.showerror("Error", f"File load failed: {e}")
    
    def reset_time_range(self):
        if hasattr(self, "original_start_time") and hasattr(self, "original_end_time"):
            self.entry_start.delete(0, tk.END)
            self.entry_start.insert(0, self.original_start_time)
    
            self.entry_end.delete(0, tk.END)
            self.entry_end.insert(0, self.original_end_time)
            
            
    def reset(self):
        self.reset_time_range()
        self.update_ranking()

    
    def get_filtered_df(self):
        try:
            start_str = self.entry_start.get()
            end_str = self.entry_end.get()
    
            # Try parsing the start and end time
            start = pd.to_datetime(start_str, format="%Y-%m-%d %H:%M:%S")
            end = pd.to_datetime(end_str, format="%Y-%m-%d %H:%M:%S")
    
            if start > end:
                messagebox.showerror("Invalid Time Range", "Start time must not be after end time.")
                self.reset_time_range()
                return self.df.copy()
    
            return self.df[(self.df["Date/Time"] >= start) & (self.df["Date/Time"] <= end)].copy()
    
        except ValueError:
            messagebox.showerror("Invalid Time Format", "Time must be in format YYYY-MM-DD HH:MM:SS.")
            self.reset_time_range()
            return self.df.copy()


    def update_ranking(self):
        if self.df is None:
            return
    
        df = self.get_filtered_df()
        ranking = []
    
        for (name, eid), group in df.groupby(["Name", "Id"]):
            group = group.sort_values("Date/Time").reset_index(drop=True)
            on_periods = []
            for i in range(len(group) - 1):
                if group.loc[i, "Status"] == "ON" and group.loc[i+1, "Status"] == "OFF":
                    duration = group.loc[i+1, "Date/Time"] - group.loc[i, "Date/Time"]
                    on_periods.append(duration.total_seconds()/60)
    
            if self.rank_type.get() == 'single_on':
                if on_periods:
                    max_dur = max(on_periods)
                    ranking.append((name, eid, f"{max_dur:.1f} min"))
            elif self.rank_type.get() == 'total_on':
                total_dur = sum(on_periods)
                ranking.append((name, eid, f"{total_dur:.1f} min"))
            elif self.rank_type.get() == 'count_on':
                count = sum(1 for status in group["Status"] if status == "ON")
                ranking.append((name, eid, f"{count} times"))
    
        # Sort
        if self.rank_type.get() != 'count_on':
            ranking.sort(key=lambda x: float(x[2].split()[0]), reverse=True)
        else:
            ranking.sort(key=lambda x: int(x[2].split()[0]), reverse=True)
    
        # Clear and insert
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in ranking[:10]:
            self.tree.insert("", "end", values=row)

    def show_unique_events(self):
            if self.df is None or self.df.empty:
                messagebox.showwarning("Warning", "DataFrame is empty or not loaded!")
                return
            
            # 从 DataFrame 提取不重复的 (Id, Name) 组合
            unique_events = self.df[['Id', 'Name']].drop_duplicates().sort_values(by='Name')
    
            # 新窗口展示
            win = tk.Toplevel(self.root)
            win.title("Unique Events and IDs")
    
            tree = ttk.Treeview(win, columns=("ID", "Event"), show="headings")
            tree.heading("ID", text=" Event ID")
            tree.heading("Event", text="Event Name")
            tree.column("ID", width=150)
            tree.column("Event", width=250)
            tree.pack(fill=tk.BOTH, expand=True)
    
            # 插入数据
            for _, row in unique_events.iterrows():
                tree.insert("", tk.END, values=(row['Id'], row['Name']))
    
            scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_event_selected(self, event):
        if self.df is None:
            return
        selected = self.tree.focus()
        if not selected:
            return
        name = self.tree.item(selected)["values"][0]
        eid = self.tree.item(selected)["values"][1]
        #self.plot_event(name, eid)
        self.plot_event_step(name, eid)
        
    def plot_single_event(self):
        df = self.get_filtered_df()
        unique_ids = df["Id"].unique().tolist()
        try:
            eid = int(self.entry_plot.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a single valid integer event ID.")
            return
        
        if eid not in unique_ids:
            messagebox.showerror("Invalid ID", f"Event ID {eid} does not exist in the data.")
            return
        
        self.plot_event_step(df[df["Id"].astype(int) == eid]["Name"].unique()[0], eid)
        

    def plot_event_step(self, name, eid):
        window = tk.Toplevel(self.root)
        window.title(f"Event: {name} ID: {eid}")
        df = self.get_filtered_df()
        group = df[df["Name"] == name].sort_values("Date/Time").reset_index(drop=True)
    
        # Map status to numeric: ON=1, OFF=0
        y = group["Status"].map({"ON": 1, "OFF": 0})
    
        fig = Figure(figsize=(10, 2))
        ax = fig.add_subplot(111)
        ax.step(group["Date/Time"], y, where='post', linewidth=2)
        ax.fill_between(group["Date/Time"], 0, y, step='post', alpha=0.3, color='red')
    
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["OFF", "ON"])
        ax.set_title(f"Event: {name} ID: {eid} (Step Plot)")
        ax.set_xlabel("Time")
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)


    # def plot_event(self, name, eid):
    #     df = self.get_filtered_df()
    #     group = df[df["Name"] == name].sort_values("Date/Time").reset_index(drop=True)
    #     fig, ax = plt.subplots(figsize=(10, 2))

    #     for i in range(len(group) - 1):
    #         t0 = group.loc[i, "Date/Time"]
    #         t1 = group.loc[i + 1, "Date/Time"]
    #         status = group.loc[i, "Status"]
    #         color = 'red' if status == "ON" else 'green'
    #         ax.plot([t0, t1], [1, 1], color=color, linewidth=10)

    #     ax.set_yticks([])
    #     ax.set_title(f"Event: {name} ID: {eid}")
    #     ax.set_xlabel("Time")
    #     fig.tight_layout()

        # if self.canvas:
        #     self.canvas.get_tk_widget().destroy()
        # self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        # self.canvas.draw()
        # self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def plot_gantt(self):
        if self.df is None:
            return
        
        raw_ids = self.entry_compare.get().split(',')
        ids = []
        for i in raw_ids:
            i = i.strip()
            if not i:
                continue
            try:
                ids.append(int(i))
            except ValueError:
                messagebox.showerror("Invalid Input", f"'{i}' is not a valid integer.")
                return
        ids = list(set(ids))
        if len(ids) == 1 or len(ids) > 8:
            messagebox.showerror("Error", "Please enter 2 to 8 event IDs")
            return
       
        df = self.get_filtered_df()
        unique_ids = df["Id"].unique().tolist()
        
        # Find ids that are NOT in unique_ids
        invalid_ids = [eid for eid in ids if eid not in unique_ids]
        if invalid_ids:
            messagebox.showerror("Invalid IDs", f"The following IDs do not exist:\n{', '.join(str(i) for i in invalid_ids)}")
            return

        window = tk.Toplevel(self.root)
        window.title("Gantt Chart - Event Comparison")
        fig = Figure(figsize=(15, 1.1 * len(ids)))
        ax = fig.add_subplot(111)
        #fig, ax = plt.subplots(figsize=(15, 1.1 * len(ids)))
        #df["Date/Time"] = pd.to_datetime(df["Date/Time"], errors="coerce")
        yticks = []
        ylabels = []
        all_selected_times = df[df["Id"].astype(int).isin(ids)]["Date/Time"]
        time_start = all_selected_times.min()
        time_end = all_selected_times.max()
        total_duration_sec = (time_end - time_start).total_seconds()
        min_display_duration = total_duration_sec * 0.001 /86400
        for idx, eid in enumerate(ids):
            group = df[df["Id"].astype(int) == eid].sort_values("Date/Time").reset_index(drop=True)
    
            y_pos = idx * 10
            yticks.append(y_pos + 5)
            ylabels.append(f"{group.iloc[0]['Name']} (ID {eid})" if not group.empty else f"ID {eid}")
    
            bars = []
            #colors = []
    
            for i in range(len(group) - 1):
                status = group.loc[i, "Status"]
                if status != "ON":
                    continue
                t0 = group.loc[i, "Date/Time"]
                t1 = group.loc[i + 1, "Date/Time"]
                
                duration = (t1 - t0).total_seconds() / 86400  # convert seconds to days
                if duration < min_display_duration:
                    duration = min_display_duration
                bars.append((mdates.date2num(t0), duration))
                #colors.append("red" if status == "ON" else "green")
    
            #ax.broken_barh(bars, (y_pos, 8), facecolors=colors)
            ax.broken_barh(bars, (y_pos, 8), facecolors="red")
        
        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels)
        ax.set_xlabel("Time")
        ax.set_title("Event Comparison (Gantt View)")
    
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()
        fig.tight_layout()
    
        # plt.tight_layout()
        # plt.show()
        
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        
    
        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # if self.canvas:
        #     self.canvas.get_tk_widget().destroy()
        # self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        # self.canvas.draw()
        # self.canvas.get_tk_widget().pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = EventLogAnalyzer(root)
    root.mainloop()
