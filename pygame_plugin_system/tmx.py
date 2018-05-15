import pygame
import tmx

from pygame_plugin_system.objects import ObjectWindow


class TMXWindow(ObjectWindow):
	def __init__(self, *, size=(0, 0), start_map_path, focus=(0, 0), tickrate, **kwargs):
		super().__init__(size=size, **kwargs)
		
		self.clock = pygame.time.Clock()
		self.tilemap = tmx.load(start_map_path, size)
		self.tilemap.set_focus(*focus)
		self.objects.add(self.tilemap)
		self.tickrate = tickrate
	
	def main_loop(self, screen: pygame.Surface):
		super().main_loop(screen)
		
		self.tilemap.update(self.clock.tick(self.tickrate))
