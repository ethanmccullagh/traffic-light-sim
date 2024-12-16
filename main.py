import numpy
import random
from Sim import Car, Lane, Event, EventList, Traversal
import math
from parameters import params

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

#SIMULATION PARAMETERS
#change these values to setup different scenarios
#PRINT EVENTS will print a real time record of the simulation and all cars entering/leaving
#NUM CARS is the number of cars that will enter over the course of the simulation
#ARR_PER_HOUR is the arrival rate in cars per hour
#SERVICE TIME is the time it takes a car to leave the intersection once they start moving
## service time mainly effects how long cars have to wait to make right/left turns
PRINT_EVENTS = params['PRINT_EVENTS']
NUM_CARS = params['NUM_CARS']
ARR_PER_HOUR = params['ARR_PER_HOUR']
SERVICE_TIME = params['SERVICE_TIME']
NUM_RUNS = params['NUM_RUNS']
lightInterval = params['lightInterval']
directionWeights = params['directionWeights']


random.seed(10)

clock = 0
departed = []
waitingInLane = []

#LIGHT CHANGE LOGIC
#change these values to change the green light intervals
# default is 36 second green for N/S and 24 second green for E/W
# values are portions of a minute so 36 seconds = 0.6 minutes
GreenLight = 0
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


turnPopulation = [STRAIGHT, RIGHT, LEFT]
turnWeights = {
    NORTH : [0.66, 0.33, 0.01],
    EAST : [0.71, 0.16, 0.13],
    SOUTH : [0.87, 0.12, 0.01],
    WEST : [0.57, 0.08, 0.35]
}

directionChoices = random.choices(directionPopulation, directionWeights, k=NUM_CARS*NUM_RUNS)

def turnChoice(dir):
    turn = random.choices(turnPopulation, turnWeights[dir], k=1)
    return turn[0]


cars = []
lastArrival = 0
for i in range(NUM_CARS*NUM_RUNS):
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

