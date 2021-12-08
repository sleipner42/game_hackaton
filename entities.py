import pygame
import random
import math 

from config import HALF_MONSTER_SIZE, BLACK, WHITE

class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.image = pygame.image.load('player.png')
        self.image2 = pygame.image.load('player_2.png')
        self.rect = pygame.Rect(50,int(480/2) - 16, 32, 32)  # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        #self.rect.move_ip(0,int(480/2) - 16)

    def update(self):
        self.rect.move_ip(*self.velocity)

class Monster(pygame.sprite.Sprite):

    def __init__(self, screen, x, y):
        super().__init__()
        self.screen = screen
        self.image = pygame.image.load('monster.png')
        self.image2 = pygame.image.load('monster_2.png')
        self.rect = pygame.Rect(0,0, HALF_MONSTER_SIZE*2, HALF_MONSTER_SIZE*2) # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        self.rect.move_ip(x,y)

    def update(self):
        self.rect.move_ip(*self.velocity)

class Shoot(pygame.sprite.Sprite):

    def __init__(self, screen, x, y):
        super().__init__()
        self.screen = screen
        self.image = pygame.image.load('shoot.png')
        self.rect = pygame.Rect(-100,-100, 15, 5) # Get rect of some size as 'image'.
        self.velocity = [0, 0]
        self.rect.move_ip(x,y)
        self.ready = True

    def update(self):
        self.rect.move_ip(*self.velocity)

        if self.rect.x > 720:
            self.ready = True
            self.velocity = [0,0]

    def move_to(self, x, y):
        self.rect.move_ip(x - self.rect.x + HALF_MONSTER_SIZE*2, y - self.rect.y + HALF_MONSTER_SIZE)
        self.ready = False

    def is_ready(self):
        return self.ready

    def reload(self):
        self.rect.x = 800



class Walls:
    
    def __init__(self, screen, cave_height):
        self.screen = screen
        self.cave_height = [cave_height] * 720
        self.middle = [int(480/2)] * 720
        self.trend = [-1,1][random.randrange(2)]
        self.trend_counter = 0

    def draw(self):
        for x, y in enumerate(self.middle):
            self.screen.set_at((x, y + self.cave_height[x]), WHITE)
            self.screen.set_at((x, y - self.cave_height[x]), WHITE)
    
    def get_cave_height(self, x):
        return self.cave_height[x]

    def update_trend(self):

        if self.trend_counter > 100:
            self.trend_counter = 0

            if self.middle[-1] < self.cave_height[-1]:
                self.trend = 1
            elif self.middle[-1] > 480 - self.cave_height[-1]:
                self.trend = -1
            else: 
                self.trend = [-1,1][random.randrange(2)]


    def update(self, dt, gamespeed):

        number_to_move = math.ceil(gamespeed*dt)
        self.trend_counter += number_to_move
        self.update_trend()

        cave_heigth = 200

        for _ in range(number_to_move):
            self.middle.pop(0)
            self.cave_height.pop(0)
        
        while len(self.middle) < 800:
            rand = random.randint(0,1)
            for x in range(random.randint(5,10)):
                self.middle.append(self.middle[-1] + rand*self.trend)

                if random.random() < 0.005 and self.cave_height[-1] > 30:
                    self.cave_height.append(self.cave_height[-1] - 1)
                else:
                    self.cave_height.append(self.cave_height[-1])

    def check_collision(self, rect):

        x_pos = rect.x
        y_pos = rect.y

        col = False
        heights = self.cave_height[x_pos:x_pos+HALF_MONSTER_SIZE * 2]

        for n, y in enumerate(self.middle[x_pos:x_pos+HALF_MONSTER_SIZE * 2]):
            upper = y + heights[n]
            lower = y - heights[n] 

            if y_pos + 32 > upper or y_pos <= lower:
                col = True
                
        return col

    def get_middle(self):
        return self.middle[720]

class InfoText:
    def __init__(self, screen):
        self.screen = screen
        self.cords = pygame.font.SysFont('Consolas', 32)

    def update(self, level, points):
        render = self.cords.render(f'Level: {level}, Points: {int(points)}', True, pygame.color.Color('White'))
        self.screen.blit(render, (10, 10))

class MonsterHandler:

    def __init__(self, screen):
        self.screen = screen
        self.monsters = []
    
    def add_monster(self,x,y):
        self.monsters.append({'monster': Monster(self.screen, x, y), 'start_y': y, 'mov_dir' : [-1,1][random.randrange(2)]})

    def update_monsters(self, dt, gamespeed, walls):

        new_monsters = []

        for monster in self.monsters:
            rect = monster['monster'].rect
            x = rect.x + HALF_MONSTER_SIZE
            mov_dir = monster['mov_dir']
            start_y = monster['start_y']

            if mov_dir == 1 and rect.y + 2*HALF_MONSTER_SIZE > start_y + walls.get_cave_height(x):
                mov_dir = -1
            elif mov_dir == -1 and rect.y - HALF_MONSTER_SIZE < start_y - walls.get_cave_height(x):
                mov_dir = 1

            monster['mov_dir'] = mov_dir

            rect.move_ip(-math.ceil(gamespeed * dt), mov_dir)

            if rect.x + HALF_MONSTER_SIZE * 2 > 0:
                new_monsters.append(monster)

        self.monsters = new_monsters
    
    def draw_monsters(self, toggle):
        for monster in self.monsters:
            if toggle:
                self.screen.blit(monster['monster'].image, monster['monster'].rect)
            else:
                self.screen.blit(monster['monster'].image2, monster['monster'].rect)

    def collide(self, rect):
        col = False
        for monster in self.monsters:
            if monster['monster'].rect.colliderect(rect):
                col = True

        return col

    def is_hit(self, projectile):
        old = len(self.monsters)
        self.monsters = [monster for monster in self.monsters if not monster['monster'].rect.colliderect(projectile.rect)]
        new = len(self.monsters)

        if old != new:
            projectile.reload()
            return 10
        else:
            return 0
