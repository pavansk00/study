import pandas as pd

lsat = [["pv" , 7], ["md", 9], ["vb", 14]] 
df = pd.DataFrame(lsat, columns=["name", "No."])
#print(df)


data = [['Geek1', 28, 'Analyst'],
        ['Geek2', 35, 'Manager'],
        ['Geek3', "29", 'Developer'],
        ['greek$', None, "qa"]]
column = ['Name', 'Age', 'Occupation']
df3 = pd.DataFrame(data, columns=column, index=['line1', 'linw2','line3', 'line4'])
df3['Age'] = pd.to_numeric(df3['Age'], errors="coerce")

#print(df3)
data1 = dict(zip(column, zip(*data)))
#print(data1)
df1 = pd.DataFrame.from_dict(dict(zip(column, zip(*data) )))
df1['Age'] = pd.to_numeric(df1['Age'], errors='coerce')

print(df1)
#print(df1)
df1 = df1.transpose()
print(df1)
df4= df3.pivot(index="Name", columns ="Occupation", values="Age")
print(df4)