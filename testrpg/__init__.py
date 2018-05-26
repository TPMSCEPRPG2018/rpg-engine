from os import chdir

import pygame

from pygame_plugin_system.rpg import RPGWindow
from .constants import *


def main():
	chdir(RESOURCES_DIR)
	player_icon = pygame.transform.smoothscale(pygame.image.load(str(PLAYER_ICON_PATH)), (TILE_SIZE, TILE_SIZE))
	enemy_icon = pygame.transform.smoothscale(pygame.image.load(str(ENEMY_ICON_PATH)), (TILE_SIZE, TILE_SIZE))
	RPGWindow(size=START_SIZE, start_map_path=MAP_PATH, tickrate=TICK_RATE, player_icon=player_icon, enemy_icon=enemy_icon, tile_size=TILE_SIZE, enemy_hp=ENEMY_HP, player_hp=PLAYER_HP, font_color=FONT_COLOR).run()
