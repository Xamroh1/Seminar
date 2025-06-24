import json
import time
import random
import os

random.seed(1337)
A = 30
T = 100
K = 6
k = K-1

def tour_berechnen(k_koord, d_koord, d_distanzen, k_distanzen, k):

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

for a in range(A):

    instanz_pfad = os.path.join("Instances")
    instanz_dateiname = "Instance_A{}.json".format(a)
    
    instanz_dateipfad = os.path.join(instanz_pfad, instanz_dateiname)

    #Instanz öffnen
    with open(instanz_dateipfad) as jsoninput:

        instanz = json.load(jsoninput)

        Depot_Koordinaten = instanz["Depot"]
        Kunden_Koordinaten = instanz["Kunden_Koordinaten"]
        Distanzmatrix_Kunden = instanz["Distanzmatrix_Kunden"]
        Distanz_Depot_Kunden = instanz["Distanz_Depot_Kunden"]

    for t in range(T):

        #Tour Berechnung
        tour, tour_distanzen, tour_kundennr = tour_berechnen(Kunden_Koordinaten, Depot_Koordinaten, Distanz_Depot_Kunden, Distanzmatrix_Kunden, k)

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