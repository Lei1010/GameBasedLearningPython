import time

import pygame
from extracter import extract_images
import os


SCREEN_WIDTH, SCREEN_HEIGHT = int(pygame.display.Info().current_w), int(pygame.display.Info().current_h)

CODE_ITALIC = 'Assets/Fonts/JetBrainsMono-Light-Italic.ttf'
CODE_REG = 'Assets/Fonts/JetBrainsMono-Light.ttf'

WHITE = (255, 255, 255)
GREEN = (117, 147, 97)
GRAY = (220, 220, 220)
BLACK = (0, 0, 0)

PERCENT_OF_SCREEN_HEIGHT = 0.1296296296296296
scale_factor = SCREEN_HEIGHT * PERCENT_OF_SCREEN_HEIGHT / 350


class Player(pygame.sprite.Sprite):
    animation_frame = 'idle'
    IDLE_PATH = 'assets/sprites/knight/idle/*.png'
    RUN_PATH = "assets/sprites/knight/run/*.png"
    ATTACK_PATH = 'assets/sprites/knight/attack/*png'

    facing_right = True
    idle_index = 1
    running_index = 0
    attack_index = 0
    speed = [0, 0]
    ANIMATION_SPEED = 4
    change_animation = 2

    RUNNING_SPEED = round(SCREEN_WIDTH / 200)  # pixels / (1/60) seconds

    idle_images = [[], []]  # left, right
    for image in extract_images(IDLE_PATH, scale_factor):
        idle_images[0].append(pygame.transform.flip(image, True, False))
        idle_images[1].append(image)

    run_images = [[], []]  # left, right
    for image in extract_images(RUN_PATH, scale_factor):
        run_images[0].append(pygame.transform.flip(image, True, False))
        run_images[1].append(image)

    attack_images = [[], []]
    for image in extract_images(ATTACK_PATH, scale_factor):
        attack_images[0].append(pygame.transform.flip(image, True, False))
        attack_images[1].append(image)

    def __init__(self, canvas):
        super(Player, self).__init__()
        self.canvas = canvas
        self.image: pygame.Surface = self.idle_images[1][0]
        self.rect: pygame.Rect = self.image.get_rect(center=(0, 350))
        self.rect.left = 0.05 * SCREEN_WIDTH
        self.moving = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def reset_change_animation(self):
        self.change_animation = self.ANIMATION_SPEED

    def get_image(self, images: list, index: int = None) -> pygame.image:
        """
        gets an image from a list of right images and left images according to direction player is facing
        :param images: list containing a right facing image(s) [0] and left facing image(s) [1]
        :param index: index of the image to return. if equal to None, images does not contain lists
        :return: the image of proper facing direction
        """
        if index is None:
            return images[self.facing_right]
        return images[self.facing_right][index]

    def update_idle(self):
        """
        Updates the idle animation
        """
        if self.change_animation <= 0:
            self.image = self.get_image(self.idle_images, self.idle_index)
            self.idle_index += 1
            if self.idle_index >= len(self.idle_images[0]):
                self.idle_index = 0
            self.reset_change_animation()
        else:
            self.change_animation -= 1

    def update_running(self):
        """
        Updates the running animations
        """
        if self.change_animation <= 0:
            self.image = self.get_image(self.run_images, self.running_index)
            self.running_index += 1
            if self.running_index >= len(self.run_images[0]):
                self.running_index = 0
            self.reset_change_animation()
        else:
            self.change_animation -= 1

    def update_attack(self):
        if self.change_animation <= 0:
            self.image = self.get_image(self.attack_images, self.attack_index)
            self.attack_index += 2
            if self.attack_index >= len(self.attack_images[0]):
                self.attack_index = 0
                self.animation_frame = 'idle'
            self.reset_change_animation()
        else:
            self.change_animation -= 2

    def update(self, seconds_passed=1 / 60):
        self.rect.y += self.speed[1]
        self.speed[1] = 0
        self.rect.x += self.speed[0]

        # if self.speed == [0, 0] and will_land and self.ON_GROUND:  # if standing still
        if self.animation_frame == 'attack':
            self.update_attack()
        elif self.speed == [0, 0]:  # if standing still
            self.update_idle()
            self.animation_frame = 'idle'
        elif self.speed[0] != 0:  # animate only if running on the ground
            self.update_running()
            self.animation_frame = 'running'
        return self.rect

    def stop(self, pressed_keys):
        if self.speed[0] == 0:
            # if right keys are still pressed
            if pressed_keys[pygame.K_RIGHT]:
                self.speed[0] += self.RUNNING_SPEED
            # if left keys are still pressed
            if pressed_keys[pygame.K_LEFT]:
                self.speed[0] -= self.RUNNING_SPEED
            if self.speed[0] > 0:
                self.facing_right = True
            elif self.speed[0] < 0:
                self.facing_right = False

        elif (pressed_keys[pygame.K_LEFT] + pressed_keys[pygame.K_a] +
              pressed_keys[pygame.K_RIGHT] + pressed_keys[pygame.K_d] == 0):
            self.image = self.get_image(self.idle_images, True)
            self.speed[0] = 0

    def force_stop(self):
        self.speed = [0, 0]

    def go_left(self):
        if self.speed[0] > -self.RUNNING_SPEED:
            self.speed[0] -= self.RUNNING_SPEED
        self.facing_right = False

    def go_right(self):
        if self.speed[0] < self.RUNNING_SPEED:
            self.speed[0] += self.RUNNING_SPEED
        self.facing_right = True


