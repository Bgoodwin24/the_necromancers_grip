import pygame
import os
import sys
from entities import *
from level import *
import json
from items import *
from constants import *
from projectiles import *

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
    current_level = Level()
    
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
    spirit = Spirit("Images/PNGs/Small Spirit-Idle.json")

    #Initial position
    if rogue.scaled_frames:
        rogue.x_pos = (SCREEN_WIDTH * 3 - rogue.scaled_frames[0][0].get_width()) // 2 - 870
        rogue.y_pos = (SCREEN_HEIGHT * 3 - rogue.scaled_frames[0][0].get_height()) // 2 + 198
    else:
        print("Warning: scaled_frames not initialized.")

    if skeleton.scaled_frames:
        skeleton.position.x = (SCREEN_WIDTH * 3 - skeleton.scaled_frames[0][0].get_width()) // 2 + 925
        skeleton.position.y = (SCREEN_HEIGHT * 3 - skeleton.scaled_frames[0][0].get_height()) // 2 + 240
    else:
        print("Warning: scaled_frames not initialized.")

    if spirit.scaled_frames:
        spirit.x_pos = (SCREEN_WIDTH * 3 - spirit.scaled_frames[0][0].get_width()) // 2 + 925
        spirit.position.x += 1550
        spirit.y_pos = (SCREEN_HEIGHT * 3 - spirit.scaled_frames[0][0].get_height()) // 2 + 240
    else:
        print("Warning: scaled_frames not initialized.")

    run = True

    #Game Loop
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

        #Clear screen
        screen.fill((0, 0, 0))

        #Movement input
        keys = pygame.key.get_pressed()

        #Update player postion and rect
        rogue.x_pos, rogue.y_pos = rogue.handle_movement(keys, rogue.x_pos, rogue.y_pos, colliders, dt)
        print(f"New position: {rogue.x_pos}, {rogue.y_pos}")
        rogue.rect = pygame.Rect(rogue.x_pos, rogue.y_pos, rogue.scaled_frames[0][0].get_width(), rogue.scaled_frames[0][0].get_height())
        #Update skeleton rect after its position has been set
        skeleton.rect = pygame.Rect(skeleton.position.x, skeleton.position.y, skeleton.scaled_frames[0][0].get_width(), skeleton.scaled_frames[0][0].get_height())
        spirit.rect = pygame.Rect(spirit.position.x, spirit.position.y, spirit.scaled_frames[0][0].get_width(), spirit.scaled_frames[0][0].get_height())
        #Draw background
        current_level.draw_level(screen, background1)

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
                        if hasattr(target, 'is_skeleton') and target.is_skeleton and target.alive and target.rect.colliderect(projectile_rect):
                            if not projectile.damage_applied:
                                skeleton.take_damage(rogue.attack)
                                print(f"Skeleton health: {skeleton.health}/1000")
                                projectile.damage_applied = True
                            if not projectile.playing_collision_animation:
                                projectile.switch_attack_animation()
                            return True
                        if hasattr(target, 'is_spirit') and target.is_spirit and target.alive and target.rect.colliderect(projectile_rect):
                            if not projectile.damage_applied:
                                spirit.take_damage(rogue.attack)
                                print(f"Spirit health: {spirit.health}/1000")
                                projectile.damage_applied = True
                            if not projectile.playing_collision_animation:
                                projectile.switch_attack_animation()
                            return True
                        return False

            elif projectile.category == "enemy":
                # Specifically handle SpiritProjectile instances
                if isinstance(projectile, SpiritProjectile):  # Check if it's a SpiritProjectile instance
                    if hasattr(target, 'rect') and target.rect:
                        if hasattr(target, 'is_rogue') and target.is_rogue and target.alive:
                            if target.rect.colliderect(projectile_rect) and not projectile.damage_applied:
                                rogue.take_damage(spirit.attack)
                                projectile.damage_applied = True
                                print(f"Rogue hit by spirit's projectile! Health: {rogue.health}")
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
                print("Rogue has finished the Death animation.")
                rogue.alive = False
                rogue.is_dying = False
                rogue.x_pos, rogue.y_pos = rogue.death_position
                # Don't allow the rogue to continue updating other animations
                pygame.quit()
                sys.exit()

            if spirit.alive:
                spirit.update(dt)  # Update spirit even when rogue is dead
                spirit.draw(screen, spirit.position.x, spirit.position.y)
        else:
            if rogue.alive and not rogue.is_dying:
                if rogue.current_animation not in ["Death", "Idle", "Run", "Run Left", "Attack", "Attack Left", "Damaged"]:
                    rogue.switch_animation("Idle", "Images/PNGs/Smaller rogue animations-Smaller Idle.json")
                    print(f"Rogue Animation: {rogue.current_animation}, Frame: {rogue.current_frame}/{len(rogue.scaled_frames) - 1}")

        # Check if skeleton/spirit are idle and in range to attack
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
                        print("Skeleton hits the rogue!")
                        if skeleton.current_frame == 3:
                            rogue.take_damage(skeleton.attack)
                            skeleton.damage_applied = True

            if skeleton.current_frame == len(skeleton.scaled_frames) - 1:  # End of animation
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
                        print("Spirit hits the rogue!")
                        if spirit.current_frame == 4:
                            rogue.take_damage(spirit.attack)
                            spirit.damage_applied = True

            if spirit.current_frame == len(spirit.scaled_frames) - 1:  # End of animation
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
        
        #Render and debug food positions
        for food in current_level.food_items:
            food.update(dt)
            food.draw(screen)

        #Handle projectile updates
        projectiles_to_remove = []
        all_projectiles = spirit.projectiles + rogue.projectiles
        for projectile in all_projectiles:
            projectile.update(dt)
            projectile.draw(screen)
            # Check if the projectile is already marked as "damage applied"
            if projectile.damage_applied:
                continue  # Skip the rest of the loop if damage is already applied

            # Handle collision and damage application
            if check_collision(projectile, rogue):
                if rogue.is_invincible:  # Skip damage if rogue is invincible
                    continue
                if projectile.category == "friendly":  # Friendly projectiles should deal damage
                    rogue.take_damage(rogue.attack)
                    print(f"Rogue hit by friendly projectile! Health: {rogue.health}")
                    projectile.damage_applied = True
                    continue  # Once damage is applied, skip further processing

            if check_collision(projectile, skeleton):
                if projectile.category == "friendly":  # If projectile is friendly and hits skeleton
                    skeleton.take_damage(rogue.attack)
                    print(f"Skeleton hit by friendly projectile! Health: {skeleton.health}")
                    projectile.damage_applied = True
                    continue  # Once damage is applied, skip further processing

            if check_collision(projectile, spirit):
                if projectile.category == "friendly":  # If projectile is friendly and hits spirit
                    spirit.take_damage(rogue.attack)
                    print(f"Spirit hit by friendly projectile! Health: {spirit.health}")
                    projectile.damage_applied = True
                    continue  # Once damage is applied, skip further processing

            # For enemy projectiles, handle the rogue's health
            if projectile.category == "enemy" and isinstance(projectile, SpiritProjectile):
                if check_collision(projectile, rogue):
                    if rogue.is_invincible:  # Skip damage if rogue is invincible
                        continue
                    rogue.take_damage(spirit.attack)
                    print(f"Rogue hit by spirit's projectile! Health: {rogue.health}")
                    projectile.damage_applied = True
                    continue  # Once damage is applied, skip further processing


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

        #Update enemy/player/level/items

        if skeleton.alive:
            if rogue.alive and not rogue.is_dying:
                skeleton.update(dt)
                skeleton.draw(screen, skeleton.position.x, skeleton.position.y)
                skeleton.handle_ai(rogue, rogue.position, dt, rogue.rect)
            else:
                # Skeleton should stop animating or move to idle after rogue's death
                skeleton.switch_animation("Idle", "Images/PNGs/Skeleton Walk Right-Small Idle Left.json")
                skeleton.update(dt)
                skeleton.draw(screen, skeleton.position.x, skeleton.position.y)

        if spirit.alive:
            spirit.update(dt)
            spirit.draw(screen, spirit.position.x, spirit.position.y)
            if rogue.alive and not rogue.is_dying:
                spirit.handle_ai(rogue, rogue.position, dt, rogue.rect)
            else:
                pass
        if rogue.is_dying or rogue.alive:
            print(f"Rogue Animation: {rogue.current_animation}, Frame: {rogue.current_frame}/{len(rogue.scaled_frames) - 1}")
            rogue.update(dt)
            rogue.draw(screen, rogue.x_pos, rogue.y_pos)

        #Check if player is near right wall to pass to next screen
        if right_wall.can_pass(rogue):
            #add code to transition to next screen
            pass

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
