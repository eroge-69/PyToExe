import tkinter as tk
import tkinter.filedialog as fd
import itertools

import sys
if sys.platform == "win32":
    import ctypes
    ctypes.windll.kernel32.SetDllDirectoryW(None)

root = tk.Tk()
root.withdraw()
pDNA_file = fd.askopenfilename(title = u'Выберите исходный файл',filetypes=[("PDNA files", ".pdna")])
root.destroy()

with open(pDNA_file) as f:
    catalogue_list = f.readlines()
f = open('C:\\bardin\\py\\%s.txt'%input('Название файла для записи результатов: '), 'w', encoding="utf-8")
catalogue_dict = {}
for i in catalogue_list:
    if i.startswith('>'):
        key = i.strip()
        catalogue_dict[key]=[]
    else:
        catalogue_dict[key].append(i.strip())
selected_plasmids = {i:[] for i in catalogue_dict}
for i,j in catalogue_dict.items():
    if len(j)>1:
        print('%s plasmids'%i[1:].capitalize())
        for ind, k in enumerate(j, start = 1):
            print(ind, k.split()[0])
        for selected in input('Select %s plasmid(s): '%i[1:]).split():
            selected = int(selected)
            selected_plasmids[i].append(j[selected-1])
    else:
        selected_plasmids[i] = j
print('\nВыбраны следующие плазмиды:')
for i,j in selected_plasmids.items():
    header = '\n%s plasmids'%i[1:].capitalize()
    print('%s\n%s'%(header,'='*len(header)))
    for k in j:
        name, size, _ = k.split()
        print(name)
        f.write('> {:<30}  {:>6} bp\n'.format(name, size))
input()

plasmid_combinations = itertools.product(*selected_plasmids.values())
print('Комбинации плазмид: ')
plasmid_combinations_list = []
for i in plasmid_combinations: 
    pDNAs = {name:{'mw':int(size)*617.96,'conc':float(conc)} for name, size, conc in [j.split() for j in i]}
    print('%s + %s + %s'%tuple(pDNAs.keys()))
    plasmid_combinations_list.append(pDNAs)

total_pDNA_mkg = float(input('\nОбщее количество пДНК, μг: '))
total_pDNA_pg = total_pDNA_mkg*10**6
f.write('\nTotal pDNA: %.2f μg\n'%(total_pDNA_mkg))
PDratio, PEIstock = (float(input('PEI/DNA ratio (e.g. 3, not 3:1): ')), float(input('PEI (mg/ml): ')))
f.write('PEI/DNA ratio: %.1f:1 (%.2f μl %.1f mg/ml PEI)\n'%(PDratio, total_pDNA_mkg*PDratio/PEIstock, PEIstock))
molar_ratio = input('Введите молярное соотношение (через пробел): ')
f.write('pDNA molar ratio is %s\n'%molar_ratio.replace(' ',':'))
f.write('Minimal volume of pDNA solution: %.2f ml\n'%(total_pDNA_mkg/60)) # 60 μg/ml pDNA + 1V PEI --> 30 μg/ml
f.write('-'*90+'\n')
molar_ratio = [float(i) for i in molar_ratio.split(' ')]

for pDNAs in plasmid_combinations_list:
    MW_sum = 0.0
    for name,coeff in zip(pDNAs, molar_ratio):
        MW_sum += pDNAs[name]['mw']*coeff
        pDNAs[name]['coeff'] = coeff
    x = total_pDNA_pg/MW_sum
    for i,j in pDNAs.items():
        pDNA_pmol = x*j['coeff']; pDNA_mkg = pDNA_pmol*j['mw']*10**-6
        pDNA_mkl = pDNA_mkg/j['conc']
        txt = '{:<40} {:>5.2f} μg/μl  {:>7.3f} pmol  {:>7.3f} μg  {:>6.2f} μl'.format(i, j['conc'], pDNA_pmol, pDNA_mkg, pDNA_mkl)
        print(txt)
        f.write(txt+'\n')
    print('-'*90); f.write('-'*90+'\n')
commentary = input('Комментарий: ')
f.write(commentary)
f.close()

if 'y' in input('Print data? (y/n): ').lower():
    import os
    input('Check if printer is on, then press Enter')
    os.startfile(f.name,"print")
    
input('OK!')