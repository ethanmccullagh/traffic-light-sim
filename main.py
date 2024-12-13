import numpy
from threading import Thread, Lock
import random
from Sim import Car, Lane, Event, EventList
import time

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

STRAIGHT = 0
RIGHT = 1
LEFT = 2

STRAIGHT_RIGHT = 3
STRAIGHT_LEFT = 4

SERVICE_TIME = 0.5

random.seed(10)

clock = 0
GreenLight = 0
departed = []

southToNorth = Lane(NORTH, STRAIGHT)
westToEast = Lane(EAST, STRAIGHT)
northToSouth = Lane(SOUTH, STRAIGHT)
eastToWest = Lane(WEST, STRAIGHT)
lanes = [southToNorth, westToEast, northToSouth, eastToWest]


cars = []
for i in range(1, 16):
    cars.append(Car(random.randrange(0, 4), STRAIGHT, random.randrange(1, 11), SERVICE_TIME))
numCars = len(cars)
cars.sort(key=lambda a : a.time)

for i in range(0, len(cars)):
    cars[i].setID(i+1)

lightInterval = 4
nextLightChange = lightInterval

eventList = EventList()

def scheduleArrival(car):
    global eventList

    lanes[car.direction].addCar(car)

    event = Event(0, car.time, car)
    eventList.add(event)

def scheduleDeparture(lane):
    global eventList
    car = lane.peek()

    curTime = car.time
    if clock > car.time: curTime = clock

    if curTime + car.service > nextLightChange: return

    lane.pop()

    car.departTime(curTime + car.service)

    event = Event(1, curTime + car.service, car)
    eventList.add(event)

def processEvent(event):
    if event._type == 0:
        print(f'ARRIVAL   {event.time} {event.car}')

    else:
        print(f'DEPARTURE {event.time} {event.car}')
        departed.append(event.car)


#main loop that runs each light cycle
while len(departed) < numCars:

   
    #get the cars that will arrive before next light change, add them to the lane and create event
    while len(cars) > 0 and cars[0].time < nextLightChange:
        scheduleArrival(cars.pop(0))

    #schedule departures for active lanes
    for lane in [lanes[GreenLight], lanes[GreenLight + 2]]:
        while lane.waiting > 0:
            scheduleDeparture(lane)

    #print events for this light cycle
    while eventList.peek():
        processEvent(eventList.pop())


    clock = nextLightChange
    nextLightChange += lightInterval
    GreenLight = (GreenLight + 1) % 2

    if(len(departed) == numCars):
        print('----END----')
        break
    print('----LIGHT CHANGE----')
    
#print(departed)
    