from event_queue import EventQueue, Event, EventType

print('inicializando queue')
queue = EventQueue()

print('agregando algunos eventos')
queue.add_event(time_clock=10, event_name='test llegada 10', event_type=EventType.ARRIVAL)
queue.add_event(time_clock=12, event_name='test llegada 12', event_type=EventType.ARRIVAL)
queue.add_event(time_clock=14, event_name='test llegada 14', event_type=EventType.ARRIVAL)
queue.add_event(time_clock=11, event_name='test llegada 11', event_type=EventType.ARRIVAL)

print('pop up algunos eventos')
for t in range(20):
    print(f'time clock = {t}:')
    events = queue.pop_up_events(t)
    for event in events:
        print('\t',event.get_event_type, event.get_event_name, 'tiene más?', queue.has_more_events) 
    