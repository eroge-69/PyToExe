import tkinter as tk
from tkinter import messagebox, font

class MergeSortVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Merge Sort Visualizer")
        self.root.configure(bg="#121212")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 700)

        self.cyan = "#53ecdb"
        self.pink = "#fe83a2"
        self.yellow = "#feec6f"
        self.text_pink = "#fe83a2"
        self.bg_white = "#ffffff"
        self.bg_dark = "#121212"
        self.highlight_color = "#e0e0e0"

        self.numbers = []
        self.steps = []
        self.step_index = 0
        self.visual_type = tk.StringVar(value="Tree")

        self.min_inputs = 6
        self.default_inputs = 6

        self.entry_visual_width = 40
        self.entry_padx = 5
        self.entry_bd = 2
        self.entry_spacing = self.entry_padx * 2 + self.entry_bd * 2
        self.entry_total_width_per_item = self.entry_visual_width + self.entry_spacing
        self.entry_height_px = 60
        
        self._start_index_of_final_messages = None 

        self.setup_ui()

    def setup_ui(self):
        self.title_font = font.Font(family="Poppins", size=18, weight="bold")
        self.label_font = font.Font(family="Poppins", size=12, weight="bold")
        self.step_font = font.Font(family="Poppins", size=11, weight="bold")
        self.index_font = font.Font(family="Poppins", size=9)

        title = tk.Label(
            self.root,
            text="MERGE SORT VISUALIZER",
            bg=self.bg_white,
            fg=self.pink,
            font=self.title_font,
            padx=10,
            pady=6,
        )
        title.pack(pady=(20, 10))

        self.top_level_container = tk.Frame(self.root, bg=self.bg_dark)
        self.top_level_container.pack(pady=5, padx=20, anchor="center")

        input_and_buttons_section = tk.Frame(self.top_level_container, bg=self.bg_dark)
        input_and_buttons_section.pack(side="left", anchor="n", padx=(0, 240))

        input_label = tk.Label(
            input_and_buttons_section,
            text="Input the numbers you want to sort (Min. of 6 numbers):",
            fg=self.pink,
            bg=self.bg_dark,
            font=self.label_font,
        )
        input_label.pack(pady=(0, 5))

        self.input_controls_container = tk.Frame(input_and_buttons_section, bg=self.bg_dark)
        self.input_controls_container.pack(pady=5, anchor="w")

        self.calculated_canvas_width = (self.entry_total_width_per_item * self.min_inputs) + (self.entry_padx * (self.min_inputs - 1))

        self.canvas_scroll_frame = tk.Frame(self.input_controls_container, bg=self.bg_dark)
        self.canvas_scroll_frame.pack(side="left", padx=(0, 10))

        self.input_canvas = tk.Canvas(self.canvas_scroll_frame,
                                       bg=self.bg_dark,
                                       height=self.entry_height_px + 20,
                                       width=self.calculated_canvas_width,
                                       highlightthickness=0)
        self.input_canvas.pack(side="top", fill="none", expand=False)

        self.h_scroll = tk.Scrollbar(self.canvas_scroll_frame, orient="horizontal", command=self.input_canvas.xview)
        self.h_scroll.pack(side="bottom", fill="x")
        self.input_canvas.configure(xscrollcommand=self.h_scroll.set)

        self.input_frame = tk.Frame(self.input_canvas, bg=self.bg_dark)
        self.input_window = self.input_canvas.create_window((0,0), window=self.input_frame, anchor="nw")

        def on_frame_configure(event):
            self.input_canvas.configure(scrollregion=self.input_canvas.bbox("all"))
            canvas_width = self.input_canvas.winfo_width()
            frame_width = self.input_frame.winfo_reqwidth()
            x_offset = max(0, (canvas_width - frame_width) // 2)
            self.input_canvas.coords(self.input_window, x_offset, 0)

        self.input_frame.bind("<Configure>", on_frame_configure)
        self.input_canvas.bind("<Configure>", on_frame_configure)

        self.entries = []
        self.index_labels = []

        for i in range(self.default_inputs):
            self._create_entry(i)

        self.root.update_idletasks()
        on_frame_configure(None)

        self.minus_btn = tk.Button(
            self.input_controls_container,
            text="−",
            width=3,
            height=1,
            font=("Poppins", 18, "bold"),
            fg=self.pink,
            bg=self.cyan,
            relief="solid",
            bd=2,
            command=self.remove_input,
            activebackground="#7ef3e0",
            activeforeground=self.pink,
        )
        self.minus_btn.pack(side="right", padx=(5, 0), pady=5)

        self.plus_btn = tk.Button(
            self.input_controls_container,
            text="+",
            width=3,
            height=1,
            font=("Poppins", 18, "bold"),
            fg=self.pink,
            bg=self.cyan,
            relief="solid",
            bd=2,
            command=self.add_input,
            activebackground="#7ef3e0",
            activeforeground=self.pink,
        )
        self.plus_btn.pack(side="right", padx=(5, 0), pady=5)

        main_btn_frame = tk.Frame(input_and_buttons_section, bg=self.bg_dark)
        main_btn_frame.pack(pady=15)

        self.start_btn = tk.Button(
            main_btn_frame,
            text="Start Sorting",
            bg=self.pink,
            fg=self.yellow,
            font=self.label_font,
            width=15,
            command=self.start_sorting,
            relief="flat",
            activebackground="#fda1b8",
            activeforeground="#fff7a3",
        )
        self.start_btn.grid(row=0, column=0, padx=15)

        self.reset_btn = tk.Button(
            main_btn_frame,
            text="Reset",
            bg=self.cyan,
            fg=self.pink,
            font=self.label_font,
            width=10,
            command=self.reset_all,
            relief="flat",
            activebackground="#7ef3e0",
            activeforeground=self.pink,
        )
        self.reset_btn.grid(row=0, column=1, padx=15)

        color_guide_frame = tk.Frame(self.top_level_container, bg=self.bg_white, padx=15, pady=15)
        color_guide_frame.pack(side="left", anchor="n")

        cg_title = tk.Label(
            color_guide_frame,
            text="Color Guides:",
            bg=self.bg_white,
            fg=self.pink,
            font=self.label_font,
            pady=5,
        )
        cg_title.pack(anchor="center")

        def color_guide_item(color, text):
            frame = tk.Frame(color_guide_frame, bg=self.bg_white)
            frame.pack(anchor="w", pady=5)
            box = tk.Label(
                frame,
                bg=color,
                width=3,
                height=1,
                relief="solid",
                bd=1,
                borderwidth=2,
                highlightthickness=0,
            )
            box.pack(side="left")
            label = tk.Label(
                frame,
                text=text,
                bg=self.bg_white,
                fg="black",
                font=("Poppins", 11, "bold"),
                padx=10,
            )
            label.pack(side="left")

        color_guide_item(self.pink, "Split")
        color_guide_item(self.cyan, "Merge")
        color_guide_item(self.yellow, "Single (Ready for Merge)")

        display_frame = tk.Frame(self.root, bg=self.bg_dark)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = tk.Frame(display_frame, bg=self.bg_white, width=650, height=420)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        left_frame.pack_propagate(False)

        left_title = tk.Label(
            left_frame,
            text="Visualize the Process:",
            bg=self.bg_white,
            fg=self.pink,
            font=self.label_font,
            pady=5,
        )
        left_title.pack(anchor="center")
        
        self.visual_canvas_frame = tk.Frame(left_frame, bg=self.bg_white)
        self.visual_canvas_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))

        self.visual_canvas = tk.Canvas(self.visual_canvas_frame, bg=self.bg_white, highlightthickness=0)
        self.visual_canvas.pack(side="left", fill="both", expand=True)

        self.v_scroll_visual = tk.Scrollbar(self.visual_canvas_frame, orient="vertical", command=self.visual_canvas.yview)
        self.v_scroll_visual.pack(side="right", fill="y")
        
        self.h_scroll_visual = tk.Scrollbar(left_frame, orient="horizontal", command=self.visual_canvas.xview)
        self.h_scroll_visual.pack(side="bottom", fill="x")

        self.visual_canvas.configure(yscrollcommand=self.v_scroll_visual.set, xscrollcommand=self.h_scroll_visual.set)

        self.canvas_drawing_area = self.visual_canvas

        right_frame = tk.Frame(display_frame, bg=self.bg_dark, width=350)
        right_frame.pack(side="right", fill="y", padx=(10, 0), pady=10)
        right_frame.pack_propagate(False)

        nav_btn_frame = tk.Frame(right_frame, bg=self.bg_dark)
        nav_btn_frame.pack(fill="x", pady=(10, 0), side="bottom")

        button_inner_frame = tk.Frame(nav_btn_frame, bg=self.bg_dark)
        button_inner_frame.pack(anchor="center")

        self.prev_btn = tk.Button(
            button_inner_frame,
            text="Previous",
            bg=self.cyan,
            fg=self.pink,
            font=self.label_font,
            width=12,
            command=self.prev_step,
            relief="flat",
            state="disabled",
            activebackground="#7ef3e0",
            activeforeground=self.pink,
        )
        self.prev_btn.pack(side="left", padx=(0, 15))

        self.next_btn = tk.Button(
            button_inner_frame,
            text="Next",
            bg=self.cyan,
            fg=self.pink,
            font=self.label_font,
            width=12,
            command=self.next_step,
            relief="flat",
            state="disabled",
            activebackground="#7ef3e0",
            activeforeground=self.pink,
        )
        self.next_btn.pack(side="left", padx=(15, 0))

        steps_frame = tk.Frame(right_frame, bg=self.bg_white, padx=15, pady=15)
        steps_frame.pack(fill="both", expand=True, pady=(0, 10))

        steps_title_frame = tk.Frame(steps_frame, bg=self.bg_white)
        steps_title_frame.pack(anchor="center", pady=(0,5)) 

        steps_title = tk.Label(
            steps_title_frame,
            text="Steps:",
            bg=self.bg_white,
            fg=self.pink,
            font=self.label_font,
        )
        steps_title.pack(side="left")

        self.step_counter_label = tk.Label(
            steps_title_frame,
            text="",
            bg=self.bg_white,
            fg="black",
            font=("Poppins", 10, "bold"),
        )
        self.step_counter_label.pack(side="left", padx=(5,0)) 

        text_scroll_frame = tk.Frame(steps_frame, bg=self.bg_white)
        text_scroll_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.steps_text = tk.Text(
            text_scroll_frame,
            bg=self.bg_white,
            fg="black",
            font=self.step_font,
            wrap="word",
            state="disabled",
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.steps_text.pack(side="left", fill="both", expand=True)

        self.steps_scrollbar = tk.Scrollbar(text_scroll_frame, orient="vertical", command=self.steps_text.yview)
        self.steps_scrollbar.pack(side="right", fill="y")
        self.steps_text.config(yscrollcommand=self.steps_scrollbar.set)

        self.steps_text.tag_config("split_highlight", background=self.pink, foreground="black")
        self.steps_text.tag_config("merge_highlight", background=self.cyan, foreground="black")
        self.steps_text.tag_config("single_highlight", background=self.yellow, foreground="black")
        
        self.steps_text.tag_config("done_message", font=("Poppins", 12, "bold"), background=self.bg_white, foreground=self.pink, justify="center") 
        self.steps_text.tag_config("final_result", font=("Poppins", 11, "bold"), background=self.bg_white, foreground=self.pink, justify="center")

    def _create_entry(self, column_index):
        e = tk.Entry(
            self.input_frame,
            width=4,
            font=("Poppins", 16, "bold"),
            justify="center",
            bg=self.yellow,
            fg="black",
            relief="solid",
            bd=2,
        )
        e.grid(row=0, column=column_index, padx=5, pady=5)
        self.entries.append(e)

        index_label = tk.Label(
            self.input_frame,
            text=f"{column_index}",
            font=self.index_font,
            bg=self.bg_dark,
            fg="white",
        )
        index_label.grid(row=1, column=column_index, padx=5, pady=(0, 5))
        self.index_labels.append(index_label)

    def _update_input_layout(self):
        self.root.update_idletasks()
        self.input_canvas.configure(scrollregion=self.input_canvas.bbox("all"))
        canvas_width = self.input_canvas.winfo_width()
        frame_width = self.input_frame.winfo_reqwidth()
        x_offset = max(0, (canvas_width - frame_width) // 2)
        self.input_canvas.coords(self.input_window, x_offset, 0)

    def add_input(self):
        self._create_entry(len(self.entries))
        self._update_input_layout()
        self.start_btn.config(state="normal")
        self.next_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
        self.clear_steps_text_log()
        self.canvas_drawing_area.delete("all")
        self.steps.clear()
        self.step_index = 0
        self.update_step_counter()
        self.next_btn.config(text="Next")
        self._start_index_of_final_messages = None

    def remove_input(self):
        if len(self.entries) > self.min_inputs:
            e = self.entries.pop()
            e.destroy()
            l = self.index_labels.pop()
            l.destroy()
            self._update_input_layout()
            self.start_btn.config(state="normal")
            self.next_btn.config(state="disabled")
            self.prev_btn.config(state="disabled")
            self.clear_steps_text_log()
            self.canvas_drawing_area.delete("all")
            self.steps.clear()
            self.step_index = 0
            self.update_step_counter()
            self.next_btn.config(text="Next")
            self._start_index_of_final_messages = None
        else:
            messagebox.showinfo("Limit reached", f"Minimum {self.min_inputs} inputs required.")

    def start_sorting(self):
        self.numbers = []
        for e in self.entries:
            val = e.get().strip()
            if val != "":
                try:
                    self.numbers.append(int(val))
                except ValueError:
                    messagebox.showerror(
                        "Invalid input", "Please enter only integers."
                    )
                    return
        
        if len(self.numbers) < self.min_inputs:
            messagebox.showerror(
                "Input Error", f"Please enter at least {self.min_inputs} numbers to sort."
            )
            return

        self.start_btn.config(state="disabled")
        self.next_btn.config(state="normal", text="Next")
        self.prev_btn.config(state="disabled")

        self.canvas_drawing_area.delete("all")
        self.clear_steps_text_log() 
        self._start_index_of_final_messages = None

        self.steps = []
        self.step_index = 0

        self.root.update_idletasks()
        canvas_width = self.visual_canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 650

        initial_drawing_width = max(canvas_width, len(self.numbers) * 70 + 50)
        self.visual_canvas.configure(scrollregion=(0, 0, initial_drawing_width, 1)) 

        self.build_steps(self.numbers, 0, 0, initial_drawing_width, 40)
        
        self._prepare_step_descriptions() 

        if self.steps:
            self.steps_text.config(state="normal")
            first_step = self.steps[0]
            start_idx = self.steps_text.index("end-1c")
            self.steps_text.insert("end", first_step['full_text_desc'] + "\n") 
            end_idx = self.steps_text.index("end-1c")
            first_step['text_range'] = (start_idx, end_idx)
            
            self.steps_text.tag_add(first_step['highlight_tag'], first_step['text_range'][0], first_step['text_range'][1])
            self.steps_text.see(first_step['text_range'][0])
            self.steps_text.config(state="disabled")
        
        self.draw_current_step_visualization()
        self.update_step_counter()
        self.check_sorting_completion()


    def reset_all(self):
        self.numbers = []
        self.steps = []
        self.step_index = 0
        self.canvas_drawing_area.delete("all")
        self.clear_steps_text_log()
        self.update_step_counter() 

        self.start_btn.config(state="normal")
        self.next_btn.config(state="disabled", text="Next")
        self.prev_btn.config(state="disabled")
        self._start_index_of_final_messages = None

        for e in self.entries:
            e.destroy()
        self.entries.clear()
        for l in self.index_labels:
            l.destroy()
        self.index_labels.clear()

        for i in range(self.default_inputs):
            self._create_entry(i)

        self._update_input_layout()

        self.visual_canvas.configure(scrollregion=(0,0,1,1))
        self.steps_text.tag_remove("split_highlight", "1.0", "end")
        self.steps_text.tag_remove("merge_highlight", "1.0", "end")
        self.steps_text.tag_remove("single_highlight", "1.0", "end")
        self.steps_text.tag_remove("done_message", "1.0", "end")
        self.steps_text.tag_remove("final_result", "1.0", "end")
        for step in self.steps:
            step['text_range'] = (None, None)

    def clear_steps_text_log(self):
        self.steps_text.config(state="normal")
        self.steps_text.delete("1.0", "end")
        self.steps_text.config(state="disabled")

    def _get_step_description(self, step):
        if step["type"] == "split":
            return f"Splitting array: {step['arr']}", "split_highlight"
        elif step["type"] == "merge":
            return f"Merging arrays to form: {step['arr']}", "merge_highlight"
        else:
            return f"Single element ready for merge: {step['arr']}", "single_highlight"

    def _prepare_step_descriptions(self):
        for i, step in enumerate(self.steps):
            text_desc, highlight_tag = self._get_step_description(step)
            step['full_text_desc'] = f"Step {i+1}: {text_desc}"
            step['highlight_tag'] = highlight_tag 
            step['text_range'] = (None, None)

    def update_step_counter(self):
        total_steps = len(self.steps)
        if total_steps > 0:
            self.step_counter_label.config(text=f"({self.step_index + 1}/{total_steps})")
        else:
            self.step_counter_label.config(text="")

    def check_sorting_completion(self):
        if self.step_index == len(self.steps) - 1 and len(self.steps) > 0:
            self.next_btn.config(text="Done!", state="disabled")
            
            messagebox.showinfo("Sorting Complete", "Sorting Complete!")

            self.steps_text.config(state="normal")
            
            if self.step_index >= 0:
                last_numerical_step = self.steps[self.step_index]
                if last_numerical_step['text_range'][0] is not None:
                    self.steps_text.tag_remove(last_numerical_step['highlight_tag'], last_numerical_step['text_range'][0], last_numerical_step['text_range'][1])

            self.steps_text.tag_remove("done_message", "1.0", "end")
            self.steps_text.tag_remove("final_result", "1.0", "end")

            current_text_content = self.steps_text.get("1.0", "end-1c")
            if current_text_content and not current_text_content.endswith("\n"):
                self.steps_text.insert("end", "\n")

            self._start_index_of_final_messages = self.steps_text.index("end-1c")

            start_index_for_tag_done = self.steps_text.index("end-1c")
            self.steps_text.insert("end", "SORTING COMPLETE!")
            line_start_done = start_index_for_tag_done.split('.')[0]
            end_index_for_tag_done = f"{line_start_done}.end"
            self.steps_text.tag_add("done_message", start_index_for_tag_done, end_index_for_tag_done)
            
            self.steps_text.insert("end", "\n")
            
            final_array = self.steps[-1]['arr']
            final_result_str = f"FINAL RESULT: {final_array}"
            
            start_index_final_result = self.steps_text.index("end-1c")
            self.steps_text.insert("end", final_result_str)
            line_start_final = start_index_final_result.split('.')[0]
            end_index_final_result = f"{line_start_final}.end"
            self.steps_text.tag_add("final_result", start_index_final_result, end_index_final_result)


            self.steps_text.see("end")
            self.steps_text.config(state="disabled")
        else:
            self.next_btn.config(text="Next", state="normal")
            if self._start_index_of_final_messages is not None:
                self.steps_text.config(state="normal")
                self.steps_text.delete(self._start_index_of_final_messages, "end")
                self._start_index_of_final_messages = None 
                self.steps_text.tag_remove("done_message", "1.0", "end") 
                self.steps_text.tag_remove("final_result", "1.0", "end") 
                self.steps_text.config(state="disabled")


    def next_step(self):
        if self.step_index < len(self.steps) - 1:
            self.steps_text.config(state="normal")

            if self.step_index >= 0:
                prev_step = self.steps[self.step_index]
                if prev_step['text_range'][0] is not None:
                    self.steps_text.tag_remove(prev_step['highlight_tag'], prev_step['text_range'][0], prev_step['text_range'][1])

            self.step_index += 1
            current_step = self.steps[self.step_index]

            current_text_content = self.steps_text.get("1.0", "end-1c")
            if current_text_content and not current_text_content.endswith("\n"):
                self.steps_text.insert("end", "\n")

            if current_step['text_range'][0] is None:
                start_idx = self.steps_text.index("end-1c")
                self.steps_text.insert("end", current_step['full_text_desc'] + "\n")
                end_idx = self.steps_text.index("end-1c")
                current_step['text_range'] = (start_idx, end_idx)
            
            if current_step['text_range'][0] is not None:
                self.steps_text.tag_add(current_step['highlight_tag'], current_step['text_range'][0], current_step['text_range'][1])
                self.steps_text.see(current_step['text_range'][0]) 
            self.steps_text.config(state="disabled")

            self.draw_current_step_visualization()
            self.update_step_counter()
            self.prev_btn.config(state="normal")
            self.check_sorting_completion()
        else:
            self.next_btn.config(state="disabled")


    def prev_step(self):
        if self.step_index > 0:
            self.steps_text.config(state="normal")

            if self.step_index == len(self.steps) - 1 and self._start_index_of_final_messages is not None:
                self.steps_text.delete(self._start_index_of_final_messages, "end")
                self._start_index_of_final_messages = None 
                self.steps_text.tag_remove("done_message", "1.0", "end") 
                self.steps_text.tag_remove("final_result", "1.0", "end") 

            current_step_to_unhighlight_and_delete = self.steps[self.step_index]
            if current_step_to_unhighlight_and_delete['text_range'][0] is not None:
                self.steps_text.tag_remove(current_step_to_unhighlight_and_delete['highlight_tag'], current_step_to_unhighlight_and_delete['text_range'][0], current_step_to_unhighlight_and_delete['text_range'][1])
                
                self.steps_text.delete(current_step_to_unhighlight_and_delete['text_range'][0], current_step_to_unhighlight_and_delete['text_range'][1])
                current_step_to_unhighlight_and_delete['text_range'] = (None, None)
                
                current_content_after_del = self.steps_text.get("1.0", "end-1c")
                if current_content_after_del and not current_content_after_del.endswith("\n"):
                    self.steps_text.insert("end", "\n")

            self.step_index -= 1
            new_current_step_to_highlight = self.steps[self.step_index]

            if new_current_step_to_highlight['text_range'][0] is not None:
                self.steps_text.tag_add(new_current_step_to_highlight['highlight_tag'], new_current_step_to_highlight['text_range'][0], new_current_step_to_highlight['text_range'][1])
                self.steps_text.see(new_current_step_to_highlight['text_range'][0]) 
            self.steps_text.config(state="disabled")

            self.draw_current_step_visualization()
            self.step_counter_label.config(text=f"({self.step_index + 1}/{len(self.steps)})")
            self.next_btn.config(state="normal", text="Next")
            if self.step_index == 0:
                self.prev_btn.config(state="disabled")
        else:
            self.prev_btn.config(state="disabled")

    def update_visualization_type(self):
        pass

    def draw_current_step_visualization(self):
        if not self.steps:
            self.canvas_drawing_area.delete("all")
            self.visual_canvas.configure(scrollregion=(0,0,1,1))
            return

        self.canvas_drawing_area.delete("all")
        self.draw_tree_visualization(self.step_index)
        
        self.root.update_idletasks()
        bbox = self.canvas_drawing_area.bbox("all")
        if bbox:
            x1, y1, x2, y2 = bbox
            self.visual_canvas.configure(scrollregion=(x1 - 20, y1 - 20, max(x2 + 20, self.visual_canvas.winfo_width()), max(y2 + 20, self.visual_canvas.winfo_height())))
        else:
            self.visual_canvas.configure(scrollregion=(0,0,1,1))


    def draw_tree_visualization(self, current_step_index):
        max_x_coord = 0
        max_y_coord = 0
        
        for index in range(current_step_index + 1):
            step = self.steps[index]
            arr = step["arr"]
            block_width_base = 50
            padding = 4
            index_offset_y = 20 

            effective_block_width = max(10, block_width_base)
            block_height = 40
            y = step["y"]

            if step["type"] == "split":
                color = self.pink
            elif step["type"] == "merge":
                color = self.cyan
            else:
                color = self.yellow
            
            if index == current_step_index and index == len(self.steps) - 1:
                color = self.pink
                outline_color = "red"
                outline_width = 3
            elif index == current_step_index:
                outline_color = "red" 
                outline_width = 3
            else:
                outline_color = "black"
                outline_width = 2


            start_x = step["x_start"] 

            for i, val in enumerate(arr):
                x = start_x + i * (effective_block_width + padding)
                
                self.canvas_drawing_area.create_rectangle(
                    x,
                    y,
                    x + effective_block_width,
                    y + block_height,
                    fill=color,
                    outline=outline_color, 
                    width=outline_width,    
                )
                self.canvas_drawing_area.create_text(
                    x + effective_block_width / 2,
                    y + block_height / 2,
                    text=str(val),
                    font=("Poppins", 14, "bold"),
                    fill="black",
                )
                self.canvas_drawing_area.create_text(
                    x + effective_block_width / 2,
                    y + block_height + index_offset_y,
                    text=f"{i}",
                    font=("Poppins", 10),
                    fill="black",
                )

                max_x_coord = max(max_x_coord, x + effective_block_width)
                max_y_coord = max(max_y_coord, y + block_height + index_offset_y + 10)

    def build_steps(self, arr, depth, current_x_start, current_x_end, y_start):
        block_width = 50
        padding = 4
        total_arr_width = len(arr) * (block_width + padding) - padding
        
        horizontal_offset = (current_x_end - current_x_start - total_arr_width) / 2
        x_pos_for_array = current_x_start + max(0, horizontal_offset) 

        if len(arr) == 1:
            step = {
                "type": "single",
                "arr": list(arr),
                "depth": depth,
                "x_start": x_pos_for_array, 
                "x_end": x_pos_for_array + total_arr_width,
                "y": y_start,
                "text_range": (None, None)
            }
            self.steps.append(step)
            return arr

        step_split = {
            "type": "split",
            "arr": list(arr),
            "depth": depth,
            "x_start": x_pos_for_array, 
            "x_end": x_pos_for_array + total_arr_width,
            "y": y_start,
            "text_range": (None, None)
        }
        self.steps.append(step_split)

        mid = len(arr) // 2
        
        left_subtree_x_start = current_x_start
        left_subtree_x_end = current_x_start + (current_x_end - current_x_start) / 2
        
        right_subtree_x_start = current_x_start + (current_x_end - current_x_start) / 2
        right_subtree_x_end = current_x_end

        left = self.build_steps(arr[:mid], depth + 1, left_subtree_x_start, right_subtree_x_start, y_start + 80)
        right = self.build_steps(arr[mid:], depth + 1, right_subtree_x_start, right_subtree_x_end, y_start + 80) 

        merged = self.merge(left, right)

        step_merge = {
            "type": "merge",
            "arr": list(merged),
            "depth": depth,
            "x_start": x_pos_for_array, 
            "x_end": x_pos_for_array + total_arr_width,
            "y": y_start,
            "text_range": (None, None)
        }
        self.steps.append(step_merge)

        return merged

    def merge(self, left, right):
        if not left:
            return right
        if not right:
            return left

        merged = []
        i, j = 0, 0
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged


if __name__ == "__main__":
    root = tk.Tk()
    app = MergeSortVisualizer(root)
    root.mainloop()