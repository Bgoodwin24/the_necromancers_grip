import pygame
from constants import *
from items import *
from entities import *

class Level:
    def __init__(self):
        self.food_items = []
        self.enemies = []
        self.spawned_positions = set ()

    #Draw background and scale
    def draw_level(self, screen, json_path):
        scaled_background = pygame.transform.scale(json_path, (SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
        screen.blit(scaled_background, (0, 0))

    def spawn_food_items(self, screen, player, item_class, x, y):
        if player.health <= 1000:
            for food in self.food_items:
                if food.position == (x, y):
                    return
            print(f"Spawning food at: ({x}, {y})")
            food = item_class("Images/PNGs/Chicken Leg-Idle.png", (x, y))
            food.load_animation("Images/PNGs/Chicken Leg-Idle.json")
            self.food_items.append(food)
            self.spawned_positions.add((x, y))
        else:
            print("Conditions not met for spawning food.")

    def update(self, dt):
        for food in self.food_items:
            food.update(dt)

    def draw_food(self, screen):
        for food in self.food_items:
            food.draw(screen)
            
    def check_food_collision(self, player_rect):
        for food in self.food_items:
            print(f"Player Rect: {player_rect}, Food Rect: {food.rect}")
            if player_rect.colliderect(food.rect):
                print(f"Collision with food at {food.rect}")
                food.collected = True

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
        self.rect = pygame.Rect(SCREEN_WIDTH * 3 + 5, 0, 1, SCREEN_HEIGHT * 3)
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
