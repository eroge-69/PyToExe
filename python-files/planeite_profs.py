# -*- coding: utf-8 -*-



import numpy as np 
from mpl_toolkits.mplot3d import Axes3D ,axes3d
import matplotlib.pyplot as plt
import matplotlib as mp

#############################################
########## Importation des données ##########
#############################################

# importation des données comme chaînes de caractères

data = np.genfromtxt('etude1.csv', dtype=str,delimiter=';',skip_header=1)

# conversion ',' en '.'
data=np.array([[data[i][j].replace(",",".") for i in range (np.shape(data)[0])] for j in range (np.shape(data)[1])])

# conversion de type
data=data.astype(float)

#création des coordonnées de points
x=data[0]
y=data[1]
z=data[2]


#####################################
########## moindres carrés ##########
#####################################

# initialisation de la matrice :
A=np.zeros((3,3)) 
b=np.zeros(3)

for i in range(len(x)):
	A+=[[x[i]*x[i],x[i]*y[i],x[i]],[x[i]*y[i],y[i]*y[i],y[i]],[x[i],y[i],1]]
	b+=[x[i]*z[i],y[i]*z[i],z[i]]

# résolution A*t+b=0 :
t=np.linalg.solve(A, b)

# évaluation de la coordonnée z du plan des moindres carrés

zt=t[0]*x+t[1]*y+t[2]

# évaluation de la distance signée des points palpés au plan des moindres carrés (inversion de la normale)

dist=-(t[0]*x+t[1]*y-z+t[2])/(np.sqrt(t[0]**2+t[1]**2+1))
dist_max=np.argmax(dist)
dist_min=np.argmin(dist)
dmin=dist[dist_min]
dmax=dist[dist_max]

# évaluation de l'écart de forme

df=dmax-dmin

# évaluation des constantes des équations des plan inter et exter matière

D=z[dist_max]-t[1]*y[dist_max]-t[0]*x[dist_max]
d=z[dist_min]-t[1]*y[dist_min]-t[0]*x[dist_min]

###############################################
############# AFFICHAGE #######################
###############################################

# préparation des chaînes de caractères pour visualisation en console

rep1='Ecart maxi négatif = {0:.3f}mm'.format(dmin)
rep2='Ecert maxi positif = {0:.3f}mm'.format(dmax)
rep3='Equation du plan optimisé :{0:.5f}*x + {1:.5f}*y +z + {2:.3f}=0'.format(-t[0],-t[1],t[2])
rep5='Equation du plan optimisé normé :{0:.5f}*x + {1:.5f}*y +z + {2:.3f}=0'.format(-t[0],-t[1],D)
rep6='Equation du plan tangent intérieur :{0:.5f}*x + {1:.5f}*y +z + {2:.3f}=0'.format(-t[0],-t[1],d)
rep4='Defaut de planeïté = {0:.3f}mm'.format(df)


print ('============= Résultats =============')
print()
print (rep1) 
print (rep2)
print ()
print (rep3)
print (rep5)
print (rep6)
print ()
print (rep4)

########## Plan des moindres carrés ##########

xs=np.linspace(x.min(),x.max(),100) # Création de 100 points sur la longueur de l'axe X
ys=np.linspace(y.min(),y.max(),100) # Création de 100 points sur la longueur de l'axe X
X,Y=np.meshgrid(xs,ys) # Création d'une grille de coordonnées
Z=t[0]*X+t[1]*Y+t[2] # Evaluation de l'ordonnée Z

########## Plan tangent extérieur matière ##########

Z_ext=t[0]*X+t[1]*Y+D # Evaluation de l'ordonnée Z

########## Plan tangent intérieur matière ##########

Z_int=t[0]*X+t[1]*Y+d # Evaluation de l'ordonnée Z


fig = plt.figure(figsize=(20,10)) # Création de la figure
ax = fig.gca(projection='3d')

ax.scatter(x, y, z, c='y', marker='+') # affichage des points palpés
ax.scatter(x[dist_max], y[dist_max], z[dist_max], s=100, c='g', marker='o') # afficher Max
ax.scatter(x[dist_min], y[dist_min], z[dist_min], s=100, c='r', marker='o') # Affichaer Min


ax.plot_wireframe(X,Y,Z,color='b', rstride=8, cstride=8,alpha=1, label='plan des moindres carrés') # plan des moindres carrés
ax.plot_wireframe(X,Y,Z_ext,color='g', rstride=8, cstride=8,alpha=1, label='plan tangent extérieur') # plan tangent extérieur
ax.plot_wireframe(X,Y,Z_int,color='r', rstride=8, cstride=8,alpha=1, label='plan tangent intérieur') # plan tangent "intérieur"
ax.plot_trisurf(x,y,z, cmap=mp.cm.hot, alpha=0.9) # Surface palpée


# paramétrage des limites sur chaque axe
ax.set_xlim(left=0,right=80)
ax.set_ylim(bottom=0,top=140)
ax.set_zlim(bottom=-0.4,top=0.4)

# Label des axes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')


ax.legend(loc='upper center', bbox_to_anchor=(0.25, 1),
          ncol=2, fancybox=True, shadow=True)
# affichage de la figure
plt.show()
