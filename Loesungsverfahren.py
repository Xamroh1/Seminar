import random
import json
import math
import time
from decimal import Decimal
import os

random.seed(12)

A = 30
T = 100
K = [2,4,6]

def Tour_Konstruieren(k_koord, d_koord, d_distanzen, k_distanzen, k):

    #Tourdaten tl
    tour = []
    tour_distanzen = []
    tour_kundennr = []

    #Offene Kunden numerieren nach Index der Koordinaten und gleichzeitig Index der Distanzmatrix-Spalte
    Offene_Kunden = set(range(len(k_koord)))

    while any(Offene_Kunden): #solange noch kunden in O
            
        if len(tour_distanzen) == 0: #Berechnung von Depot aus
            stop = erster_stopp(Offene_Kunden, d_distanzen, k)
            
            #Daten zu tl hinzufügen
            tour.append(k_koord[stop[0]])
            tour_distanzen.append(round(stop[1],2))
            tour_kundennr.append(stop[0])

            #Stop aus O löschen
            Offene_Kunden.remove(stop[0])
        
        else: #Berechnung aller nachfolgenden Stops
            stop = weitere_stopps(Offene_Kunden, k_distanzen, stop, k)
            
            #Daten zu tl hinzufügen
            tour.append(k_koord[stop[0]])
            tour_distanzen.append(round(stop[1],2))
            tour_kundennr.append(stop[0])

            #Stop aus O löschen
            Offene_Kunden.remove(stop[0])

    #Rückfahrt zum Depot
    tour.append(d_koord)
    tour_distanzen.append(d_distanzen[stop[0]])

    return tour, tour_distanzen, tour_kundennr

def erster_stopp(O, depot_distanzen, k):

    #füllen mit O und zugehöriger Distanz
    aktuelle_Kandidaten = []

    #Enumeration aller Kunden
    for Kundennummer in O: 
        distanz = depot_distanzen[Kundennummer] #Distanz zu Index von 0 in Depotdistanzen
        aktuelle_Kandidaten.append((Kundennummer, distanz))

    aktuelle_Kandidaten_sortiert = sorted(aktuelle_Kandidaten, key= lambda x: x[1]) #sortieren der Kunden nach distanz zum Depot
    stop = aktuelle_Kandidaten_sortiert[random.randint(0,k)] #auswählen eines der k-besten Kunden

    return stop

def weitere_stopps(O, kunden_distanzen, vorheriger_stop, k):

    matrix_zeile = kunden_distanzen[vorheriger_stop[0]] #Zeile der Distanzmatrix des vorherigen Kunden zu allen anderen und sich

    aktuelle_Kandidaten = []

    if k > len(aktuelle_Kandidaten): #kann kann größer als sein als die Anzahl der noch offenen Kunden -> Error Überlauf
        k = len(aktuelle_Kandidaten)

    #Enumeration aller Kunden
    for Kundennummer in O:
        if vorheriger_stop[0] != Kundennummer: #Ausschluss des bereits angefahrenen Kunden (selbst) aus den Kandidaten
            distanz = matrix_zeile[Kundennummer] #Spaltenwert aus Distantmatrix zur Zeile des vorherigen Kunden
            aktuelle_Kandidaten.append((Kundennummer, distanz))

    aktuelle_Kandidaten_sortiert = sorted(aktuelle_Kandidaten, key= lambda x: x[1]) #sortieren der Kunden nach distanz zum vorherigen Kunden
    stop = aktuelle_Kandidaten_sortiert[random.randint(0,k)] #auswählen eines der k-besten Kunden

    return stop

def Tour_safe(a, t, K, tour, tour_distanzen, tour_kundennr):

    #Speichern von tourdaten
    tour_pfad = os.path.join("Tours")
    os.makedirs(tour_pfad, exist_ok=True)
    
    tour_filename = "Tour_Data_A{}_T{}_K{}".format(a,t,K)
    tour_dateipfad = os.path.join(tour_pfad, tour_filename)

    file_content = {
        "Tour_Koordinaten" : tour,
        "Tour_Distanzen" : tour_distanzen,
        "Tour_Kundennummern" : tour_kundennr
    }

    jsonformat = json.dumps(file_content, indent= 1)
    
    with open(tour_dateipfad + ".json", "w") as f:
        f.write(jsonformat)

    return

