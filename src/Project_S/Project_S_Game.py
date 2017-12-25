'''
@author: Kulvinder Lotay
@version: v0.9
@description: The code below loads all the game graphics and sets the global
              constants. All assets are taken from opengameart.org

              Below that, it defines the classes for Vehicle,
              of which Spaceship is a subclass with the movement properties
              to move along the x-direction, player information such as lives,
              health, and powerups, along with a method for shooting
              The EnemyShip class is a subclass
              of Spaceship, which overrides some of its methods.
              Other classes defined are the Explosions, and the Obstacle class,
              of which Asteroid and Debris are subclasses of.
              Finally there is a bullets class, which is used in the shoot
              method for spaceship.

              The Game initalizes the sprites, background and background
              music, and checks for collisions between the spaceship
              and obstacles. If this occurs the player loses some health,
              until health goes below a certain level causing the player
              to lose a life. Bullets shot from the spaceship are also
              checked against the obstacle list for collisions, if that occurs
              both objects are destroyed, unless it is a collision between an
              enemy bullet and player object. When an obstacle is shot and
              successfully destroyed, the score is incremented, displayed
              on the center of the top of the screen.
              There are also methods for collecting the player high score, with
              a prompt, and then displaying the appropriate high score screen.
              Once the player is out of lives, they will be presented with a
              high score entry box, where the player inputs their name.
              On completion, the current score will be written to the
              local score_file.txt, from which the top 10 high scores will then
              be loaded. The game is designed so that the difficulty will
              increase by default, as more obstacles are destroyed, there is a
              chance for more enemy spaceships to spawn.

@instruction: In order to play the game, the left, right and spacebar keys are
              used in order to interact with the player spaceship. You may move
              left of right, and press space in order to shoot obstacles in
              your path, watch out for enemy spaceships - they are also able
              to shoot. Make sure to avoid being hit by obstacles, as you will
              lose health, lives and eventually the game if that occurs.



'''
import pygame
import random

from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# --- Global constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (150, 150, 150)
PURPLE = (153, 51, 153)

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600

# Other parameters for game
DIFFICULTY = 15
POWERUP_TIME = 4000

FPS = 60

# Load all game graphics
background = pygame.image.load(path.join(img_dir, 'spacefield_a-000.png'))
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_rect = background.get_rect()

spaceship_img = pygame.image.load(path.join(img_dir, 'player.png'))
spaceship_dmg = pygame.image.load(path.join(img_dir, 'playerDamaged.png'))
enemyship_img = pygame.image.load(path.join(img_dir, 'enemyShip.png'))
asteroid_img = pygame.image.load(path.join(img_dir, 'meteorSmall.png'))
debris_img = pygame.image.load(path.join(img_dir, 'enemyUFO.png'))
bullet_img = pygame.image.load(path.join(img_dir, 'laserGreen.png'))
bullet_img2 = pygame.image.load(path.join(img_dir, 'laserRed.png'))
powerup_health_img = pygame.image.load(path.join(img_dir, 'shield_gold.png'))
powerup_gun_img = pygame.image.load(path.join(img_dir, 'bolt_gold.png'))

# Animation sprite lists
explosion_anim = []
spaceship_explosion = []

# Define fpnt type for score
font_name = pygame.font.match_font('Calibri')


# --- Classes ---
class Vehicle(pygame.sprite.Sprite):
    """ This class represents a vehicle. """
    def __init__(self, x_position, y_position):
        super().__init__()
        self.position = [x_position, y_position]


class Spaceship(Vehicle):
    """ This class represents the spaceship. """
    width = 50
    height = 38

    def __init__(self):
        super().__init__(SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT - Spaceship.height - 30)
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.orig_image = pygame.transform.scale(spaceship_img,
                                                 (Spaceship.width,
                                                  Spaceship.height))
        self.dmg_image = pygame.transform.scale(spaceship_dmg,
                                                (Spaceship.width,
                                                 Spaceship.height))
        self.image = self.orig_image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
