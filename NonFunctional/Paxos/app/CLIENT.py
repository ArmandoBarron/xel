from Proposer import Paxos

def twoChoice(totalResources,workload):
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

workload = []

acc = [{"host":"localhost:6501"},{"host":"localhost:6502"},{"host":"localhost:6503"}]
resources = []
total_resources = len(resources)

#paxos
proposer = Paxos(acc)
proposer.process()
###################




