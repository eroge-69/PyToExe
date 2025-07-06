import os

class dataReader:
    
    def __init__(self, ipath, opath_fp, opath_out, opath_pp, opath_ref):
        self.ipath = ipath
        self.opath_fp = opath_fp
        self.opath_out = opath_out
        self.opath_pp = opath_pp
        self.opath_ref = opath_ref
        
        self.readFile()
        self.formatFile()
        self.exportFile()

    def readFile(self):    
        file = open(self.ipath, "r")
        self.data = file.read().split('\n')
        file.close()
        
    def printFile(self):
        print(self.data)
        print(type(self.data))
        
    def formatFile(self):
        
        lines = [i.split('\t') for i in self.data]
        
        self.lines_fp = [i for i in lines if i[1]=='FP' or i[1]=='FID']
        self.lines_out = [i for i in lines if i[1]=='OUT']
        self.lines_pp = [i for i in lines if i[1]=='PP' or i[1]=='PAP']
        self.lines_ref = [i for i in lines if i[1]=='REF']
        
        self.lines_pp_dict = {}
        
        header_fp = ['Gemeinde', 'KGname', 'Mnr', 'Mnart', 'SE', 'Fnr', 'X', 'Y', 'Z']
        header_out = ['Gemeinde', 'KGname', 'Mnr', 'Mnart', 'SE', 'X', 'Y', 'Z']
        
        for i,j in enumerate(self.lines_fp):
            self.lines_fp[i] = j[2:8]
            self.lines_fp[i].pop(1)
            self.lines_fp[i].insert(0, 'G')
            self.lines_fp[i].insert(0, '66328.25.01') #################### change year here ############################ 
            self.lines_fp[i].insert(0, 'Pichla bei Radkersburg')
            self.lines_fp[i].insert(0, 'Tieschen')
            
        for i,j in enumerate(self.lines_out):
            self.lines_out[i] = j[2:8]
            self.lines_out[i].pop(1)
            self.lines_out[i].insert(0, 'G')
            self.lines_out[i].insert(0, '66328.25.01') #################### change year here ############################ 
            self.lines_out[i].insert(0, 'Pichla bei Radkersburg')
            self.lines_out[i].insert(0, 'Tieschen')
            self.lines_out[i].pop(5)
            
        self.lines_fp.insert(0, header_fp)
        self.lines_out.insert(0, header_out)
        suid_list = []
        
        for i,j in enumerate(self.lines_pp):
            self.lines_pp[i] = j[2:8]
            self.lines_pp[i].pop(2)
            self.lines_pp[i][1] = 'target '+self.lines_pp[i][1]
            if self.lines_pp[i][0] not in suid_list:
                suid_list.append(self.lines_pp[i][0])
            
        for i in suid_list:
            self.lines_pp_dict[i] = [j for j in self.lines_pp if j[0] == i]
            for k in range(len(self.lines_pp_dict[i])):
                self.lines_pp_dict[i][k].pop(0)
            self.lines_pp_dict[i].sort()
                
        for i,j in enumerate(self.lines_ref):
            self.lines_ref[i] = j[3:8]
            self.lines_ref[i].pop(1)
            self.lines_ref[i][0] = 'REF'+self.lines_ref[i][0]
                
    
    def exportFile(self):
        
        if len(self.lines_fp) > 0:        
            with open(self.opath_fp, "w") as fp:
                for i in self.lines_fp:
                    fp.write(i[0]+','+i[1]+','+i[2]+','+i[3]+','+i[4]+','+i[5]+','+i[6]+','+i[7]+','+i[8]+'\n')
                
        if len(self.lines_out) > 0:
            with open(self.opath_out, "w") as out:
                for i in self.lines_out:
                    out.write(i[0]+','+i[1]+','+i[2]+','+i[3]+','+i[4]+','+i[5]+','+i[6]+','+i[7]+'\n')
                
        for p in (self.lines_pp_dict.keys()):
            with open(self.opath_pp+'_SE'+p+'_pp.txt', "w") as pp:
                for i in self.lines_pp_dict[p]:
                    pp.write(i[0]+','+i[1]+','+i[2]+','+i[3]+'\n')
                    
        if len(self.lines_ref) > 0:
            with open(self.opath_ref, "w") as ref:
                for i in self.lines_ref:
                    ref.write(i[0]+','+i[1]+','+i[2]+','+i[3]+'\n')

######################################################################################################################################

names = os.listdir('.')

for i in names:
    try:
        if i[-3:] == 'txt' and i[-7:-4] not in ['_fp', 'out', '_pp', 'ref', 'Log']:
            try:
                name = i[:-4]
                export = dataReader(i, name+'_fp.txt', name+'_out.txt', name, name+'_ref.txt')
            except:
                with open('ErrorLog.txt', "a") as errorFile:
                    errorFile.write("\n\nFailed to format Data, input file seems to be invalid!\n   The Problem appeared at: ")
                    errorFile.write(i)
    except:
        with open('ErrorLog.txt', "a") as errorFile:
                    errorFile.write("\n\nFailed to open file, naming convention was ignored!\n   The Problem appeared at: ")
                    errorFile.write(i)

    

