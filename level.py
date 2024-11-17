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
            food = item_class("Images/PNGs/Chicken Leg-Idle.png", (x, y))
            food.load_animation("Images/PNGs/Chicken Leg-Idle.json")
            self.food_items.append(food)
            self.spawned_positions.add((x, y))

    def update(self, dt):
        for food in self.food_items:
            food.update(dt)

    def draw_food(self, screen):
        for food in self.food_items:
            food.draw(screen)

    def switch_animation(self, json_path):
        self.load_animation(json_path)
        self.current_frame = 0
        self.current_time = 0

    def load_animation(self, json_path):
        try:
            with open(json_path, "r") as f:
                animation_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Could not find animation data file at path: {json_path}")
            return

        #Extract relevant data
        frames_data = animation_data["frames"]
        sprite_sheet_path = animation_data["meta"]["image"]
        sprite_sheet_path = os.path.join(os.path.dirname(json_path), sprite_sheet_path)

        #Load sprite sheet
        try:
            self.sprite_sheet = pygame.image.load(sprite_sheet_path)
        except pygame.error as e:
            print(f"Error loading sprite sheet: {sprite_sheet_path}: {e}")
            return

        #Extract and process frames
        self.scaled_frames = []
        for frame_data in frames_data:
            x = frame_data["frame"]["x"]
            y = frame_data["frame"]["y"]
            w = frame_data["frame"]["w"]
            h = frame_data["frame"]["h"]
            duration = frame_data["duration"]
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w , h))
            scaled_frame = pygame.transform.scale(
                frame, (frame.get_width() * self.scale_factor, frame.get_height() * self.scale_factor)
            )
            self.scaled_frames.append((scaled_frame, duration))
            
    def check_food_collision(self, player, player_rect):
        for food in self.food_items:
            if player_rect.colliderect(food.rect) and not food.collected:
                food.collect(player)
                food.switch_animation("Images/PNGs/Chicken Leg-Omnomnom.json")
    
    def remove_collected_items(self):
        self.food_items = [food for food in self.food_items if not food.collected or not food.finished_animation]

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
