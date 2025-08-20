import os
d = os.path.dirname(__file__) # directory of script
p = r'{}/results/graphs'.format(d) # path to be created

try:
    os.makedirs(p)
except OSError:
    pass