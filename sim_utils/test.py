from event_queue import EventQueue, Event, EventType

print('inicializando queue')
queue = EventQueue()

print('agregando algunos eventos')
queue.add_event(Event(clock=10, type_of_event=EventType.DEMAND, event_name='Test demanda 10'))
queue.add_event(Event(clock=14, type_of_event=EventType.DEMAND, event_name='Test demanda 14'))
queue.add_event(Event(clock=13, type_of_event=EventType.DEMAND, event_name='Test demanda 13'))
queue.add_event(Event(clock=11, type_of_event=EventType.DEMAND, event_name='Test demanda 11'))
queue.add_event(Event(clock=10, type_of_event=EventType.DEMAND, event_name='Test2 demanda 10'))
print('pop up algunos eventos')
for t in range(20):
    print(f'time clock = {t}:')
    events = queue.pop_up_events(t)
    for event in events:
        print('\t',event.get_event_type, event.get_event_name, 'tiene más?', queue.has_more_events) 
    