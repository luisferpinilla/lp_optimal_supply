from enum import Enum
@DeprecationWarning
class EventType(Enum):
    """Type of event

    Args:
        Enum ([type]): describes event
    """
    DEMAND=0
    PURCHASE_ORDER=1
    ARRIVAL=2
    