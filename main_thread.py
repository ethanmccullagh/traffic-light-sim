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

clock = 0

def populate(cars, lanes, lock):
    global clock

    while len(cars) > 0:
        lock.acquire()
        if cars[0].time <= clock:
            car = cars.pop(0)

            for i in range(0, len(lanes)):
                if car.direction == lanes[i].direction:
                    lanes[i].addCar(car)
                    #print('car added')
        lock.release()
        time.sleep(0.05)

def simLights(lanes, departed, lock):
    global clock
    GreenLight = 0
    count = 1

    while len(departed) < 4 and count < 11:
        lock.acquire()
        print(clock)
        print(lanes[0])
        print(lanes[1])
        print(GreenLight)
        print('----------')
        if not lanes[GreenLight].isEmpty():
            departed.append(lanes[GreenLight].pop())

        

        if clock % 2 == 0:
            GreenLight = (GreenLight + 1) % 2
            clock += 1

        clock += 1
        lock.release()
        time.sleep(0.05)
        

        count+=1
                    
westToEast = Lane(EAST, STRAIGHT)
eastToWest = Lane(WEST, STRAIGHT)

print(westToEast.direction)
print(eastToWest.isEmpty())

car1 = Car(EAST, STRAIGHT, 1)
car2 = Car(WEST, STRAIGHT, 2)
car3 = Car(WEST, STRAIGHT, 3)
car4 = Car(EAST, STRAIGHT, 4)

cars = [car1, car2, car3, car4]
lanes = [westToEast, eastToWest]
departed = []

lock = Lock()
t1 = Thread(target=populate, args=(cars, lanes, lock))
t2 = Thread(target=simLights, args=(lanes, departed, lock))
t1.start()
t2.start()

t1.join()
t2.join()
print('##########')
print(clock)
print(westToEast)
print(eastToWest)
print(departed)