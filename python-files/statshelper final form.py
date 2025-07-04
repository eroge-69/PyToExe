print('enter any invalid input to start calculating')
print()
while True:
    end=True
    list=[]
    enter=0
    while True:
        enter=input('number: ')
        try:
            list.append(float(enter))
        except ValueError:
            if len(list)==0:
                print('enter at least one value')
            else:    
                break
    print('sorting the list will change the correlation coefficient and line of best fit')
    print()
    while True:
        try:
            sort=int(input('to sort the list, enter 1. Else enter 0: '))
            if sort==1:
                list.sort()
                break
            elif sort==0:
               break
            else:
                print('enter 1 or 0 only')       
        except ValueError:
            print('enter 1 or 0 only')   
    
    
    
    print()
    print(list)
    print()
    print('no. of elements:')
    print(len(list))
    print('min value:')
    print(min(list))
    print('max value:')
    print(max(list))
    length=len(list)
    if length % 2 == 0:
        median = (list[length // 2 - 1] + list[length // 2]) / 2.0
        print('Median')
        print(median)
    else:
            median = list[length // 2]
            print('Median:')
            print(median)
    
    total = 0
    for ele in range(0,length):
        total = total + list[ele]
    mean=total/length
    print('sum of values:')
    print(total)
    print('arithmetic mean:')
    print(mean)
    print()
    
    product=1
    for i in range(0,length):
        product*=list[i]
    print('product:')   
    print(product)
    print()
    print('geometric mean:')
    print(product**(1/length))
    varsum=0
    for i in range(0,length):
        varsum+=(list[i]-mean)**2
    variance=varsum/length
    print("standard variance:")
    print(variance)

    deviation=variance**(1/2)
    print("standard deviation:")
    print(deviation)
    print()
    
    try:
        s2x=(varsum)/(length-1)
        print("sample variance(s2x):")
        print(s2x)
        sx=s2x**(1/2)
        print("sample standard deviation(sx):")
        print(sx)
    except ZeroDivisionError:
        print('s2x and sx not defined due to only one element being present')
    print()
    
    diffilist=0
    meani=(length+1)/2
    for i in range(1,length+1):
        diffilist+=(i-meani)*(list[i-1]-mean)
    
    varsumi=0
    for i in range(1,length+1):
        varsumi+=(i-meani)**2
        
    try:
        r=diffilist/(varsumi*varsum)**0.5
        print('correlation coefficient(r):')
        print(r)
    except ZeroDivisionError:
        print('correlation coefficient not defined ')   
    print()
    try:    
        meani=0
        for i in range(1,length+1):
            meani+=i
        meani=meani/length
           
        varsumilist=0
        for i in range(0,length):
            varsumilist+=(i+1-meani)*(list[i]-mean)
        
        m=round(varsumilist/varsumi,5)
        
        c=round(mean-m*meani,5)
        
        if c>0:
            print('line of best fit equation:')
            print('y=',m,"x+",c)
        elif c<0:
            print('line of best fit equation:')
            print('y=',m,"x-",c)
        elif c==0:
            print('line of best fit equation:')
            print('y=',m,'x')
        else:
            print('Something went wrong. Try again')
        print('y is the value in the list and x is its\
        position')
        while True:
            print()
            try:
                print('enter an unknown position in the list to \
     predict its value: ')
                x=input()
                x=float(x)
                print()
                print('the value for this position is:')
                print(m*x+c)
            except ValueError:
                break   
    except ZeroDivisionError:
        print('infinite lines of best fit')
        
    print('_-'*20)
    print()
#range funtion doesn't include the last value