import json
import time
import math
import os #zum ablegen der lösungsdatei in ordnern
from decimal import Decimal #nutzung von decimal, da genaugkeitsfehler bei float-variablen und speicherlänge aufgetreten sind

A = 30
T = 100
K = 6
k = K-1

def Tourbewertung_inkl_laden(a, k, t, max_b, Distanzen_K_L):

    #Tourordner und Dateinamen abrufen
    tour_pfad = os.path.join("Tours")

    tour_filename = "Tour_Data_A{}_T{}_K{}.json".format(a,t,k)
    tour_dateipfad = os.path.join(tour_pfad, tour_filename)

    #Tourdaten laden
    with open(tour_dateipfad) as jsontour:
        tour_data = json.load(jsontour)

    Tour_Distanzen = tour_data["Tour_Distanzen"]
    Tour_Kundenindex = tour_data["Tour_Kundennummern"]

    #tourdaten initialisieren für dekom2
    tour_dauer = Decimal("0.00")
    SoC = Decimal(str(max_b))

    i = 0
    while i < len(Tour_Kundenindex):
        
        aktueller_Kundenindex = Tour_Kundenindex[i]
        
        
        if i == len(Tour_Kundenindex) -1: #Kundenreihenfolge der Tour, um auf Distanzmatrixzeilen zuzugreifen
            distanz = Decimal(str(Tour_Distanzen[i]))
            tour_dauer += distanz
        else:
            nächster_Kundenindex = Tour_Kundenindex[i+1] #zugriff auf nächsten kunden
            distanz = Decimal(str(Tour_Distanzen[i]))
            beste_nächste_Ladestation = Decimal(str(min(Distanzen_K_L[nächster_Kundenindex]))) #Ladestation nach aktuellem Kunden


        if SoC > distanz + beste_nächste_Ladestation: #Reicht SoC für nächsten Kunden und die beste Ladestation danach    
            tour_dauer += Decimal(str(Tour_Distanzen[i]))
            SoC -= Decimal(str(Tour_Distanzen[i]))
            i += 1

        else: #wenn nicht dann laden
            ladeweg_hinweg = Decimal(str(min(Distanzen_K_L[aktueller_Kundenindex]))) #Laden an der von DIESEM Kunden beste Ladestation!
            index = Distanzen_K_L[aktueller_Kundenindex].index(float(ladeweg_hinweg))
            
            ladezeit = Decimal("15") #const

            #Distanz Ladestation zu nächstem Kunde
            lade_rückweg = Decimal(str(Distanzen_K_L[nächster_Kundenindex][index]))

            tour_dauer += ladeweg_hinweg + ladezeit + lade_rückweg
            SoC =  Decimal(str(max_b))
            i += 2 #Weg zum nächsten Kunden von Ladestation getätigt

    return tour_dauer 

#Erstellen einer Lösungsdatei / csv
lösung_pfad = os.path.join("Results")
os.makedirs(lösung_pfad, exist_ok=True)

lösung_dateiname = "results.csv"
lösung_dateipfad = os.path.join(lösung_pfad, lösung_dateiname)

if not os.path.exists(lösung_dateipfad):

    with open(lösung_dateipfad, "w") as file:
        file.write("A;T;K;dauer;solvetime\n")

#Erstellen einer Lösungsdatei für beste Touren
beste_tour_dateiname = "best_results.csv"
beste_tour_dateipfad = os.path.join(lösung_pfad, beste_tour_dateiname) #Pfad bleibt der selbe

if not os.path.exists(beste_tour_dateipfad):

    with open(beste_tour_dateipfad, "w") as file:
        file.write("A;K;best_tour;shortest_duration;solvetime\n")

#Tourbewertung und Ergebnisspeicherung pro Instanz
for a in range(A):
    
    #Instanz laden für Kunden-Ladestation-Matrix
    instanz_pfad = os.path.join("Instances")
    instanz_dateiname = "Instance_A{}.json".format(a)
    
    instanz_dateipfad = os.path.join(instanz_pfad, instanz_dateiname)

    with open(instanz_dateipfad) as jsoninstanz:
        instanz_data = json.load(jsoninstanz)

    max_b = instanz_data["Batterie"] #maximale Batteriekapazität der Instanz
    Distanzmatrix_Kunden_Ladestation = instanz_data["Distanzmatrix_Kunden_Ladestation"] #100x50

    #Initialisierung von "t*" und "d*"
    beste_tour = None
    geringste_Dauer = math.inf

    #Alle Touren T in Instanz a aus A inklusive Ladekapazität bewerten
    for t in range(T):

        #Lösungsdauer startzeit
        starttime = time.perf_counter_ns()

        #Bewertung der tour tl aus der Menge aller Touren in Instanz a aus A
        d = Tourbewertung_inkl_laden(a, K, t, max_b, Distanzmatrix_Kunden_Ladestation)

        #Solvetime
        solvetime = time.perf_counter_ns() - starttime

        #Tourergebnis formatieren
        result = [a,t,K,float(d),round(solvetime,8)]

        stringresult = [str(value).replace(".",",") for value in result]
        sep = ";"
        result_zeile = sep.join(stringresult)

        #Tourergebnis schreiben
        with open(lösung_dateipfad, "a") as file:
            file.write(result_zeile + "\n")

        #Check für geringste Dauer und beste Tour ID
        if d < geringste_Dauer:
            beste_tour = t
            geringste_Dauer = d

    #Ergebnisse der besten Tour mit geringster Distanz pro Instanz formatieren und schreiben
    beste_tour_dauer = [a,K,beste_tour,float(geringste_Dauer),round(solvetime,8)]
    stringbeste_tour_dauer = [str(value).replace(".",",") for value in beste_tour_dauer]

    beste_tour_dauer_zeile = sep.join(stringbeste_tour_dauer)

    with open(beste_tour_dateipfad, "a") as file:
        file.write(beste_tour_dauer_zeile + "\n")