from projectiles import Projectile
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
        self.attack_start_position = pygame.Vector2(self.position.x, self.position.y)
        self.is_attacking = False
        self.is_moving = False
        self.projectile_spawned = False
        self.is_dying = False
        self.projectiles = []
        self.load_animation(json_path)
        
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

    def check_attack_collision(self, other):
         return self.position.distance_to(other.position) <= self.radius + other.radius

    def take_damage(self, damage_amount):
        self.health -= damage_amount
        #Ensure health never goes below zero
        self.health = max(0, self.health)
        if self.health == 0:
            print("Game over, better luck next time!")
            self.die()

    def attack_projectile(self, x, y, json_path):
        pass

    #def attack(self, other, json_path):
        #if self.check_attack_collision:
            #self.

    def die(self, animation_name, json_path):
        self.death_position = (self.position)
        self.switch_animation(animation_name, json_path)
        self.is_dying = True
        print(f"Oh no! {self.__class__.__name__} has died!")

    def cleanup(self):
        pass

    def update(self, dt):
        if not self.alive:
            return

        if self.is_dying:
            if self.current_frame == len(self.scaled_frames) - 2:
                self.alive = False

        # Update the current frame based on the animation time
        if self.scaled_frames:
            self.current_time += dt * 1000
            frame_duration = self.scaled_frames[self.current_frame][1]
            #Check if we should advance the frame
            if self.current_time >= frame_duration:
                self.current_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.scaled_frames)
                #Reset the attack position if the attack animation completes
                if self.is_attacking and self.current_frame == 0:
                    self.is_attacking = False
                    self.attack_start_position = None
                    self.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")

    #Return default attack position, can be overwritten by children
    def get_attack_position(self, screen):
        if self.attack_start_position is None:
            print("Error: Attack start position is not set")
            return self.position.x, self.position.y
        attack_x, attack_y = self.attack_start_position.x, self.attack_start_position.y
        return attack_x, attack_y

    def draw(self, screen, x_pos, y_pos):
        if not self.alive:
            return    
        #If attacking use stored attack position
        if self.current_animation in ["Attack", "Attack Left"]:
            attack_x, attack_y = self.get_attack_position(screen)
            print(f"Drawing attack at {attack_x}, {attack_y}")
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (attack_x, attack_y))
                print(f"Drawing at scaled frames {attack_x}, {attack_y}")
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (x_pos, y_pos))
                print(f"Drawing at {x_pos}, {y_pos}")

    def switch_animation(self, animation_name, json_path):
        self.position = pygame.Vector2(self.position.x, self.position.y)
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

    #Gets player size(rect)
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

