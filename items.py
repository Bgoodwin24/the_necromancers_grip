import pygame
import json
from entities import *

class Items:
    def __init__(self, image, position, heal_amount=1000):
        self.image = pygame.image.load("Images/PNGs/Chicken Leg-Idle.png")
        self.position = pygame.Vector2(position) if isinstance(position, tuple) else position
        self.heal_amount = heal_amount
        self.rect = self.image.get_rect(topleft=self.position)
        self.collected = False
        self.animation_playing = False
        self.finished_animation = False
        self.sprite_sheet = None
        self.scale_factor = 4
        self.scaled_image = pygame.transform.scale(self.image, 
                                                   (self.image.get_width() * self.scale_factor, 
                                                    self.image.get_height() * self.scale_factor))
        self.scaled_frames = []
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

    def update(self, dt):
        if self.animation_playing:
            self.current_time += dt * 1000
            frame_duration = self.scaled_frames[self.current_frame][1]
            if self.current_time >= frame_duration:
                self.current_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.scaled_frames)
                if self.current_frame == 0:
                    self.finished_animation = True
                    self.animation_playing = False
                    self.collected = True

    def draw(self, screen):
        if not self.collected:
            if self.animation_playing:
                    frame_surface = self.scaled_frames[self.current_frame][0]
                    screen.blit(frame_surface, self.rect.topleft)
            else:
                screen.blit(self.scaled_image, self.rect.topleft)
    
    def collect(self, player):
        self.animation_playing = True
        player.heal(self.heal_amount)   

    def check_item_collision(self, player):
        return self.rect.colliderect(player.rect)
    
    def switch_animation(self, json_path):
        self.load_animation(json_path)
        self.current_frame = 0
        self.current_time = 0
        self.finished_animation = False

    def is_animation_finished(self):
        return self.finished_animation