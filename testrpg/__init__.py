from random import uniform
from sys import exit

import pygame

from rpgengine import Window
from testrpg.constants import *

window = Window()

size = width, height = START_SIZE
speed = list(START_SPEED)

screen = pygame.display.set_mode(size, pygame.RESIZABLE)

ball = pygame.image.load("intro_ball.gif")
ball_rect = ball.get_rect()


@window.add_loop
def _main_loop():
	global ball_rect, speed
	
	ball_rect = ball_rect.move(speed)
	
	speed[0] += uniform(-MAX_ACCELERATION, MAX_ACCELERATION)
	speed[1] += uniform(-MAX_ACCELERATION, MAX_ACCELERATION)
	
	if (ball_rect.left < 0 and speed[0] < 0) or (ball_rect.right > width and speed[0] > 0):
		speed[0] = -speed[0]
	
	if (ball_rect.top < 0 and speed[1] < 0) or (ball_rect.bottom > height and speed[1] > 0):
		speed[1] = -speed[1]
	
	screen.fill(BACKGROUND)
	screen.blit(ball, ball_rect)
	pygame.display.flip()


@window.add_handler(pygame.QUIT)
def _on_quit(evt):
	exit()


@window.add_handler(pygame.VIDEORESIZE)
def _on_resize(evt):
	global screen, size, width, height
	
	size = width, height = evt.size
	screen = pygame.display.set_mode(size, pygame.RESIZABLE)


if __name__ == '__main__':
	window.run()
