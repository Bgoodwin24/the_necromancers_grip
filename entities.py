from projectiles import Projectile, SpiritProjectile
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
        self.death_position = pygame.Vector2(self.position.x, self.position.y)
        self.damaged_position = pygame.Vector2(self.position.x, self.position.y)
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
        self.rect = None
        self.death_position = pygame.Vector2(self.position.x, self.position.y)
        if self.current_frame == len(self.scaled_frames) - 1:
            self.switch_animation(animation_name, json_path)
            self.is_dying = True
            self.alive = False
            print(f"Oh no! {self.__class__.__name__} has died!")

    def cleanup(self):
        pass

    def update(self, dt):
        if not self.alive:
            return

        if self.is_dying:
            if self.current_frame == len(self.scaled_frames) - 2:
                self.alive = False
            else:
                self.current_time += dt * 1000
                frame_duration = self.scaled_frames[self.current_frame][1]


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
                    if self.alive and not self.is_dying:
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
            
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (attack_x, attack_y))
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (x_pos, y_pos))
                

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
        self.attack = 125
        self.is_rogue = True
        self.is_damaged = False
        self.is_invincible = False
        self.has_played_damaged_animation = False

        self.position = pygame.Vector2(x_pos, y_pos)
        self.attack_start_position = self.position.copy()

        # Initial frame size setup
        if self.scaled_frames:
            frame_surface = self.scaled_frames[self.current_frame][0]
            self.frame_width = frame_surface.get_width()
            self.frame_height = frame_surface.get_height()
        else:
            self.width = 32
            self.height = 48

        self.rect = pygame.Rect(self.position.x, self.position.y, self.frame_width, self.frame_height)
        self.category = "friendly"
        self.invincibility_timer = 0

    def set_position(self, x, y):
        self.position.update(x, y)

    def get_position(self):
        return self.position.x, self.position.y

    def get_attack_position(self, screen):
        if self.current_animation == "Attack Left":
            attack_x = self.position.x
        else:
            attack_x = self.position.x

        attack_y = self.position.y + 80
        return attack_x, attack_y

    def handle_movement(self, keys, x_pos, y_pos, colliders, dt):
        self.attack_cooldown = 0.5
        new_x_pos = x_pos
        new_y_pos = y_pos
        movement_speed = PLAYER_SPEED
        self.is_moving = False
        self.attack_cooldown -= dt

        # Lock position during attack or damaged state
        if self.is_damaged:
            return x_pos, y_pos
        
        # Lock position during attack state
        if self.is_attacking:
            return x_pos, y_pos

        # Left movement
        if keys[pygame.K_a]:
            self.is_moving = True
            if self.alive:
                if self.current_animation != "Run Left" and not self.is_attacking:
                    self.switch_animation("Run Left", "Images/PNGs/Small rogue animations-Small Run left.json")
                new_x_pos -= movement_speed * dt
    
        # Right movement
        if keys[pygame.K_d]:
            self.is_moving = True
            if self.alive:
                if self.current_animation != "Run" and not self.is_attacking:
                    self.switch_animation("Run", "Images/PNGs/Small rogue animations-Small Run.json")
                new_x_pos += movement_speed * dt

        # Switch to idle if not moving
        if self.alive and not self.is_dying:
            if not self.is_moving and not self.is_attacking and not self.is_damaged:
                if self.current_animation != "Idle":
                    self.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")

        # Handle attack logic
        if keys[pygame.K_SPACE] and self.attack_cooldown <= 0 and not self.is_attacking:
            self.is_attacking = True
            self.projectile_spawned = False
            self.attack_start_position = self.position.copy()
            if self.current_animation == "Run Left":
                self.switch_animation("Attack Left", "Images/PNGs/Small projectile-Attack Left.json")
            else:
                self.switch_animation("Attack", "Images/PNGs/Small projectile-Attack.json")
            self.attack_cooldown = 0.5

        # Check collision
        if not self.check_collision(pygame.Rect(new_x_pos, y_pos, self.frame_width, self.frame_height), colliders):
            x_pos = new_x_pos
        if not self.check_collision(pygame.Rect(x_pos, new_y_pos, self.frame_width, self.frame_height), colliders):
            y_pos = new_y_pos

        # Update actual position in the rogue object
        self.set_position(x_pos, y_pos)

        return x_pos, y_pos

    def heal(self, heal_amount):
        self.health += heal_amount
        self.health = min(self.health, self.max_health)

    def spawn_projectiles(self, attack_x, attack_y):
        if not self.projectile_spawned and self.is_attacking:
            if self.current_animation in ["Attack", "Idle"] and self.alive:
                velocity = pygame.Vector2(500, 0)
                proj_path = "Images/PNGs/Small projectile-Attack.json"
                projectile = Projectile(attack_x + 70, attack_y, proj_path, velocity, max_distance=200, category="friendly")
                self.alive = True
                self.projectiles.append(projectile)
                self.is_attacking = False
            elif self.current_animation == "Attack Left":
                velocity = pygame.Vector2(-500, 0)
                proj_path = "Images/PNGs/Small projectile-Attack Left.json"
                projectile = Projectile(attack_x - 120, attack_y, proj_path, velocity, max_distance=200, category="friendly")
                self.alive = True
                self.projectiles.append(projectile)
                self.is_attacking = False
            self.projectile_spawned = True

    def update(self, dt):
        super().update(dt)

        if self.is_invincible:
            self.invincibility_timer += dt
            if self.invincibility_timer > 3:
                self.is_invincible = False
                self.invincibility_timer = 0

        # Death animation trigger
        if self.health == 0 and not self.is_dying:
            self.is_dying = True
            self.current_frame = 0
            self.death_position = self.position.x - 100, self.position.y - 20
            self.switch_animation("Death", "Images/PNGs/Rogue-Death.json")

        # Handle death animation progression (Stop after last frame)
        if self.is_dying:
            if self.current_frame >= len(self.scaled_frames) - 1:
                self.alive = False
            else:
                self.current_frame += 1
            return  # Stop animation progress for death animation

        # Handle damaged animation
        if self.is_damaged and not self.is_dying:
            if not self.has_played_damaged_animation:
                self.has_played_damaged_animation = True
                self.switch_animation("Damaged", "Images/PNGs/Small rogue animations-Small Damaged.json")

            if self.current_frame >= len(self.scaled_frames) - 1:
                self.is_damaged = False  # Unlock damaged state
                self.has_played_damaged_animation = False

                # Switch back to idle only after animation finishes
                if not self.is_attacking and not self.is_moving:
                    self.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")
                elif self.is_moving:
                    self.switch_animation("Run", "Images/PNGs/Small rogue animations-Small Run.json")
                elif self.is_attacking:
                    self.switch_animation("Attack", "Images/PNGs/Small rogue animations-Small Attack.json")

        # Handle attack logic and reset after attack
        if self.is_attacking and not self.is_dying:
            if self.current_frame == 5 and not self.projectile_spawned:
                attack_x, attack_y = self.get_attack_position(None)
                self.spawn_projectiles(attack_x, attack_y)
            elif self.current_frame >= len(self.scaled_frames) - 1:
                self.is_attacking = False
                self.projectile_spawned = False
                if self.is_moving:
                    self.switch_animation("Run", "Images/PNGs/Small rogue animations-Small Run.json")
                else:
                    self.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")

        # Regular animation logic for other states
        if self.current_frame >= len(self.scaled_frames):
            if self.current_animation != "Damaged" and not self.is_dying:
                self.current_frame = 0

        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
            if not projectile.alive:
                self.projectiles.remove(projectile)

    def draw(self, screen, x_pos, y_pos):
        if self.is_dying:
            x_pos, y_pos = self.death_position

        if self.current_animation == "Damaged":
            x_pos, y_pos = self.position.x - 50, self.position.y

        if not self.alive:
            return

        if self.current_animation in ["Attack", "Attack Left"]:
            attack_x, attack_y = self.get_attack_position(screen)
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (attack_x, attack_y))
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (x_pos, y_pos))

    def take_damage(self, damage_amount):
        if not self.is_invincible:
            self.is_damaged = True
            self.is_invincible = True
            self.invincibility_timer = 0
            self.current_frame = 0
        self.health -= damage_amount
        self.health = max(0, self.health)
        print(f"Rogue took {damage_amount} damage. Health: {self.health}")
        if self.health == 0:
            print("Game over, better luck next time!")

    def get_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.frame_width, self.frame_height)

