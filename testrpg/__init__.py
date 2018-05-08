from sys import exit

import pygame

from pygame_easy_event import PygameEasyEvent

pygame_easy_event = PygameEasyEvent()

size = width, height = 500, 400
speed = [1, 1]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("intro_ball.gif")
ball_rect = ball.get_rect()


def main_loop():
	global ball_rect, speed
	
	ball_rect = ball_rect.move(speed)
	if ball_rect.left < 0 or ball_rect.right > width:
		speed[0] = -speed[0]
	if ball_rect.top < 0 or ball_rect.bottom > height:
		speed[1] = -speed[1]
	
	screen.fill(black)
	screen.blit(ball, ball_rect)
	pygame.display.flip()


@pygame_easy_event.add_handler(pygame.QUIT)
def _on_quit(evt):
	exit()


pygame_easy_event.do_loop(main_loop)
