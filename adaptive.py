import numpy
import random
from Sim import Car, Lane, Event, EventList, Traversal
import math

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

SERVICE_TIME = 1/8

PRINT_EVENTS = False

NUM_CARS = 550
ARR_PER_HOUR = 550

random.seed(11)

clock = 0
departed = []
waitingInLane = []

GreenLight = 0
lightInterval = [0.6, 0.4]
nextLightChange = lightInterval[GreenLight]

southToNorth = Lane(NORTH, STRAIGHT_RIGHT)
westToEast = Lane(EAST, STRAIGHT_RIGHT)
northToSouth = Lane(SOUTH, STRAIGHT_RIGHT)
eastToWest = Lane(WEST, STRAIGHT_RIGHT)
northLeft = Lane(NORTH, STRAIGHT_LEFT)
eastLeft = Lane(EAST, STRAIGHT_LEFT)
southLeft = Lane(SOUTH, STRAIGHT_LEFT)
westLeft = Lane(WEST, STRAIGHT_LEFT)
lanes = [southToNorth, westToEast, northToSouth, eastToWest, northLeft, eastLeft, southLeft, westLeft]

## Generate cars
def exponential(mean):
    return -mean*math.log(random.random())

meanInterArrivalTimeSeconds = 60/ARR_PER_HOUR

directionPopulation = [NORTH, EAST, SOUTH, WEST]
directionWeights = [0.3, 0.2, 0.3, 0.2]

turnPopulation = [STRAIGHT, RIGHT, LEFT]
turnWeights = {
    NORTH : [0.66, 0.33, 0.01],
    EAST : [0.71, 0.16, 0.13],
    SOUTH : [0.87, 0.12, 0.01],
    WEST : [0.57, 0.08, 0.35]
}

directionChoices = random.choices(directionPopulation, directionWeights, k=NUM_CARS)

def turnChoice(dir):
    turn = random.choices(turnPopulation, turnWeights[dir], k=1)
    return turn[0]


cars = []
lastArrival = 0
for i in range(NUM_CARS):
    nextArrival = lastArrival + exponential(meanInterArrivalTimeSeconds)

    cars.append(Car(directionChoices[i], turnChoice(directionChoices[i]), nextArrival, SERVICE_TIME, i+1))

    lastArrival = nextArrival

NUM_CARS = len(cars)
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
                #print('turn not allowed', car)
                return None

            if turnTime < curTime: turnTime = curTime
            else: turnTime += drag

            car.setDepartTime(turnTime + car.service)

        lane.pop()

        if car.turn == STRAIGHT: lane.addTraversal(Traversal(curTime, car.service))

        if not car.dep: car.setDepartTime(curTime + car.service)

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

    if turnTime < clock: turnTime = clock

    if turnTime + car.service >= nextLightChange or car.setDepartTime(turnTime + car.service) == None: return False

    scheduleDeparture(lane, 0)

    return True


def processEvent(event, announce):
    if event._type == 0 and announce:
        print(f'ARRIVAL   ({event.time}) {event.car}')
    elif event._type == 1:
        if announce : print(f'DEPARTURE ({event.time}) {event.car}')
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

    
def printLightStatus():
    if GreenLight == 0: print('----NORTH/SOUTH----', clock)
    else : print('----EAST/WEST----', clock)

    print('WAITING')
    print(' N  E  S  W  N  E  S  W ')
    print([item.waiting for item in lanes])

def countWaiting():
    waitingInLane.append(0)
    for lane in lanes:
        waitingInLane[len(waitingInLane)-1] += lane.waiting

#main loop that runs each light cycle
while len(departed) < NUM_CARS:

    if PRINT_EVENTS: printLightStatus()
    
    

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
            if not scheduleDeparture(lane, drag) : break

    #schedule right turns for inactive lanes
    for lane in [inactiveL1, inactiveL2]:
        while lane.waiting > 0 and lane.peek().turn == RIGHT:
            if not scheduleRightTurnOnRed(lane) : break

    #print events for this light cycle
    while eventList.peek():
        processEvent(eventList.pop(), PRINT_EVENTS)

    activeL1.traversals =[]
    activeL2.traversals =[]


    clock = nextLightChange
    
    GreenLight = (GreenLight + 1) % 2
    nextLightChange += lightInterval[GreenLight]

    countWaiting()

    if PRINT_EVENTS and len(departed) == NUM_CARS:
        print('----END----')
        break
    

#departed.sort(key=lambda x:x.id)
#for i in departed: print(i)

