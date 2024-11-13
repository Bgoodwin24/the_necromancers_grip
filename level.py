import pygame
from constants import *
from items import *
from entities import *

class Level:
    def __init__(self):
        self.food_items = []
        self.enemies = []

    #Draw background and scale
    def draw_level(self, screen, json_path):
        scaled_background = pygame.transform.scale(json_path, (SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
        screen.blit(scaled_background, (0, 0))

    def spawn_food_items(self, player):
        for _ in range(2):
            food = Items(-100, 100)
            if player.health <= 1000:
                self.food_items.append(food)

    def update(self, dt):
        for food in self.food_items:
            food.update(dt)

    def draw_food(self, screen):
        for food in self.food_items:
            food.draw(screen)
            
    def check_food_collision(self, player_rect):
        for food in self.food_items:
            if food.rect.colliderect(player_rect):
                food.collect()


    def check_collision(self, player_rect, colliders):
        for collider in colliders:
            if player_rect.colliderect(collider):
                return True
        return False

    def add_enemies(self, json_path, num_enemies):
        pass

    def check_enemies_dead(self):
        return all(enemy.health <= 0 for enemy in self.enemies)
    
class RightWall:
    def __init__(self, level):
        self.rect = pygame.Rect(SCREEN_WIDTH * 3 + 430, 0, 1, SCREEN_HEIGHT * 3)
        self.level = level

    def can_pass(self, player):
        if self.level.check_enemies_dead():
            return True
        return False
    
    def handle_collision(self, player):
        if self.rect.colliderect(player.get_rect(player.position.x, player.position.y)):
            if self.can_pass(player):
                self.transition_to_next_level()
    
    def transition_to_next_level(self):
        #load new level, reset positions, load background/enemies
        pass