#       pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.x_speed = 0
        self.health = 100
        self.shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'laser5.wav'))
        self.power = 1
        self.power_time = pygame.time.get_ticks()
        self.expl_sound = pygame.mixer.Sound(path.join(snd_dir,
                                                       'explosion.wav'))

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

        # If health is below a certain amount, show damaged spaceship
        if self.health <= 50:
            self.image = self.dmg_image.copy()
        else:
            self.image = self.orig_image.copy()

        # Check hide timer, if hidden for more than 1 second, reshow ship
        # at correct location
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.x = SCREEN_WIDTH / 2
            self.rect.y = SCREEN_HEIGHT - Spaceship.height - 30

        # Check for if powerup is active
        if self.power >= 2 and
        pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

    def shoot(self, all_sprites_list, bullet_list):
        """ Shoot bullet taking into account any powerups"""
        # Check current powerup status
        if self.power == 1:
            bullet = Bullet(self.rect.x +
                            (Spaceship.width / 2) -
                            (Bullet.bullet_width / 2),
                            self.rect.y)
            all_sprites_list.add(bullet)
            bullet_list.add(bullet)
            self.shoot_sound.play()
        elif self.power >= 2:
            bullet1 = Bullet(self.rect.x + (Bullet.bullet_width / 2),
                             self.rect.y)
            bullet2 = Bullet(self.rect.x + (Spaceship.width) -
                             (Bullet.bullet_width / 2), self.rect.y)
            all_sprites_list.add(bullet1)
            all_sprites_list.add(bullet2)
            bullet_list.add(bullet1)
            bullet_list.add(bullet2)

    def hide(self):
        """ Hide the spaceship on death until re-spawn """
        self.hidden = True
        # Use a timer to re-show ship if there are still lives
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT + 200)

    def powerup(self):
        """ Powerup player shots on gun powerup """
        self.power += 1
        self.power_time = pygame.time.get_ticks()


class EnemyShip(Spaceship):
    """ This class represents an enemy spaceship. """
    def __init__(self):
        super().__init__()
        self.lives = 0
        self.image = pygame.transform.scale(enemyship_img,
                                            (Spaceship.width - 5,
                                             Spaceship.height - 5))
        self.shoot_timer = pygame.time.get_ticks()
        self.shoot_rate = random.randrange(1000, 4000)
        self.velocity = [0, random.randrange(2, 7)]
        self.image.set_colorkey(BLACK)
        self.radius = 18
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = (random.randrange(-300, -20) - Spaceship.height - 5)
        self.y_speed = 0
        self.shoot_sounds = []
        for snd in ['laserfire01.ogg', 'laserfire02.ogg']:
            self.shoot_sounds.append(pygame.mixer.Sound(path.join(snd_dir,
                                                                  snd)))

    def update(self):
        """ Move the enemy ship """
        self.rect.y += self.velocity[1]
        if self.rect.y > SCREEN_HEIGHT + self.height:
            self.reset_pos()

    def reset_pos(self):
        """ Call when the enemy falls off the screen. """
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = random.randrange(-300, -20)

    def shoot(self, all_sprites_list, obstacle_list):
        """ Shoot bullet """
        bullet = Bullet(self.rect.x + (Spaceship.width / 2) -
                        (Bullet.bullet_width / 2), self.rect.y)
        bullet.y_speed = 10
        bullet.image = bullet_img2
        all_sprites_list.add(bullet)
        obstacle_list.add(bullet)
        self.shoot_sound.play()


class PowerUp(pygame.sprite.Sprite):
    """ This class represents powerups """
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(['health', 'gun'])

        # There are gun and health powerups
        if self.type == 'health':
            self.image = powerup_health_img
        elif self.type == 'gun':
            self.image = powerup_gun_img

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        # Set powerup speed
        self.y_speed = 2

    def update(self):
        self.rect.y += self.y_speed
        # Kill if it moves off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


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

    def __init__(self):
        self.width = random.randrange(20, 40)
        self.height = random.randrange(20, 40)
        self.meteor_size = random.randrange(30, 60)

        # Call super class constructor with instance dimensions
        super().__init__(self.width, self.height)
        # Keep original image for rotation
        self.image_orig = pygame.transform.scale(asteroid_img,
                                                 (self.meteor_size,
                                                  self.meteor_size))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = random.randrange(-300, -20)
        # Define collision radius
        self.radius = int(self.rect.width * .9 / 2)
        self.rot = 0
        # Define random rotation speed
        self.rot_speed = random.randrange(-9, 9)
        self.last_update = pygame.time.get_ticks()
        # Store explosion sounds
        self.expl_sounds = []
        for snd in ['expl3.wav', 'expl6.wav']:
            self.expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir,
                                                                 snd)))
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

    def rotate(self):
        """ Method to rotate asteroids """
        # Track current time
        current_time = pygame.time.get_ticks()
        # Check for last update
        if current_time - self.last_update > 50:
            self.last_update = current_time
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        """ Update method """
        super().update()
        self.rotate()


