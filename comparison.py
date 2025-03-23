import openpyxl
import pandas as pd

df1 = pd.read_excel("C:\Users\Kavita\OneDrive\CIP\Webscraping\Tagesanzeiger\Done\Sunday.xlsx")
df2 = pd.read_excel("C:\Users\Kavita\OneDrive\CIP\Webscraping\Tagesanzeiger\Done\SundayPM.xlsx")

col1 = df1.iloc[:, 0].dropna().astype(str)
col2 = df2.iloc[:, 0].dropna().astype(str)


gemeinsam = set(col1).intersection(set(col2))

nur_in_datei1 = set(col1) - set(col2)

nur_in_datei2 = set(col2) - set(col1)

print(" Gemeinsam:")
print(gemeinsam)

print("\n Nur in Datei 1:")
print(nur_in_datei1)

print("\n Nur in Datei 2:")
print(nur_in_datei2)
