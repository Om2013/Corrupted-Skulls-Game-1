import random 
# ------------------- Difficulty -------------------
difficulty = input("Select difficulty (E=Easy / M=Medium / H=Hard / R=Random): ").strip().upper()
if difficulty == "R":
    difficulty = random.choice(["E", "M", "H"])
    print(f"Your difficulty is '{difficulty}'")

if difficulty == "E":
    cauldron_speed, skull_spawn_rate, max_health, total_skeleton_health = 15, 60, 120, 40
elif difficulty == "M":
    cauldron_speed, skull_spawn_rate, max_health, total_skeleton_health = 10, 45, 130, 80
elif difficulty == "H":
    cauldron_speed, skull_spawn_rate, max_health, total_skeleton_health = 8, 30, 140, 120
else:
    print("Invalid choice, defaulting to Medium")
    difficulty == "M"
    cauldron_speed, skull_spawn_rate, max_health, total_skeleton_health = 10, 45, 130, 80

#-------------------Libraries------------------------
import pygame
import pymunk
import pymunk.pygame_util
import sys

# ------------------- Pygame Setup -------------------
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss: Corrupted Skulls")
clock = pygame.time.Clock()
FPS = 60

# ------------------- Pymunk Setup -------------------
space = pymunk.Space()
space.gravity = (0, 600)

# ------------------- Fonts -------------------
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 50)

# ------------------- Game Variables -------------------
frame_count = 0
skulls = []
running = True
score = 0
cauldron_health = max_health
skeleton_health = total_skeleton_health
gameover = False
gamewin = False
max_frames = 4200
cauldron_x = WIDTH // 2

# ------------------- Assets -------------------
skull_image = pygame.image.load("skull_image.png").convert_alpha()
skull_image = pygame.transform.scale(skull_image, (40, 40))
cauldron_image = pygame.image.load("cauldron_image.png").convert_alpha()
cauldron_image = pygame.transform.scale(cauldron_image, (200, 200))
background_image = pygame.image.load("background_image.jpg").convert_alpha()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# ------------------- Sounds -------------------
background_music = pygame.mixer.Sound("background_music_cauldron.mp3")
skull_impact = pygame.mixer.Sound("spooky_impact.mp3")
skull_impact.set_volume(0.125)
gameover_sound = pygame.mixer.Sound("gameover.wav")
gamewin_sound = pygame.mixer.Sound("gamewin.mp3")
boss_intro_sound = pygame.mixer.Sound("boss_intro.mp3")
boss_intro_sound.set_volume(1.0)

# ------------------- Play Boss Intro Non-Blocking -------------------
background_music.set_volume(0.5)    
boss_intro_sound.play(1)          
background_music.play(-1)   
background_music.set_volume(1)

# ------------------- Functions -------------------
def create_skull():
    x = random.randint(50, WIDTH - 50)
    body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 15))
    body.position = (x, 0)
    shape = pymunk.Circle(body, 15)
    shape.elasticity = 0.4
    space.add(body, shape)
    return body, shape

def draw_cauldron(x):
    screen.blit(cauldron_image, (x - 100, HEIGHT - 200))

def draw_health_bar(value, max_value, y, color=(0, 255, 0), label="Health"):
    margin, height = 20, 30  # space from screen edges and height of the bar
    bar_width = WIDTH - 2 * margin  # total width of the bar minus margins
    pygame.draw.rect(screen, (255, 0, 0), (margin, y, bar_width, height))  # draw background (missing health) in red
    pygame.draw.rect(screen, color, (margin, y, bar_width * value / max_value, height))  # width proportional to current health
    screen.blit(font.render(f"{label}: {value}/{max_value}", True, (255, 255, 255)), (margin, y + height + 5))  # draw text below bar


def timer(frame_count, fps, total_frames):
    time_left = max(0, (total_frames - frame_count) // fps)
    text = font.render(f"Time: {time_left}", True, (255, 255, 255))
    screen.blit(text, (WIDTH - 200, 200))
    return time_left

# --- Main Loop ---
while running:
    screen.blit(background_image, (0, 0))
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move Cauldron
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and cauldron_x > 100:
        cauldron_x -= cauldron_speed
    if keys[pygame.K_RIGHT] and cauldron_x < WIDTH - 100:
        cauldron_x += cauldron_speed

    # Spawn Skulls
    if frame_count % skull_spawn_rate == 0 and len(skulls) + (total_skeleton_health - skeleton_health) < total_skeleton_health:
        skulls.append(create_skull())

    # Physics Step
    space.step(1 / FPS)

    # Skull Logic
    for body, shape in skulls[:]:
        x, y = body.position
        if y > HEIGHT - 120 and abs(x - cauldron_x) < 100:  # Caught
            score += 10
            skeleton_health -= 1
            skull_impact.play()
            space.remove(body, shape)
            skulls.remove((body, shape))
        elif y > HEIGHT + 50:  # Missed
            cauldron_health -= 10
            cauldron_health = max(cauldron_health, 0)
            space.remove(body, shape)
            skulls.remove((body, shape))

    # Draw Skulls
    for body, shape in skulls:
        x, y = body.position
        screen.blit(skull_image, (int(x) - 20, int(y) - 20))

    # Draw UI
    draw_cauldron(cauldron_x)
    draw_health_bar(skeleton_health, total_skeleton_health, y=20, color=(0, 200, 255), label="Boss : Corrupted Skulls Health")
    draw_health_bar(cauldron_health, max_health, y=100, color=(0, 255, 0), label="Cauldron Health")
    screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (WIDTH - 200, 250))
    timer(frame_count, FPS, max_frames)

    # Win/Lose Logic
    if not gameover:
        if cauldron_health <= 0 or frame_count >= max_frames:
            gamewin = False
            gameover = True
        elif skeleton_health <= 0 and cauldron_health > 0:
            gamewin = True
            gameover = True

    # Game Over Screen
    if gameover:
        screen.fill("white")
        background_music.stop()
        gameover_sound.play()
        text = font.render("Corrupted Cauldron", True, "red")
        if gamewin:
            text = font.render("YOU SAVED THE CAULDRON!", True, "green")
        
           
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
