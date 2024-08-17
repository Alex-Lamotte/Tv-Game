

"""
Created on Tue Mar 26 17:53:16 2024

@author: Alex
"""

import pygame
import sys


# Initialize the game engine
pygame.init()


#initalize the text

pygame.font.init()

#add the damage variable
global lives
lives=3
# Define the game screen size
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Define the boundaries of the map

import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))  # Create a surface of specified width and height
        self.image.fill((0, 255, 0))  # Fill the surface with a color (green)
        self.rect = self.image.get_rect()  # Get the rect for positioning
        self.rect.topleft = (x, y)  # Set the position of the platform

    def draw(self, screen):
        # Draw the platform to the screen
        screen.blit(self.image, self.rect)
        
class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, next_room):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 200, 0))  # Fill with a color to distinguish it (e.g., orange for the door)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.next_room = next_room  # The room this door will lead to



class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,velocity,left_stop=0,right_stop=SCREEN_WIDTH):
        super().__init__()
        self.image=pygame.Surface((width,height))
        self.image.fill((0,0,0))
        self.rect=self.image.get_rect()
        self.rect.topleft= (x,y)
        self.velocity=(velocity)
        self.right_hit=False
        self.left_stop=left_stop
        self.right_stop=right_stop
        
        
    def update(self):
        if self.right_hit==False:
            self.rect.x+=self.velocity
            if self.rect.right>=self.right_stop:
                self.right_hit=True
                
            
        elif self.right_hit==True:
            self.rect.x-=self.velocity
            if self.rect.x<=self.left_stop:
                self.right_hit=False
        
    
    def draw(self, screen):
        # Draw the enemy to the screen
        screen.blit(self.image, self.rect)
        


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = self.load_images()
        self.player_images = self.images  # Create a surface for the player
        self.index=0
        self.image=self.player_images[self.index]
        
        
       
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)  # Position the player
        self.velocity = pygame.math.Vector2(0, 0)  # Initialize velocity
        self.on_ground = False  # A flag to track whether the player is on the ground
        self.gravity = 0.5  # Gravity constant
        self.jump_speed = -10  # Initial velocity for jumps (negative for upward)
        self.waitTimer = 0 #used to delay update of sprite
        

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -5  # Move left
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = 5  # Move right
        else:
            self.velocity.x = 0  # Stop horizontal movement when no key is pressed

        # Jumping logic
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity.y = self.jump_speed
            self.on_ground = False  # The player is no longer on the ground

    def update(self):
        self.waitTimer += 1
        
        if self.waitTimer % 10==0:
            self.index += 1
        if self.index >= len(self.images):
            self.index = 0  # Reset index
        self.image = self.images[self.index]  # Update the image

        self.handle_keys()
        
        # Apply gravity
        self.velocity.y += self.gravity
    
        # Move the player horizontally
        self.rect.x += self.velocity.x
        # Horizontal collision check would go here (if implemented in Player class)
    
        # Keep the player on the screen (simple boundary checking)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.y<0:
            self.rect.y=0

    def draw(self, screen):
        # Draw the player to the screen
        screen.blit(self.image, self.rect)
        
    def load_images(self):
        filenames = [f"Sprite{i}.png" for i in range(0,4)]
        images = [pygame.image.load(filename) for filename in filenames]
        return images


