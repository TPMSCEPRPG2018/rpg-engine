from os import chdir

import pygame

from pygame_plugin_system.rpg import RPGWindow
from .constants import *


class TestRPGWindow(RPGWindow):
	def __init__(self, *, size=START_SIZE, start_map_path=MAP_PATH, tickrate=TICK_RATE, player_icon_path=PLAYER_ICON_PATH, **kwargs):
		player_icon = pygame.image.load(str(player_icon_path))
		super().__init__(size=size, start_map_path=start_map_path, tickrate=tickrate, player_icon=player_icon, **kwargs)


def main():
	chdir(RESOURCES_DIR)
	TestRPGWindow().run()
