from skrf import Network
# import matplotlib
import matplotlib.pyplot as plt
import numpy as np

directory = 'D:/連接器/Python code test/Wxpython/'

# load single-ended data
se_s28p = Network(directory + 'pcie6_164p_20250625-SI.s28p')
se_s28p.renumber([1,2,5,6,9,10,13,14,17,18,21,22,25,26], [2,1,6,5,10,9,14,13,18,17,22,21,26,25])
# transform to mixed-modes

mm_dut = se_s28p.copy()
mm_dut.se2gmm(p = 14)
# d_ports = [0,1,2,3,4,5,6,7,8,9,10,11]
d_ports = np.arange(14)
spDD = mm_dut.subnetwork(d_ports)
spDD.renumber([1,2,3,4,5,6,7,8,9,10,11,12],[7,1,8,2,9,3,10,4,11,5,12,6])
# spDD.write_touchstone('spDD_153_z0_42p5_py.s12p')

# matplotlib.interactive(True)
plt.figure(figsize=(20, 10))
plt.title('Frequency')
# se_s28p.plot_s_db(9, 12)
# se_dut.plot_s_db(1, 0, marker = 'd', linestyle='None')
# se_s28p.plot_s_db(11, 14)
spDD.plot_s_db(9, 0)
spDD.plot_s_db(9, 2)
spDD.plot_s_db(9, 3)
plt.xlim((0, 25e9))
# plt.ylim((-50, 5))
# plt.legend(loc='lower right')
# plt.savefig(directory +'se-zc-dut')
# plt.show()
