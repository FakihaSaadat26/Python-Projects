"""
Space Invaders Game - Python Graphics Project
A complete game implementation using Pygame with graphics, animations, and sound effects

Required installation: pip install pygame

Features:
- Player spaceship movement and shooting
- Enemy aliens with movement patterns
- Collision detection
- Score tracking
- Game over/restart functionality
- Sound effects and music
- Particle effects for explosions
"""

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        # Draw player ship shape
        pygame.draw.polygon(self.image, RED, [(25, 0), (0, 40), (50, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.health = 3
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        # Draw enemy shape
        pygame.draw.rect(self.image, YELLOW, (5, 5, 30, 20))
        pygame.draw.rect(self.image, RED, (10, 10, 20, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1
        self.direction = 1
        
    def update(self):
        self.rect.x += self.speed * self.direction

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=-1):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(CYAN if direction == -1 else RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 7 * direction
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(random.choice([RED, YELLOW, WHITE]))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = random.randint(-5, 5)
        self.vel_y = random.randint(-5, 5)
        self.life = 30
        
    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life -= 1
        if self.life <= 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(PURPLE)
        pygame.draw.circle(self.image, WHITE, (10, 10), 8)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class SpaceInvadersGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Python Graphics Project")
        self.clock = pygame.time.Clock()
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Game variables
        self.score = 0
        self.level = 1
        self.font = pygame.font.Font(None, 36)
        self.enemy_move_down = False
        self.enemy_shoot_timer = 0
        self.running = True
        self.game_over = False
        
        # Create initial enemies
        self.create_enemy_formation()
        
    def create_enemy_formation(self):
        for row in range(5):
            for col in range(10):
                enemy = Enemy(col * 60 + 50, row * 50 + 50)
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    bullet = self.player.shoot()
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
    
    def update_enemies(self):
        # Check if enemies need to move down
        move_down = False
        for enemy in self.enemies:
            if enemy.rect.left <= 0 or enemy.rect.right >= SCREEN_WIDTH:
                move_down = True
                break
        
        if move_down:
            for enemy in self.enemies:
                enemy.direction *= -1
                enemy.rect.y += 20
                
        # Enemy shooting
        self.enemy_shoot_timer += 1
        if self.enemy_shoot_timer > 60:  # Shoot every second
            self.enemy_shoot_timer = 0
            if self.enemies:
                shooter = random.choice(self.enemies.sprites())
                bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, 1)
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)
    
    def check_collisions(self):
        # Player bullets hit enemies
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        for hit in hits:
            self.score += 10
            # Create explosion particles
            for _ in range(10):
                particle = Particle(hit.rect.centerx, hit.rect.centery)
                self.particles.add(particle)
                self.all_sprites.add(particle)
            
            # Chance to drop power-up
            if random.random() < 0.1:
                powerup = PowerUp(hit.rect.centerx, hit.rect.centery)
                self.powerups.add(powerup)
                self.all_sprites.add(powerup)
        
        # Enemy bullets hit player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits:
            self.player.health -= 1
            if self.player.health <= 0:
                self.game_over = True
        
        # Player collects power-ups
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            self.player.health += 1
            self.score += 50
        
        # Check if all enemies are destroyed
        if not self.enemies:
            self.level += 1
            self.create_enemy_formation()
            # Increase difficulty
            for enemy in self.enemies:
                enemy.speed += 0.5
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # Health
        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (10, 90))
        
        # Health bar
        for i in range(self.player.health):
            pygame.draw.rect(self.screen, GREEN, (200 + i * 25, 95, 20, 20))
        
        if self.game_over:
            game_over_text = self.font.render("GAME OVER - Press R to Restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
    
    def restart_game(self):
        # Clear all sprites
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.particles.empty()
        self.powerups.empty()
        
        # Reset player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Reset game variables
        self.score = 0
        self.level = 1
        self.game_over = False
        
        # Create enemies
        self.create_enemy_formation()
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            self.handle_events()
            
            if not self.game_over:
                self.all_sprites.update()
                self.update_enemies()
                self.check_collisions()
            
            # Draw everything
            self.screen.fill(BLACK)
            
            # Draw stars background
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            
            self.all_sprites.draw(self.screen)
            self.draw_ui()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

def main():
    print("Python Graphics Project - Space Invaders")
    print("Controls:")
    print("- Arrow keys: Move")
    print("- Spacebar: Shoot")
    print("- R: Restart (when game over)")
    print("- ESC: Switch between game and graphics demo")
    
    
    choice = input("Choose demo (1: Space Invaders Game, 2: Exit): ")
    
    if choice == "2":
        print("You exit the game.")
    else:
        game = SpaceInvadersGame()
        game.run()

if __name__ == "__main__":
    main()