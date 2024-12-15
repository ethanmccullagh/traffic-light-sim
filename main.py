import numpy
from threading import Thread, Lock
import random
from Sim import Car, Lane, Event, EventList, Traversal
import time

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

STRAIGHT = 0
RIGHT = 1
LEFT = 2

STRAIGHT_RIGHT = lambda x : x==0 or x==1
STRAIGHT_LEFT = lambda x : x==0 or x==2
STRAIGHT_RIGHT_LEFT = lambda x : x >= 0 and x <= 2

SERVICE_TIME = 0.5

random.seed(11)

clock = 0
GreenLight = 0
departed = []

southToNorth = Lane(NORTH, STRAIGHT_RIGHT)
westToEast = Lane(EAST, STRAIGHT_RIGHT)
northToSouth = Lane(SOUTH, STRAIGHT_RIGHT)
eastToWest = Lane(WEST, STRAIGHT_RIGHT)
northLeft = Lane(NORTH, STRAIGHT_LEFT)
eastLeft = Lane(EAST, STRAIGHT_LEFT)
southLeft = Lane(SOUTH, STRAIGHT_LEFT)
westLeft = Lane(WEST, STRAIGHT_LEFT)
lanes = [southToNorth, westToEast, northToSouth, eastToWest, northLeft, eastLeft, southLeft, westLeft]


cars = []
for i in range(1, 21):
    cars.append(Car(random.randrange(0, 4), random.randrange(0, 3), random.randrange(1, 12), SERVICE_TIME))
numCars = len(cars)
cars.sort(key=lambda a : a.time)

for i in range(0, len(cars)):
    cars[i].setID(i+1)


lightInterval = 4
nextLightChange = lightInterval

eventList = EventList()

def scheduleArrival(car):
    global eventList

    if car.turn == LEFT:
        lanes[car.direction + 4].addCar(car)
    else:
        lanes[car.direction].addCar(car)

    event = Event(0, car.time, car)
    eventList.add(event)

def scheduleDeparture(lane, drag):
    global eventList
    car = lane.peek()
    curTime = car.time

    if clock > car.time: curTime = clock

    curTime += drag

    if curTime + car.service > nextLightChange: return None

    if lane.turnsAllowed(car.turn):
        if car.turn == LEFT:
            if car.accel< curTime: car.accel = curTime
            turnTime = turnAllowed(car)

            if not turnTime:
                print('turn not allowed', car)
                return None

            if turnTime < curTime: turnTime = curTime
            else: turnTime += drag

            car.departTime(turnTime + car.service)

        lane.pop()

        if car.turn == STRAIGHT: lane.addTraversal(Traversal(curTime, car.service))

        if not car.dep: car.departTime(curTime + car.service)

        event = Event(1, car.departTime, car)
        eventList.add(event)
    else :
        print('Error wrong turn assignment')
        exit()

    return 1

def scheduleRightTurnOnRed(lane):
    global eventList
    car = lane.peek()

    turnTime = turnAllowed(car)

    if not turnTime: return False

    car.departTime(turnTime + car.service)

    scheduleDeparture(lane, 0)

    return True


def processEvent(event):
    if event._type == 0:
        print(f'ARRIVAL   ({event.time}) {event.car}')

    else:
        print(f'DEPARTURE ({event.time}) {event.car}')
        departed.append(event.car)

def turnAllowed(car):
    global lanes

    if car.turn == RIGHT:
        destLane = lanes[(car.direction + 1) % 4]
        if destLane.isBusy(car.accel, car.service):   
            return destLane.nextWindow(car.accel, car.service, nextLightChange)
        
    if car.turn == LEFT:
        destLane = lanes[(car.direction + 2) % 4]
        if destLane.isBusy(car.accel, car.service):   
            return destLane.nextWindow(car.accel, car.service, nextLightChange)
    
    return car.accel 

    



#main loop that runs each light cycle
while len(departed) < numCars:

    if GreenLight == 0: print('----NORTH/SOUTH----')
    else : print('----EAST/WEST----')

    activeL1 = lanes[GreenLight]
    activeL1L = lanes[GreenLight + 4]
    activeL2 = lanes[GreenLight + 2]
    activeL2L = lanes[GreenLight + 6]
    inactiveL1 = lanes[GreenLight + 1]
    inactiveL2 = lanes[(GreenLight + 3) % 4]

   
    #get the cars that will arrive before next light change, add them to the lane and create event
    while len(cars) > 0 and cars[0].time < nextLightChange:
        scheduleArrival(cars.pop(0))
    

    #schedule departures for active lanes
    for lane in [activeL1, activeL2, activeL1L, activeL2L]:
        drag = 0
        while lane.waiting > 0:
            
            if not scheduleDeparture(lane, drag) : 
                print('break')
                break

          

    #schedule right turns for inactive lanes
    for lane in [inactiveL1, inactiveL2]:
        while lane.waiting > 0 and lane.peek().turn == RIGHT:
            if not scheduleRightTurnOnRed(lane) : break

    #print events for this light cycle
    while eventList.peek():
        processEvent(eventList.pop())

    activeL1.traversals =[]
    activeL2.traversals =[]


    clock = nextLightChange
    nextLightChange += lightInterval
    GreenLight = (GreenLight + 1) % 2

    if(len(departed) == numCars):
        print('----END----')
        break
    
    
#for i in departed: print(i)
    