class Skeleton(Entity):
    def __init__(self, json_path, x_pos=0, y_pos=0):
        super().__init__(json_path, PLAYER_RADIUS)
        self.image = pygame.image.load("Images/PNGs/Skeleton-Idle.png")
        self.current_animation = "Idle"
        self.health = 1000
        self.max_health = 1000
        self.attack = 500
        self.is_skeleton = True
        self.is_dying = False
        self.ground_y = + 652
        self.facing_direction = "Left"
        self.is_attacking = False
        self.damage_applied = False
        self.damage_pending = False
        self.is_damaged = False
        self.is_invincible = False
        self.position = pygame.Vector2(x_pos, y_pos)
        self.attack_start_position = self.position.copy()

        #Initial frame size setup
        if self.scaled_frames:
            frame_surface = self.scaled_frames[self.current_frame][0]
            self.frame_width = frame_surface.get_width()
            self.frame_height = frame_surface.get_height()
        else:
            self.width = 64
            self.height = 64
        
        self.rect = self.get_rect()

    def get_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.scaled_frames[0][0].get_width(), self.scaled_frames[0][0].get_height())

    def set_position(self, x, y):
        self.position.update(x, y)

    def get_position(self):
        return self.position.x, self.position.y

    def get_attack_position(self, screen):
        if self.facing_direction == "Right":
            attack_x = self.position.x + 50
        else:
            attack_x = self.position.x - 50

        attack_y = self.position.y + 80
        return attack_x, attack_y

    def update(self, dt):
        super().update(dt)
        if not self.alive:
            return
        
        if self.is_invincible:
            self.invincibility_timer += dt
            if self.invincibility_timer > 2:
                self.is_invincible = False
                self.invincibility_timer = 0
        
        self.rect = self.get_rect()
        self.position.y = self.ground_y

        if self.health == 0:
            if not self.is_dying:
                self.is_dying = True
                self.switch_animation("Death", "Images/PNGs/Skeleton-Death.json")
                if self.current_frame == len(self.scaled_frames) - 1:
                    self.die("Death", "Images/PNGs/Skeleton-Death.json")
            return

        if self.damage_pending:
            if self.facing_direction == "Left" and self.current_frame == len(self.scaled_frames) - 1:
                self.switch_animation("Walk", "Images/PNGs/Skeleton Walk Right-Walk Left.json")
                self.damage_pending = False
            elif self.facing_direction == "Right" and self.current_frame == len(self.scaled_frames) - 1:
                self.switch_animation("Walk Right", "Images/PNGs/Skeleton Walk Right-Walk Right.json")
                self.damage_pending = False
    
    def draw(self, screen, x_pos, y_pos):
        if not self.alive:
            return
        
        if self.is_dying:
            x_pos, y_pos = self.death_position

        if self.current_animation == "Damaged":
            self.position.x + 10
            self.position.y += 75
            frame_surface, _ = self.scaled_frames[self.current_frame]

        elif self.current_animation == "Damaged Right":
            self.position.x + 10
            self.position.y += 75
            frame_surface, _ = self.scaled_frames[self.current_frame]

        # If attacking, use stored attack position
        if self.current_animation in ["Attack", "Attack Right"]:
            self.position.x + 90
            self.position.y - 75
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (self.position.x, self.position.y))
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (self.position.x, self.position.y))

    def take_damage(self, damage_amount):
        if not self.is_invincible:
            self.is_damaged = True
            self.is_invincible = True
            self.invincibility_timer = 0
            self.current_frame = 0
        self.health -= damage_amount
        # Ensure health never goes below zero
        self.health = max(0, self.health)
        
        if self.health > 0:
            # Switch to damaged animation if still alive
            if self.facing_direction == "Left" and self.current_animation != "Damaged":
                self.switch_animation("Damaged", "Images/PNGs/Small Skeleton-Damaged.json")
            elif self.facing_direction == "Right" and self.current_animation != "Damaged Right":
                self.switch_animation("Damaged Right", "Images/PNGs/Small Skeleton-Damaged Right.json")
            
            self.damage_pending = True
        else:
            # If health is zero, immediately switch to the death animation
            if self.current_animation != "Death" and not self.is_dying:
                self.is_dying = True
                self.switch_animation("Death", "Images/PNGs/Skeleton-Death.json")
                print("Skeleton has died, starting death animation.")
        if self.is_attacking:
            self.damage_pending = True

    def handle_movement(self, keys, x_pos, y_pos, colliders, dt):
        if not self.alive:
            return

        if self.current_animation == "Damaged":
            return x_pos, y_pos
        
        #handle x,y for run and run left
        new_x_pos, new_y_pos = x_pos, y_pos
        movement_speed = PLAYER_SPEED
        self.is_moving = False

        #Lock position during attack
        if self.is_attacking:
            return x_pos, y_pos

        #Attack
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_start_position = self.position.copy()
            if self.current_animation == "Walk":
                self.switch_animation("Attack", "Images/PNGs/Skeleton Walk Right-Attack.json")
            elif self.current_animation == "Walk Right":
                self.facing_direction = "Right"
                self.switch_animation("Attack Right", "Images/PNGs/Skeleton Walk Right-Attack Right.json")

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
        
        # Update actual position in the skeleton object
        self.set_position(x_pos, y_pos)

        return x_pos, y_pos
    
    def handle_ai(self, player, player_position, dt, player_rect):
        if not self.alive:
            return

        self.rect = self.get_rect()

        if self.current_animation in ["Death", "Damaged"]:
            self.death_position = self.position
            return
        
        distance = self.position.x - player_position.x
        attack_range = 80

        if not player.alive or player.current_animation == "Death" or player.is_dying:
            self.is_attacking = False
            self.switch_animation("Idle", "Images/PNGs/Skeleton-Idle.json")
            print(f"Rogue is dead, Skeleton switching to {self.current_animation}, {self.current_frame}/{len(self.scaled_frames) - 1}")
        
        #Stop from walking through player
        if abs(distance) <= attack_range:
            if not self.is_attacking:
                self.is_attacking = True
                if distance > 0:
                    self.facing_direction = "Left"
                    if self.current_animation != "Attack":
                        self.switch_animation("Attack", "Images/PNGs/Skeleton Walk Right-Attack.json")
                else:
                    self.facing_direction = "Right"
                    if self.current_animation != "Attack Right":
                        self.switch_animation("Attack Right", "Images/PNGs/Skeleton Walk Right-Attack Right.json")
            return

        #Reset attack if out of range or animation is done
        if self.is_attacking and self.current_frame == len(self.scaled_frames) - 1:
            if self.current_animation in ["Attack", "Attack Right"] and self.current_frame == len(self.scaled_frames) - 1:
                self.is_attacking = False
                self.switch_animation("Idle", "Images/PNGs/Skeleton-Idle.json")

        #Movement
        if distance > 0:
            if abs(distance) > attack_range:
                if self.current_animation != "Walk Left":
                    self.switch_animation("Walk Left", "Images/PNGs/Skeleton Walk Right-Walk Left.json")
                self.position.x -= ENEMY_SPEED * dt
        elif distance < 0:
            if abs(distance) > attack_range - 20:
                if self.current_animation != "Walk Right":
                    self.switch_animation("Walk Right", "Images/PNGs/Skeleton Walk Right-Walk Right.json")
                self.position.x += ENEMY_SPEED * dt
                
    #def cleanup(self):
        #if self in self.level.enemies:
            #self.level.enemies.remove(self)

