'''
@author: Kulvinder Lotay
@version: v0.1
@description: The code below loads all the game graphics and sets the global 
              constants. All assets are taken from opengameart.org
              
              Below that, it defines the classes for Vehicle,
              of which Spaceship is a subclass with the movement properties
              to move along the x-direction.
              Other classes defined are the Obstacle class,
              of which Asteroid and Debris are subclasses of.
              Finally there is a bullets class, which is used in the shoot
              method for spaceship.
              
              The Game initalizes the sprites and background, and checks for
              collisions between the spaceship and obstacles. If this occurs
              the game ends, although there will be an implementation of lives
              in the next version. Bullets shot from the spaceship are also
              checked against the obstacle list for collisions, if that occurs
              both objects are destroyed. When an obstacle is shot and
              successfully destroyed, the score is incremented, although it is
              not displayed on screen in the v0.1 of the game, but is rather
              printed to the console. A high score and feedback system still
              need to be implemented in order to make use of the scoring system.
              
@instruction: In order to play the game, the left, right and spacebar keys are
              used in order to interact with the player spaceship. You may move
              left of right, and press space in order to shoot obstacles in
              your path (enemy spaceships will be implemented in next version).
              Make sure to avoid being hit by obstacles, as you will lose the
              game if that occurs.
            


'''
import pygame
import random
 
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
 
# --- Global constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
 
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600

FPS = 60
 
