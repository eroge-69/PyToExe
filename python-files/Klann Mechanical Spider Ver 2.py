# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 15:08:10 2017

@author: DIYwalkers.com

Diagrams of Klann's linkage is here:
https://www.diywalkers.com/klanns-linkage-plans.html
    
This linkage built in LEGO can be seen here:
https://www.diywalkers.com/klanns-spider-ver-2.html

NOTE: to animate the plot in Anaconda I needed to 
run "%matplotlib qt" in the console before running this code 
"""
#to animate first type in console:
#%matplotlib qt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import copy
import math

sim_scale=1
#Set moving to True to make Klann walk across screen
moving=False
#moving=True

#create 2 dictionaries to store the joints' X and Y coordinates
xdict={}
ydict={}
mech="klann"
#sub dictionaries make it easier to add other mechanisms
xdict[mech]={}
ydict[mech]={}
#do the same for the Bar lengths
bar={}
bar[mech]={}
#In order to more quickly animate a graph of a mechanism we'll want to send all 
#joint values for a given crank rotation to the graphing function at once
#We can do this by saving all calculated joint values for a given crank rotation to a List variable.
#Lists are another data structure, useful for saving a list of things that don't require keys.
#First, make 2 dictionaries to store each mech's list
xlist={}
ylist={}
#The lists are added to these dictionaries after the joint calc function 

#we'll also want to save the entire mechanism (all joints) to a dictionary with crank rotation as key.  
#create one for X and one for Y here:
entire_mech_x={}
entire_mech_y={} 
mech="klann"
entire_mech_x[mech]={}
entire_mech_y[mech]={} 

#and make a dict for each mech's foot-path
footpath_x={}
footpath_y={}
footpath_x[mech]={}
footpath_y[mech]={} 

bar[mech,0]=3*sim_scale 

#uncomment below for Klann's patented linkage 
bar[mech,2]=6.6*sim_scale
bar[mech,3]=3.59*sim_scale#4*sim_scale
bar[mech,4]=5.84*sim_scale
bar[mech,5]=10.04*sim_scale
bar[mech,6]=5.79*sim_scale
bar[mech,7]=10.04*sim_scale
#the following are the frame connections distances from the center of the crank
low_frameX=6.6
low_frameY=1.97
high_frameX=2.6
high_frameY=6.9
B7_angle=30.
B6_angle=12.8

#UNCOMMENT below for LEGO Klann Ver 2
#bar[mech,2]=7*sim_scale
#bar[mech,3]=4*sim_scale#4*sim_scale
#bar[mech,4]=6*sim_scale
#bar[mech,5]=10*sim_scale
#bar[mech,6]=6*sim_scale
#bar[mech,7]=10*sim_scale
#the following are the frame connections distances from the center of the crank
#low_frameX=7
#low_frameY=2
#high_frameX=3
#high_frameY=7
#B7_angle=29.
#B6_angle=0.0   

#Circle algo calcs for X and Y coordinates     
def jnt_x(ax, ay, bx, by, al, bl):
    dist = ((ax-bx)**2 + (ay-by)**2)**.5
    sidea = (al**2 - bl**2 + dist**2)/2/dist
    if al - sidea > 0:
        height = (al**2 - sidea**2)**.5
    else:
        height = 0
    Dpointx = (ax+sidea*(bx-ax)/dist)
    x1 = Dpointx + height*(ay-by)/dist
    x2 = Dpointx-height*(ay-by)/dist
    return x1,x2         

def jnt_y(ax, ay, bx, by, al, bl):
    dist = ((ax-bx)**2 + (ay-by)**2)**.5
    sidea = (al**2 - bl**2 + dist**2)/2/dist
    if al - sidea > 0:
        height = (al**2 - sidea**2)**.5
    else:
        height = 0
    Dpointy = (ay+sidea*(by-ay)/dist)
    y1 = Dpointy - height*(ax-bx)/dist
    y2 = Dpointy+height*(ax-bx)/dist
    return y1,y2    

#define 4 solutions for circle algo
high = 0
low = 1
left = 2
right = 3

def circle_algo(mech,j1,j2,b1,b2,i,solution):    
    x1,x2=jnt_x(xdict[mech,j1,i], ydict[mech,j1,i], xdict[mech,j2,i], ydict[mech,j2,i], bar[mech,b1], bar[mech,b2])
    y1,y2=jnt_y(xdict[mech,j1,i], ydict[mech,j1,i], xdict[mech,j2,i], ydict[mech,j2,i], bar[mech,b1], bar[mech,b2])
  #  print x1,y1
  #  print x2,y2
    if solution==high:
        if y1>y2:
            return x1,y1
        else:
            return x2,y2
    elif solution==low:
        if y1<y2:
            return x1,y1
        else:
            return x2,y2
    elif solution==right:
        if x1>x2:
            return x1,y1
        else:
            return x2,y2
    elif solution==left:
        if x1<x2:
            return x1,y1
        else:
            return x2,y2

def lineextend(X1, Y1, X2, Y2, Length):
    #print "change in X=",X2 - X1,"change in Y=",Y2 - Y1
    slopeangle = np.arctan2(Y2 - Y1,X2 - X1 )
    #print slopeangle
    myXlineextend = X1 - Length * np.cos(slopeangle)
    myYlineextend = Y1 - Length * np.sin(slopeangle)
    return myXlineextend,myYlineextend

def lineextendBentDegrees(X1, Y1, X2, Y2, Length,Angle):
    Angle2=Angle/180*np.pi
    slopeangle = np.arctan2(Y2 - Y1,X2 - X1 )#+Angle/180*np.pi
    myXlineextend = X1 - Length * np.cos(slopeangle+Angle2)
    myYlineextend = Y1 - Length * np.sin(slopeangle+Angle2)
    return myXlineextend,myYlineextend
    
 
#define how many simulations per rotation of the crank
#for example, to calculate every degree of crank rotation 
#you would set "rotationIncrements" to 360
#the higher rotationIncrements, the slower the sim
rotationIncrements=120
#since we want the mechs to walk farther than 1 rotation, set a loop_count variable to to walk farther
loop_count=rotationIncrements*4

#and make a dict for the following values
xcenter={}
ycenter={}    
avgspeed={}
xstart={}
xchange={}
#Klann's speed and starting position
xcenter[mech]=11*sim_scale
ycenter[mech]=8*sim_scale
if moving==False:
    avgspeed[mech]=0
    xstart[mech]=-11
else:
    avgspeed[mech]=-0.28*120/rotationIncrements*sim_scale
    xstart[mech]=50*sim_scale
xchange[mech]=xstart[mech]
       
def calc_joints(): 
#Your function code will loop thru one complete rotation of the crank
#You can step thru 2 Pi rotations in any increment you choose.  Say you start out with 100 increments
#This requires a step of 0.02 to go from 0 to 2. 
    for i in range(rotationIncrements):
        theta = (i / (rotationIncrements - 0.0)) * 2 * math.pi #creates rotationIncrements angles from 0 - 2pi
        mech="klann"
        joint=0
        xdict[mech,joint,i]=xcenter[mech]
        ydict[mech,joint,i]=ycenter[mech]

        joint=3
        xdict[mech,joint,i]=xcenter[mech]-low_frameX*sim_scale
        ydict[mech,joint,i]=ycenter[mech]-low_frameY*sim_scale
        
        joint=5
        xdict[mech,joint,i]=xcenter[mech]-high_frameX*sim_scale
        ydict[mech,joint,i]=ycenter[mech]+high_frameY*sim_scale
      
        joint=1
        xdict[mech,joint,i]=xcenter[mech]+bar[mech,0]*np.cos(-1*np.float64(theta))
        ydict[mech,joint,i]=ycenter[mech]+bar[mech,0]*np.sin(-1*np.float64(theta))

        joint=4
        j1=1
        b1=2
        j2=3      
        b2=3   
        xdict[mech,joint,i], ydict[mech,joint,i]=circle_algo(mech,j1,j2,b1,b2,i,high)
            
        joint=6
        j1=4
        j2=1
        b1=4
        xdict[mech,joint,i],ydict[mech,joint,i]=lineextendBentDegrees(xdict[mech,j1,i],ydict[mech,j1,i],xdict[mech,j2,i],ydict[mech,j2,i],bar[mech,b1],-1*B6_angle)
        
        joint=7
        j1=5
        b1=6
        j2=6       
        b2=5  
        xdict[mech,joint,i], ydict[mech,joint,i]=circle_algo(mech,j1,j2,b1,b2,i,high)

        joint=8
        j1=6
        j2=7
        b1=7
        xdict[mech,joint,i],ydict[mech,joint,i]=lineextendBentDegrees(xdict[mech,j1,i],ydict[mech,j1,i],xdict[mech,j2,i],ydict[mech,j2,i],bar[mech,b1],B7_angle)
    
        joint=103
        xdict[mech,joint,i]=xcenter[mech]+low_frameX*sim_scale
        ydict[mech,joint,i]=ycenter[mech]-low_frameY*sim_scale
        
        joint=105
        xdict[mech,joint,i]=xcenter[mech]+high_frameX*sim_scale
        ydict[mech,joint,i]=ycenter[mech]+high_frameY*sim_scale
        
        joint=104
        j1=1
        b1=2
        j2=103
        b2=3     
        xdict[mech,joint,i], ydict[mech,joint,i]=circle_algo(mech,j1,j2,b1,b2,i,high)
            
        joint=106
        j1=104
        j2=1
        b1=4
        xdict[mech,joint,i],ydict[mech,joint,i]=lineextendBentDegrees(xdict[mech,j1,i],ydict[mech,j1,i],xdict[mech,j2,i],ydict[mech,j2,i],bar[mech,b1],B6_angle)
        
        joint=107
        j1=105
        b1=6
        j2=106       
        b2=5       
        xdict[mech,joint,i], ydict[mech,joint,i]=circle_algo(mech,j1,j2,b1,b2,i,high)

        joint=108
        j1=106
        j2=107
        b1=7
        xdict[mech,joint,i],ydict[mech,joint,i]=lineextendBentDegrees(xdict[mech,j1,i],ydict[mech,j1,i],xdict[mech,j2,i],ydict[mech,j2,i],bar[mech,b1],-1*B7_angle)

#add joints to lists for plotting
    #create dict to hold mech's foot-path lists
    x_foot_path_list={}
    y_foot_path_list={}
    mech='klann'
    x_foot_path_list[mech]=[]
    y_foot_path_list[mech]=[]
                
    for i in range(loop_count):
        mech='klann'    
        xlist[mech]=[]
        ylist[mech]=[] 
        plot_joint_order=[0,1,4,3,4,6,7,5,7,6,8,6,4,1,0,1,104,103,104,106,107,105,5,3,0,103,105,107,106,108,106,104,1,0]
        for joint in  plot_joint_order:
            xlist[mech].append(xdict[mech,joint,np.mod(i,rotationIncrements)]+xchange[mech])
            ylist[mech].append(ydict[mech,joint,np.mod(i,rotationIncrements)])          
        for joint in  plot_joint_order:
            xlist[mech].append(xdict[mech,joint,np.mod(i+rotationIncrements/2,rotationIncrements)]+xchange[mech])
            ylist[mech].append(ydict[mech,joint,np.mod(i+rotationIncrements/2,rotationIncrements)])                 
        joint=8#108
        x_foot_path_list[mech].append(xdict[mech,joint,np.mod(i,rotationIncrements)]+xchange[mech])
        y_foot_path_list[mech].append(ydict[mech,joint,np.mod(i,rotationIncrements)])
        footpath_x[mech,i]=copy.deepcopy(x_foot_path_list[mech])
        footpath_y[mech,i]  =copy.deepcopy(y_foot_path_list[mech]) 
        xchange[mech]=xchange[mech]+avgspeed[mech]
        entire_mech_x[mech,i]=xlist[mech]
        entire_mech_y[mech,i]=ylist[mech]
      
                 
fig1 = plt.figure(figsize = (21, 6.9))
ax = fig1.add_subplot(111)
ax = plt.axes(xlim=(-38, 38), ylim=(-3, 22))
ax.set_title("Klann's Mechanical Spider", fontsize=18)

fig1.set_facecolor('white')
line, = ax.plot([], [], '-o', ms=round(7*sim_scale), lw=2,color='b', mfc='red') #linkage line
line2, = ax.plot([], [], '-o', lw=0, ms=1, alpha=1, mfc='red',mec='red') #foot-path line
               
def init():   
    line.set_data([], [])
    return line,

def animate(i):
    mech='klann'
    line.set_data(entire_mech_x[mech,i] , entire_mech_y[mech,i])
    line2.set_data(footpath_x[mech,i],footpath_y[mech,i])

    return line2, line,

calc_joints()

#to make the animation run faster set "blit=True"
ani = animation.FuncAnimation(fig1, animate, frames=loop_count,interval=0, blit=False, init_func=init)
plt.show() 

