with open('bruteArchive.txt') as fin, open('out.txt','w') as fout:
    for line in fin:
        fout.write(line.rstrip('\n') + ',\n')
