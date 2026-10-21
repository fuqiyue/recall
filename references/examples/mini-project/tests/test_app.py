import unittest
from src.app import greet

class GreetingTests(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(greet("Recall"), "Hello, Recall")
