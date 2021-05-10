## Brendan Sigale - Quiz 1 - 2021/02/09

climate = 'Tropical'
temps = [-0.96, -14.38, 11.66, 40.07, 48.72, 0.55, 4.73, 24.82, 32.55, 31.98, -3.08, 36.41, 39.16]

tropical = 30
continental = 25
otherwise = 18

def folding(climate, temps):
    if climate == 'Tropical':
        for i in range(len(temps)):
            if temps[i] <= tropical:
                print("F")
            else:
                print("U")
    if climate == 'Continental':
        for i in range(len(temps)):
            if temps[i] <= continental:
                print("F")
            else:
                print("U")
    if climate != 'Tropical' and climate != 'Continental':
        for i in range(len(temps)):
            if temps[i] <= otherwise:
                print("F")
            else:
                print("U")
                


folding(climate, temps)