#Actual player class for this game
class Rogue(Entity):
    def __init__(self, json_path, x_pos=0, y_pos=0):
        super().__init__(json_path, PLAYER_RADIUS)
        self.image = pygame.image.load("Images/PNGs/Smaller rogue animations-Smaller Idle.png")
        self.current_animation = "Idle"
        self.health = 2000
        self.max_health = 2000
        self.attack = 250

        self.position = pygame.Vector2(x_pos, y_pos)
        self.attack_start_position = self.position.copy()

        #Initial frame size setup
        if self.scaled_frames:
            frame_surface = self.scaled_frames[self.current_frame][0]
            self.frame_width = frame_surface.get_width()
            self.frame_height = frame_surface.get_height()
        else:
            self.width = 32
            self.height = 48

        self.rect = pygame.Rect(self.position.x, self.position.y, self.frame_width, self.frame_height)

    def set_position(self, x, y):
        self.position.update(x, y)

    def get_position(self):
        return self.position.x, self.position.y

    def get_attack_position(self, screen):
        if self.current_animation == "Attack Left":
            attack_x = self.position.x - 50
        else:
            attack_x = self.position.x - 50

        attack_y = self.position.y + 80
        return attack_x, attack_y
    
    def handle_movement(self, keys, x_pos, y_pos, colliders, dt):
        new_x_pos = x_pos
        new_y_pos = y_pos
        movement_speed = PLAYER_SPEED
        self.is_moving = False

        #Lock position during attack
        if self.is_attacking:
            return x_pos, y_pos

        #Left
        if keys[pygame.K_a]:
            self.is_moving = True
            if self.current_animation != "Run Left" and not self.is_attacking:
                self.switch_animation("Run Left", "Images/PNGs/Small rogue animations-Small Run left.json")
            new_x_pos -= movement_speed * dt
    
        #Right
        elif keys[pygame.K_d]:
            self.is_moving = True
            if self.current_animation != "Run" and not self.is_attacking:
                self.switch_animation("Run", "Images/PNGs/Small rogue animations-Small Run.json")
            new_x_pos += movement_speed * dt

        #If not moving switch to idle
        if not self.is_moving and not self.is_attacking:
            if self.current_animation != "Idle":
                self.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")

        #Attack
        if keys[pygame.K_SPACE] and not self.is_attacking:
            self.is_attacking = True
            self.projectile_spawned = False
            self.attack_start_position = self.position.copy()
            if self.current_animation == "Run Left":
                self.switch_animation("Attack Left", "Images/PNGs/Small rogue animations-Small Attack Left-Attack Left.json")
            else:
                self.switch_animation("Attack", "Images/PNGs/Small rogue animations-Small Attack-Attack.json")

        #Get width and height of current frame
        if self.scaled_frames:
            frame_surface = self.scaled_frames[0][0]
            frame_width = frame_surface.get_width()
            frame_height = frame_surface.get_height()
        else:
            frame_width = 0
            frame_height = 0

        #Ensure frame width and frame height are numeric
        frame_width = int(frame_width) if frame_width else 0
        frame_height = int(frame_height) if frame_height else 0

        #Check collision
        if not self.check_collision(pygame.Rect(new_x_pos, y_pos, self.frame_width, self.frame_height), colliders):
            x_pos = new_x_pos
        if not self.check_collision(pygame.Rect(x_pos, new_y_pos, self.frame_width, self.frame_height), colliders):
            y_pos = new_y_pos
        else:
            print(f"Invalid frame dimensions: width={frame_width}, height={frame_height}")
        
        # Update actual position in the rogue object
        self.set_position(x_pos, y_pos)

        return x_pos, y_pos

    def heal(self, heal_amount):
        self.health += heal_amount
        #Cap health at max
        self.health = min(self.health, self.max_health)

    def spawn_projectiles(self, attack_x, attack_y):
        if not self.projectile_spawned and self.is_attacking:
            if self.current_animation in ["Attack", "Idle"]:
                velocity = pygame.Vector2(500, 0)
                proj_path = "Images/PNGs/Small rogue animations-Small Attack Projectile-Attack Projectile.json"
                projectile = Projectile(attack_x, attack_y, proj_path, velocity, max_distance=200, category="friendly")
                self.is_attacking = False
            elif self.current_animation == "Attack Left":
                velocity = pygame.Vector2(-500, 0)
                proj_path = "Images/PNGs/Small rogue animations-Small Attack Projectile Left-Attack Projectile Left.json"
                projectile = Projectile(attack_x - 400, attack_y, proj_path, velocity, max_distance=150, category="friendly")
                self.is_attacking = False
            self.projectiles.append(projectile)
            self.projectile_spawned = True

    def update(self, dt):
        super().update(dt)

        if self.is_attacking:
            attack_x, attack_y = self.get_attack_position(None)

            #Spawn projectiles at the 6th frame of the attack animation
            if self.current_frame == 5 and not self.projectile_spawned:
                self.spawn_projectiles(attack_x, attack_y)
            
            #End attack and allow movement after attack finishes
            if self.current_frame == len(self.scaled_frames) - 1:
                self.is_attacking = False
                self.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")

        #Update exisiting projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
            if not projectile.alive:
                self.projectiles.remove(projectile)

    def draw(self, screen, x_pos, y_pos):
        if self.is_dying:
            x_pos, y_pos = self.death_position

        if self.current_animation == "Damaged":
            x_pos, y_pos = self.position.x, self.position.y

        if not self.alive:
            return

        # If attacking, use stored attack position
        if self.current_animation in ["Attack", "Attack Left"]:
            attack_x, attack_y = self.get_attack_position(screen)
            print(f"Drawing attack at {attack_x}, {attack_y}")
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (attack_x, attack_y))
                print(f"Drawing at scaled frames {attack_x}, {attack_y}")
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (x_pos, y_pos))
                print(f"Drawing at {x_pos}, {y_pos}")

    def take_damage(self, damage_amount):
        self.switch_animation("Damaged", "Images/PNGs/Small rogue animations-Small Damaged.json")
        self.health -= damage_amount
        #Ensure health never goes below zero
        self.health = max(0, self.health)
        print(f"Rogue took damage at: {self.position}")
        if self.health == 0:
            print("Game over, better luck next time!")
            self.die("Death", "Images/PNGs/Rogue-Death.json")

#def cleanup(self):
    #if self in self.level.enemies:
        #self.level.enemies.remove(self)
