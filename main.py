import pygame
from config import HALF_MONSTER_SIZE, BLACK, WHITE, COLORS
from entities import Player, MonsterHandler, Monster, Shoot, Walls, InfoText

successes, failures = pygame.init()
print("Initializing pygame: {0} successes and {1} failures.".format(successes, failures))

screen = pygame.display.set_mode((720, 480))
clock = pygame.time.Clock()
FPS = 60

running = True

def reset_game():

    global monster_spawner, gamespeed, jump, jump_count, gravity, monster_per_second, level, timer, points
    monster_spawner = 0
    gamespeed = 200
    jump = False
    jump_count = 1
    gravity = 10
    monster_per_second = 1/3
    level = 1
    timer = 0
    points = 0

    global player, walls, text, mh, projectile, pause_text

    player = Player(screen)
    walls = Walls(screen, 150)
    text = InfoText(screen)
    mh = MonsterHandler(screen)
    projectile = Shoot(screen, -100, -100)
    pause_text = pygame.font.SysFont('Consolas', 32).render('Du förlorade', True, pygame.color.Color('White'))


def have_lost(player):
    return (walls.check_collision(player.rect) | mh.collide(player.rect))

reset_game()

toggle = True
animate = 0

while running:
    dt = clock.tick(FPS) / 1000 
    screen.fill(COLORS[level])

    # Increasing difficlty
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                jump = True
                jump_count = 1
            if event.key == pygame.K_k and projectile.is_ready():
                projectile.move_to(player.rect.x, player.rect.y)
                projectile.velocity[0] = 400*dt
            if event.key == pygame.K_r and have_lost(player):
                reset_game()

    if not have_lost(player):
        timer += dt

        if (timer // 10 + 1) != level:
            level += 1
            gamespeed += 50
            monster_per_second = monster_per_second * 2

        if jump:
            if jump_count >= 0:
                y = (jump_count * abs(jump_count)) * 5
                jump_count -= dt*5
                player.velocity[1] = -y
            else:
                jump_count = 2
                player.velocity[1] = 0
                jump = False

        player.velocity[1] += gravity * dt

        player.update()
        projectile.update()
        
        monster_spawner+=dt
        
        walls.update(dt, gamespeed)
        mh.update_monsters(dt, gamespeed, walls)

        if monster_spawner > 1/monster_per_second:
            mh.add_monster(720, walls.get_middle() - HALF_MONSTER_SIZE) 
            monster_spawner = 0

        points += mh.is_hit(projectile) * level
        points += dt * level

    else:
        screen.blit(pause_text, (100, 100))
     
    mh.draw_monsters(toggle)
    text.update(level, points)
    walls.draw()

    animate += dt

    if animate > 0.1:
        toggle = not toggle
        animate = 0

    if toggle:
        screen.blit(player.image, player.rect)
    else:
        screen.blit(player.image2, player.rect)
    
    screen.blit(projectile.image, projectile.rect)
    
    pygame.display.update() 