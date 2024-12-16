import parameters

dScale = [0.49, 0.01]

params = {
    'PRINT_EVENTS' : False,
    'NUM_CARS' : 550,
    'ARR_PER_HOUR' : 550,
    'SERVICE_TIME' : 1/8,
    'NUM_RUNS' : 2,
    'lightInterval' : [0.6, 0.4],
    'directionWeights' : [dScale[0], dScale[1], dScale[0], dScale[1]],
}

parameters.params = params


import main
import adaptive

foo = False

for i in [main, adaptive]:


    data = i.departed
    waitingData = i.waitingInLane
    waitingData.pop()


    arrTimeData = [i.time for i in data]
    arrTimeData.sort()
    interArrivalTimes = [arrTimeData[0]]

    timeWaiting = [ i.accel - i.time for i in data]
    timeSpent = [ i.departTime - i.time for i in data]

    for i in range(1, len(arrTimeData)): 
        interArrivalTimes.append(arrTimeData[i] - arrTimeData[i - 1])


    mean = lambda x : sum(x)/len(x)

    if not foo: print('-MAIN-')
    else: print('-ADAPTIVE-')
    print('Number of cars', len(data))
    print('Mean inter arrival times',mean(interArrivalTimes))
    print('Mean time waiting in lane', mean(timeWaiting))
    print('Mean time spent in intersection', mean(timeSpent))
    print('Mean cars waiting in lanes',mean(waitingData))
    print('Max cars waiting in lanes',max(waitingData))
    print()

    foo = True

