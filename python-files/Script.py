import pandas as pd

#load the CSV
df = pd.read_csv("input.csv")
#drop the unnessaray columns
df = df.drop(["CVR%","AOV","Days since campaign start","Sessions","Transactions"],axis='columns')

##remove all values which are 0 
df = df[(df!=0).all(1)]
##check prerequesities
df = df[df['Campaign'].str.count('_') >= 3]

#df = df[~df['Campaign'].str.contains('test',case=False,na=False)]

#df = df[~df['Campaign'].str.contains(r'\bAUT\b', case=False, na=False)]



#sort the values by date
#df = df.sort_values(by=['Campaign'], ascending=True)

df[['Date','Region','type','Name','test']] = df['Campaign'].str.split('_',n=4,expand=True)


#drop aggregated col
df.drop('Campaign', axis=1, inplace=True)

#move revenue col to end
col = 'GBP Revenue'
df = df[[c for c in df.columns if c != col] + [col]]


print(df.head)


#aggregation sum of revenue by name
df = df.groupby('Name',as_index=False)['GBP Revenue'].sum()


df['GBP Revenue'] = df['GBP Revenue'].astype(int)

df['GBP Revenue'] = df['GBP Revenue'].astype(int).apply(lambda x: f"{x:,}")
df['GBP Revenue'] = '£'+ df['GBP Revenue'].astype(str)

print(df.head)
#save to output file
df.to_csv('output.csv', encoding='utf-8-sig',index=False)