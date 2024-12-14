import numpy
import threading

# Going to use lanes like queues at the grocery store
# Traffic light will be like the clerk
# Service time will reflect time car is accelerating into intersection
# Intersection itself is another queuing system that is event based
# Queue waiting at light will be object based on the cars waiting
# Cars entering the intersection will then create arrival/departure events 
# After car completes its turn it leaves the system entirely
# So there are object based queues for the lanes waiting to enter the intersection
# Within the intersection there are events to track the movement of the cars
# Time spent in intersection will be added to the service time from accelerating
#
# First sim will be cars moving straight through a one way light with no turns

cardinals = {
    0 : 'North',
    1 : 'East',
    2 : 'South',
    3 : 'West'
}

turns = {
    0 : 'Straight',
    1 : 'Right',
    2 : 'Left'
}

class Car:
    def __init__(self, direction, turn, time, service):
        self.turn = turn
        self.direction = direction
        self.time = time
        self.dep = False
        self.service = service
        self.accel = time

    def __str__(self):
        if self.dep :return  f'Car {self.id} (Arrived: {self.time}, Started: {self.accel}, Departed: {self.departTime}, Direction: {cardinals[self.direction]}, Turn: {turns[self.turn]})'
        return f'Car {self.id} (Arrived: {self.time}, Direction: {cardinals[self.direction]}, Turn: {turns[self.turn]})'
    
    def __repr__(self):
        return str(self)
    
    def departTime(self, time):
        self.dep = True
        self.departTime = time
        self.accel = time - self.service
        
    def setID(self, id):
        self.id = id
    
        
        
class Lane:
    def __init__(self, direction, turnsAllowed):
        self.turnsAllowed = turnsAllowed
        self.direction = direction
        self.queue = []
        self.waiting = 0
        self.traversals = []

    def __str__(self):
        return f'{self.queue}'
    
    def addTraversal(self, traversal):
        self.traversals.append(traversal)

    def isBusy(self, time, duration):
        for tr in self.traversals:
            if tr.isConflict(time, duration):
                return True
        return False
    
    def nextWindow(self, time, duration, lightChange):
        for tr in self.traversals:
            if tr.isConflict(time, duration):
                if tr.time >= time and (tr.time + tr.duration + duration) < lightChange and not self.isBusy(tr.time + tr.duration, duration):
                    return tr.time + tr.duration
        print(self.traversals)
        return None

    

    def addCar(self, car):
        self.queue.append(car)
        self.waiting += 1

    def pop(self):
        self.waiting -= 1
        return self.queue.pop(0)
    
    def peek(self):
        if len(self.queue) == 0: return []
        return self.queue[0]
    
    def isEmpty(self):
        return self.waiting == 0
        
class EventList:
    def __init__(self):
        self.events = []

    def add(self, event):
        self.events.append(event)
        self.events.sort(key=lambda x : x.time)

    def pop(self):
        if len(self.events) == 0 : return None
        return self.events.pop(0)
    
    def peek(self):
        if len(self.events) == 0 : return None
        return self.events[0]

        
class Event:
    #_type is dep or arr
    #used to track cars entering and leaving the intersection
    #lane is the lane the car came from
    def __init__(self, _type, time, car):
        self._type = _type
        self.time = time
        self.car = car

class Traversal:
    def __init__(self, time, duration):
        self.time = time
        self.duration = duration

    def __str__(self):
        return f'time:{self.time}, duration:{self.duration}'
    
    def __repr__(self):
        return str(self)

    def isConflict(self, time, duration):
        if self.time <= time and time < (self.time + self.duration):
            return True
        if self.time <= (time + duration) and (time + duration) <= (self.time + self.duration):
            return True
        return False
