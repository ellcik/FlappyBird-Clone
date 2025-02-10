import pygame
import random
import os

pygame.init()
pygame.mixer.init()


WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")


background = pygame.image.load("Photos/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pygame.mixer.music.load("Sounds/music.mp3")
pygame.mixer.music.play(-1)


bird_img = pygame.image.load("Photos/bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (40, 30))


bird_x = 50
bird_y = HEIGHT // 2
gravity = 0.5
jump_strength = -8
bird_velocity = 0


pipe_width = 50
pipe_gap = 200
pipes = []
pipe_speed = 3
spawn_pipe_event = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_pipe_event, 1500)


font = pygame.font.Font(None, 36)
score = 0
game_over = False

levels = {
    1: {"pipes": 5, "target_score": 10, "gap": 170},
    2: {"pipes": 10, "target_score": 20, "gap": 160},
    3: {"pipes": 15, "target_score": 30, "gap": 150},
    4: {"pipes": 20, "target_score": 40, "gap": 140}
}

max_level = 4

flap_sound = pygame.mixer.Sound("Sounds/flap.wav")
hit_sound = pygame.mixer.Sound("Sounds/hit.wav")

class Pipe:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.passed = False



def read_progress():
    if os.path.exists("progress.txt"):
        with open("progress.txt", "r") as file:
            return int(file.read())
    return 1


def save_progress(level):
    with open("progress.txt", "w") as file:
        file.write(str(level))


def show_next_level_screen():
    global current_level, game_over

    pygame.mixer.Sound("Sounds/win_sound.mp3").play()

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    screen.blit(overlay, (0, 0))

    level_message = font.render(f"Level {current_level} Completed!", True, (0, 255, 0))
    screen.blit(level_message, (WIDTH // 2 - level_message.get_width() // 2, HEIGHT // 2 - 100))

    next_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2, 140, 50)
    pygame.draw.rect(screen, (0, 200, 0), next_button, border_radius=15)
    next_text = font.render("Next Level", True, (255, 255, 255))
    screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.collidepoint(event.pos):
                    waiting = False

    game_over = False
    reset_game(current_level + 1)


def reset_game(level):
    global bird_y, bird_velocity, pipes, score, game_over, current_level
    bird_y = HEIGHT // 2
    bird_velocity = 0
    score = 0
    game_over = False
    current_level = level
    pipes = []
    spawn_pipe(current_level)


def show_game_over_dialog():
    global game_over, score, high_score

    pygame.mixer.Sound("Sounds/game_over.mp3").play()

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    screen.blit(overlay, (0, 0))

    game_over_text = font.render("Game Over!", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

    restart_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2, 140, 50)
    pygame.draw.rect(screen, (0, 200, 0), restart_button, border_radius=15)
    restart_text = font.render("Restart", True, (255, 255, 255))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

    home_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 70, 140, 50)
    pygame.draw.rect(screen, (200, 0, 0), home_button, border_radius=15)
    home_text = font.render("Home", True, (255, 255, 255))
    screen.blit(home_text, (WIDTH // 2 - home_text.get_width() // 2, HEIGHT // 2 + 80))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.collidepoint(event.pos):
                    save_progress(current_level)
                    reset_game(current_level)
                    return
                elif home_button.collidepoint(event.pos):
                    save_progress(current_level)
                    show_main_menu()
                    return



def draw_bird(x, y):
    screen.blit(bird_img, (x, int(y)))


def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, (34, 177, 76), pipe.rect)


def spawn_pipe(level):
    global pipes
    pipes = []

    pipe_count = levels[level]["pipes"]
    pipe_gap = levels[level]["gap"]

    last_x = WIDTH

    for i in range(pipe_count):
        pipe_height = random.randint(120, HEIGHT // 2)
        gap_height = pipe_gap

        top_pipe_y = 0
        bottom_pipe_y = pipe_height + gap_height

        if bottom_pipe_y > HEIGHT - 100:
            bottom_pipe_y = HEIGHT - 100

        horizontal_gap = last_x + random.randint(150, 250 )

        top_pipe = Pipe(horizontal_gap, top_pipe_y, pipe_width, pipe_height)
        bottom_pipe = Pipe(horizontal_gap, bottom_pipe_y, pipe_width, HEIGHT - bottom_pipe_y)

        pipes.append(top_pipe)
        pipes.append(bottom_pipe)

        last_x = horizontal_gap


def check_level_up():
    global current_level

    if score >= levels[current_level]["target_score"]:
        if current_level < max_level:
            show_next_level_screen()
        else:
            show_victory_message()


def show_victory_message():
    global game_over

    pygame.mixer.Sound("Sounds/win_sound.mp3").play()

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    screen.blit(overlay, (0, 0))

    win_font = pygame.font.Font(None, 70)
    win_text = win_font.render("YOU WIN!", True, (255, 255, 255))
    shadow_text = win_font.render("YOU WIN!", True, (0, 0, 0))

    screen.blit(shadow_text, (WIDTH // 2 - shadow_text.get_width() // 2 + 2, HEIGHT // 2 - 100 + 2))
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 100))

    new_game_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2, 140, 50)
    pygame.draw.rect(screen, (0, 200, 0), new_game_button, border_radius=15)
    new_game_text = font.render("New Game", True, (255, 255, 255))
    screen.blit(new_game_text, (WIDTH // 2 - new_game_text.get_width() // 2, HEIGHT // 2 + 10))

    home_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 70, 140, 50)
    pygame.draw.rect(screen, (200, 0, 0), home_button, border_radius=15)
    home_text = font.render("Home", True, (255, 255, 255))
    screen.blit(home_text, (WIDTH // 2 - home_text.get_width() // 2, HEIGHT // 2 + 80))

    pygame.display.update()


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    save_progress(1)
                    reset_game(1)
                    return
                elif home_button.collidepoint(event.pos):
                    save_progress(1)
                    show_main_menu()
                    return

def show_main_menu():
    global current_level

    menu_running = True
    logo = pygame.image.load("Photos/logo.png").convert_alpha()
    logo = pygame.transform.scale(logo, (200, 80))

    last_level = read_progress()

    while menu_running:
        screen.blit(background, (0, 0))

        screen.blit(logo, (WIDTH // 2 - logo.get_width() // 2, 50))

        level_font = pygame.font.Font(None, 40)
        if last_level > 1:
            level_text = f"Last Reached Level: {last_level}"
        else:
            level_text = "Start from Level 1"
        level_text_render = level_font.render(level_text, True, (100, 150, 170))
        shadow_text = level_font.render(level_text, True, (0, 0, 0))

        screen.blit(shadow_text, (WIDTH // 2 - shadow_text.get_width() // 2 + 2, 225 + 2))
        screen.blit(level_text_render, (WIDTH // 2 - level_text_render.get_width() // 2, 225))

        start_button = pygame.Rect(WIDTH // 2 - 60, 280, 120, 50)
        quit_button = pygame.Rect(WIDTH // 2 - 60, 350, 120, 50)

        pygame.draw.rect(screen, (0, 200, 0), start_button, border_radius=15)
        pygame.draw.rect(screen, (200, 0, 0), quit_button, border_radius=15)

        start_text = font.render("Start", True, (255, 255, 255))
        quit_text = font.render("Quit", True, (255, 255, 255))

        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 295))
        screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 365))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    current_level = last_level
                    reset_game(current_level)
                    menu_running = False
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()

show_main_menu()
current_level = read_progress()
reset_game(current_level)
spawn_pipe(current_level)


while True:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
            flap_sound.play()
            bird_velocity = jump_strength


    if current_level == max_level and score >= levels[current_level]["target_score"]:
        show_victory_message()

    if score >= levels[current_level]["target_score"]:
        check_level_up()

    if not game_over:
        bird_velocity += gravity
        bird_y += bird_velocity

        for pipe in pipes:
            pipe.rect.x -= pipe_speed

        pipes = [pipe for pipe in pipes if pipe.rect.x > -pipe_width]

        for pipe in pipes:
            if pipe.rect.colliderect(pygame.Rect(bird_x, bird_y, 50, 35)):
                game_over = True
                hit_sound.play()
                show_game_over_dialog()

        if bird_y < 0 or bird_y > HEIGHT:
            game_over = True
            hit_sound.play()
            show_game_over_dialog()

        # Броење на поени
        for pipe in pipes:
            if pipe.rect.x + pipe_width < bird_x and not pipe.passed:
                pipe.passed = True
                score += 1

    draw_bird(bird_x, bird_y)
    draw_pipes(pipes)

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    level_text = font.render(f"Level: {current_level}", True, (255, 255, 255))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 10))

    pygame.display.update()
    pygame.time.delay(30)