def get_image(images: list, index: int = None) -> pygame.image:
    return images[index]


class Enemy(pygame.sprite.Sprite):
    enemy1_idle_path = "assets/sprites/enemy_1/idle/*.png"
    enemy1_hurt_path = "assets/sprites/enemy_1/hurt/*.png"
    enemy1_dying_path = "assets/sprites/enemy_1/dying/*png"

    change_animation = 2
    idle_index = 1
    animation_frame = 'idle'

    enemy1_idle_images = []
    for image in extract_images(enemy1_idle_path, scale_factor * 1.5):
        enemy1_idle_images.append(pygame.transform.flip(image, True, False))

    enemy1_hurt_images = []
    for image in extract_images(enemy1_hurt_path, scale_factor * 1.5):
        enemy1_hurt_images.append(pygame.transform.flip(image, True, False))

    enemy1_dying_images = []
    for image in extract_images(enemy1_dying_path, scale_factor * 1.5):
        enemy1_dying_images.append(pygame.transform.flip(image, True, False))

    def __init__(self):
        super(Enemy, self).__init__()
        self.image: pygame.Surface = self.enemy1_idle_images[0]
        self.rect: pygame.Rect = self.image.get_rect(center=(0, 350))
        self.rect.left = 0.5 * SCREEN_WIDTH
        self.count_hit = 0
        self.killed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update_idle(self):
        if self.change_animation <= 0:
            self.image = get_image(self.enemy1_idle_images, self.idle_index)
            self.idle_index += 2
            if self.idle_index >= len(self.enemy1_idle_images):
                self.idle_index = 0
            self.change_animation = 2
        else:
            self.change_animation -= 1

    def update_hurt(self):
        if self.change_animation <= 0:
            self.image = get_image(self.enemy1_hurt_images, self.idle_index)
            self.idle_index += 2
            if self.idle_index >= len(self.enemy1_hurt_images):
                self.idle_index = 0
                self.animation_frame = 'idle'
            self.change_animation = 2
        else:
            self.change_animation -= 1

    def update_dying(self):
        if self.change_animation <= 0:
            self.image = get_image(self.enemy1_dying_images, self.idle_index)
            self.idle_index += 2
            if self.idle_index >= len(self.enemy1_dying_images):
                self.idle_index = 0
                self.killed = True
            self.change_animation = 2
        else:
            self.change_animation -= 2

    def update(self, seconds_passed=1 / 60):
        if self.count_hit == 4:
            self.update_dying()
        elif self.animation_frame == 'hurt':
            self.update_hurt()
        elif self.animation_frame == 'idle':  # if standing still
            self.update_idle()
            self.animation_frame = 'idle'

        return self.rect


