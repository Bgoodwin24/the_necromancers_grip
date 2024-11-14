import pygame
import json
from constants import *
import os

#Just for if there were other player classes to choose from
class Entity:
    def __init__(self, json_path, radius, scale_factor=4):
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius
        self.position = pygame.Vector2(0, 0)
        self.json_path = json_path
        self.scale_factor = scale_factor
        self.scaled_frames = []
        self.current_frame = 0
        self.current_time = 0
        self.alive = True
        self.load_animation(json_path)
        
        #Load json animation data
    def load_animation(self, json_path):
        pass

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        if self.health <=0:
            self.die()

    def die(self, json_path):
        pass

    def cleanup(self):
        pass

    def update(self, dt):
        if not self.alive:
            return
        
        if self.scaled_frames:
            self.current_time += dt * 1000

            frame_duration = self.scaled_frames[self.current_frame][1]

            if self.current_time >= frame_duration:
                self.current_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.scaled_frames)

    def draw(self, screen, x, y):
        if not self.alive:
            return
            
        if self.scaled_frames:
            frame_surface, frame_duration = self.scaled_frames[self.current_frame]
            screen.blit(frame_surface, (x, y))
        else:
            print("No frames to draw.")

    def switch_animation(self, animation_name, json_path):
        self.load_animation(json_path)
        self.current_animation = animation_name
        self.current_frame = 0
        self.current_time = 0

    def get_rect(self, x, y):
        if self.scaled_frames:
            frame_surface = self.scaled_frames[self.current_frame][0]
            return pygame.Rect(x, y, frame_surface.get_width(), frame_surface.get_height())
        return pygame.Rect(0, 0, 0, 0)
    
    def check_collision(self, player_rect, colliders):
        for collider in colliders.values():
            if player_rect.colliderect(collider):
                return True
        return False
    
    def check_attack_collision(self, other):
         return self.position.distance_to(other.position) <= self.radius + other.radius

#Actual player class for this game
class Rogue(Entity):
    def __init__(self, json_path, position):
        super().__init__(json_path, PLAYER_RADIUS)
        self.position = pygame.Vector2(position)
        self.image = pygame.image.load("Images/PNGs/Rogue-Idle.png")
        self.current_animation = "idle"
        self.health = 1000
        self.max_health = 2000
        self.attack = 250

        if self.scaled_frames:
            frame_surface = self.scaled_frames[self.current_frame][0]
            self.frame_width = frame_surface.get_width()
            self.frame_height = frame_surface.get_height()
        else:
            self.width = 32
            self.height = 48

        self.rect = pygame.Rect(self.position.x, self.position.y, self.frame_width, self.frame_height)

    def handle_movement(self, keys, x_pos, y_pos, colliders, dt):
        new_x_pos = x_pos
        new_y_pos = y_pos
        movement_speed = PLAYER_SPEED

        #Left
        if keys[pygame.K_a]:
            if self.current_animation != "Run Left":
                self.switch_animation("Run Left", "Images/PNGs/Rogue-Run Left.json")
            new_x_pos -= movement_speed * dt
    
        #Right
        elif keys[pygame.K_d]:
            if self.current_animation != "Run":
                self.switch_animation("Run", "Images/PNGs/Rogue-Run.json")
            new_x_pos += movement_speed * dt

        else:
            if self.current_animation != "Idle":
                self.switch_animation("Idle", "Images/PNGs/Rogue-Idle.json")

        #Attack
        #if keys[pygame.K_SPACE]:
            #pass

        #Process key release events
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d, pygame.K_SPACE]:
                    self.switch_animation("Idle", "Images/PNGs/Rogue-Idle.json")

        #Get width and height of current frame
        if self.scaled_frames:
            frame_surface = self.scaled_frames[0][0]
            frame_width = frame_surface.get_width()
            frame_height = frame_surface.get_height()
        else:
            frame_width = 0
            frame_height = 0

        frame_width = float(frame_width) if frame_width else 0
        frame_height = float(frame_height) if frame_height else 0

        #Check collision
        if frame_width > 0 and frame_height > 0:
            if not self.check_collision(pygame.Rect(new_x_pos, y_pos, frame_width, frame_height), colliders):
                x_pos = new_x_pos
        
            if not self.check_collision(pygame.Rect(x_pos, new_y_pos, frame_width, frame_height), colliders):
                y_pos = new_y_pos
        else:
            print(f"Invalid frame dimensions: width={frame_width}, height={frame_height}")
        
        return x_pos, y_pos

    def heal(self, heal_amount):
        self.health += heal_amount
        #Cap health at max
        self.health = min(self.health, self.max_health)

    def take_damage(self, damage_amount):
        super().take_damage(damage_amount)
        if not self.alive:
            print("Game over, better luck next time!")
            pygame.quit()

    def die(self, json_path):
        pygame.image.load(json_path)
        self.alive = False
        print(f"Oh no! {self.__class__.__name__} has died!")
        

    #Load json animation data
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
        frames = []
        for frame_data in frames_data:
            x = frame_data["frame"]["x"]
            y = frame_data["frame"]["y"]
            w = frame_data["frame"]["w"]
            h = frame_data["frame"]["h"]
            duration = frame_data["duration"]
            frame = self.sprite_sheet.subsurface(pygame.Rect(x, y, w , h))
            frames.append((frame, duration))

        #Scaling
        self.scale_factor = 4
        self.scaled_frames = []
        for frame, duration in frames:
            scaled_frame = pygame.transform.scale(frame, (frame.get_width() * self.scale_factor, frame.get_height() * self.scale_factor))
            self.scaled_frames.append((scaled_frame, duration))

    def check_attack_collision(self, enemy):
        if self.position.distance_to(enemy.position) <= self.radius + enemy.radius:
            enemy.health -= self.attack

#def cleanup(self):
    #if self in self.level.enemies:
        #self.level.enemies.remove(self)
