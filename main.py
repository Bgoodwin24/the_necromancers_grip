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

    #Initial position
    if rogue.scaled_frames:
        rogue.x_pos = (SCREEN_WIDTH * 3 - rogue.scaled_frames[0][0].get_width()) // 2 - 870
        rogue.y_pos = (SCREEN_HEIGHT * 3 - rogue.scaled_frames[0][0].get_height()) // 2 + 198
    else:
        print("Warning: scaled_frames not initialized.")

    if skeleton.scaled_frames:
        skeleton.x_pos = (SCREEN_WIDTH * 3 - skeleton.scaled_frames[0][0].get_width()) // 2 + 925
        skeleton.y_pos = (SCREEN_HEIGHT * 3 - skeleton.scaled_frames[0][0].get_height()) // 2 + 252
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

        #Draw background
        current_level.draw_level(screen, background1)

        #Conditional food spawns
        if rogue.health <= 1000:
            current_level.spawn_food_items(screen, rogue, Items, 500, 764)

        #Entity Deaths
        if rogue.health == 0:
            rogue.die("Images/PNGs/Rogue-Death.json")
        if skeleton.health == 0:
            skeleton.die("Images/PNGs/Skeleton-Death.json")

        #Render and debug food positions
        for food in current_level.food_items:
            food.update(dt)
            food.draw(screen)

        #Update enemy
        if skeleton.alive:
            skeleton.update(dt)
            skeleton.draw(screen, skeleton.x_pos, skeleton.y_pos)

        #Handle projectile updates
        projectiles_to_remove = []
        for projectile in rogue.projectiles:
            projectile.update(dt)
            projectile.draw(screen)

            #Collision with skeleton
            if projectile.check_collision(skeleton):
                print(f"Projectile hit skeleton at {skeleton.get_position()}")
                skeleton.take_damage(rogue.attack)
                projectile.alive = False
                if rogue.current_animation == "Attack":
                    projectile.switch_animation("Attack Collision", "Images/PNGs/Small rogue animations-Attack Collision-Attack Collision.json")
                if rogue.current_animation == "Attack Left":
                    projectile.switch_animation("Attack Collision Left", "Images/PNGs/Small rogue animations-Small Attack Collision Left-Attack Collision Left.json")
            #Mark for removal if not alive
            if not projectile.alive:
                projectiles_to_remove.append(projectile)
        #Remove projectiles
        rogue.projectiles = [p for p in rogue.projectiles if p.alive]

        #For boss projectile
        #if projectile.category == "enemy" and projectile.check_collision(rogue):
            #rogue.take_damage(500)
        #elif projectile.category == "friendly":
            #pass
        #For rogue projectile
        #if projectile.category == "enemy" and projectile.check_collision(skeleton):
            #skeleton.take_damage(250)
        #elif projectile.category == "friendly":
            #pass
        #if projectile.check_collision(spirit):
            #spirit.take_damage(250)
        #if skeleton.attack.check_collision(rogue):
            #rogue.take_damage(334)

        #Update level
        current_level.update(dt)
        current_level.draw_food(screen)

        #Check for collision player/food
        current_level.check_food_collision(rogue, rogue.rect)
        current_level.remove_collected_items()

        #Update player/level/items
        if rogue.alive:
            rogue.update(dt)
            rogue.draw(screen, rogue.x_pos, rogue.y_pos)
        else:
            run = False

        #Check if player is near right wall to pass to next screen
        if right_wall.can_pass(rogue):
            #add code to transition to next screen
            pass

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
