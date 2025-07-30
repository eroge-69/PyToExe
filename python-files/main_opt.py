import sys
import random
sys.path.append("trend_trade_backtest")
from random_file import createrandom_float_and_int_number as random_gen
from other_files import function as function
from other_files import check_bounds as check_bounds
from other_files import finding_min_properties as finding_min_properties
from other_files import selection_partner as selection_partner
from other_files import Results as Results
from other_files import check_convergence as check_convergence
from other_files import finding_best_fitness as finding_best_fitness
from trend_trade_backtest.main import trend_trade_data as initial_data



trend_b='ETH3LUSDT_1H'
trade_b='ETH3LUSDT_15'

trend_f='ETH3SUSDT_1H'
trade_f='ETH3SUSDT_15'

name='Long_Short'+'1H'

trend_data,trade_data=initial_data(trend=trend_b,trade=trade_b)


N=20
D=4
maxiteration=50
v=[1,3]
nn=[5,20]
t=[5,10]
k=[12,18]
s=[26,40]


data=random_gen(N_raws=N,v=v,nn=nn,t=t,k=k,s=s)

fitness=function(trend_data=trend_data,trade_data=trade_data,data=data)

for i in range(0,maxiteration):
    print(i)
    for j in range(0,N):

        f_max,X_best,X_mean=finding_min_properties(data=data,fitness=fitness['Return System'])
        Tf=round(1+random.random())
        X_new=data.iloc[j]+random.random()*(X_best-Tf*X_mean)
        X_new=check_bounds(X_new=X_new,bound=[v,nn,t,k,s])
        f_new=function(trend_data=trend_data,trade_data=trade_data,data=X_new)

        if f_new['Return System'].iloc[0]>fitness['Return System'].iloc[j]:
            data.iloc[j]=X_new.astype('float64')
            fitness.iloc[j]=f_new.iloc[0]

        pa_i=selection_partner(n=N,j=j)
        X_p=data.iloc[pa_i]
        f_p=fitness.iloc[pa_i]

        if fitness['Return System'].iloc[j]<f_p['Return System'].iloc[0]:
            X_new=data.iloc[j]+random.random()*(data.iloc[j]-X_p)
            X_new=check_bounds(X_new=X_new,bound=[v,nn,t,k,s])
            f_new=function(trend_data=trend_data,trade_data=trade_data,data=X_new)
            if f_new['Return System'].iloc[0]>fitness['Return System'].iloc[j]:
                data.iloc[j]=X_new.astype('float64')
                fitness.iloc[j]=f_new

        if fitness['Return System'].iloc[j]>f_p['Return System'].iloc[0]:
            X_new=data.iloc[j]-random.random()*(data.iloc[j]-X_p)
            X_new=check_bounds(X_new=X_new,bound=[v,nn,t,k,s])
            f_new=function(trend_data=trend_data,trade_data=trade_data,data=X_new)
            if f_new['Return System'].iloc[0]>fitness['Return System'].iloc[j]:
                data.iloc[j]=X_new.astype('float64')
                fitness.iloc[j]=f_new



duration=[[trend_data.index[0],trend_data.index[-1]],[trade_data.index[0],trade_data.index[-1]]]


#Results(data=data,trend_f=trend_f,trade_f=trade_f,fitness=fitness,duration=duration,N=N,maxiteration=maxiteration,name=name,)
Results(data=data,fitness=fitness,duration=duration,N=N,maxiteration=maxiteration,name=name,)