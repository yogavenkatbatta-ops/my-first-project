import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GTA San Andreas Style Race - Realistic Cars")

icon = pygame.image.load("car.ico")
pygame.display.set_icon(icon)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED_RACE = (220, 20, 20)
RED_DARK = (160, 10, 10)
YELLOW_ACCENT = (255, 215, 0)
BLACK_GLOSS = (20, 20, 25)
WHEEL_DARK = (15, 15, 20)
WHEEL_RIM = (180, 190, 200)
GLASS_TINT = (60, 100, 180, 160)
SHADOW = (0, 0, 0, 90)
EXHAUST = (110, 110, 120, 180)
SKY_TOP = (90, 140, 230)
SKY_BOTTOM = (160, 200, 255)
GRASS = (25, 90, 30)
GRASS_LIGHT = (60, 140, 50)
ROAD_ASPHALT = (45, 45, 55)
ROAD_FADE = (75, 75, 85)
LINE_WHITE = (240, 240, 245)
FINISH_BROWN = (120, 60, 20)

# Fonts
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 44)
font_small = pygame.font.Font(None, 32)
font_tiny = pygame.font.Font(None, 26)   # ← ADDED THIS LINE

clock = pygame.time.Clock()

FINISH_DIST = 22000
ROAD_WIDTH = 340
PLAYER_POS_Y = HEIGHT - 140
ACCEL = 0.22
BRAKE = 0.18
FRICTION = 0.968
MAX_SPEED = 22
TURN_SPEED = 0.085
LERP_STRENGTH = 0.18
ANGLE_DAMP = 0.0009

player = {
    'color': RED_RACE, 'x': WIDTH//2, 'target_x': WIDTH//2,
    'speed': 0, 'dist': 0, 'angle': 0, 'trail': []
}
ai_cars = [
    {'color': (70, 110, 220), 'x': 180, 'target_x': 180, 'speed': 7.8, 'dist': 1400, 'angle': 0, 'trail': []},
    {'color': (70, 220, 110), 'x': 420, 'target_x': 420, 'speed': 7.4, 'dist': 900, 'angle': 0, 'trail': []}
]
all_cars = [player] + ai_cars

bg_scroll = 0.0
game_state = 0

