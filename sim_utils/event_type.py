from enum import Enum

class EventType(Enum):
    '''
    Determine the type of events
    '''
    PURCHASE_ORDER=1
    ARRIVAL=2
    