def Tourbewertung_inkl_laden(max_b, Distanzen_K_L, Tour_Distanzen, Tour_Kundenindex):

    #tourdaten initialisieren für dekom2
    tour_dauer = Decimal("0.00")
    SoC = Decimal(str(max_b))

    i = 0
    while i < len(Tour_Kundenindex):
        
        aktueller_Kundenindex = Tour_Kundenindex[i] #Zugriff auf matrizen durch Index
        
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

def Tourbewertung_safe(a, t, K, d, solvetime):

    #Tourbewertung formatieren
    result = [a,t,K,float(d),round(solvetime,8)]

    stringresult = [str(value).replace(".",",") for value in result]
    sep = ";"
    result_zeile = sep.join(stringresult)

    #Tourergebnis schreiben
    with open(lösung_dateipfad, "a") as file: #append an gesamtresults
        file.write(result_zeile + "\n")

    return

def BestTour_safe(a,k,index, duration, time):
    
    best = [a,k,index,float(duration),round(time,8)]
    
    stringbest = [str(value).replace(".",",") for value in best]
    sep = ";"
    beste_tour_dauer_zeile = sep.join(stringbest)

    with open(beste_tour_dateipfad, "a") as file:
        file.write(beste_tour_dauer_zeile + "\n")

    return

#Erstellen einer Lösungsdatei / csv
lösung_pfad = os.path.join("Results")
os.makedirs(lösung_pfad, exist_ok=True) #Ordner erstellen

lösung_dateiname = "results.csv"
lösung_dateipfad = os.path.join(lösung_pfad, lösung_dateiname) #Nutzung von Path join aufgrund von Problemen mit strings

if not os.path.exists(lösung_dateipfad):

    with open(lösung_dateipfad, "w") as file:
        file.write("A;T;K;dauer;solvetime\n")

#Erstellen einer Lösungsdatei für beste Touren
beste_tour_dateiname = "best_results.csv"
beste_tour_dateipfad = os.path.join(lösung_pfad, beste_tour_dateiname) #Pfad bleibt der selbe

if not os.path.exists(beste_tour_dateipfad):

    with open(beste_tour_dateipfad, "w") as file:
        file.write("A;K;best_tour;shortest_duration;solvetime\n")

for a in range(A):
    
    #Initialisierung von t* und d*
    beste_tour = None
    geringste_Dauer = math.inf
    geringste_Solvetime = math.inf

    #Laden von Instanzdaten
    instanz_pfad = os.path.join("Instances")
    instanz_dateiname = "Instance_A{}.json".format(a)
    
    instanz_dateipfad = os.path.join(instanz_pfad, instanz_dateiname)

    #Instanz öffnen
    with open(instanz_dateipfad) as jsoninput:

        instanz = json.load(jsoninput)

        Batterie = instanz["Batterie"]
        Depot_Koordinaten = instanz["Depot"]
        Kunden_Koordinaten = instanz["Kunden_Koordinaten"]
        Distanzmatrix_Kunden = instanz["Distanzmatrix_Kunden"]
        Distanz_Depot_Kunden = instanz["Distanz_Depot_Kunden"]
        KundenLadenMatrix = instanz["Distanzmatrix_Kunden_Ladestation"]

    for k in K:

        k_rand = k-1

        for t in range(T):

            #Solvetime-Startzeit für Konstruktion # bewertung 
            starttime = time.perf_counter_ns()

            #Tour Berechnung
            tour, tour_distanzen, tour_kundennr = Tour_Konstruieren(Kunden_Koordinaten, Depot_Koordinaten, Distanz_Depot_Kunden, Distanzmatrix_Kunden, k_rand)

            #Tourbewertung inkluse Laden
            d = Tourbewertung_inkl_laden(Batterie, KundenLadenMatrix, tour_distanzen, tour_kundennr)

            #Solvetime end
            solvetime = time.perf_counter_ns() - starttime

            #Check für geringste Dauer und beste Tour ID
            if d < geringste_Dauer:
                beste_tour = t
                geringste_Dauer = d
                geringste_Solvetime = solvetime

            #Tour speichern
            Tour_safe(a, t, k, tour, tour_distanzen, tour_kundennr)

            #Tourbewertung speichern
            Tourbewertung_safe(a, t, k, d, solvetime)

        #Ergebnisse der besten Tour mit geringster Distanz pro Instanz speichern
        BestTour_safe(a,k,beste_tour,geringste_Dauer,geringste_Solvetime)
