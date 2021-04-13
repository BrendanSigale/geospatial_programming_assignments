## Brendan Sigale
## Geospatial Programming
## Quiz 2
## Question 3

testList = [2, 8, 64, 16, 32, 4, 16, 8]

i=0
for i in range(len(testList)):
    if testList.count(testList[i]) > 1:
        print("The list contains duplicate values.")
        s = list(set(testList))
        print("The following list is sorted and contains no duplicates")
        print(sorted(s))
        break
    if i == len(testList)-1 and testList.count(testList[-1]) == 1:
        print("The list contains no duplicate values")
        break
    else:
        i+=1