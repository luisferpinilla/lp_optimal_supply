import unittest
from unittest.main import main
from event_queue import EventQueue, Event, EventType
import numpy as np


class pruebas(unittest.TestCase):

    def test_queue(self):
        self.assertTrue(True)

    def test_value(self):
        self.assertEqual(first=True, second=False, msg='Bad!!!')

if __name__ == '__main__':
    unittest.main()    
