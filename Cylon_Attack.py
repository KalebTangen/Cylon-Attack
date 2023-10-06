import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
FULLSCREEN = True
if FULLSCREEN:
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
else:
    WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)  # Blue color for player's projectiles
RED = (255, 0, 0)  # Red color for projectiles
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 75
PLAYER_SPEED = 5
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
OBSTACLE_SPEED = 3
PROJECTILE_WIDTH, PROJECTILE_HEIGHT = 10, 20
PROJECTILE_SPEED = 8
PLAYER_LIVES = 3
PLAYER_PROJECTILE_DAMAGE = 10
OBSTACLE_PROJECTILE_DAMAGE = 5

# Game states
MENU = 0
GAME = 1

class Player:
    def __init__(self):
        self.image = pygame.image.load("vipers.png")
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.reset_position()
        self.lives = PLAYER_LIVES
        self.projectiles = []
        self.engine_flame_visible = False

    def reset_position(self):
        self.x = (WIDTH - PLAYER_WIDTH) // 2
        self.y = HEIGHT - PLAYER_HEIGHT

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.y -= PLAYER_SPEED
            self.engine_flame_visible = True
            # Prevent the player from going off-screen up
            if self.y < 0:
                self.y = 0
        else:
            self.engine_flame_visible = False
        if keys[pygame.K_DOWN]:
            self.y += PLAYER_SPEED
            # Prevent the player from going off-screen down
            if self.y > HEIGHT - PLAYER_HEIGHT:
                self.y = HEIGHT - PLAYER_HEIGHT

        # Wrap around the screen horizontally (left and right)
        if self.x < 0:
            self.x = WIDTH - PLAYER_WIDTH
        elif self.x > WIDTH - PLAYER_WIDTH:
            self.x = 0

    def shoot(self):
        projectile_x = self.x + (PLAYER_WIDTH // 2) - (PROJECTILE_WIDTH // 2)
        projectile_y = self.y
        self.projectiles.append(Projectile(projectile_x, projectile_y, BLUE))

class Obstacle:
    def __init__(self):
        self.image = pygame.image.load("CylonRadiers.png")
        self.image = pygame.transform.scale(self.image, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        self.reset_position()
        self.projectiles = []

    def reset_position(self):
        self.x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
        self.y = 0

    def move(self):
        self.y += OBSTACLE_SPEED
        if self.y > HEIGHT:
            self.reset_position()

    def shoot(self):
        projectile_x = self.x + (OBSTACLE_WIDTH // 2) - (PROJECTILE_WIDTH // 2)
        projectile_y = self.y + OBSTACLE_HEIGHT
        self.projectiles.append(Projectile(projectile_x, projectile_y, RED))

class Projectile:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = PROJECTILE_WIDTH
        self.height = PROJECTILE_HEIGHT
        self.color = color

    def move(self, speed):
        self.y += speed

class Game:
    def __init__(self):
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cylon Attack")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_state = MENU
        self.player = Player()
        self.obstacles = []
        self.score = 0
        self.enemy_fire_rate = 1.0
        self.enemy_fire_cooldown = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.game_state == MENU:
                    if event.key == pygame.K_UP:
                        self.enemy_fire_rate += 0.1
                    elif event.key == pygame.K_DOWN and self.enemy_fire_rate > 0.1:
                        self.enemy_fire_rate -= 0.1
                    elif event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif self.game_state == GAME:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = MENU  # Return to the menu

    def start_game(self):
        self.game_state = GAME
        self.player = Player()
        self.obstacles = []
        self.score = 0
        self.player.lives = PLAYER_LIVES  # Reset player lives
        self.player.reset_position()  # Reset player position

    def generate_obstacles(self):
        if random.randint(1, 100) < 10:
            obstacle = Obstacle()
            self.obstacles.append(obstacle)

    def update_game(self):
        keys = pygame.key.get_pressed()

        if self.game_state == GAME:
            self.player.move(keys)
            self.generate_obstacles()

            for obstacle in self.obstacles:
                obstacle.move()
                if obstacle.y > HEIGHT:
                    self.obstacles.remove(obstacle)
                    self.score += 10

                if random.uniform(0, 1) < self.enemy_fire_rate and self.enemy_fire_cooldown <= 0:
                    obstacle.shoot()
                    self.enemy_fire_cooldown = 1.0 / self.enemy_fire_rate

            if self.enemy_fire_cooldown > 0:
                self.enemy_fire_cooldown -= 1 / 60

            for projectile in self.player.projectiles:
                projectile.move(-PROJECTILE_SPEED)
                if projectile.y < 0:
                    self.player.projectiles.remove(projectile)

            for projectile in self.player.projectiles:
                for obstacle in self.obstacles:
                    if (
                        projectile.x < obstacle.x + OBSTACLE_WIDTH
                        and projectile.x + projectile.width > obstacle.x
                        and projectile.y < obstacle.y + OBSTACLE_HEIGHT
                        and projectile.y + projectile.height > obstacle.y
                    ):
                        self.player.projectiles.remove(projectile)
                        self.obstacles.remove(obstacle)
                        self.score += 10

            for obstacle in self.obstacles:
                for projectile in obstacle.projectiles:
                    projectile.move(PROJECTILE_SPEED)
                    if (
                        self.player.x < projectile.x + projectile.width
                        and self.player.x + PLAYER_WIDTH > projectile.x
                        and self.player.y < projectile.y + projectile.height
                        and self.player.y + PLAYER_HEIGHT > projectile.y
                    ):
                        self.player.lives -= OBSTACLE_PROJECTILE_DAMAGE
                        obstacle.projectiles.remove(projectile)

            # Collision with enemies
            for obstacle in self.obstacles:
                if (
                    self.player.x < obstacle.x + OBSTACLE_WIDTH
                    and self.player.x + PLAYER_WIDTH > obstacle.x
                    and self.player.y < obstacle.y + OBSTACLE_HEIGHT
                    and self.player.y + PLAYER_HEIGHT > obstacle.y
                ):
                    self.player.lives -= OBSTACLE_PROJECTILE_DAMAGE

            # Check for player out of lives
            if self.player.lives <= 0:
                self.game_state = MENU  # Return to the menu

        elif self.game_state == MENU:
            # Handle menu logic
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def draw_game(self):
        self.screen.fill(BLACK)

        if self.game_state == MENU:
            menu_text = self.font.render("Press SPACE to Start or ESC to Exit", True, WHITE)
            menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(menu_text, menu_rect)
        elif self.game_state == GAME:
            self.screen.blit(self.player.image, (self.player.x, self.player.y))
            if self.player.engine_flame_visible:
                engine_flame_rect = pygame.Rect(self.player.x, self.player.y + PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT // 2)
                pygame.draw.polygon(self.screen, RED, [(engine_flame_rect.left, engine_flame_rect.top),
                                                       (engine_flame_rect.centerx, engine_flame_rect.bottom),
                                                       (engine_flame_rect.right, engine_flame_rect.top)])

            for obstacle in self.obstacles:
                self.screen.blit(obstacle.image, (obstacle.x, obstacle.y))

            for projectile in self.player.projectiles:
                pygame.draw.rect(self.screen, BLUE, (projectile.x, projectile.y, projectile.width, projectile.height))

            for obstacle in self.obstacles:
                for projectile in obstacle.projectiles:
                    pygame.draw.rect(self.screen, RED, (projectile.x, projectile.y, projectile.width, projectile.height))

            lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
            self.screen.blit(lives_text, (10, 10))
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (WIDTH - 10 - score_text.get_width(), 10))

def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update_game()
        game.draw_game()
        pygame.display.flip()  # Update the display
        game.clock.tick(60)

if __name__ == "__main__":
    main()
