import pygame
import json
import os
from constants import *
from level import *

class Projectile:
    def __init__(self, x, y, json_path, velocity, max_distance=300, category="enemy"):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(velocity)
        self.alive = True
        self.has_spawned = False
        self.scaled_frames = []
        self.current_frame = 0
        self.current_time = 0
        self.max_distance = max_distance
        self.category = category
        self.distance_traveled = 0
        self.load_animation(json_path)

    def load_animation(self, json_path):
        with open(json_path, "r") as f:
            animation_data = json.load(f)
        
        frames_data = animation_data["frames"]
        sprite_sheet_path = animation_data["meta"]["image"]
        sprite_sheet_path = os.path.join(os.path.dirname(json_path), sprite_sheet_path)

        sprite_sheet = pygame.image.load(sprite_sheet_path)

        frames = []
        for frame_data in frames_data:
            x = frame_data["frame"]["x"]
            y = frame_data["frame"]["y"]
            w = frame_data["frame"]["w"]
            h = frame_data["frame"]["h"]
            duration = frame_data["duration"]
            frame = sprite_sheet.subsurface(pygame.Rect(x, y, w, h))
            frames.append((frame, duration))

        self.scaled_frames = [(pygame.transform.scale(frame, (frame.get_width() * 4, frame.get_height() * 4)), duration) for frame, duration in frames]
    
    def update(self, dt):
        if not self.alive:
            return
        
        self.current_time += dt * 1000
        frame_duration = self.scaled_frames[self.current_frame][1]
        if self.current_time >= frame_duration:
            self.current_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.scaled_frames)
        #Update position
        self.position += self.velocity * dt
        self.distance_traveled += self.velocity.length() * dt
        #Check if projectile exceeds max distance
        if self.distance_traveled >= self.max_distance:
            self.alive = False
        
    def check_colliders(self, colliders):
        projectile_rect = self.get_rect()
        for collider in colliders.values():
            if projectile_rect.colliderect(collider):
                self.alive = False
                return True
        return False
    
    def draw(self, screen):
        if self.scaled_frames:
            frame_surface, _ = self.scaled_frames[self.current_frame]
            screen.blit(frame_surface, self.position)

    def check_collision(self, other):
        if not self.alive:
            return False

        projectile_rect = self.get_rect()
        if projectile_rect.colliderect(other.get_rect(other.position.x, other.position.y)):
            self.alive = False
            return True
        return False
    
    def switch_animation(self, animation_name, json_path):
        self.load_animation(json_path)
        self.current_animation = animation_name
        self.current_frame = 0
        self.current_time = 0

        if animation_name == "Attack" or animation_name == "Attack Left":
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                self.frame_width = frame_surface.get_width()
                self.frame_height = frame_surface.get_height()
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[0]
                self.frame_width = frame_surface.get_width()
                self.frame_height = frame_surface.get_height()

    def get_rect(self):
        frame_surface, _ = self.scaled_frames[self.current_frame]
        return pygame.Rect(self.position.x, self.position.y, frame_surface.get_width(), frame_surface.get_height())
