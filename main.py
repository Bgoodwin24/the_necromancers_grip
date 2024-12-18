import pygame
import os
import sys
from entities import *
from level import *
import json
from items import *
from constants import *
from projectiles import *
from healthbars import *

def main():
    pygame.init()

    #Set screen/window caption/clock
    screen = pygame.display.set_mode((SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
    pygame.display.set_caption("The Necromancers Grip")
    clock = pygame.time.Clock()

    #Background files
    background1 = pygame.image.load("Images/PNGs/Graveyard Background No Repeat.png")
    background2 = pygame.image.load("Images/PNGs/Graveyard Background.png")

    #Levels
    start_level = Level()
    second_level = Level()
    last_level = Level()
    all_levels = [
        start_level,
        second_level,
        last_level,
    ]
    current_level = start_level
    
    #Colliders
    left_wall = pygame.Rect(-5, 0, 5, SCREEN_HEIGHT * 3)
    ground = pygame.Rect(0, SCREEN_HEIGHT * 3 - 175, SCREEN_WIDTH * 3, 5)
    right_wall = RightWall(current_level)

    colliders = {
        "left_wall": left_wall,
        "right_wall": right_wall.rect,
        "ground": ground
    }

    #Load entities
    rogue = Rogue("Images/PNGs/Smaller rogue animations-Smaller Idle.json")
    skeleton = Skeleton("Images/PNGs/Skeleton-Idle.json")
    skeleton2 = Skeleton("Images/PNGs/Skeleton-Idle.json")
    spirit = Spirit("Images/PNGs/Small Spirit-Idle.json")
    arrow = Arrow("Images/PNGs/Next Level Arrow-Next Level.json")
    end_text = EndText("Images/PNGs/End Text-Exit Text.json")

    #Load healthbars
    rogue_bar = HealthBar("Images/PNGs/Health Bar-Base Bar.json", rogue)
    skeleton_bar = HealthBar("Images/PNGs/Skeleton Health Bar-Skelton Base Bar.json", skeleton)
    skeleton2_bar = HealthBar("Images/PNGs/Skeleton Health Bar-Skelton Base Bar.json", skeleton2)
    spirit_bar = HealthBar("Images/PNGs/Boss Health Bar-Boss Base Bar.json", spirit)

    all_bars = [
        rogue_bar,
        skeleton_bar,
        skeleton2_bar,
        spirit_bar,
    ]

    #Enemy list
    spawn_timer = None

    def initialize_enemy_list(level):
        if level == start_level:
            return [skeleton]
        elif level == second_level:
            return [skeleton, skeleton2]
        elif level == last_level:
            return [skeleton, skeleton2, spirit]
        else:
            return []

    #Initial position
    if rogue.scaled_frames:
        rogue.x_pos = (SCREEN_WIDTH * 3 - rogue.scaled_frames[0][0].get_width()) // 2 - 870
        rogue.y_pos = (SCREEN_HEIGHT * 3 - rogue.scaled_frames[0][0].get_height()) // 2 + 198
    else:
        print("Warning: scaled_frames not initialized.")

    if skeleton.scaled_frames:
        skeleton.position.x = (SCREEN_WIDTH * 3 - skeleton.scaled_frames[0][0].get_width()) // 2 + 200
        skeleton.position.y = (SCREEN_HEIGHT * 3 - skeleton.scaled_frames[0][0].get_height()) // 2 + 240
    else:
        print("Warning: scaled_frames not initialized.")

    if skeleton2.scaled_frames:
        skeleton2.position.x = (SCREEN_WIDTH * 3 - skeleton2.scaled_frames[0][0].get_width()) // 2 + 500
        skeleton2.position.y = (SCREEN_HEIGHT * 3 - skeleton2.scaled_frames[0][0].get_height()) // 2 + 240
    else:
        print("Warning: scaled_frames not initialized.")

    if spirit.scaled_frames:
        spirit.x_pos = (SCREEN_WIDTH * 3 - spirit.scaled_frames[0][0].get_width()) // 2 + 925
        spirit.position.x += 1550
        spirit.y_pos = (SCREEN_HEIGHT * 3 - spirit.scaled_frames[0][0].get_height()) // 2 + 240
    else:
        print("Warning: scaled_frames not initialized.")

    if arrow.scaled_frames:
        arrow.position.x = (SCREEN_WIDTH * 3 - arrow.scaled_frames[0][0].get_width()) // 2
        arrow.position.y = (SCREEN_HEIGHT * 3 - arrow.scaled_frames[0][0].get_height()) // 2
    else:
        print("Warning: scaled_frames not initialized.")

    #Health bars
    def advanced_rogue_health(self):
        transition_width = 0
        transition_color = (222, 0, 0)

        #Stop target health exceeding player health
        if rogue.target_health >= rogue.max_health:
            rogue.target_health = rogue.max_health
        
        #Healing leading bar trail
        if rogue.health < rogue.target_health:
            previous_health = rogue.health
            rogue.health += rogue.health_change_speed
            if rogue.health > rogue.target_health:
                rogue.health = rogue.target_health
            transition_width = int((rogue.target_health - previous_health) / rogue.health_ratio) - 5
            transition_color = (73, 176, 0)

        #Damage leading bar trail
        elif rogue.health > rogue.target_health:
            if rogue.target_health >= rogue.max_health:
                rogue.target_health = rogue.max_health
            previous_health = rogue.health
            rogue.health -= rogue.health_change_speed
            transition_width = int((previous_health - rogue.target_health) / rogue.health_ratio)
            transition_color = (166, 0, 0)
        
        #Assign bars
        rogue_bar_rect = pygame.Rect(112, 947, rogue.health / rogue.health_ratio, 28)

        #Start transition bar at appropriate position based on healing or damage
        if transition_color == (73, 176, 0):  #Healing
            transition_bar_start = rogue_bar_rect.right
            rogue_transition_bar_rect = pygame.Rect(transition_bar_start, 947, transition_width, 28)
            pygame.draw.rect(screen, (106, 190, 48), rogue_bar_rect)
            pygame.draw.rect(screen, transition_color, rogue_transition_bar_rect)
        else:
            transition_bar_start = rogue_bar_rect.right - transition_width
            rogue_transition_bar_rect = pygame.Rect(transition_bar_start, 947, transition_width, 28)
            pygame.draw.rect(screen, (106, 190, 48), rogue_bar_rect)
            pygame.draw.rect(screen, transition_color, rogue_transition_bar_rect)

        #Draw bars
        pygame.draw.rect(screen, (106, 190, 48), rogue_bar_rect)
        pygame.draw.rect(screen, transition_color, rogue_transition_bar_rect)

    def advanced_skeleton_health(self):
        transition_width = 0
        transition_color = (222, 0, 0)

        #Stop target health exceeding player health
        if skeleton.target_health >= skeleton.max_health:
            skeleton.target_health = skeleton.max_health
        
        #Healing leading bar trail
        if skeleton.health < skeleton.target_health and skeleton.summoning:
            previous_health = skeleton.health
            skeleton.health += skeleton.health_change_speed
            if skeleton.health > skeleton.target_health:
                skeleton.health = skeleton.target_health
            transition_width = int((skeleton.target_health - previous_health) / skeleton.health_ratio) - 5
            transition_color = (73, 176, 0)

        #Damage leading bar trail
        elif skeleton.health > skeleton.target_health:
            if skeleton.target_health >= skeleton.max_health:
                skeleton.target_health = skeleton.max_health
            previous_health = skeleton.health
            skeleton.health -= skeleton.health_change_speed
            transition_width = int((previous_health - skeleton.target_health) / skeleton.health_ratio)
            transition_color = (166, 0, 0)
        
        #Assign bars
        skeleton_bar_rect = pygame.Rect(1512, 1027, skeleton.health / skeleton.health_ratio, 28)

        #Start transition bar at appropriate position based on healing or damage
        if transition_color == (73, 176, 0):  #Healing
            transition_bar_start = skeleton_bar_rect.right
            skeleton_transition_bar_rect = pygame.Rect(transition_bar_start, 1027, transition_width, 28)
            pygame.draw.rect(screen, (106, 190, 48), skeleton_bar_rect)
            pygame.draw.rect(screen, transition_color, skeleton_transition_bar_rect)
        else:
            transition_bar_start = skeleton_bar_rect.right - transition_width
            skeleton_transition_bar_rect = pygame.Rect(transition_bar_start, 1027, transition_width, 28)
            pygame.draw.rect(screen, (106, 190, 48), skeleton_bar_rect)
            pygame.draw.rect(screen, transition_color, skeleton_transition_bar_rect)

        #Draw bars
        pygame.draw.rect(screen, (106, 190, 48), skeleton_bar_rect)
        pygame.draw.rect(screen, transition_color, skeleton_transition_bar_rect)

    def advanced_skeleton2_health(self):
        transition_width = 0
        transition_color = (222, 0, 0)

        #Stop target health exceeding player health
        if skeleton2.target_health >= skeleton2.max_health:
            skeleton2.target_health = skeleton2.max_health

        #Damage leading bar trail
        elif skeleton2.health > skeleton2.target_health:
            if skeleton2.target_health >= skeleton2.max_health:
                skeleton2.target_health = skeleton2.max_health
            previous_health = skeleton2.health
            skeleton2.health -= skeleton2.health_change_speed
            transition_width = int((previous_health - skeleton2.target_health) / skeleton2.health_ratio)
            transition_color = (166, 0, 0)
        
        #Assign bars
        skeleton2_bar_rect = pygame.Rect(1012, 1027, skeleton2.health / skeleton2.health_ratio, 28)

        #Start transition bar at appropriate position based on damage
        transition_bar_start = skeleton2_bar_rect.right - transition_width
        skeleton2_transition_bar_rect = pygame.Rect(transition_bar_start, 1027, transition_width, 28)

        #Draw bars
        pygame.draw.rect(screen, (106, 190, 48), skeleton2_bar_rect)
        pygame.draw.rect(screen, transition_color, skeleton2_transition_bar_rect)

    def advanced_spirit_health(self):
        transition_width = 0
        transition_color = (222, 0, 0)

        #Stop target health exceeding player health
        if spirit.target_health >= spirit.max_health:
            spirit.target_health = spirit.max_health

        #Damage leading bar trail
        elif spirit.health > spirit.target_health:
            if spirit.target_health >= spirit.max_health:
                spirit.target_health = spirit.max_health
            previous_health = spirit.health
            spirit.health -= spirit.health_change_speed
            transition_width = int((previous_health - spirit.target_health) / spirit.health_ratio)
            transition_color = (166, 0, 0)
        
        #Assign bars
        spirit_bar_rect = pygame.Rect(1512, 947, spirit.health / spirit.health_ratio, 28)

        #Start transition bar at appropriate position based on damage
        transition_bar_start = spirit_bar_rect.right - transition_width
        spirit_transition_bar_rect = pygame.Rect(transition_bar_start, 947, transition_width, 28)

        #Draw bars
        pygame.draw.rect(screen, (106, 190, 48), spirit_bar_rect)
        pygame.draw.rect(screen, transition_color, spirit_transition_bar_rect)

    #Game loop
    run = True

    transitioning = False
    transition_timer = None

    enemy_list = initialize_enemy_list(current_level)

    while run:

        #Fps control
        dt = clock.tick(60) / 1000.0

        #Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not rogue.is_attacking:
                    rogue.is_attacking = True
                    rogue.projectile_spawned = False
                    if rogue.current_animation == "Run Left":
                        rogue.switch_animation("Attack Left", "Images/PNGs/Small rogue animations-Small Attack Left-Attack Left.json")
                    else:
                        rogue.switch_animation("Attack", "Images/PNGs/Small rogue animations-Small Attack-Attack.json")
                if current_level == last_level and event.key == pygame.K_ESCAPE and len(enemy_list) == 0:
                    pygame.quit()
                    sys.exit()
        
        #Clear screen
        screen.fill((0, 0, 0))

        #Draw levels
        if current_level == start_level:
            current_level.draw_level(screen, background1)
        if current_level == second_level:
            current_level.draw_level(screen, background1)
        if current_level == last_level:
            current_level.draw_level(screen, background2)

        #Movement input
        keys = pygame.key.get_pressed()

        #Update player postion and rect
        rogue.x_pos, rogue.y_pos = rogue.handle_movement(keys, rogue.x_pos, rogue.y_pos, colliders, dt)
        rogue.rect = pygame.Rect(rogue.x_pos, rogue.y_pos, rogue.scaled_frames[0][0].get_width() + 20, rogue.scaled_frames[0][0].get_height())
        #Update skeleton rect after its position has been set
        skeleton.rect = pygame.Rect(skeleton.position.x, skeleton.position.y, skeleton.scaled_frames[0][0].get_width(), skeleton.scaled_frames[0][0].get_height())
        spirit.rect = pygame.Rect(spirit.position.x, spirit.position.y, spirit.scaled_frames[0][0].get_width(), spirit.scaled_frames[0][0].get_height())

        #Conditional food spawns
        if rogue.health <= 1000:
            current_level.spawn_food_items(screen, rogue, Items, 500, 764)

        #Handle collision based on category
        def check_collision(projectile, target):
            if not projectile.alive:
                return False
            
            projectile_rect =  projectile.rect = pygame.Rect(projectile.position.x, projectile.position.y, projectile.scaled_frames[0][0].get_width(), projectile.scaled_frames[0][0].get_height())
            if projectile.category == "friendly":
                    if hasattr(target, 'rect') and target.rect:
                        if hasattr(target, 'is_rogue') and target.is_rogue and target.alive and target.rect.colliderect(projectile_rect):
                            return False
                        if target.is_dying:
                            return
                        if hasattr(target, 'is_skeleton') and target.is_skeleton and target.alive and target.rect.colliderect(projectile_rect):
                            if not projectile.damage_applied:
                                skeleton.take_damage(rogue.attack)
                                projectile.damage_applied = True
                            if not projectile.playing_collision_animation:
                                projectile.switch_attack_animation()
                            return True
                        if hasattr(target, 'is_spirit') and target.is_spirit and target.alive and target.rect.colliderect(projectile_rect):
                            if not projectile.damage_applied:
                                spirit.take_damage(rogue.attack)
                                projectile.damage_applied = True
                            if not projectile.playing_collision_animation:
                                projectile.switch_attack_animation()
                            return True
                        return False

            elif projectile.category == "enemy":
                # Specifically handle SpiritProjectile instances
                if isinstance(projectile, SpiritProjectile):  # Check if it's a SpiritProjectile instance
                    if hasattr(target, 'rect') and target.rect:
                        if hasattr(target, 'is_rogue') and target.is_rogue and target.alive and target.rect.colliderect(projectile_rect):
                            if target.is_invincible:
                                return False
                            if not projectile.damage_applied:
                                rogue.take_damage(spirit.attack)
                                projectile.damage_applied = True
                            if not projectile.playing_collision_animation:
                                projectile.switch_spirit_attack_animation()
                            return True
                        if hasattr(target, 'is_skeleton') and target.is_skeleton and target.alive:
                            return False  # Skeleton should not be hit by enemy projectiles
                        if hasattr(target, 'is_spirit') and target.is_spirit and target.alive:
                            return False  # Spirit should not be hit by its own projectiles

            return False

        #Entity Deaths
        if rogue.is_dying:
            rogue.draw(screen, rogue.x_pos, rogue.y_pos)
            if rogue.current_frame >= len(rogue.scaled_frames) - 1:
                rogue.alive = False
                rogue.is_dying = False
                rogue.x_pos, rogue.y_pos = rogue.death_position
                #Don't allow the rogue to continue updating other animations
                pygame.quit()
                sys.exit()

            if spirit.alive:
                spirit.update(dt)  #Update spirit even when rogue is dead
                spirit.draw(screen, spirit.position.x, spirit.position.y, rogue)
        else:
            if rogue.alive and not rogue.is_dying:
                if rogue.current_animation not in ["Death", "Idle", "Run", "Run Left", "Attack", "Attack Left", "Damaged"]:
                    rogue.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")

        if rogue.current_animation == "Death":
            rogue.rect = pygame.Rect(rogue.position.x, rogue.position.y + 50, rogue.frame_width - 530, rogue.frame_height - 110)
        if rogue.current_animation == "Idle":
            rogue.rect = pygame.Rect(rogue.position.x, rogue.position.y + 110, rogue.frame_width, rogue.frame_height - 110)
        if rogue.current_animation in ["Attack", "Attack Left"]:
            rogue.rect = pygame.Rect(rogue.position.x, rogue.position.y + 80, rogue.frame_width, rogue.frame_height)
        if rogue.current_animation in ["Run", "Run Left"]:
            rogue.rect = pygame.Rect(rogue.position.x, rogue.position.y + 120, rogue.frame_width + 20, rogue.frame_height - 120)
        if rogue.current_animation in ["Damaged", "Damaged Left"]:
            rogue.rect = pygame.Rect(rogue.position.x - 42, rogue.position.y + 110, rogue.frame_width - 20, rogue.frame_height - 110)
        
        #Check if skeleton/spirit are idle and in range to attack
        distance_to_player = skeleton.position.x - rogue.x_pos
        if skeleton.is_attacking:
            attack_damage_frame = 3
            if skeleton.current_animation in ["Attack", "Attack Right"]:
                attack_x, attack_y = skeleton.get_attack_position(screen)

                if not rogue.alive and skeleton.alive:
                    skeleton.is_attacking = False
                    skeleton.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
            
                if skeleton.current_frame == attack_damage_frame:
                    if rogue.rect and skeleton.rect.colliderect(rogue.rect) and not skeleton.damage_applied:
                        if skeleton.current_frame == 3:
                            rogue.take_damage(skeleton.attack)
                            skeleton.damage_applied = True

            if skeleton.current_frame == len(skeleton.scaled_frames) - 1:  #End of animation
                skeleton.is_attacking = False
                skeleton.damage_applied = False

        if spirit.is_attacking:
            attack_damage_frame = 4
            if spirit.current_animation in ["Attack", "Attack Right"]:
                attack_x, attack_y = spirit.get_attack_position(screen)

                if not rogue.alive and spirit.alive:
                    spirit.is_attacking = False
                    spirit.switch_animation("Idle", "Images/PNGs/Small Spirit-Idle.json")

                if spirit.current_frame == attack_damage_frame:
                    if rogue.rect and spirit.rect.colliderect(rogue.rect) and not spirit.damage_applied:
                        if spirit.current_frame == 4:
                            rogue.take_damage(spirit.attack)
                            spirit.damage_applied = True

            if spirit.current_frame == len(spirit.scaled_frames) - 1:  #End of animation
                spirit.is_attacking = False
                spirit.damage_applied = False

        elif rogue.alive:
            if abs(distance_to_player) < 150 and not skeleton.is_attacking:
                skeleton.is_attacking = True
                if skeleton.position.x < rogue.x_pos:
                        skeleton.facing_direction = "Right"
                        skeleton.switch_animation("Attack Right", "Images/PNGs/Skeleton Walk Right-Attack Right.json")
                else:
                    skeleton.facing_direction = "Left"
                    skeleton.switch_animation("Attack", "Images/PNGs/Skeleton Walk Right-Attack.json")
        else:
            skeleton.is_attacking = False
            skeleton.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
            if abs(distance_to_player) < 150 and not spirit.is_attacking:
                spirit.is_attacking = True
                if spirit.position.x < rogue.x_pos:
                        spirit.facing_direction = "Right"
                        spirit.switch_animation("Attack Right", "Images/PNGs/Skeleton Walk Right-Attack Right.json")
                else:
                    spirit.facing_direction = "Left"
                    spirit.switch_animation("Attack", "Images/PNGs/Skeleton Walk Right-Attack.json")
            else:
                spirit.is_attacking = False
                spirit.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
        
        if skeleton2.is_attacking:
            attack_damage_frame = 3
            if skeleton2.current_animation in ["Attack", "Attack Right"]:
                attack_x, attack_y = skeleton2.get_attack_position(screen)

                if not rogue.alive and skeleton2.alive:
                    skeleton2.is_attacking = False
                    skeleton2.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
            
                if skeleton2.current_frame == attack_damage_frame:
                    if rogue.rect and skeleton2.rect.colliderect(rogue.rect) and not skeleton2.damage_applied:
                        if skeleton2.current_frame == 3:
                            rogue.take_damage(skeleton2.attack)
                            skeleton2.damage_applied = True

            if skeleton2.current_frame == len(skeleton2.scaled_frames) - 1:  #End of animation
                skeleton2.is_attacking = False
                skeleton2.damage_applied = False

        if rogue.alive:
            if abs(distance_to_player) < 150 and not skeleton2.is_attacking:
                skeleton2.is_attacking = True
                if skeleton2.position.x < rogue.x_pos:
                        skeleton2.facing_direction = "Right"
                        skeleton2.switch_animation("Attack Right", "Images/PNGs/Skeleton Walk Right-Attack Right.json")
                else:
                    skeleton2.facing_direction = "Left"
                    skeleton2.switch_animation("Attack", "Images/PNGs/Skeleton Walk Right-Attack.json")
        else:
            skeleton2.is_attacking = False
            skeleton2.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")

        #Render and debug food positions
        for food in current_level.food_items:
            food.update(dt)
            food.draw(screen)

        #Handle projectile updates
        projectiles_to_remove = []
        all_projectiles = spirit.projectiles + rogue.projectiles
        for projectile in rogue.projectiles:
            for enemy in enemy_list:
                if enemy.is_dying:
                    projectile.position.x = enemy.position.x
                    
        for projectile in all_projectiles:
            projectile.update(dt)
            projectile.draw(screen)
            #Check if the projectile is already marked as "damage applied"
            if projectile.damage_applied:
                continue  #Skip the rest of the loop if damage is already applied

            #Handle collision and damage application
            if check_collision(projectile, skeleton):
                if projectile.category == "friendly":  #If projectile is friendly and hits skeleton
                    projectile.position.x = skeleton.position.x - 80
                    skeleton.take_damage(rogue.attack)
                    projectile.damage_applied = True
                    continue  #Once damage is applied, skip further processing

            if check_collision(projectile, skeleton2):
                if projectile.category == "friendly":  #If projectile is friendly and hits skeleton
                    projectile.position.x = skeleton2.position.x - 80
                    skeleton2.take_damage(rogue.attack * 2)
                    projectile.damage_applied = True
                    continue  #Once damage is applied, skip further processing

            if check_collision(projectile, spirit):
                if projectile.category == "friendly":  #If projectile is friendly and hits spirit
                    projectile.position.x = spirit.position.x - 80
                    spirit.take_damage(rogue.attack)
                    projectile.damage_applied = True
                    continue  #Once damage is applied, skip further processing

            #For enemy projectiles, handle the rogue's health
            if projectile.category == "enemy" and isinstance(projectile, SpiritProjectile):
                if check_collision(projectile, rogue):
                    if rogue.is_invincible:  #Skip damage if rogue is invincible
                        continue
                    rogue.take_damage(spirit.attack)
                    projectile.damage_applied = True
                    continue  #Once damage is applied, skip further processing


            #Mark for removal if not alive
            if not projectile.alive:
                projectiles_to_remove.append(projectile)
        #Remove projectiles
        rogue.projectiles = [p for p in rogue.projectiles if p.alive]
        spirit.projectiles = [p for p in spirit.projectiles if p.alive]

        #Update level
        current_level.update(dt)
        current_level.draw_food(screen)

        #Check for collision player/food
        current_level.check_food_collision(rogue, rogue.rect)
        current_level.remove_collected_items()

        #Update health bars
        rogue_bar.position.x = 0
        rogue_bar.position.y = 895
        rogue_bar.update(dt)
        rogue_bar.draw(screen, 0, 895)

        for enemy in enemy_list:
            if enemy == skeleton and skeleton.alive:
                if skeleton.alive:
                    skeleton_bar.position.x = 1400
                    skeleton_bar.position.y = 975
                    skeleton_bar.update(dt)
                    skeleton_bar.draw(screen, 1400, 975)
                    advanced_skeleton_health(skeleton)
            if enemy == skeleton2 and skeleton2.alive:
                if skeleton2.alive:
                    skeleton2_bar.position.x = 900
                    skeleton2_bar.position.y = 975
                    skeleton2_bar.update(dt)
                    skeleton2_bar.draw(screen, 900, 975)
                    advanced_skeleton2_health(skeleton2)
            if enemy == spirit and spirit.alive:
                spirit_bar.position.x = 1400
                spirit_bar.position.y = 895
                spirit_bar.update(dt)
                spirit_bar.draw(screen, 1400, 895)
                advanced_spirit_health(spirit)

        enemy_list = [enemy for enemy in enemy_list if enemy.alive]

        #Update enemy/player/level/items
        if skeleton in enemy_list:
            if skeleton.alive:
                if rogue.alive and not rogue.is_dying:
                    skeleton.update(dt)
                    skeleton.draw(screen, skeleton.position.x, skeleton.position.y, rogue)
                    skeleton.handle_ai(rogue, rogue.position, dt, rogue.rect)
                else:
                    #Skeleton should stop animating or move to idle after rogue's death
                    skeleton.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
                    skeleton.update(dt)
                    skeleton.draw(screen, skeleton.position.x, skeleton.position.y, rogue)

        if skeleton2 in enemy_list:
            if skeleton2.alive:
                if rogue.alive and not rogue.is_dying:
                    skeleton2.update(dt)
                    skeleton2.draw(screen, skeleton2.position.x, skeleton2.position.y, rogue)
                    skeleton2.handle_ai(rogue, rogue.position, dt, rogue.rect)
                else:
                    #Skeleton should stop animating or move to idle after rogue's death
                    skeleton2.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
                    skeleton2.update(dt)
                    skeleton2.draw(screen, skeleton2.position.x, skeleton2.position.y, rogue)
        
        if spirit in enemy_list:
            if spirit.alive:
                spirit.update(dt)
                spirit.draw(screen, spirit.position.x, spirit.position.y, rogue)
                if rogue.alive and not rogue.is_dying:
                    spirit.handle_ai(rogue, rogue.position, dt, rogue.rect)
                else:
                    pass
        if rogue.is_dying or rogue.alive:
            rogue.update(dt)
            rogue.draw(screen, rogue.x_pos, rogue.y_pos)
            advanced_rogue_health(rogue)

        #Level transition
        def can_pass():
            if all(enemy.health <= 0 for enemy in enemy_list):
                if current_level in [start_level, second_level]:
                    arrow.update(dt)
                    arrow.draw(screen)
                    return True
                
        if current_level == last_level and len(enemy_list) == 0:
            end_text.update(dt)
            end_text.draw(screen)

        if current_level == last_level:
            if spirit.alive and skeleton not in enemy_list and skeleton2 not in enemy_list:
                if spawn_timer is None:  #Start the timer if not already started
                    spawn_timer = pygame.time.get_ticks()
                
                elapsed_time = pygame.time.get_ticks() - spawn_timer
                if elapsed_time > 7000:
                    skeleton.reset(health=1000)
                    skeleton2.reset(health=1000)
                    skeleton.position.x = 1000
                    skeleton2.position.x = 1500
                    enemy_list.append(skeleton)
                    enemy_list.append(skeleton2)
                    
                    skeleton.switch_animation("Summon", "Images/PNGs/Skeleton-Summon.json")
                    skeleton2.switch_animation("Summon", "Images/PNGs/Skeleton-Summon.json")
                    
                    skeleton.summoning = True
                    skeleton2.summoning = True

                    spawn_timer = None
            else:
                spawn_timer = None

        #Check if player is near right wall to pass to next screen
        if can_pass() and rogue.is_moving and rogue.rect.colliderect(right_wall.rect):
            if not transitioning:
                transitioning = True
                transition_timer = pygame.time.get_ticks()

        #Handle level transition
        if transitioning:
            elapsed_time = pygame.time.get_ticks() - transition_timer
            if elapsed_time > 250:
                if current_level == start_level:
                    current_level = second_level
                elif current_level == second_level:
                    current_level = last_level
                transitioning = False
                enemy_list = initialize_enemy_list(current_level)
                for enemy in enemy_list:
                    if isinstance(enemy, Skeleton):
                        enemy.reset(health=1000)
                    elif isinstance(enemy, Skeleton):
                        enemy.reset(health=1000)
                    elif isinstance(enemy, Spirit):
                        enemy.reset(health=1500)

                right_wall.rect = RightWall(current_level).rect

                #Reset rogue's position
                rogue.x_pos = (SCREEN_WIDTH * 3 - rogue.scaled_frames[0][0].get_width()) // 2 - 830
                rogue.y_pos = (SCREEN_HEIGHT * 3 - rogue.scaled_frames[0][0].get_height()) // 2 + 198
                rogue.rect = pygame.Rect(
                    rogue.x_pos,
                    rogue.y_pos,
                    rogue.scaled_frames[0][0].get_width(),
                    rogue.scaled_frames[0][0].get_height(),
                )
                if skeleton.scaled_frames:
                    skeleton.position.x = (SCREEN_WIDTH * 3 - skeleton.scaled_frames[0][0].get_width()) // 2 + 200
                    skeleton.position.y = (SCREEN_HEIGHT * 3 - skeleton.scaled_frames[0][0].get_height()) // 2 + 240

                if skeleton2.scaled_frames:
                    skeleton2.position.x = (SCREEN_WIDTH * 3 - skeleton2.scaled_frames[0][0].get_width()) // 2 + 500
                    skeleton2.position.y = (SCREEN_HEIGHT * 3 - skeleton2.scaled_frames[0][0].get_height()) // 2 + 240

                if spirit.scaled_frames:
                    spirit.x_pos = (SCREEN_WIDTH * 3 - spirit.scaled_frames[0][0].get_width()) // 2 + 925
                    spirit.y_pos = (SCREEN_HEIGHT * 3 - spirit.scaled_frames[0][0].get_height()) // 2 + 240
                        
            else:
                #Screen fades to black during transition
                screen.fill((0, 0, 0))
                pygame.display.flip()
                continue  #Skip the rest of the loop during transition

        #Check if the player can transition
        if not transitioning:
            if can_pass() and rogue.rect.colliderect(right_wall.rect):
                transitioning = True
                transition_timer = pygame.time.get_ticks()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
