import main

data = main.departed
waitingData = main.waitingInLane
waitingData.pop()


arrTimeData = [i.time for i in data]
arrTimeData.sort()
interArrivalTimes = [arrTimeData[0]]

timeWaiting = [ i.accel - i.time for i in data]
timeSpent = [ i.departTime - i.time for i in data]

for i in range(1, len(arrTimeData)): 
    interArrivalTimes.append(arrTimeData[i] - arrTimeData[i - 1])


mean = lambda x : sum(x)/len(x)


print(mean(interArrivalTimes))
print(mean(timeWaiting))
print(mean(timeSpent))
print(mean(waitingData))

