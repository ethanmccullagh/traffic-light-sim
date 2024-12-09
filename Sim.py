class Car:
    def __init__(self, lane, turn, time):
        self.direction = lane
        self.turn = turn
        self.time = time
        
class Lights:
    def __init__(self, traversals):
        self.traversals = traversals
        
    #returns a boolean given a turn to check if that turn can be made
    # Examples
    # Turning right on a red light, traffic for lane being turned into must be clear within intersection
    # Turning left, Oncoming traffic going straight for both lanes must be clear. 
    #       Cars from the oncoming lanes that are turning can be ignored
    # So different rules for right turns and left turns. Straight throughs dont need to be checked
    def isTurnClear(srcDir, direction):
        pass
    
        
        
class Lane:
    cardinals ={
        0 : 'North',
        1 : 'East',
        2 : 'South',
        3 : 'West'
    }
    
    turningLanes = {
        0 : 'Straight and Right',
        1 : 'Straight and Left'
    }
    
    def __init__(self, turnsAllowed, direction):
        self.turnsAllowed = turnsAllowed
        self.direction = direction
        self.queue = []
        
class Event:
    #_type is dep or arr
    #used to track cars entering and leaving the intersection
    #lane is the lane the car came from
    def __init__(self, _type, time, lane, straight):
        self._type = _type
        self.time = time
        self.lane = lane
        self.straight = straight
    