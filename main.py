import numpy
from threading import Thread, Lock
import random
from Sim import Car, Lane, Event, Lights
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
fourWayLights = Lights(lanes)

cars = []
for i in range(1, 16):
    cars.append(Car(random.randrange(0, 4), STRAIGHT, random.randrange(1, 11), SERVICE_TIME))
numCars = len(cars)
cars.sort(key=lambda a : a.time)

for i in range(0, len(cars)):
    cars[i].setID(i+1)

lightInterval = 4
nextLightChange = lightInterval

    
    


#main loop that runs each light cycle
while len(departed) < numCars:
    if len(cars) == 0: fourWayLights.simLights(nextLightChange, clock, departed)
    
    #loop that adds the cars arriving on this light cycle
    while len(cars) > 0 and cars[0].time < nextLightChange:
        car = cars.pop(0)
        clock = car.time
        
        fourWayLights.addCar(car)
        # if the next car gets here before this car can leave, skip the sim
        if len(cars) > 0 and cars[0].time > (car.time + car.service):
            fourWayLights.simLights(nextLightChange, clock, departed)

    clock = nextLightChange
    nextLightChange += lightInterval
    GreenLight = (GreenLight + 1) % 2
    fourWayLights.setGreen(GreenLight)
    if(len(departed) == numCars):
        print('----END----')
        break
    print('----LIGHT CHANGE----')
    
#print(departed)
    