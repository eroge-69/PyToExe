import tkinter as tk
import tkinter.filedialog
import csv


class App(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("IES Value Editor")
    self.geometry("300x300")
    start = tk.Button(text="Select IES File", command=self.open_csv)
    start.pack()
    tk.Label(text="Enter Factor").pack()
    self.factor_entry = tk.Entry()
    self.factor_entry.pack()
    convert = tk.Button(text="Update Values", command=self.convert)
    convert.pack()
    save = tk.Button(text="Save", command=self.save_csv)
    save.pack()

  def open_csv(self):
    filename = tkinter.filedialog.askopenfilename()
  
    with open(filename) as csvfile:
      file_data = csv.reader(csvfile, delimiter=' ')
      self.data_list = list(file_data)
  
    for i in range(len(self.data_list)):
      if self.data_list[i][0] == "TILT=NONE":
          self.header = i
          self.x_angles = int(self.data_list[i+1][3])
          self.y_angles = int(self.data_list[i+1][4])
  
    self.header_lines = self.data_list[:self.header+3]
    self.horiz = [val for sublist in self.data_list[self.header+3:self.header+4] for val in sublist if val!='']
    self.vert = [val for sublist in self.data_list[self.header+4:self.header+5] for val in sublist if val!='']
    self.new_ies = self.data_list[self.header+5:]
    
  def reformat(self):
      def fix_rows(data, index_start, num):
          angle_row = [val for val in data[index_start] if val!='']
          row_count = len(data[index_start])
          new_row = []
          while row_count < num:
              new_line = [val for val in data[index_start] if val!='']
              new_row.extend(new_line)
              row_count=len(new_row)
              index_start+=1
          return new_row, index_start

      def chunks(lst, n):
          for i in range(0, len(lst), n):
              yield lst[i:i+n]

      horiz, idx = fix_rows(self.data_list, self.header+3, self.x_angles)
      vert, idx2 = fix_rows(self.data_list, idx, self.y_angles)
      ies_data = self.data_list[idx2:]
      fix_lines = [item for sublist in ies_data for item in sublist if item!='']
      new_ies = [chunk for chunk in chunks(fix_lines, self.x_angles)]
      self.horiz = horiz
      self.vert = vert
      self.new_ies = new_ies
      return self.horiz, self.vert, self.new_ies
    
  def convert(self):
    if len(self.horiz) < self.x_angles:
      self.horiz, self.vert, self.new_ies = self.reformat()
    self.header_lines.append(self.horiz)
    self.header_lines.append(self.vert)
    new = []
    factor = float(self.factor_entry.get())
    
    for j in range(len(self.new_ies)):
      ies_row = [int(float(i)) for i in self.new_ies[j] if i!='']
      new_line = [int(i*factor) for i in ies_row]
      new.append(new_line)
    
    self.export_data = self.header_lines+new
  def save_csv(self):
    output = tkinter.filedialog.asksaveasfilename() 
    with open(f"{output}.ies", mode='w', newline='') as file:
      writer = csv.writer(file, delimiter=' ')
      writer.writerows(self.export_data)


app = App()
app.mainloop()