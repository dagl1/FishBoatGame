import pygame, os
from states.state import State

class OverWorld(State):
    def __init__(self, game):
        State.__init__(self, game)