class Room: 
    
    def __init__(self,respawn_coords=(0,650)):
        self.platforms=pygame.sprite.Group()
        self.enemies=pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.player= None
        self.objects = []  # List of objects in the room
        self.text = ""  # Text specific to this 
        self.respawn_point = respawn_coords  # Default respawn point
        
    def set_respawn_point(self, x, y):
        self.respawn_point = (x, y)
        print(f"Set respawn point for room: {self.respawn_point}")

    
    def add_platform(self,platform):
        self.platforms.add(platform)
        
    def add_door(self, door):
        self.doors.add(door)  # Adding doors to their own group
        
    def add_enemy(self,enemy):
        self.enemies.add(enemy)
        
    def set_player(self,player):
        self.player= player
        
    def draw(self, screen):
        screen.fill((0, 200, 250))
        self.platforms.draw(screen)
        self.doors.draw(screen)  # Draw doors separately
        self.enemies.draw(screen)
        if self.player:
            self.player.draw(screen)
        for obj in self.objects:
            obj.draw(screen)
        # Draw room-specific text if it exists
        if self.text:
            font = pygame.font.Font(None, 36)
            text_surface = font.render(self.text, True, (255, 255, 255))
            screen.blit(text_surface, (200, 150))  # Adjust position as needed
            
    def clear_room(self):
        self.platforms.empty()
        self.enemies.empty()
    
    def handle_collisions(self):
        # Check horizontal collisions
        self.player.rect.x += self.player.velocity.x
        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if self.player.velocity.x > 0:  # Moving right
                    self.player.rect.right = platform.rect.left
                elif self.player.velocity.x < 0:  # Moving left
                    self.player.rect.left = platform.rect.right
    
        # Check vertical collisions
        self.player.rect.y += self.player.velocity.y
        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if self.player.velocity.y > 0:  # Falling down
                    self.player.rect.bottom = platform.rect.top
                    self.player.velocity.y = 0
                    self.player.on_ground = True
                elif self.player.velocity.y < 0:  # Moving up
                    self.player.rect.top = platform.rect.bottom
                    self.player.velocity.y = 0
    
        # Check for ground collision after checking platform collisions
        if self.player.rect.bottom >= SCREEN_HEIGHT:
            self.player.rect.bottom = SCREEN_HEIGHT
            self.player.velocity.y = 0
            self.player.on_ground = True
                    
        for enemy in self.enemies: 
            if pygame.sprite.collide_rect(self.player,enemy):
                print("yo yo its me the enemy!!!")
                global lives
                self.player=Player(0,650)
                lives-=1
                if lives<=0:
                    pygame.quit()
            
    
    def update(self):
        self.platforms.update()
        self.enemies.update()
        if self.player:
            self.player.update()
            
        # here is the collision update
        self.handle_collisions()
        
