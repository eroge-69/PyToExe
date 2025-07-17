out_file_name = input('Enter out. file name: ')

parameters = []
charge = ''
xyz = []

with open(out_file_name, "r") as out_file:
    
    lines = out_file.readlines()
    n = 0
    for line in lines:
        if '* xyz' in line:
            charge = line.split('*')[1].strip()
            
        if 'FINAL ENERGY EVALUATION AT THE STATIONARY POINT' in line:
            n = 1
            
        if n == 1:
            length = len(line.split())
            
            if length == 4:
            
                xyz.append(line.strip())
                
                
            if 'CARTESIAN COORDINATES (A.U.)' in line:
                break
        
        
parameters_SP = ['! RKS M06L D3zero def2-TZVPP def2/J', 
              '! defgrid3 TightSCF',
              '%scf MaxIter 500 end']


with open(out_file_name.split('.')[0] + '_SP.inp', 'w') as file:
    
    for line in parameters_SP:
        file.write(f"{line}\n")
        
    file.write('\n')
    file.write("* " + charge + "\n")
    
    for line in xyz:
        file.write(f"{line}\n")
        
    file.write("*\n")
    
    
    
parameters_S = ['! RKS M06L D3zero def2-TZVPP def2/J',
              '! CPCM defgrid3 TightSCF\n',
              '%cpcm',
              'smd true',
              'SMDsolvent "THF"',
              'end\n',
              '%scf MaxIter 500 end']

with open(out_file_name.split('.')[0] + '_S.inp', 'w') as file:
    
    for line in parameters_S:
        file.write(f"{line}\n")
        
    file.write('\n')
    file.write("* " + charge + "\n")
    
    for line in xyz:
        file.write(f"{line}\n")
        
    file.write("*\n")

print('SP an S files have been generated')
