import random
import math
import json
import os

random.seed(12)

A = 30
anzahl_kunden = 100
anzahl_ladesaeulen = 50

def eukldist(p1,p2):
    distanz = round(
        math.sqrt( (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 ),
        2
    )

    return distanz

def instance_gen(I,L):

    Depot = [0,0]

    Kunden = []
    Ladestationen = []

    Batteriekapazität = 0

    #Kunden und Ladesäulenkoordianten zwischen -100 und 100
    for i in range(I):
        Kunden.append([
            random.randint(-100,100),
            random.randint(-100,100)
        ])

    for l in range(L):
        Ladestationen.append([
            random.randint(-100,100),
            random.randint(-100,100)
        ])

    #Distanzmatrizen berechen

    #Kundenmatrix
    Distanzmatrix_Kunden = []

    for k1 in Kunden:
        zeile = []
        
        for k2 in Kunden:
            distanz = eukldist(k1,k2)

            #Batteriecheck
            if distanz > Batteriekapazität:
                Batteriekapazität = distanz

            zeile.append(distanz)

        Distanzmatrix_Kunden.append(zeile)


    #Depotmatrix
    Distanzen_Depot = []

    for k in Kunden:
        distanz = eukldist(Depot,k)

        Distanzen_Depot.append(distanz)

    #KundenLadeMatrix
    Distanzmatrix_Kunden_Laden = []

    for k in Kunden:
        zeile = []

        for l in Ladestationen:
            distanz = eukldist(k,l)

            #Batteriecheck
            if distanz > Batteriekapazität:
                Batteriekapazität = distanz

            zeile.append(distanz)

        Distanzmatrix_Kunden_Laden.append(zeile)


    return Depot, Kunden, Ladestationen, Distanzmatrix_Kunden, Distanzen_Depot, Distanzmatrix_Kunden_Laden, Batteriekapazität

def instance_safe(a, Depot, Batterie, Kunden_Koord, Ladestationen_Koord, Kundenmatrix, Depotdistanzen, KundenLadenMatrix):
    
    pfad = os.path.join("Instances")
    os.makedirs(pfad, exist_ok=True)
    
    dateiname = "Instance_A{}.json".format(a)
    dateipfad = os.path.join(pfad, dateiname)

    datei_inhalt = {
        "Depot" : Depot,
        "Batterie" : Batterie,
        "Kunden_Koordinaten" : Kunden_Koord,
        "Ladestationen_Koordinaten" : Ladestationen_Koord,
        "Distanzmatrix_Kunden" : Kundenmatrix,
        "Distanz_Depot_Kunden" : Depotdistanzen,
        "Distanzmatrix_Kunden_Ladestation" : KundenLadenMatrix
    }

    jsonformat = json.dumps(datei_inhalt, indent= 1)

    with open(dateipfad, "w") as file:
        file.write(jsonformat)
    
    return

for a in range(A):

    Depot, Kunden_Koord, Ladestationen_Koord, Kundenmatrix, Depotdistanzen, KundenLadenMatrix, Batterie = instance_gen(anzahl_kunden,anzahl_ladesaeulen)

    #Tourspeichern
    instance_safe(a, Depot, Batterie, Kunden_Koord, Ladestationen_Koord, Kundenmatrix, Depotdistanzen, KundenLadenMatrix)