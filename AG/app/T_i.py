from random import randint
from random import seed
def roundRobin(totalResources,totalInputs):
    print("SE COORDINA CON ROUND ROBIN")
    coordinator = {}
    for i in range(totalInputs):
        coordinator[i] = i%totalResources
    return coordinator


def pseudorandom(totalResources,totalInputs):
    print("SE COORDINA CON PSEUDORANDOM")
    seed()
    coordinator = {}
    for i in range(totalInputs):
        coordinator[i] = value = randint(0, totalResources-1)
    return coordinator


def twoChoice(totalResources,work):
    print("SE COORDINA CON TWO CHOICE")
    record = [0] * totalResources
    coordinator = {}
    totalInputs = len(work)
    for i in range(totalInputs):
        workToDo = len(work[i])
        
        random1 = randint(0, totalResources-1)
        random2 = randint(0, totalResources-1)
        
        if(record[random1] <= record[random2]):
            coordinator[i] = random1
            record[random1] += workToDo
        else:
            coordinator[i] = random2
            record[random2] += workToDo
    print(record)
    return coordinator

