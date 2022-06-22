# - tsgpandas.py -
# Juni 2022, <Hubert.Hoegl@t-online.de>

'''
Folgendes muss installiert sein:

pip install pandas
pip install altair
pip install selenium
pip install altair_saver
sudo apt install chromium-chromedriver

Pandas
  Getting Started: https://pandas.pydata.org/docs/getting_started/index.html
  User Guide: https://pandas.pydata.org/docs/user_guide/
  API Referenz: https://pandas.pydata.org/docs/reference/

Altair
  https://altair-viz.github.io
'''

import pandas as pd
from datetime import datetime, timedelta, date
import numpy as np
from IPython.display import display
import altair as alt
import altair_saver

alt.renderers.enable('altair_saver', fmts=['vega-lite', 'png'])

YEAR = timedelta(365)  # Tage im Jahr
ENDDATE = datetime(2022, 12, 31)

DAT = "../Mitglieder/22-05-18 Mitglieder gesamt - extern.csv"

df = pd.read_csv(DAT)

def to_dt(s):
    # s is a date string with format "17.09.2022"  # evtl auch "%m/%d/%Y"
    return datetime.strptime(s, "%d.%m.%Y")

# An die Mitgliederliste werden zwei Spalten angehaengt, die erste ist 'DTObj',
# in dieser ist das Geburtsdatum als DateTime Objekt enthalten. In der zweiten
# angehaengten Spalte ist entweder ein "M" (Mitglied) oder ein "S"
# (Schnupperkind).

L = []
for i in df.index:
    # print(df.iloc[i].Nachname, df.iloc[i].Vorname, to_dt(df.iloc[i].Geburtsdatum))
    L.append(to_dt(df.iloc[i].Geburtsdatum))
ser = pd.Series(L)

M = []
for i in df.index:
    M.append("M")
status = pd.Series(M)

df2 = pd.concat([ser, status], axis=1)
df2.columns = ['DTObj', 'Status']

# Zwei Spalten 'DTObj' und 'Status' werden angehaengt
df3 = df.join(df2)

# Einlesen der Schnupperkinder-und-sonstige Tabelle. Die Spalte "M/S" gibt an,
# ob das Kind Schnupperkind (S), Mitglied (M) oder aktuell nichts macht (R).
# https://docs.google.com/spreadsheets/d/1SesKRufr5PS6zLYLo8IGShFTGV700ttDq8be45Pa6-A/edit#gid=602162883
DAT = "Schnupperkinder-und-sonst-22.6.2022.csv"
df5 = pd.read_csv(DAT)
# display(df5.to_string())


# An die Mitgliederliste df3 werden nun die Kinder aus der Liste df5
# angehaengt, die noch nicht Mitglieder sind. Es wird zunaechst geprueft, ob
# Vor- und Nachname in der Mitgliederliste vorhanden ist. Falls nicht, wird
# das Kind angehaengt. Falls die Spalte "M/S" ein "R" enthaelt, wird das Kind
# nicht an die Liste angehaengt.

k = 0
for i in df5.index:
    v, n = df5.iloc[i].Vorname, df5.iloc[i].Nachname
    if [v, n] != [np.nan, np.nan]:  # Leere Zeilen herausfischen
        d = df3.loc[(df3.Vorname == v) & (df3.Nachname == n)]
        m = df5["M/S"].iloc[i]
        # m kann sein: M -> Mitglied, S -> Schnupperkind, B -> Ballspielgruppe
        # (B ist auch Schnupperkind), R -> ruht (macht kein Training)
        if d.empty:
            # Kind in df3 aufnehmen, falls M/S nicht R
            if m != 'R':
                g = datetime.strptime(df5["Geburtsdatum"].iloc[i], "%d.%m.%Y")
                row = { 'Status': 'S', 'Vorname': v, 'Nachname': n, 'DTObj': g}
                df3 = pd.concat([df3, pd.DataFrame(row, index=[0])]).reset_index(drop=True)

                # .append() ist wesentlich simpler, jedoch deprecated
                # df3 = df3.append(row, ignore_index=True)

                k = k + 1
                # print("Schnupperkind aufnehmen:", k, i, v, n, m, g)
            else:
                # print("ignoriere", i, v, n, m)
                pass
        else:
            # print("Bereits Mitglied", i, v, n, m)
            pass

# print(df3)

print("{} Schnupperkinder in Liste aufgenommen".format(k))

# Jetzt alle Kinder unter 18 Jahren herausfischen und nach Alter sortieren
# Das ergibt dann die Liste df4
df4 = df3.loc[df3.DTObj >= to_dt("1.1.2004")]
# print(df4) # unsortiert
df4 = df4.sort_values(by="DTObj") # aufsteigend sortiert
df4 = df4.reset_index(drop=True)

# Nun eine neue Tabelle df5 aus der Tabelle df4 machen, in der Status (S, M),
# Vorname, Nachname, Geburtsdatum (Date Object) und das Alter als Kommazahl
# enthalten ist.
df5 = pd.DataFrame()

n = 0
for i in df4.index:
    d = df4.iloc[i].DTObj
    td = ENDDATE - d
    q = td/YEAR
    n += 1
    # Alter ist eine Kommazahl, die das Alter am Tag ENDDATE angibt.
    row = {'Status': df4.iloc[i].Status, 'Vorname': df4.iloc[i].Vorname,
            'Nachname': df4.iloc[i].Nachname, 'Geburtsdatum': d.date(),
            'Alter': q}
    df5 = pd.concat([df5, pd.DataFrame(row, index=[0])])

df5 = df5.reset_index(drop=True)

print("Das angegebene Alter wird am Tag {} erreicht.".format(ENDDATE.date()))

# XXX to do: die Spalte 'Alter' mit nur zwei Nachkommastellen ausgeben, {:4.2f}
display(df5.to_string())


df7 = pd.DataFrame()

for i in range(4, 18):
    a = float(i)
    df6 = df5.loc[(a <= df5.Alter) & (df5.Alter < a+1)]
    n = len(df6)
    m = len(df6[df6.Status == 'M'])
    # print("Alter {} - {}: {} M={} S={}".format(a, a+1, n, m, n-m))
    # row = {'Alter': a, 'Anz': n, 'AnzMitgl': m, 'AnzSchnupp': n-m }
    row = {'Alter': a, 'Anzahl': m, 'Kategorie': 'Mitglied'}
    # print(df6)
    df7 = pd.concat([df7, pd.DataFrame(row, index=[0])])
    row = {'Alter': a, 'Anzahl': n-m, 'Kategorie': 'Schnupperkind'}
    df7 = pd.concat([df7, pd.DataFrame(row, index=[0])])


chart = alt.Chart(df7, title="TSG Tennis-Jugend 2022 (4-17 Jahre)").mark_bar().encode(
    x=alt.X("Alter", title="Alter"),
    y=alt.Y("sum(Anzahl)", title="Anzahl"),
    color='Kategorie').properties(width=800, height=500, padding=20)

print("Bild out.svg wird ausgegeben.")
altair_saver.save(chart, "out.svg")

# XXX to do: Gruppieren in die einzelnen Mannschaften fuer 2023
# U18, ab 1.1.2005 und spaeter
# U15, ab 1.1.2008 und spaeter
# U12, ab 1.1.2011 und spaeter
# U10, ab 1.1.2013 und spaeter
# U9, ab 1.1.2014 und spaeter