class Game:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((1200, 700))
        
        self.rooms = [self.create_roomX(),self.create_room1(), self.create_room2(), self.create_room3(),self.create_room4(),self.create_room5(),self.create_room6(),self.create_room7(),self.create_room8()]
        self.current_room_index = 0
        self.current_room = self.rooms[self.current_room_index]
        
        
    def draw_text(self, text, position):
        text_surface = self.font.render(text, True, (1, 1, 1))  # White text
        self.screen.blit(text_surface, position)
        
    def respawn_player(self):
        respawn_x, respawn_y = self.current_room.respawn_point
        self.player.x = respawn_x
        self.player.y = respawn_y
        self.player.velocity_y = 0  # Assuming you want to reset the player's vertical velocity
        
    def create_roomX(self):
        print("yo yo its me create room 1!!!")
        room= Room(respawn_coords=(100,100))
        
               
        room.text="space or up arrow to jump and a/d or left and right to move. make it to the yellow coin!"
       
        #add such stuff
        player=Player(100,100)
        
    
        #pillar
        plat1=Platform(450,130,300,520)
        
        
        #ladder steps2
        plat2=Platform(400,630,50,20)
        plat3=Platform(400,550,50,20)
        
        plat4=Platform(0,500,150,10)
        plat5=Platform(0,425,100,10)
        plat6=Platform(0,325,50,10)
        plat7=Platform(250,335,200,20)
        plat8=Platform(200,235,250,5)
        plat9=Platform(400,150,50,20)
        
        
       
        room.add_platform(plat9)
        room.add_platform(plat8)
        room.add_platform(plat7)
        room.add_platform(plat3)
        room.add_platform(plat4)
        room.add_platform(plat6)
        room.add_platform(plat5)
        room.add_platform(plat2)
        room.add_platform(plat1)
        room.set_player(player)
        room.add_door(Door(1160,90,30,30,1))
        
        return room
        
    def create_room1(self):
        print("yo yo its me create room 1!!!")
        room= Room()
        #add such stuff
        player=Player(0,650)
     
        enemy=Enemy(450,80,50,50,5,450,750)
        
        room.add_enemy(enemy)
        #pillar
        plat1=Platform(450,130,300,520)
        
        
        #ladder steps2
        plat2=Platform(400,630,50,20)
        plat3=Platform(400,550,50,20)
        
        plat4=Platform(0,500,150,10)
        plat5=Platform(0,425,100,10)
        plat6=Platform(0,325,50,10)
        plat7=Platform(250,335,200,20)
        plat8=Platform(200,235,250,5)
        plat9=Platform(400,150,50,20)
        
        
       
        room.add_platform(plat9)
        room.add_platform(plat8)
        room.add_platform(plat7)
        room.add_platform(plat3)
        room.add_platform(plat4)
        room.add_platform(plat6)
        room.add_platform(plat5)
        room.add_platform(plat2)
        room.add_platform(plat1)
        room.set_player(player)
        room.add_door(Door(1160,90,30,30,2))
    
        return room
    
    def create_room2(self):
        
        
        room= Room()
        #add such stuff
       
        player=Player(0,650)
       
        enemy=Enemy(800,450,50,50,5,800)
        plat1=Platform(150,520,300,5)
        plat2=Platform(750,650,450,5)
        plat3=Platform(800,500,400,5)
        plat4=Platform(150,600,300,5)
        #top
        plat5=Platform(1000,100,200,50)
        #laddar
        plat6=Platform(1150,430,50, 20)
        plat7=Platform(1150,360,50, 20)
        plat8=Platform(1150,290,50, 20)
        plat9=Platform(1150,220,50, 20)
        plat10=Platform(1150,150,50, 20)
        
        plat11=Platform(700,220,300,10)
        plat12=Platform(320,140,300,20)
        room.add_platform(plat12)
        room.add_platform(plat11)
        room.add_platform(plat10)
        room.add_platform(plat9)
        room.add_platform(plat8)
        room.add_platform(plat7)
        room.add_platform(plat6)
        room.add_platform(plat5)
        room.add_platform(plat4)
        room.add_platform(plat3)
        room.add_platform(plat1)
        room.add_platform(plat2)
        room.set_player(player)
        room.add_enemy(enemy)
        room.add_door(Door(1100,50,30,30,3))
        
        return room
    
    def create_room3(self):
        #room height is 700 and width is 1200 (both start from top left so bottom is screen is 700 and the very right is 1200)
        room= Room()
        room.text = "You have reached the end of level 1! good job. you have 3 tickets"
        #add such stuff
        player=Player(0,650)
       
        plat1=Platform(250,630,300,20)
        plat2=Platform(400,540,300,20)
        room.add_door(Door(1160,490,30,30,4))
        room.add_platform(plat2)
        
        room.add_platform(plat1)
   
        room.set_player(player)
        return room
    
    def create_room4(self):
        room=Room()
        room.text = "Find your way out that hole!"
        player=Player(0,650)
        plat1=Platform(200,330,950,20)
        plat2=Platform(200,350,20,350)
        plat3=Platform(0,650,1,1)
        plat4=Platform(199,600,1,1)
        plat5=Platform(0,550,1,1)
        plat6=Platform(199,500,1,1)
        plat7=Platform(0,450,1,1)
        plat8=Platform(199,400,1,1)
        plat9=Platform(0,350,1,1)
        plat10=Platform(600,265,100,20)
        
       
        room.add_platform(plat10)
        
        room.add_platform(plat8)
        room.add_platform(plat9)
        room.add_platform(plat4)
        room.add_platform(plat5)
        room.add_platform(plat6)
        room.add_platform(plat7)
        room.add_platform(plat1)
        room.add_platform(plat2)
        room.add_platform(plat3)
        room.set_player(player)
        enemy1=Enemy(300,280,50,50,1,300)
        enemy2=Enemy(350,280,50,50,2,300)
        enemy3=Enemy(400,280,50,50,4,300)
        enemy4=Enemy(450,280,50,50,8,300)
        enemy5=Enemy(500,280,50,50,16,300)
        enemy6=Enemy(300,480,50,50,1,300)
        enemy7=Enemy(350,480,50,50,2,300)
        enemy8=Enemy(400,480,50,50,4,300)
        enemy9=Enemy(450,480,50,50,8,300)
        enemy10=Enemy(500,480,50,50,16,300)
        
  
        room.add_enemy(enemy1)
        room.add_enemy(enemy2)
        room.add_enemy(enemy3)
        room.add_enemy(enemy4)
        room.add_enemy(enemy5)
        room.add_enemy(enemy6)
        room.add_enemy(enemy7)
        room.add_enemy(enemy8)
        room.add_enemy(enemy9)
        room.add_enemy(enemy10)
        
        room.add_door(Door(220,670,980,30,5))
        return room
    
    def create_room5(self):
        room=Room()
        room.text = " hard jumps!"
        player=Player(0,0)
        wall=Platform(100, 0, 40, 650)
        plat1=Platform(140,600,570,50 )
        plat2=Platform(1010,550, 50,50)
        plat3=Platform(1150,625,50,50)
        pillar2=Platform(910,500,50,100)
        pillar3=Platform(810,450,50,150)
        pillar4=Platform(710,400,50,200)
        enemy1=Enemy(1150,650,50,50,5,100)
        room.add_enemy(enemy1)
        lad1=Platform(140, 510, 50, 20)
        lad2=Platform(140, 440, 50, 20)
        lad3=Platform(140, 370, 50, 20)
        lad4=Platform(140, 300, 50, 20)
        lad5=Platform(140, 230, 50, 20)
        lad6=Platform(140, 160, 50, 20)
        lad7=Platform(140, 90, 50, 20)
        step1=Platform(710,160,300,20)
        room.add_platform(step1)
        room.add_platform(lad7)
        room.add_platform(lad6)
        room.add_platform(lad5)
        room.add_platform(lad4)
        room.add_platform(lad3)
        room.add_platform(lad2)
        room.add_platform(lad1)
        
        room.add_platform(lad1)
        room.set_player(player)
        room.add_platform(wall)
        room.add_platform(plat1)
        room.add_platform(plat2)
        room.add_platform(plat3)
        room.add_platform(pillar2)
        room.add_platform(pillar3)
        room.add_platform(pillar4)
       
        room.add_door(Door(1100,50,30,30,6))
        return room
    
    def create_room6(self):
        room=Room()
        player=Player(0,650)
        room.text="you have four tickets! you can stop now, or keep going for one more."
        room.set_player(player)
        room.add_door(Door(1100,650,30,30,7))
        return room
    
    def create_room7(self):
        room=Room()
        player=Player(0,650)
        room.set_player(player)
        plat1=Platform(300, 150, 50,445)
        plat11=Platform(300, 650, 50,50)
        plat2=Platform(900, 300, 50,295)
        plat22=Platform(900, 650, 50,50)
        enemy1=Enemy(250,600,50,50,10,250,950)
        enemy2=Enemy(250,600,50,50,100,250,950)
        step1=Platform(1,650,1,1)
        step2=Platform(1,575,1,1)
        step3=Platform(1,500,1,1)
        step4=Platform(1,425,1,1)
        step5=Platform(1,350,1,1)
        step6=Platform(1,275,1,1)
        step7=Platform(1,200,1,1)
        step8=Platform(1,125,1,1)
        room.add_platform(step1)
        room.add_platform(step2)
        room.add_platform(step3)
        room.add_platform(step4)
        room.add_platform(step5)
        room.add_platform(step6)
        room.add_platform(step7)
        room.add_platform(step8)
        room.add_enemy(enemy2)
        room.add_enemy(enemy1)
        room.add_platform(plat11)
        room.add_platform(plat1)
        room.add_platform(plat22)
        room.add_platform(plat2)
        
        room.add_door(Door(1150, 650, 30,30, 8))
        return room
        
    def create_room8(self):
        room=Room()
        player=Player(0,650)
        room.set_player(player)
        room.text="YOU WON HAZZA YAY GOOD JOB"
        return room

    
    def switch_room(self,new_room_index):
        self.current_room.clear_room()
        #clear current room
        
        self.current_room=self.rooms[new_room_index]
        self.current_room_index=new_room_index
        
        #respawn character
        
    def run(self):
        # game loop here
        running = True
        clock = pygame.time.Clock()  # Create a clock object to manage the frame rate
    
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
            self.current_room.update()
    
            # Check if the player reaches the door before drawing the current room
            if self.player_reaches_door():
                # The room will be switched if the player reaches a door
                continue  # Skip the rest of the loop to avoid drawing the old room after switching
           # Render (draw) section
            # Here you blit the text surface onto the screen
            self.screen.fill((150, 0, 150))  # Clear the screen with black before drawing
            
            self.current_room.draw(self.screen)
            self.draw_text(f"Lives: {lives}", (50, 50))
         
            
            pygame.display.flip()  # Update the full display Surface to the screen
            clock.tick(60)  # Cap the frame rate at 60 FPS
        

    def player_reaches_door(self):
        for door in self.current_room.doors:
            if self.current_room.player.rect.colliderect(door.rect):
                self.switch_room(door.next_room)
                return True
        return False
    
    
game= Game()
game.run()
pygame.quit()

