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

random.seed(10)

def populate(cars, lanes):
    while len(cars) > 0 and cars[0].time <= clock:
        car = cars.pop(0)
        for i in range(0, len(lanes)):
            if car.direction == lanes[i].direction:
                lanes[i].addCar(car)
                print(f'ARRIVED @ {clock}: {car}')
   

def simLights(lanes, departed):

    for lane in lanes:
        while lane.waiting > 0:
            departed.append(lane.pop())
            print(f'DEPARTED @ {clock}:  {departed[len(departed)-1]}')
                    
southToNorth = Lane(NORTH, STRAIGHT)
westToEast = Lane(EAST, STRAIGHT)
northToSouth = Lane(SOUTH, STRAIGHT)
eastToWest = Lane(WEST, STRAIGHT)

cars = []

for i in range(1, 11):
    cars.append(Car(random.randrange(0, 4), STRAIGHT, i))


lanes = [southToNorth, westToEast, northToSouth, eastToWest]
departed = []
numCars = len(cars)
GreenLight = 0
clock = 1

while len(departed) < numCars :


    populate(cars, lanes)

    simLights([lanes[GreenLight], lanes[GreenLight+2]], departed)
    
    clock += 1
    if clock % 4 == 0:
        GreenLight = (GreenLight + 1) % 2
        print('----LIGHT CHANGE----')
    