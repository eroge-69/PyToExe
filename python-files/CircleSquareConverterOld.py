# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 22:55:51 2024

@author: jschwarz
"""
from win32api import GetSystemMetrics
from tkinter import filedialog
#import tk as tk
import ezdxf
import os
import numpy as np
import tkinter as tk
import sys


def selectDXF():
    global main_win_destroy
    file_dir, file_ext = os.path.splitext(filedialog.askopenfilename(title='Select DXF File', filetypes=[('DXF','.dxf')]))
    for i, v in enumerate(main_win.winfo_children()):
        if i > 0: v.destroy()     
    dxf_doc=ezdxf.readfile(file_dir+file_ext)
    dxf_msp = dxf_doc.modelspace()
    
    def operation(function_type):

        for i, v in enumerate(main_win.winfo_children()):
            if i > 0: v.destroy()
        bigListbox = tk.Listbox(main_win, 
                                selectmode="multiple", 
                                height=len(dxf_doc.layers))
 
        for i, v in enumerate([l.dxf.name for l in dxf_doc.layers]):
            bigListbox.insert(i, v)
            
        def checkState(): 
            global main_win_destroy
            selectedIndices = bigListbox.curselection()
            
            
            error_check = False
            if function_type == 1:
                if var1.get()+var2.get() == 0 or var1.get()+var2.get() == 2:
                    for i, v in enumerate(main_win.winfo_children()):
                        if i > 0: v.destroy()
                    err_string = 'ERROR \n\n Please select a rectangle option'

                    if len(selectedIndices)==0:
                        err_string += '\n\n Please select a layer'

                    tk.TkButton(main_win,
                                            text='Reset', 
                                            command=Cir2Sq).pack(side='bottom', pady=50)
                    tk.Label(main_win,
                                           text=err_string).pack(side='bottom', pady=20)
                    error_check = True
                elif len(selectedIndices)==0: 
                    for i, v in enumerate(main_win.winfo_children()):
                        if i > 0: v.destroy()

                    tk.TkButton(main_win,
                                            text='Reset',
                                            command=Cir2Sq).pack(side='bottom', pady=50)
                    tk.Label(main_win,
                                           text='ERROR \n\n Please select a layer').pack(side='bottom', pady=20)
                    error_check = True
                else: 
                    error_check = False
                
            elif function_type == 0:
                circle_radius = main_win.winfo_children()[3].get()
                if len(selectedIndices)==0:
                    error_check = True
                    for i, v in enumerate(main_win.winfo_children()):
                        if i > 0: v.destroy()
 
                    tk.TkButton(main_win,
                                            text='Reset',
                                            command=Sq2Cir).pack(side='bottom', pady=50)
                    tk.Label(main_win,
                                           text='ERROR \n\n Please select a layer').pack(side='bottom', pady=20)
                else:
                    error_check - False
                
            if error_check == False:
                if function_type==1:
                    if var1.get() == 1: sq_type = 0
                    elif var2.get() == 1: sq_type = 1 
                
                layer_list=[]
                # Loop over the selected indices and get the values of the selected items
                for index in selectedIndices:
                    layer_list.append(bigListbox.get(index))
                    
                for layer_name in layer_list:


                    j=0
                    for E in dxf_doc.entities:
                        
                        if function_type==1:
                            if isinstance(E, ezdxf.entities.circle.Circle): 
                                if j == 0: 
                                    dxf_doc.layers.add(name=layer_name+'_pythonCir2Sq', color = 6)
                                if E.get_dxf_attrib('layer') == layer_name:
                                    xc = E.get_dxf_attrib('center')[0]
                                    yc = E.get_dxf_attrib('center')[1]
                                    r = E.get_dxf_attrib('radius')
                                    
                                    if sq_type == 0: a = 1
                                    elif sq_type == 1: a = np.sin(np.pi/4)
                                                
                                    sq = dxf_msp.add_lwpolyline([(xc - r*a, yc + r*a),
                                                                 (xc + r*a, yc + r*a),
                                                                 (xc + r*a, yc - r*a),
                                                                 (xc - r*a, yc - r*a)],
                                                                dxfattribs={'layer':layer_name+'_pythonCir2Sq'})
                                    sq.closed = True
                                j += 1
                        elif function_type==0:
                            if isinstance(E, ezdxf.entities.lwpolyline.LWPolyline):
                                if j == 0:
                                    dxf_doc.layers.add(name=layer_name+'_pythonSq2Cir', color = 3)
                                if E.get_dxf_attrib('layer') == layer_name:
                                    sq_points=[]
                                    for i, p in enumerate(E.vertices_in_wcs()):

                                        if i <= 2:
                                            sq_points.append((p[0],p[1]))
                                    xc = 0.5*(sq_points[0][0] + sq_points[1][0])
                                    yc = 0.5*(sq_points[0][1] + sq_points[2][1])
           
                                    if circle_radius == '': c_radius = abs(0.5*(sq_points[0][0]-sq_points[1][0]))
                                    else: c_radius = circle_radius
                                    dxf_msp.add_circle(center=(xc, yc), radius=c_radius, dxfattribs={'layer':layer_name+'_pythonSq2Cir'})
                                j += 1
                    dxf_doc.saveas(file_dir+'_python'+file_ext)
                    os.startfile(file_dir+'_python'+file_ext)  
                    main_win.destroy()
            return
        
        if function_type == 0:
            tk.Label(main_win,
                                   text='Please enter desired radius in inches').pack(side='top')
            tk.CTkEntry(main_win).pack(side='top',pady=50)
            
        elif function_type == 1:
            var1 = tk.IntVar(main_win)
            var2 = tk.IntVar(main_win)
            tk.CTkCheckBox(main_win, 
                                      text = 'Fit to Radius', 
                                      checkbox_height=20,
                                      checkbox_width=20,
                                      variable=var1).pack(side='top', pady=20)
            tk.CTkCheckBox(main_win, 
                                      text = 'Inscribed',
                                      checkbox_height=20,
                                      checkbox_width=20,
                                      variable=var2).pack(side='top', pady=20)

        tk.Label(main_win,
                               text='Layer Selector').pack(side='top')
        bigListbox.pack(side='top')
        tk.TkButton(main_win, 
                                text='Submit', 
                                command=checkState).pack(side='bottom', pady=50)
        
        return
    
    def Sq2Cir():
        operation(0)
        return
        
    def Cir2Sq():
        operation(1)
        return
    tk.TkButton(main_win,
                           text='Circles to Squares', 
                           command=Cir2Sq).pack(side='top', pady=100)
    tk.TkButton(main_win,
                           text='Squares to Circles', 
                           command=Sq2Cir).pack(side='top', pady=100)

    return


if __name__ == "__main__":  
    main_win_destroy=False
    main_win = tk.Toplevel()
    main_win.title("Circle-Square-Converter v1.0 -~- Jared Schwarz")
    main_win.geometry(str(int(GetSystemMetrics(0)/4))+'x'+str(int(GetSystemMetrics(1)-200)))
    main_win.resizable(False, False)
    tk.Label(main_win,
                           text='User:  '+str(os.getcwd()[9:][:os.getcwd()[9:].find('\\')])+'  ').pack(side='top', pady=50)
    tk.Button(main_win,
                            text='Select a DXF File',
                            command=selectDXF).pack(side='bottom', pady=50)
    
    main_win.mainloop()
    