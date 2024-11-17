import pygame
import os
import sys
from entities import *
from level import *
import json
from items import *
from constants import *


    #sprite_sheet_skelton = 
    #sprite_sheet_boss = 
    #sprite_sheet_item = 

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
    ground = pygame.Rect(0, SCREEN_HEIGHT * 3 - 140, SCREEN_WIDTH * 3, 5)
    right_wall = RightWall(current_level)

    colliders = {
        "left_wall": left_wall,
        "right_wall": right_wall.rect,
        "ground": ground
    }

    #Offset for initial position
    offset_x = -870
    offset_y = 198

    #Load player idle
    rogue = Rogue("Images/PNGs/Smaller rogue animations-Smaller Idle.json", (offset_x, offset_y))

    #Initial position
    if rogue.scaled_frames:
        x_pos = (SCREEN_WIDTH * 3 - rogue.scaled_frames[0][0].get_width()) // 2 + offset_x
        y_pos = (SCREEN_HEIGHT * 3 - rogue.scaled_frames[0][0].get_height()) // 2 + offset_y
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

        #Clear screen
        screen.fill((0, 0, 0))

        #Movement input
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d, pygame.K_SPACE]:
                    rogue.switch_animation("Idle", "Image/PNGs/Smaller rogue animations-Smaller Idle.json")

        #Update player postion and rect
        x_pos, y_pos = rogue.handle_movement(keys, x_pos, y_pos, colliders, dt)
        rogue.rect = pygame.Rect(x_pos, y_pos, rogue.scaled_frames[0][0].get_width(), rogue.scaled_frames[0][0].get_height())

        #Draw background
        current_level.draw_level(screen, background1)

        #Conditional food spawns
        if rogue.health <= 1000:
            current_level.spawn_food_items(screen, rogue, Items, 500, 764)

        #Entity Deaths
        if rogue.health == 0:
            rogue.die("Images/PNGs/Rogue-Death.json")

        #Render and debug food positions
        for food in current_level.food_items:
            food.update(dt)
            food.draw(screen)
        
        #Update player/level/items
        rogue.update(dt)
        rogue.draw(screen, x_pos, y_pos)

        #Check for collision player/food
        current_level.check_food_collision(rogue, rogue.rect)

        #Remove collected items
        current_level.remove_collected_items()

        #Update level
        current_level.update(dt)
        current_level.draw_food(screen)

        #Check if player is near right wall to pass to next screen
        if right_wall.can_pass(rogue):
            #add code to transition to next screen
            pass

        #for enemy in enemies:
            #for attack in Attacks:
                #if enemy.check_collision(player_attack):
                    #pass
                    #run attack collision pngs

        #player.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
