import pygame
import json
from entities import *

class Items:
    def __init__(self, x, y, heal_amount=1000):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.heal_amount = heal_amount
        self.collected = False
        self.image = pygame.image.load("Images/PNGs/Chicken Leg-Idle.json")

    def update(self, dt):
        pass

    def draw(self, screen):
        if not self.collected:
           screen.blit(self.image, self.rect.topleft)
    
    def collect(self, player):
        self.collected = True
        self.switch_animation("Omnomnom", "Images/PNGs/Chicken Leg-Omnomnom.json")
        player.heal(self.heal_amount)

    def check_item_collision(self, player):
        return self.rect.colliderect(player.get_rect(player.position.x, player.position.y))
