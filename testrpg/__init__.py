from os import chdir

import pygame

from pygame_plugin_system.rpg import RPGWindow
from .constants import *


class TestRPGWindow(RPGWindow):
	def __init__(self, *, size, start_map_path, tickrate, player_icon, tile_size, **kwargs):
		super().__init__(size=size, start_map_path=start_map_path, tickrate=tickrate, player_icon=player_icon, tile_size=tile_size, **kwargs)


def main():
	chdir(RESOURCES_DIR)
	player_icon = pygame.transform.smoothscale(pygame.image.load(str(PLAYER_ICON_PATH)), (TILE_SIZE, TILE_SIZE))
	TestRPGWindow(size=START_SIZE, start_map_path=MAP_PATH, tickrate=TICK_RATE, player_icon=player_icon, tile_size=TILE_SIZE).run()
