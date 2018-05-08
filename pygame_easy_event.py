from collections import defaultdict

import pygame

__all__ = ['PygameEasyEvent']


class PygameEasyEvent:
	def __init__(self):
		pygame.init()
		self.event_handlers = defaultdict(list)
	
	def do_loop(self, main_loop):
		while 1:
			for event in pygame.event.get():
				for handler in self.event_handlers[event.type]:
					handler(event)
			
			main_loop()
	
	def add_handler(self, event_type):
		def decorator(handler):
			self.event_handlers[event_type].append(handler)
		
		return decorator
