import numpy
import threading
from Sim import Car, Lane, Event, Lights

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

STRAIGHT = 0
RIGHT = 1
LEFT = 2

STRAIGHT_RIGHT = 3
STRAIGHT_LEFT = 4



#create lanes

westToEast = Lane(EAST, STRAIGHT)
eastToWest = Lane(WEST, STRAIGHT)

print(westToEast.direction)
print(eastToWest.isEmpty())

car1 = Car(EAST, STRAIGHT, 1)
car2 = Car(WEST, STRAIGHT, 2)
car3 = Car(WEST, STRAIGHT, 3)
car4 = Car(EAST, STRAIGHT, 4)

cars = [car1, car2, car3, car4]
departed = []

clock = 0

while len(cars) > 0:

    if cars[0].time >= clock:
        #add to lane
        if cars[0].direction == EAST:
            westToEast.addCar(cars.pop(0))

        elif cars[0].direction == WEST:
            eastToWest.addCar(cars.pop(0))

    clock +=1 

print(clock)
print(westToEast)
print(eastToWest)