class Debris(Obstacle):
    """ This class represents debri obstacles """

    def __init__(self):
        self.width = random.randrange(10, 16)
        self.height = random.randrange(10, 16)
        self.debri_size = random.randrange(10, 16)

        super().__init__(self.width, self.height)
        self.image = debris_img
        self.image = pygame.transform.scale(debris_img, (self.debri_size,
                                                         self.debri_size))
        self.image.set_colorkey(BLACK)
        self.rect.x = random.randrange(SCREEN_WIDTH - self.width)
        self.rect.y = random.randrange(-300, 20)


class Bullet(pygame.sprite.Sprite):
    """ This class represents bullets that the spaceship shoots """

    bullet_width = 10
    bullet_height = 20

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
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """ This class represents explosion objects """
    def __init__(self, center):
        super().__init__()
        self.image = explosion_anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        """ Explode and go throw different sprite images until end """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.frame += 1
            if self.frame == len(explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Game(object):
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """

    def __init__(self):
        """ Constructor. Create all our attributes and initialize
        the game. """

        self.score = 0
        self.highscore = False
        self.high_score = 0
        self.high_name = ""
        self.cur_name = ""
        self.game_over = False
        self.game_over_timer = 0
        self.difficulty = 0
        self.score_file = "score_file.txt"

        # Create sprite lists
        self.bullet_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.obstacle_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Create the block sprites
        for _i in range(DIFFICULTY):
            asteroid = Asteroid()

            self.obstacle_list.add(asteroid)
            self.all_sprites_list.add(asteroid)

        for _x in range(DIFFICULTY//3):
            debris = Debris()

            self.obstacle_list.add(debris)
            self.all_sprites_list.add(debris)

        # Create enemy ships
        for _z in range(DIFFICULTY//5):
            enemy = EnemyShip()

            self.obstacle_list.add(enemy)
            self.enemy_list.add(enemy)
            self.all_sprites_list.add(enemy)

        # Create the player spaceship
        self.spaceship = Spaceship()
        self.all_sprites_list.add(self.spaceship)

        # Game music
        pygame.mixer.music.load(path.join(
            snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
        pygame.mixer.music.set_volume(0.4)

        # Loop indefinitely
        pygame.mixer.music.play(loops=-1)

        # Populate explosion_anim list
        for i in range(9):
            filename = 'regularExplosion0{}.png'.format(i)
            img = pygame.image.load(path.join(img_dir, filename)).convert()
            img = pygame.transform.scale(img, (60, 60))
            img.set_colorkey(BLACK)
            explosion_anim.append(img)

        # Populate spaceship_explosion list
        for i in range(9):
            filename = 'sonicExplosion0{}.png'.format(i)
            img = pygame.image.load(path.join(img_dir, filename)).convert()
            img.set_colorkey(BLACK)
            spaceship_explosion.append(img)

        # Set spaceship lives color key
        self.spaceship_lives_img = pygame.transform.scale(spaceship_img,
                                                          (25, 19))
        self.spaceship_lives_img.set_colorkey(BLACK)

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """
        if not self.highscore:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYUP:
                    if self.game_over:
                        time = pygame.time.get_ticks() - self.game_over_timer
                        if (time > 1000):
                            self.__init__()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.spaceship.shoot(self.all_sprites_list,
                                             self.bullet_list)

            for enemy in self.enemy_list:
                if pygame.time.get_ticks() -
                enemy.shoot_timer > enemy.shoot_rate:
                    enemy.shoot(self.all_sprites_list, self.obstacle_list)
                    enemy.shoot_timer = pygame.time.get_ticks()

        return False

    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        if not self.game_over and not self.highscore:
            # Move all the sprites
            self.all_sprites_list.update()

            # See if the player spaceship has collided with anything.
            hits = pygame.sprite.spritecollide(self.spaceship,
                                               self.obstacle_list,
                                               True,
                                               pygame.sprite.collide_circle)

            # If it has, reduce player spaceship health
            for hit in hits:
                self.spaceship.health -= hit.radius * 2
                # Show explosion and play explosion sound
                expl = Explosion(hit.rect.center)
                self.spaceship.expl_sound.play()
                self.all_sprites_list.add(expl)
                # If health is below 0, lose a life, otherwise the game ends
                if self.spaceship.health <= 0:
                    self.explode_on_death =
                    Explosion(self.spaceship.rect.center)
                    self.all_sprites_list.add(self.explode_on_death)
                    self.spaceship.hide()
                    self.spaceship.lives -= 1
                    self.spaceship.health = 100

            # End the game only once the final explosion animation completes
            if self.spaceship.lives <= 0 and not self.explode_on_death.alive():
                # Go to highscore mode, where the highscores will be displayed
                self.highscore = True

            # Check for powerups
            poweruphits = pygame.sprite.spritecollide(self.spaceship,
                                                      self.powerups,
                                                      True)

            for hit in poweruphits:
                if hit.type == 'health':
                    self.spaceship.health += random.randrange(10, 30)
                    if self.spaceship.health >= 100:
                        self.spaceship.health = 100
                if hit.type == 'gun':
                    self.spaceship.powerup()

            # See if any of the bullets have hit any of the obstacles.
            bullet_hit_list = pygame.sprite.groupcollide(self.bullet_list,
                                                         self.obstacle_list,
                                                         True,
                                                         True)

            # Check the list of collisions.
            for obstacle in bullet_hit_list:
                dice_roll = random.randint(1, 6)
                if dice_roll > 4:
                    enemy = EnemyShip()
                    self.all_sprites_list.add(enemy)
                    self.obstacle_list.add(enemy)
                    self.enemy_list.add(enemy)
                    enemy.expl_sound.play()
                else:
                    asteroid = Asteroid()
                    self.all_sprites_list.add(asteroid)
                    self.obstacle_list.add(asteroid)
                    random.choice(asteroid.expl_sounds).play()
                self.score += 1
                expl = Explosion(obstacle.rect.center)
                self.all_sprites_list.add(expl)
                if random.random() > 0.9:
                    powerup = PowerUp(obstacle.rect.center)
                    self.all_sprites_list.add(powerup)
                    self.powerups.add(powerup)
                    # print(self.score)

            if len(self.obstacle_list) == 0:
                self.highscore = True

    # High score entry box, loaded on death
    def enterbox(self, screen, txt, font):
        """ Represents the high score entry box """
        box_x = SCREEN_WIDTH
        box_y = 100
        # Keep track of entered name
        name = ""

        # Set box parameters such as colors
        box = pygame.surface.Surface((box_x, box_y))
        box.fill(PURPLE)
        pygame.draw.rect(box, BLACK, (0, 0, box_x, box_y), 1)
        text_surf = font.render(txt, True, BLACK)
        text_rect = text_surf.get_rect(center=(box_x//2, int(box_y*0.3)))
        box.blit(text_surf, text_rect)

        # Show the name in the textbox
        def show_name(screen, name):
            pygame.draw.rect(box, WHITE, (50, 60, box_x-100, 20), 0)
            text_surf = font.render(name, True, BLACK)
            text_rect = text_surf.get_rect(center=(box_x//2, int(box_y*0.7)))
            box.blit(text_surf, text_rect)
            screen.blit(box, (0, box_y//2))
            pygame.display.flip()

        # Input loop
        enterbox_screen = True
        while enterbox_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    inkey = event.key
                    if inkey in [13, 271]:  # enter/return key
                        enterbox_screen = False
                        return name
                    elif inkey == 8:  # backspace key
                        name = name[:-1]
                    elif inkey <= 300:
                        # TODO, handle different types of input
                        # if pygame.key.get_mods()
                        # & pygame.KMOD_SHIFT and 122 >= inkey >= 97:
                        # inkey -= 32  # handles CAPITAL input
                        name += chr(inkey)

            # Show a round cursor if no name has been inputted
            if name == "":
                for color in [PURPLE, WHITE]:
                    pygame.draw.circle(box, color, (box_x//2,
                                                    int(box_y*0.7)), 7, 0)
                    screen.blit(box, (0, box_y//2))
                    pygame.display.flip()
                    pygame.time.wait(300)
            # Update name on the screen
            show_name(screen, name)

    def display_frame(self, screen):
        """ Display everything to the screen for the game. """

        # Highscore display mode, prompt for user name and then show top 10
        if self.highscore:
            font = pygame.font.Font(font_name, 18)
            self.high_name, self.high_score = read_high_score(self.score_file)

            # Oh look, you found the easter egg!
            riddle = random.choice(
                ["At night they come without being fetched, " +
                 "and by day they are lost without being stolen",
                 "Prepare to be mindblown - what is the Fermi Paradox?",
                 "Who says we can't go to Mars - " +
                 "if only you hadn't killed us all",
                 "Ever been to Uganda? The pearl of Africa awaits",
                 "What would you do with $1,000,000?",
                 "Forget about Bitcoin, get in with Ether",
                 "The answer to everything is 42"])

            # Check current score against high score
            if self.score == 42:
                self.cur_name = self.enterbox(screen,
                                              "SOLVE ME A RIDDLE: " + riddle,
                                              font)
            elif self.score > self.high_score:
                self.cur_name = self.enterbox(screen,
                                              "YOU HAVE BEATEN THE HIGH " +
                                              "SCORE - Enter your name:", font)
            elif self.score == self.high_score:
                self.cur_name = self.enterbox(screen, "HIGH SCORE EQUALLED -" +
                                              " Enter your name:", font)
            elif self.score < self.high_score:
                st1 = "Highscore is "
                st2 = " made by "
                st3 = "   Enter your name:"
                txt = st1+str(self.high_score)+st2+self.high_name+st3
                self.cur_name = self.enterbox(screen, txt, font)

            # If no name has been passed, exit
            if self.cur_name is None or len(self.cur_name) == 0:
                self.highscore = False
                return

            # Write current score to score file
            write_out(self.score_file, self.cur_name, self.score)

            # Show top ten scores
            if top10_scores(screen, self.score_file, font) is False:
                self.game_over_timer = pygame.time.get_ticks()
                self.highscore = False
                self.game_over = True

        # Display game over screen
        elif self.game_over:
            screen.fill(BLACK)
            screen.blit(background, background_rect)
            draw_text(screen, "GAME OVER", 64,
                      SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
            draw_text(screen, "Arrow keys move, Space to fire", 22,
                      SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            draw_text(screen, "Press any key to begin", 18,
                      SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
            pygame.display.flip()

        # Otherwise, display game objects
        if not self.game_over and not self.highscore:

            screen.fill(BLACK)
            screen.blit(background, background_rect)

            self.all_sprites_list.draw(screen)

            # Draw score
            draw_text(screen, str(self.score), 18, SCREEN_WIDTH/2, 10)

            # Draw lives
            draw_lives(screen, SCREEN_WIDTH - 100, 5, self.spaceship.lives,
                       self.spaceship_lives_img)

            # Draw health bar
            draw_health_bar(screen, 5, 5, self.spaceship.health)

            pygame.display.flip()


# Show the top 10 scores from the score file
def top10_scores(screen, file_name, font):
    x_length = SCREEN_WIDTH
    y_length = SCREEN_HEIGHT

    file = open(file_name, 'r')
    rows = file.readlines()

    # Iterate through rows
    all_scores = []
    for row in rows:
        sep = row.index(',')
        name = row[:sep]
        score = int(row[sep+1:-1])
        all_scores.append((score, name))

    file.close()

    # Sort scores
    all_scores.sort(reverse=True)
    best_scores = all_scores[:10]

    screen.fill(BLACK)
    box = pygame.surface.Surface((x_length, y_length))
    box.fill(PURPLE)
    pygame.draw.rect(box, WHITE, (50, 12, x_length - 100, 35), 0)
    pygame.draw.rect(box, WHITE, (50, y_length - 60, x_length - 100, 35), 0)
    pygame.draw.rect(box, BLACK, (0, 0, x_length, y_length), 1)
    text_surf = font.render("HIGHSCORE", True, BLACK)
    text_rect = text_surf.get_rect(center=(x_length//2, 30))
    box.blit(text_surf, text_rect)
    text_surf = font.render("Press ENTER to continue", True, BLACK)
    text_rect = text_surf.get_rect(center=(x_length//2, SCREEN_HEIGHT - 42))
    box.blit(text_surf, text_rect)

    for i, entry in enumerate(best_scores):
        text_surf = font.render(entry[1] + " " + str(entry[0]), True, BLACK)
        text_rect = text_surf.get_rect(center=(x_length//2, 30*i+80))
        box.blit(text_surf, text_rect)

    screen.blit(box, (0, 0))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and
            event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                return False


# Read the high score name and value from the score file
def read_high_score(file_name):
    file = open(file_name, 'r')
    rows = file.readlines()
    file.close

    high_score = 0
    high_name = ""

    for row in rows:
        name, score = row.strip().split(",")
        score = int(score)

        if score > high_score:
            high_score = score
            high_name = name

    return high_name, high_score


# Startup splash screen
def draw_start_screen(screen):
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    draw_text(screen, "PROJECT S", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
    draw_text(screen, "by Kulvinder Lotay", 22,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    draw_text(screen, "Press any key to begin", 18,
              SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4)
    pygame.display.flip()


# The score text
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# Draw lives
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# Draw health bar
def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0

    HEALTH_BAR_LENGTH = 100
    HEALTH_BAR_HEIGHT = 10

    fill = (pct / 100) * HEALTH_BAR_LENGTH
    outline_rect = pygame.Rect(x, y, HEALTH_BAR_LENGTH, HEALTH_BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# Write out to the score file
def write_out(score_file, name, score):
    open_scores_file = open(score_file, 'a')
    print(name + ",", score, file=open_scores_file)
    open_scores_file.close()


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

    # Startup splash screen
    waiting = True
    draw_start_screen(screen)
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                waiting = False

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
