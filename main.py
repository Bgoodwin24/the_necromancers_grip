import pygame
import os
import sys
from entities import *
from level import *
import json
from items import *
from constants import *
#from attacks import Attacks

    #sprite_sheet_skelton = 
    #sprite_sheet_boss = 
    #sprite_sheet_item = 

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3))
    pygame.display.set_caption("The Necromancers Grip")
    clock = pygame.time.Clock()

    #Load player idle
    rogue = Rogue("Images/PNGs/Rogue-Idle.json")

    #Background files
    background1 = pygame.image.load("Images/PNGs/Graveyard Background No Repeat.png")
    background2 = pygame.image.load("Images/PNGs/Graveyard Background.png")

    #Levels
    current_level = Level()
    
    #Colliders
    left_wall = pygame.Rect(-90, 0, 5, SCREEN_HEIGHT * 3)
    ground = pygame.Rect(0, SCREEN_HEIGHT * 3 - 140, SCREEN_WIDTH * 3, 5)
    right_wall = RightWall(current_level)

    colliders = {
        "left_wall": left_wall,
        "right_wall": right_wall.rect,
        "ground": ground
    }

    #Offset for initial position
    offset_x = -695
    offset_y = 208

    #Initial position
    if rogue.scaled_frames:
        x_pos = (SCREEN_WIDTH * 3 - rogue.scaled_frames[0][0].get_width()) // 2 + offset_x
        y_pos = (SCREEN_HEIGHT * 3 - rogue.scaled_frames[0][0].get_height()) // 2 + offset_y
    else:
        print("Warning: scaled_frames not initialized.")

    run = True

    def check_collision(player_rect, colliders):
        for collider in colliders:
            if player_rect.colliderect(collider):
                return True
        return False

    #Game Loop
    while run:
        #Fps control
        dt = clock.tick(60) / 1000.0
        
        #Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        screen.fill((0, 0, 0))

        #Draw background
        current_level.draw_level(screen, background1)
        
        #Update player and level
        rogue.update(dt)
        rogue.draw(screen, x_pos, y_pos)

        current_level.update(dt)
        current_level.draw_food(screen)

        #Item
        current_level.food_items = [food for food in current_level.food_items if not food.check_item_collision(rogue)]


        #Movement input
        keys = pygame.key.get_pressed()
        x_pos, y_pos = rogue.handle_movement(keys, x_pos, y_pos, colliders)

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
