from collections import defaultdict

import pygame

pygame.init()

__all__ = ['Window']


class Window:
	def __init__(self):
		self.event_handlers = defaultdict(list)
		self.loops = []
	
	def add_handler(self, event_type):
		def decorator(handler):
			self.event_handlers[event_type].append(handler)
		
		return decorator
	
	def add_loop(self, loop):
		self.loops.append(loop)
	
	def run(self):
		while 1:
			for event in pygame.event.get():
				for handler in self.event_handlers[event.type]:
					handler(event)
			
			for loop in self.loops:
				loop()