class GameZone:
    def __init__(self, background):
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT * 0.75))
        self.background = pygame.image.load(background).convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.75)))
        self.rect = (0, 0)
        self.sprite_list = pygame.sprite.Group()
        self.player = None
        self.enemy = None
        self.collide_rect = pygame.Rect((0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT * 0.75))

    def set_player(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy

    def update(self, screen):
        screen.blit(self.background, self.rect)
        self.player.update()
        self.enemy.update()

    def draw(self, screen):
        self.sprite_list.draw(screen)


class Wizard(pygame.sprite.Sprite):
    change_animation = 2
    idle_index = 1

    wizard_path = "assets/sprites/wizards/wizard/1_IDLE_00*.png"
    wizard_fire_path = "assets/sprites/wizards/wizard_fire/1_IDLE_00*.png"
    wizard_ice_path = "assets/sprites/wizards/wizard_ice/1_IDLE_00*.png"

    wizard_images = []  # Only right face
    for image in extract_images(wizard_path, scale_factor * 1.5):
        wizard_images.append(pygame.transform.flip(image, True, False))

    wizard_fire_images = []
    for image in extract_images(wizard_fire_path, scale_factor * 1.5):
        wizard_fire_images.append(pygame.transform.flip(image, True, False))

    wizard_ice_images = []
    for image in extract_images(wizard_ice_path, scale_factor * 1.5):
        wizard_fire_images.append(pygame.transform.flip(image, True, False))

    def __init__(self, chap):
        super(Wizard, self).__init__()
        if chap == 1:
            self.image: pygame.Surface = self.wizard_images[0]
            self.idle_image = self.wizard_images
        elif chap == 2:
            self.image: pygame.Surface = self.wizard_fire_images[0]
            self.idle_image = self.wizard_fire_images
        elif chap == 3:
            self.image: pygame.Surface = self.wizard_ice_images[0]
            self.idle_image = self.wizard_ice_images
        self.rect: pygame.Rect = self.image.get_rect(center=(0, 350))
        self.rect.left = 0.8 * SCREEN_WIDTH

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.change_animation <= 0:
            self.image = get_image(self.idle_image, self.idle_index)
            self.idle_index += 1
            if self.idle_index >= len(self.idle_image):
                self.idle_index = 0
            self.change_animation = 2
        else:
            self.change_animation -= 1


class CommandZone:
    inactive_color = (68, 87, 96)
    active_color = (57, 69, 76)
    font_reg = pygame.font.Font(CODE_REG, int(25 / 1200 * SCREEN_HEIGHT))
    font_italic = pygame.font.Font(CODE_REG, int(25 / 1000 * SCREEN_HEIGHT))
    font_height = int(25 / 1000 * SCREEN_HEIGHT)

    def __init__(self, text=''):
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT * 0.25))
        self.rect = (0, SCREEN_HEIGHT * 0.75)
        self.collide_rect = pygame.Rect(self.rect, (SCREEN_WIDTH, SCREEN_HEIGHT * 0.25))
        self.active = False
        self.color = self.inactive_color
        self.text = ''
        self.txt_surface = self.font_reg.render(self.text, True, WHITE)
        self.lines = [self.text]
        self.order_lines = 0
        self.cursor = pygame.Rect(self.txt_surface.get_rect().topright, (1, self.font_height))
        self.run_button = pygame.Rect((SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9),
                                      (0.12 * SCREEN_WIDTH, 0.05 * SCREEN_HEIGHT))

    def draw(self, screen, chapter=0):
        self.image.fill(self.color)  # Draw Command Zone
        screen.blit(self.image, self.rect)  # Blit surface
        self.text_guide(screen, chapter)
        # Blit text line by line
        for i in range(self.order_lines + 1):
            height = SCREEN_HEIGHT * 0.75 + self.font_height * (i + 1) + 4
            self.txt_surface = self.font_reg.render(self.lines[i], True, WHITE)
            screen.blit(self.txt_surface, (50, height))  # Blit the text

        # Draw blinking cursor
        if time.time() % 1 > 0.5 and self.active:
            pygame.draw.rect(screen, WHITE, self.cursor)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.collide_rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.color = self.active_color
            else:
                self.active = False
                self.color = self.inactive_color

        # Take user input
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.order_lines += 1
                    self.text = ''
                    self.lines.append(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    if self.text:
                        self.text = self.text[:-1]
                    elif self.order_lines != 0:
                        self.lines.pop(self.order_lines)
                        self.order_lines -= 1
                        self.text = self.lines[self.order_lines]
                        self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.lines[self.order_lines] = self.text
                # Identify location to render blinking cursor
                height = SCREEN_HEIGHT * 0.75 + self.font_height * (self.order_lines + 1) + 4
                self.txt_surface = self.font_reg.render(self.text, True, WHITE)
                self.cursor.topright = (self.txt_surface.get_rect().right + 50, height)

    def text_guide(self, screen, number):
        text = ''
        if number == 0:
            text = "Welcome to this new adventure. We will ask you a few question before we start"
        elif number == 1:
            text = "Do you want to have sound for each hit? (Yes/No)"
        return screen.blit(self.font_italic.render(text, True, GREEN), self.rect)

    def verify_input(self, text, number):
        text = (" ".join(text.split()))
        result = ""
        alert = ""
        if number == 1:
            if not result.lower():
                alert = "It's not wrong to have a variable including upper case. However, it's not the regulation name." \
                        "From next chapter, let's consider variable including uppercase is wrong. Keep it mind that!"

            if text == "no":
                result = "Turn off hit sound successfully"
            elif text == "yes":
                result = "Turn on hit sound successfully"
            else:
                result = "Make sure you entered correctly only Yes or No?"
        return result

    def exec_code(self):
        line = ""
        for i in range(self.order_lines+1):
            line += self.lines[i] + "\n"
        with open("exec_microbit.py", "w") as file:
            file.write(line)

        os.system('uflash exec_microbit.py')


class Images(pygame.sprite.Sprite):
    def __init__(self, source, center):
        super().__init__()
        self.image = pygame.image.load(source)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def draw(self, screen):
        screen.blit(self.image, self.rect)