def draw_realistic_race_car(car, sx, sy, scale=1.0):
    if scale < 0.25: return

    w = 92 * scale
    h = 38 * scale
    wing_w = 110 * scale
    wing_h = 14 * scale

    # motion trail
    for i, (tx, ty, alpha) in enumerate(car['trail'][-8:]):
        a = int(60 * alpha * (1 - i/8))
        trail_surf = pygame.Surface((int(w*1.1), int(h*1.1)), pygame.SRCALPHA)
        pygame.draw.ellipse(trail_surf, (car['color'][0], car['color'][1], car['color'][2], a), (0, 0, w*1.1, h*1.1))
        screen.blit(trail_surf, (int(tx - w*0.55), int(ty - h*0.5)))

    # shadow
    sh = pygame.Surface((int(100*scale), int(40*scale)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, SHADOW, (0, 10*scale, 100*scale, 20*scale))
    screen.blit(sh, (int(sx - 50*scale), int(sy + 12*scale)))

    # main body - aerodynamic race shape
    points = [
        (sx - w*0.48, sy - h*0.1),
        (sx + w*0.48, sy - h*0.1),
        (sx + w*0.52, sy + h*0.35),
        (sx + w*0.50, sy + h*0.78),
        (sx - w*0.50, sy + h*0.78),
        (sx - w*0.52, sy + h*0.35),
    ]
    pygame.draw.polygon(screen, BLACK_GLOSS, points, 4)
    pygame.draw.polygon(screen, car['color'], points)

    # darker lower body
    lower = [(sx - w*0.50, sy + h*0.45), (sx + w*0.50, sy + h*0.45),
             (sx + w*0.52, sy + h*0.78), (sx - w*0.52, sy + h*0.78)]
    pygame.draw.polygon(screen, RED_DARK, lower)

    # yellow side stripe
    stripe = [(sx - w*0.45, sy + h*0.25), (sx + w*0.45, sy + h*0.25),
              (sx + w*0.48, sy + h*0.55), (sx - w*0.48, sy + h*0.55)]
    pygame.draw.polygon(screen, YELLOW_ACCENT, stripe)

    # cockpit glass
    glass = pygame.Rect(sx - w*0.32, sy - h*0.05, w*0.64, h*0.55)
    pygame.draw.ellipse(screen, GLASS_TINT, glass)

    # large rear wing
    wing_points = [
        (sx - wing_w/2, sy - h*0.15),
        (sx + wing_w/2, sy - h*0.15),
        (sx + wing_w/2 - 8*scale, sy + wing_h - h*0.15),
        (sx - wing_w/2 + 8*scale, sy + wing_h - h*0.15)
    ]
    pygame.draw.polygon(screen, BLACK_GLOSS, wing_points)
    pygame.draw.polygon(screen, car['color'], [(x,y+4*scale) for x,y in wing_points])

    # wheels
    for wx, wy_off in [(-w*0.42, h*0.22), (w*0.42, h*0.22), (-w*0.42, h*0.68), (w*0.42, h*0.68)]:
        wx += sx
        wy = sy + wy_off
        pygame.draw.circle(screen, WHEEL_DARK, (int(wx), int(wy)), int(13*scale))
        pygame.draw.circle(screen, WHEEL_RIM, (int(wx), int(wy)), int(9*scale))
        pygame.draw.circle(screen, BLACK, (int(wx), int(wy)), int(5*scale))

    # number 44 (like in the photo)
    num = font_tiny.render("44", True, WHITE)
    screen.blit(num, (sx - 12*scale, sy + h*0.1))

def draw_road(scrolled):
    y = -scrolled % 1800 + HEIGHT
    while y > -1800:
        prog = max(0.0, min(1.0, (HEIGHT - y) / HEIGHT))
        alpha = int(100 + 155 * prog)

        s = pygame.Surface((ROAD_WIDTH, 180), pygame.SRCALPHA)
        pygame.draw.rect(s, (*ROAD_ASPHALT, alpha), (0, 0, ROAD_WIDTH, 180))
        pygame.draw.rect(s, (*ROAD_FADE, alpha), (0, 90, ROAD_WIDTH, 90))
        screen.blit(s, (WIDTH//2 - ROAD_WIDTH//2, int(y)))
        y -= 1800

    ly = (-scrolled * 0.48) % 110
    while ly < HEIGHT:
        h = 32 + 20 * (ly / HEIGHT)
        pygame.draw.rect(screen, LINE_WHITE, (WIDTH//2 - 6, int(ly), 12, int(h)))
        ly += 110

    ey = (-scrolled * 0.28) % 70
    while ey < HEIGHT:
        pygame.draw.rect(screen, YELLOW_ACCENT, (WIDTH//2 - ROAD_WIDTH//2 - 16, int(ey), 16, 50))
        pygame.draw.rect(screen, YELLOW_ACCENT, (WIDTH//2 + ROAD_WIDTH//2, int(ey), 16, 50))
        ey += 70

def draw_finish():
    d = FINISH_DIST - player['dist']
    if d > 1200: return
    p = max(0, 1 - d / 1200)
    by = int(35 * p)
    bw, bh = 240, 65
    pygame.draw.rect(screen, FINISH_BROWN, (WIDTH//2 - bw//2, by, bw, bh))
    pygame.draw.rect(screen, BLACK, (WIDTH//2 - bw//2, by, bw, bh), 4)
    t = font_large.render("FINISH", True, WHITE)
    screen.blit(t, t.get_rect(center=(WIDTH//2, by + 10)))

def draw_background(scrolled):
    for i in range(HEIGHT//2):
        t = i / (HEIGHT//2)
        c = (
            int(SKY_TOP[0]*(1-t) + SKY_BOTTOM[0]*t),
            int(SKY_TOP[1]*(1-t) + SKY_BOTTOM[1]*t),
            int(SKY_TOP[2]*(1-t) + SKY_BOTTOM[2]*t)
        )
        pygame.draw.line(screen, c, (0, i), (WIDTH, i))

    gy = -scrolled % 360
    while gy < HEIGHT:
        s = pygame.Surface((WIDTH//2, 360), pygame.SRCALPHA)
        for _ in range(18):
            x = random.randint(0, WIDTH//2)
            y = random.randint(0, 360)
            pygame.draw.circle(s, GRASS_LIGHT, (x, y), random.randint(4,9))
        screen.blit(s, (0, int(gy)))
        screen.blit(pygame.transform.flip(s, True, False), (WIDTH//2, int(gy)))
        gy += 360

    draw_road(scrolled)
    draw_finish()

def draw_hud():
    pos = sorted(all_cars, key=lambda c: c['dist'], reverse=True).index(player) + 1
    spd = int(player['speed'] * 18)
    dist_m = int(player['dist'] / 10)
    txt = f"Pos: {pos}/3   {spd} km/h   {dist_m}m"
    s = font_small.render(txt, True, WHITE)
    screen.blit(s, (12, 12))

running = True
while running:
    dt = clock.tick(60) / 1000.0 * 60
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if game_state == 1 and e.type == pygame.KEYDOWN:
            running = False

    if game_state == 0:
        keys = pygame.key.get_pressed()

        accel = (keys[pygame.K_UP] or keys[pygame.K_w]) - (keys[pygame.K_DOWN] or keys[pygame.K_s]) * 0.4
        player['speed'] += accel * ACCEL
        player['speed'] *= FRICTION
        player['speed'] = max(0, min(MAX_SPEED, player['speed']))

        turn = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        player['target_x'] += turn * TURN_SPEED * 200
        player['target_x'] = max(40, min(WIDTH-40, player['target_x']))

        player['x'] += (player['target_x'] - player['x']) * LERP_STRENGTH
        player['angle'] = (player['target_x'] - WIDTH//2) * ANGLE_DAMP

        player['dist'] += player['speed'] * dt
        bg_scroll = player['dist'] * 0.82

        player['trail'].append((player['x'], PLAYER_POS_Y, player['speed']/MAX_SPEED))
        if len(player['trail']) > 12:
            player['trail'].pop(0)

        for ai in ai_cars:
            ai['speed'] = 7.4 + random.uniform(-0.6, 0.6)
            ai['dist'] += ai['speed'] * dt

            ai['lane_timer'] = ai.get('lane_timer', 0) - dt/60
            if ai['lane_timer'] <= 0:
                ai['target_x'] += random.choice([-90, 90])
                ai['target_x'] = max(40, min(WIDTH-40, ai['target_x']))
                ai['lane_timer'] = random.uniform(2.2, 5.5)

            ai['x'] += (ai['target_x'] - ai['x']) * LERP_STRENGTH * 0.75
            ai['angle'] = (ai['target_x'] - WIDTH//2) * ANGLE_DAMP * 0.7

            ai['trail'].append((ai['x'], PLAYER_POS_Y - (ai['dist']-player['dist'])*0.36, ai['speed']/MAX_SPEED))
            if len(ai['trail']) > 10:
                ai['trail'].pop(0)

            if abs(ai['dist'] - player['dist']) < 320 and abs(ai['x'] - player['x']) < 100:
                ai['speed'] *= 0.88

        if player['dist'] >= FINISH_DIST:
            game_state = 1

        screen.fill(BLACK)
        draw_background(bg_scroll)

        for ai in ai_cars:
            reld = ai['dist'] - player['dist']
            if reld < 60 or reld > 2200: continue
            sc = max(0.28, 1 - reld / 2200)
            y = PLAYER_POS_Y - reld * 0.36
            draw_realistic_race_car(ai, ai['x'], y, sc)

        draw_realistic_race_car(player, player['x'], PLAYER_POS_Y, 1.18)

        draw_hud()

    else:
        screen.fill(BLACK)
        places = sorted(all_cars, key=lambda c: c['dist'], reverse=True)
        pos = places.index(player) + 1

        title = font_large.render("YOU WIN!" if pos == 1 else "Race Over", True, WIN_GOLD if pos == 1 else WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 90)))

        y = HEIGHT//2 - 10
        for i, c in enumerate(places):
            col = WIN_GOLD if c is player else WHITE
            txt = f"{i+1}st: {'You' if c is player else 'Racer'}"
            s = font_medium.render(txt, True, col)
            screen.blit(s, s.get_rect(center=(WIDTH//2, y)))
            y += 60

        inst = font_small.render("Press any key to exit", True, WHITE)
        screen.blit(inst, inst.get_rect(center=(WIDTH//2, HEIGHT - 50)))

    pygame.display.update()

pygame.quit()
sys.exit()