class Spirit(Entity):
    def __init__(self, json_path, x_pos=0, y_pos=0):
        super().__init__(json_path, PLAYER_RADIUS)
        self.image = pygame.image.load("Images/PNGs/Small Spirit-Idle.png")
        self.current_animation = "Idle"
        self.health = 1500
        self.max_health = 1500
        self.attack = 500
        self.is_spirit = True
        self.is_dying = False
        self.ground_y = + 475
        self.facing_direction = "Left"
        self.is_attacking = False
        self.damage_applied = False
        self.damage_pending = False
        self.is_damaged = False
        self.is_invincible = False
        self.position = pygame.Vector2(x_pos, y_pos)
        self.attack_start_position = self.position.copy()
        self.category = "enemy"

        #Initial frame size setup
        if self.scaled_frames:
            frame_surface = self.scaled_frames[self.current_frame][0]
            self.frame_width = frame_surface.get_width()
            self.frame_height = frame_surface.get_height()
        else:
            self.width = 64
            self.height = 64
        
        self.rect = self.get_rect()

    def get_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.scaled_frames[0][0].get_width(), self.scaled_frames[0][0].get_height())

    def set_position(self, x, y):
        self.position.update(x, y)

    def get_position(self):
        return self.position.x, self.position.y
    
    def get_attack_position(self, screen):
        if self.facing_direction == "Right":
            attack_x = self.position.x + 50
        else:
            attack_x = self.position.x - 50

        attack_y = self.position.y + 80
        return attack_x, attack_y

    def update(self, dt):
        super().update(dt)
        if not self.alive:
            return
        
        if self.is_invincible:
            self.invincibility_timer += dt
            if self.invincibility_timer > 2:
                self.is_invincible = False
                self.invincibility_timer = 0
        
        self.rect = self.get_rect()
        self.position.y = self.ground_y

        if self.health == 0:
            self.position.y += 55
            if not self.is_dying:
                self.is_dying = True
                self.switch_animation("Death", "Images/PNGs/Small Spirit-Death.json")
                if self.current_frame == len(self.scaled_frames) - 1:
                    self.die("Death", "Images/PNGs/Small Spirit-Death.json")
            return
        
        # Handle attack logic and reset after attack
        if self.is_attacking:
            if self.current_frame == 4 and not self.projectile_spawned:
                attack_x, attack_y = self.get_attack_position(None)
                self.spawn_projectiles(attack_x, attack_y)
            elif self.current_frame >= len(self.scaled_frames) - 1:
                self.is_attacking = False
                self.switch_animation("Idle", "Images/PNGs/Small Spirit-Idle.json")
        
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(dt)
            print(f"Projectile at ({projectile.get_rect})")
            if not projectile.alive:
                self.projectiles.remove(projectile)

        if self.damage_pending:
            if self.facing_direction == "Left" and self.current_frame == len(self.scaled_frames) - 1:
                self.switch_animation("Walk", "Images/PNGs/Small Spirit-Idle.json")
                self.damage_pending = False
            elif self.facing_direction == "Right" and self.current_frame == len(self.scaled_frames) - 1:
                self.switch_animation("Walk Right", "Images/PNGs/Small Spirit-Idle Right.json")
                self.damage_pending = False
    
    def draw(self, screen, x_pos, y_pos):
        if not self.alive:
            return
        
        if self.is_dying:
            x_pos, y_pos = self.death_position

        for projectile in self.projectiles:
            projectile.draw(screen)

        if self.current_animation == "Damaged":
            self.position.x + 10
            self.position.y 
            frame_surface, _ = self.scaled_frames[self.current_frame]

        elif self.current_animation == "Damaged Right":
            self.position.x + 10
            self.position.y
            frame_surface, _ = self.scaled_frames[self.current_frame]

        # If attacking, use stored attack position
        if self.current_animation in ["Attack", "Attack Right"]:
            self.position.x + 90
            self.position.y - 75
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (self.position.x, self.position.y))
        else:
            if self.scaled_frames:
                frame_surface, _ = self.scaled_frames[self.current_frame]
                screen.blit(frame_surface, (self.position.x, self.position.y))

    def take_damage(self, damage_amount):
        if not self.is_invincible:
            self.is_damaged = True
            self.is_invincible = True
            self.invincibility_timer = 0
            self.current_frame = 0
        self.health -= damage_amount
        # Ensure health never goes below zero
        self.health = max(0, self.health)
        
        if self.health > 0:
            # Switch to damaged animation if still alive
            if self.facing_direction == "Left" and self.current_animation != "Damaged":
                self.switch_animation("Damaged", "Images/PNGs/Small Spirit-Damaged.json")
            elif self.facing_direction == "Right" and self.current_animation != "Damaged Right":
                self.switch_animation("Damaged Right", "Images/PNGs/Small Spirit-Damaged Right.json")
            
            self.damage_pending = True
        else:
            # If health is zero, immediately switch to the death animation
            if self.current_animation != "Death" and not self.is_dying:
                self.is_dying = True
                self.switch_animation("Death", "Images/PNGs/Small Spirit-Death.json")
                print("Skeleton has died, starting death animation.")
        if self.is_attacking:
            self.damage_pending = True

    def handle_movement(self, keys, x_pos, y_pos, colliders, dt):
        if not self.alive:
            return

        if self.current_animation == "Damaged":
            return x_pos, y_pos
        
        #handle x,y for run and run left
        new_x_pos, new_y_pos = x_pos, y_pos
        movement_speed = PLAYER_SPEED
        self.is_moving = False

        #Lock position during attack
        if self.is_attacking:
            return x_pos, y_pos

        #Attack
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_start_position = self.position.copy()
            if self.current_animation == "Walk":
                self.switch_animation("Attack", "Images/PNGs/Small Spirit-Attack.json")
            elif self.current_animation == "Walk Right":
                self.facing_direction = "Right"
                self.switch_animation("Attack Right", "Images/PNGs/Small Spirit-Attack Right.json")

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
        
        # Update actual position in the spirit object
        self.set_position(x_pos, y_pos)

        return x_pos, y_pos

    def spawn_projectiles(self, attack_x, attack_y):
        if not self.projectile_spawned and self.is_attacking:
            if self.current_animation in ["Attack", "Idle"] and self.alive:
                velocity = pygame.Vector2(-500, 0)
                proj_path = "Images/PNGs/Small Spirit Projectile-Projectile.json"
                projectile = SpiritProjectile(attack_x - 150, attack_y + 170, proj_path, velocity, max_distance=350, category="enemy")
                self.alive = True
                self.projectiles.append(projectile)
                self.projectile_spawned = True
                print(f"Spawned projectile at ({projectile.get_rect}) with velocity {velocity}")
            elif self.current_animation == "Attack Right":
                velocity = pygame.Vector2(500, 0)
                proj_path = "Images/PNGs/Small Spirit Projectile-Projectile Right.json"
                projectile = SpiritProjectile(attack_x + 160, attack_y + 170, proj_path, velocity, max_distance=350, category="enemy")
                self.alive = True
                self.projectiles.append(projectile)
                self.projectile_spawned = True
                print(f"Spawned projectile right at ({projectile.get_rect}) with velocity {velocity}")

            self.projectile_spawned = False
            if not self.is_attacking:
                self.projectile_spawned = False

    def handle_ai(self, player, player_position, dt, player_rect):
        if not self.alive:
            return
            
        self.rect = self.get_rect()

        if self.current_animation in ["Death", "Damaged"]:
            self.death_position = self.position
            return
            
        distance = self.position.x - player_position.x
        attack_range = 500

        if not player.alive or player.current_animation == "Death" or player.is_dying:
            self.is_attacking = False
            self.switch_animation("Idle", "Images/PNGs/Small Spirit-Idle.json")
            print(f"Rogue is dead, Spirit switching to {self.current_animation}, {self.current_frame}/{len(self.scaled_frames) - 1}")
            
        #Stop from walking through player
        if abs(distance) <= attack_range:
            if not self.is_attacking:
                self.is_attacking = True
                if distance > 0:
                    self.facing_direction = "Left"
                    if self.current_animation != "Attack":
                        self.switch_animation("Attack", "Images/PNGs/Small Spirit-Attack.json")
                        if self.current_frame == len(self.scaled_frames) - 1:
                            self.spawn_projectiles(self.position.x, self.position.y)
                else:
                    self.facing_direction = "Right"
                    if self.current_animation != "Attack Right":
                        self.switch_animation("Attack Right", "Images/PNGs/Small Spirit-Attack Right.json")
                        if self.current_frame == len(self.scaled_frames) - 1:
                            self.spawn_projectiles(self.position.x, self.position.y)
            return

        #Reset attack if out of range or animation is done
        if self.is_attacking and self.current_frame == len(self.scaled_frames) - 1:
            if self.current_animation in ["Attack", "Attack Right"] and self.current_frame == len(self.scaled_frames) - 1:
                self.is_attacking = False
                self.switch_animation("Idle", "Images/PNGs/Small Spirit-Idle.json")

        #Movement
        if distance > 0:
            if abs(distance) > attack_range:
                if self.current_animation != "Walk Left":
                    self.switch_animation("Walk Left", "Images/PNGs/Small Spirit-Idle.json")
                self.position.x -= ENEMY_SPEED * dt
        elif distance < 0:
            if abs(distance) > attack_range - 20:
                if self.current_animation != "Walk Right":
                    self.switch_animation("Walk Right", "Images/PNGs/Small Spirit-Idle Right.json")
                self.position.x += ENEMY_SPEED * dt
        
    #def cleanup(self):
        #if self in self.level.enemies:
            #self.level.enemies.remove(self)