#Load all game graphics
background = pygame.image.load(path.join(img_dir, 'spacefield_a-000.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_rect = background.get_rect()

spaceship_img = pygame.image.load(path.join(img_dir, 'player.png'))
asteroid_img = pygame.image.load(path.join(img_dir, 'meteorSmall.png'))
debris_img = pygame.image.load(path.join(img_dir, 'enemyUFO.png'))
bullet_img = pygame.image.load(path.join(img_dir, 'laserGreen.png'))
 
# --- Classes ---
 
 
class Vehicle(pygame.sprite.Sprite):
    """ This class represents a vehicle. """
    def __init__(self, x_position, y_position):
        super().__init__()
        self.position = [x_position, y_position]

class Spaceship(Vehicle):
    """ This class represents the spaceship. """
    width = 50
    height = 40
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH / 2, SCREEN_HEIGHT - Spaceship.height - 30)
        self.lives = 3
        self.image = pygame.transform.scale(spaceship_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.x_speed = 0
 
    def update(self):
        """ Update the spaceship location. """
        # Reset space speed to zero to ensure player doesn't keep moving
        self.x_speed = 0
        
        # Check for left or right key presses, and adjust x_speed accordingly
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x_speed = -9
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x_speed = 9
        self.rect.x += self.x_speed
        
        # Make sure spaceship does not go off screen
        if self.rect.x + 50 > SCREEN_WIDTH:
            self.rect.x = SCREEN_WIDTH - Spaceship.width
        if self.rect.x < 0:
            self.rect.x = 0
            
    def shoot(self, all_sprites_list, bullet_list):
        bullet = Bullet(self.rect.x + (Spaceship.width / 2) - (Bullet.bullet_width / 2), self.rect.y)
        all_sprites_list.add(bullet)
        bullet_list.add(bullet)
        
        
            
class Obstacle(pygame.sprite.Sprite):
    """ This class represents an obstacle the player must dodge or shoot. """
    def __init__(self, width, height):
        super().__init__()
        
        self.velocity = [random.randrange(-2, 2), random.randrange(1, 5)]
        
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        
    def reset_pos(self):
        """ Call when the obstacle falls off the screen. """
        self.velocity = [random.randrange(-2, 2), random.randrange(1, 4)]
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = random.randrange(-300, -20)
        
    def update(self):
        """ Move the obstacle. """
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # If obstacle moves off screen, bring it back on screen
        if self.rect.y > SCREEN_HEIGHT + self.height:      
            self.reset_pos()
            
class Asteroid(Obstacle):
    """ This class represents an asteroid obstacle """
#     color = YELLOW
    
    def __init__(self):
        self.width = random.randrange(20, 40)
        self.height = random.randrange(20, 40)
        
        super().__init__(self.width, self.height)
        self.image = asteroid_img
        self.image.set_colorkey(BLACK)
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = random.randrange(-300, -20)
        
class Debris(Obstacle):
    """ This class represents debri obstacles """
#     color = RED
    
    def __init__(self):
        self.width = random.randrange(10, 16)
        self.height = random.randrange(10, 16)
        
        super().__init__(self.width, self.height)
        self.image = debris_img
        self.image = pygame.transform.scale(debris_img, (self.width, self.height))
        self.image.set_colorkey(BLACK)
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = random.randrange(-300, 20)
        
        
class Bullet(pygame.sprite.Sprite):
    bullet_width = 10
    bullet_height = 20
    
    """ This class represents bullets that the spaceship shoots """
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_speed = -10
        
    def update(self):
        self.rect.y += self.y_speed
        # Check if bullet moves off screen
        if self.rect.y < 0:
            self.kill()

class Game(object):
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """
 
    def __init__(self):
        """ Constructor. Create all our attributes and initialize
        the game. """
 
        self.score = 0
        self.game_over = False
        self.difficulty = 0
        
        # Create sprite lists
        self.bullet_list = pygame.sprite.Group()
        self.obstacle_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        
 
        # Create the block sprites
        for _i in range(30):
            asteroid = Asteroid()
 
            self.obstacle_list.add(asteroid)
            self.all_sprites_list.add(asteroid)
            
        for _x in range(5):
            debris = Debris()

            self.obstacle_list.add(debris)
            self.all_sprites_list.add(debris)
 
        # Create the player spaceship
        self.spaceship = Spaceship()
        self.all_sprites_list.add(self.spaceship)
 
    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.__init__()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.spaceship.shoot(self.all_sprites_list, self.bullet_list)
 
        return False
 
    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        if not self.game_over:
            # Move all the sprites
            self.all_sprites_list.update()
 
            # See if the player spaceship has collided with anything.
            if (pygame.sprite.spritecollide(self.spaceship, self.obstacle_list, True)):
                self.game_over = True
            
            # See if any of the bullets have hit any of the obstacles.
            bullet_hit_list = pygame.sprite.groupcollide(self.bullet_list, self.obstacle_list, True, True)
 
            # Check the list of collisions.
            for _obstacle in bullet_hit_list:
                asteroid = Asteroid()
                self.all_sprites_list.add(asteroid)
                self.obstacle_list.add(asteroid)
                self.score += 1
                print(self.score)
 
            if len(self.obstacle_list) == 0:
                self.game_over = True
 
    def display_frame(self, screen):
        """ Display everything to the screen for the game. """
        screen.fill(BLACK)
        screen.blit(background, background_rect)
 
        if self.game_over:
            # font = pygame.font.Font("Serif", 25)
            font = pygame.font.SysFont("serif", 25)
            text = font.render("Game Over, click to restart", True, YELLOW)
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])
 
        if not self.game_over:
            self.all_sprites_list.draw(screen)
 
        pygame.display.flip()
 
 
def main():
    """ Main program function. """
    # Initialize Pygame and set up the window
    pygame.init()
 
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("Project S")
 
    # Create our objects and set the data
    done = False
    clock = pygame.time.Clock()
 
    # Create an instance of the Game class
    game = Game()
 
    # Main game loop
    while not done:
 
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
 
        # Update object positions, check for collisions
        game.run_logic()
 
        # Draw the current frame
        game.display_frame(screen)
 
        # Pause for the next frame
        clock.tick(FPS)
 
    # Close window and exit
    pygame.quit()
 
# Call the main function, start up the game
if __name__ == "__main__":
    main()