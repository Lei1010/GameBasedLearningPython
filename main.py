from math import floor
import os
import platform
import json
import sys

import pygame

from pygame import gfxdraw, K_w, K_a, K_d, K_UP, K_LEFT, K_RIGHT, K_ESCAPE, K_F4, K_p, K_RALT, K_LALT, K_SPACE, \
    MOUSEBUTTONDOWN, QUIT, KEYUP, KEYDOWN, K_TAB, K_v, K_h, K_BACKSPACE, K_q, K_m, K_r, RLEACCEL, K_RETURN

# CONSTANTS
WHITE = 255, 255, 255
BLACK = 0, 0, 0
MATTE_BLACK = 20, 20, 20
GREEN = 40, 175, 99
RED = 255, 0, 0
YELLOW = 250, 237, 39
DARK_GREEN = 0, 128, 0
LIGHT_BLUE = 0, 191, 255
GREY = 204, 204, 204
BLUE = 33, 150, 243
BACKGROUND = 174, 222, 203

FONT_BOLD = 'assets/fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'assets/fonts/OpenSans-Regular.ttf'
FONT_LIGHT = 'assets/fonts/OpenSans-Light.ttf'

CONFIG_FILE = 'config.json'
config = {'DEBUG': False, 'background_music': True, "chapter": 0, }
music_playing = False
delta_time = 0


def save_config():
    with open(CONFIG_FILE, 'w') as fp:
        json.dump(config, fp, indent=4)


try:
    with open(CONFIG_FILE) as f:
        _config = json.load(f)
except FileNotFoundError:
    _config = {}
save_file = False
for k, v in config.items():
    try:
        config[k] = _config[k]
    except KeyError:
        save_file = True
if save_file:
    save_config()
DEBUG = config['DEBUG']


def text_objects(text, font, color=BLACK):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def create_hud_text(text, color):
    text_surf, text_rect = text_objects(text, HUD_TEXT, color)
    text_rect.topleft = -2, -5
    bg_w, text_bg_h = text_surf.get_size()
    bg_w += 10
    bg = pygame.Surface((bg_w, text_bg_h), pygame.SRCALPHA, 32)
    bg.fill((50, 50, 50, 160))
    bg.blit(text_surf, (5, 0))
    return bg, text_rect


def button(text, x, y, w, h, click, inactive_color=BLUE, active_color=LIGHT_BLUE, text_color=WHITE):
    mouse = pygame.mouse.get_pos()
    return_value = False
    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pygame.draw.rect(SCREEN, active_color, (x, y, w, h))
        if click and pygame.time.get_ticks() > 100:
            SELECT_SOUND.play()
            return_value = True
    else:
        pygame.draw.rect(SCREEN, inactive_color, (x, y, w, h))

    text_surf, text_rect = text_objects(text, SMALL_TEXT, color=text_color)
    text_rect.center = (int(x + w / 2), int(y + h / 2))
    SCREEN.blit(text_surf, text_rect)
    return return_value


def round_button(text, x, y, w, h, click, inactive_color=BLUE, active_color=LIGHT_BLUE, text_color=WHITE):
    mouse = pygame.mouse.get_pos()
    return_value = False
    x, y, w, h = int(x), int(y), int(w), int(h)
    if h % 2 == 0:
        h += 1
    radius = h // 2

    if x < mouse[0] < x + w and y < mouse[1] < y + h:  # if mouse is hovering the button
        pygame.draw.rect(SCREEN, active_color, (x, y, w, h))
        draw_circle(SCREEN, x, (y + h // 2), radius=radius, color=active_color)
        draw_circle(SCREEN, (x + w), (y + h // 2), radius=radius, color=active_color)
        if click and pygame.time.get_ticks() > 100:
            SELECT_SOUND.play()
            return_value = True
    else:
        pygame.draw.rect(SCREEN, inactive_color, (x, y, w, h))
        draw_circle(SCREEN, x, (y + h // 2), radius=radius, color=inactive_color)
        draw_circle(SCREEN, (x + w), (y + h // 2), radius=radius, color=inactive_color)

    text_surf, text_rect = text_objects(text, SMALL_TEXT, color=text_color)
    text_rect.center = (x + w // 2, y + h // 2)
    SCREEN.blit(text_surf, text_rect)
    return return_value


def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def toggle_btn(text, x, y, w, h, click, text_color=BLACK, enabled=True, draw_toggle=True, blit_text=True,
               enabled_color=LIGHT_BLUE, disabled_color=GREY):
    mouse = pygame.mouse.get_pos()
    # draw_toggle and blit_text are used to reduce redundant drawing and blitting (improves quality)
    rect_height = h // 2
    if rect_height % 2 == 0:
        rect_height += 1
    if enabled and draw_toggle:
        pygame.draw.rect(SCREEN, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, rect_height))
        pygame.draw.rect(SCREEN, enabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, rect_height))
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, enabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, enabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 5, WHITE)  # small inner circle
    elif draw_toggle:
        pygame.draw.rect(SCREEN, WHITE, (x + TOGGLE_WIDTH - h // 4, y, TOGGLE_ADJ + h, rect_height))
        pygame.draw.rect(SCREEN, disabled_color, (x + TOGGLE_WIDTH, y, TOGGLE_ADJ, rect_height))
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, disabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH + TOGGLE_ADJ), y + h // 4, h // 4, disabled_color)
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 5, WHITE)  # small inner circle
    if blit_text:
        text_surf, text_rect = text_objects(text, MEDIUM_TEXT, color=text_color)
        text_rect.topleft = (x, y)
        SCREEN.blit(text_surf, text_rect)
    return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pygame.time.get_ticks() > 100


def check_button(text, x, y, w, h, click, text_color=BLACK, enabled=True, draw_btn=True, blit_text=True,
                 enabled_color=LIGHT_BLUE,
                 disabled_color=GREY):
    """
    Display text and radio button
    """
    mouse = pygame.mouse.get_pos()
    rect_height = h // 2
    if rect_height % 2 == 0:
        rect_height += 1
    if enabled and draw_btn:
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, enabled_color)
    elif draw_btn:
        draw_circle(SCREEN, int(x + TOGGLE_WIDTH), y + h // 4, h // 4, disabled_color)

    if blit_text:
        text_surf, text_rect = text_objects(text, MEDIUM_TEXT, color=text_color)
        text_rect.topleft = (x, y)
        SCREEN.blit(text_surf, text_rect)

    return x < mouse[0] < x + w and y < mouse[1] < y + h and click and pygame.time.get_ticks() > 100


def display_text(text, x, y, text_color=BLACK, blit_text=True):
    """
    Display text on Screen
    :param text: text need to display
    :param text_color: Black by default
    :param blit_text: improve quality by running once
    :return: None
    """
    if blit_text:
        text_surf, text_rect = text_objects(text, MEDIUM_TEXT, color=text_color)
        text_rect.topleft = (x, y)
        SCREEN.blit(text_surf, text_rect)


def hide_mouse():
    pygame.mouse.set_visible(False)


def show_mouse():
    pygame.mouse.set_visible(True)


def main_menu_setup():
    show_mouse()
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('Hope STEM Game', MENU_TEXT)
    text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 4))
    SCREEN.blit(text_surf, text_rect)
    text_surf, text_rect = text_objects('Created by Lei', LARGE_TEXT)
    text_rect.center = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGHT * 0.84))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()


def main_menu():
    global ticks
    main_menu_setup()
    start_game = False
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4
                                                 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                                                 or event.key == K_q or event.key == K_ESCAPE))
            if event.type == QUIT or alt_f4:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                start_game = True
            elif event.type == MOUSEBUTTONDOWN:
                click = True
        if chapter == 0:
            if button('N E W  G A M E', *button_layout_4[0], click):
                start_game = True
            if button('S E T T I N G S', *button_layout_4[1], click):
                settings_menu()
                main_menu_setup()
            elif button('Q U I T  G A M E', *button_layout_4[2], click):
                sys.exit()
        else:
            if button('R E S U M E', *button_layout_4[0], click):
                start_game = True
            if button('N E W  G A M E', *button_layout_4[1], click):
                new_game()
                start_game = True
            if button('S E T T I N G S', *button_layout_4[2], click):
                settings_menu()
                main_menu_setup()
            elif button('Q U I T  G A M E', *button_layout_4[3], click):
                sys.exit()

        if start_game:
            while start_game:
                start_game = game() == 'Restart'
            main_menu_setup()
        pygame.display.update(button_layout_4)
        clock.tick(60)


def settings_menu():
    SCREEN.fill(WHITE)
    text_surf, text_rect = text_objects('Settings', MENU_TEXT)
    text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()
    first_run = draw_bg_toggle = True
    while True:
        click = False
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])
                                                 or event.key == K_q))
            if event.type == QUIT or alt_f4:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                click = True
        if toggle_btn('Background Music', *button_layout_4[0], click, enabled=config['background_music'],
                      draw_toggle=draw_bg_toggle, blit_text=first_run):
            config['background_music'] = not config['background_music']
            save_config()
            draw_bg_toggle = True

        elif button('B A C K', *button_layout_4[1], click):
            return
        else:
            draw_bg_toggle = False
        first_run = False
        pygame.display.update(button_layout_4)
        clock.tick(60)


def game():
    global music_playing
    global chapter

    if not music_playing and config['background_music']:
        # TODO: add music
        # pygame.mixer.Channel(0).play(MUSIC_SOUND, loops=-1)
        music_playing = True
    player = Player()
    if chapter == 0:
        chapter_0(player)
        chapter = 1
    initial_chapter = floor(chapter)
    background = 'Assets/Images/background/background_{}.png'.format(str(chapter))
    running = True
    SCREEN.fill(BLACK)
    first_run = True
    if chapter > 1:
        enemy = Enemy(initial_chapter)
        wizard = Wizard(initial_chapter)
    game_zone = GameZone(background)
    command_zone = CommandZone()
    while running:
        click = False

        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
            if event.type == KEYDOWN and not command_zone.active:
                if event.key == K_ESCAPE or event.key == K_SPACE and not command_zone.active:
                    pygame.mixer.Channel(0).pause()
                    music_playing = False
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'
                    if config['background_music']:
                        pygame.mixer.Channel(0).unpause()
                        music_playing = True
                if event.key == K_LEFT:
                    player.go_left()
                elif event.key == K_RIGHT and player.moving:
                    player.go_right()
                elif event.key == K_RETURN:
                    player.animation_frame = 'attack'
            elif event.type == KEYUP:
                if event.key in (K_d, K_RIGHT, K_a, K_LEFT, K_RETURN):
                    player.stop(pygame.key.get_pressed())
            command_zone.handle_event(event)

        command_zone.draw(SCREEN)
        game_zone.update(SCREEN)
        player.draw(SCREEN)
        player.update()

        if chapter == 1:
            chapter_1(command_zone, game_zone)

        elif chapter == 2:
            if not enemy.dead:
                if round_button("R U N", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                                SCREEN_HEIGHT * 0.05, click):
                    command_zone.exec_command()
                enemy.draw(SCREEN)
                enemy.update()
                if first_run:
                    command_zone.sample_code(2)
                    first_run = False

                if pygame.sprite.collide_rect(player, enemy):
                    player.moving = False
                    if player.animation_frame == 'attack':
                        enemy.count_hit += 1
                        enemy.animation_frame = 'hurt'

                else:
                    player.moving = True
            else:
                player.moving = True
                wizard.draw(SCREEN)
                wizard.update()
                if pygame.sprite.collide_rect(player, wizard):
                    player.moving = False
                    trunk_chosen = display_trunks(wizard)
                    if trunk_chosen == 1:
                        chapter = 2.2
                        game()
                    elif trunk_chosen == 2:
                        chapter = 2.3
                    else:
                        chapter = 2.4
                    game()
        elif chapter == 2.2:
            chapter_2_2(command_zone)
            chapter = 2
            game()
        elif chapter == 2.3:
            chapter_2_3()
            chapter = 2
            game()

        elif chapter == 3:
            if not enemy.killed:
                enemy.draw(SCREEN)
                if pygame.sprite.collide_rect(player, enemy):
                    player.moving = False
                    if player.animation_frame == 'attack':
                        sign += 1
                        if sign == 1:
                            enemy.count_hit += 1
                        if sign == 13:
                            enemy.animation_frame = 'hurt'
                    else:
                        sign = 0
                else:
                    player.moving = True
            else:
                enemy.kill()
                chapter = 3.1
                player.moving = True
        elif chapter == 4:
            pass

        """Debug here"""

        """Config here"""
        pygame.display.update()
        clock.tick(24)


def chapter_0(player):
    background = pygame.image.load("Assets/scroll_0/scroll48.jpg").convert()
    pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    scroll_sound = pygame.mixer.Sound("Assets/Audio/scroll.ogg")

    if config['background_music']:
        pygame.mixer.Channel(0).play(scroll_sound, loops=-1)

    # for i in range(1, 49):
    #     source = "Assets/scroll_0/scroll_0{}.jpg".format(str(i))
    #     background = pygame.image.load(source)
    #     image = pygame.Surface.lo
    #     pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    #     SCREEN.blit(background, (0, 0))
    #     clock.tick(40)

    SCREEN.blit(background, (0, 0))
    while True:
        click = False
        for event in pygame.event.get():
            handle_input(event)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_SPACE:
                    pygame.mixer.Channel(0).pause()
                    game.music_playing = False
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'
                    if config['background_music']:
                        pygame.mixer.Channel(0).play(scroll_sound, loops=-1)

            if event.type == MOUSEBUTTONDOWN:
                click = True

        if round_button(" N E X T", int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.9), int(BUTTON_WIDTH * 0.5),
                        int(BUTTON_HEIGHT * 0.5), click, inactive_color=BLACK, active_color=GREY):
            break
        pygame.display.update()
        clock.tick(24)


def chapter_1(command_zone, game_zone):
    success_sound = pygame.mixer.Sound('Assets/Audio/success.ogg')
    ready_sound = pygame.mixer.Sound("Assets/Audio/ready.ogg")
    if config['background_music']:
        pygame.mixer.Channel(0).play(ready_sound, loops=-1)

    player = Player(False, False, 0.2, 0.55, 1.5)
    scroll_stage = 1
    scroll = Images('Assets/Scroll_1/1.png', (SCREEN_WIDTH/1.4, SCREEN_HEIGHT/3))

    next_img = Images('Assets/materials/next.png', (SCREEN_WIDTH/1.4 + scroll.rect.width*0.25,
                                                    SCREEN_HEIGHT/3 + scroll.rect.height*0.2))

    back_img = Images('Assets/materials/back.png', (SCREEN_WIDTH/1.4 + scroll.rect.width*0.25-next_img.rect.width,
                                                    SCREEN_HEIGHT/3 + scroll.rect.height*0.2))

    while True:
        click = False
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
            command_zone.handle_event(event)
            if event.type == KEYDOWN and not command_zone.active:
                if event.key == K_ESCAPE or event.key == K_SPACE and not command_zone.active:
                    pygame.mixer.Channel(0).pause()
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'
                    if config['background_music']:
                        pygame.mixer.Channel(0).play(ready_sound, loops=-1)

            if next_img.is_clicked(event) and scroll_stage < 4:
                scroll_stage += 1
                scroll = Images('Assets/Scroll_1/{}.png'.format(str(scroll_stage)),
                                (SCREEN_WIDTH / 1.4, SCREEN_HEIGHT / 3))
            if back_img.is_clicked(event) and scroll_stage > 1:
                scroll_stage -= 1
                scroll = Images('Assets/Scroll_1/{}.png'.format(str(scroll_stage)),
                                (SCREEN_WIDTH / 1.4, SCREEN_HEIGHT / 3))

        command_zone.draw(SCREEN)
        game_zone.update(SCREEN)
        player.draw(SCREEN)
        scroll.draw(SCREEN)
        if scroll_stage < 4:
            next_img.draw(SCREEN)
        if scroll_stage > 1:
            back_img.draw(SCREEN)

        if round_button("R U N", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                        SCREEN_HEIGHT * 0.05, click):
            shield, sword = command_zone.exec_command()
            if shield or sword:
                success_sound.play()
            player = Player(shield, sword, 0.2, 0.55, 1.5)

        if not player.shield and not player.sword:
            player.update_idle()
        else:
            player.update()

        if player.shield and player.sword and player.rect.left > SCREEN_WIDTH:
            break

        pygame.display.update()
        clock.tick(30)


def display_trunks(wizard):
    trunk_1 = Images("Assets/Images/treasure/trunk_1a.png", (SCREEN_WIDTH / 8,
                                                             SCREEN_HEIGHT / 2))

    trunk_2 = Images("Assets/Images/treasure/trunk_1b.png", (SCREEN_WIDTH / 2.9,
                                                             SCREEN_HEIGHT / 2))
    trunk_3 = Images("Assets/Images/treasure/trunk_1c.png", (SCREEN_WIDTH / 1.8,
                                                             SCREEN_HEIGHT / 2))
    chose = False
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((*BLACK, 160))
    SCREEN.blit(background, (0, 0))
    challenge_1 = Images("Assets/Images/challenge/challenge_1.png", (SCREEN_WIDTH * 0.89,
                                                                     SCREEN_HEIGHT * 0.32))

    while not chose:
        wizard.draw(SCREEN)
        challenge_1.draw(SCREEN)
        trunk_1.draw(SCREEN)
        trunk_2.draw(SCREEN)
        trunk_3.draw(SCREEN)
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if trunk_1.rect.collidepoint(x, y):
                    chose = 1
                elif trunk_2.rect.collidepoint(x, y):
                    chose = 2
                elif trunk_3.rect.collidepoint(x, y):
                    chose = 3
        pygame.display.update()
        clock.tick(60)
    return chose


def chapter_2_2(command_zone):
    """
    Micro-bit challenge
    Executive code in command_zone.exec_microbit() function
    """
    background = 'Assets/Images/background/background_2.2.png'
    player = Player(width=0.2, height=0.55)
    enemy = MovingSprite("Assets/Sprites/Flaming_demon", 0.7, 0.5, 1.7)
    game_zone = GameZone(background)
    answer = ""

    while True:
        click = False
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
            command_zone.handle_event(event)
            if event.type == KEYDOWN and not command_zone.active:
                if event.key == K_ESCAPE or event.key == K_SPACE and not command_zone.active:
                    pygame.mixer.Channel(0).pause()
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'
        game_zone.update(SCREEN)
        player.draw(SCREEN)
        player.update_idle()
        command_zone.draw(SCREEN)
        if answer != "Correct":
            enemy.draw(SCREEN)
            enemy.update_idle()
            if round_button("R U N", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                            SCREEN_HEIGHT * 0.05,
                            click):
                answer = command_zone.exec_microbit()
            command_zone.error_message(SCREEN, answer)
        elif not enemy.dead:
            enemy.draw(SCREEN)
            enemy.update_dying()

        pygame.display.update()
        clock.tick(24)


def chapter_2_3():
    """
    Answer giving question
    Break while loop by either answering correctly or 2 times wrong
    :return: None
    """
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill(WHITE)
    SCREEN.blit(background, (0, 0))
    player = Player()
    chose = False
    ans_1 = ans_2 = ans_3 = False
    draw_button = first_run = True
    wrong = 0
    while not chose:
        click = False
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
        player.draw(SCREEN)
        display_text("What are the differences between 'While' and 'For'?", button_x_start, SCREEN_HEIGHT * 3.5 // 13,
                     blit_text=first_run)
        display_text("Check all the correct answers.", button_x_start, SCREEN_HEIGHT * 4 // 13,
                     blit_text=first_run)
        if check_button("What is it?", *button_layout_4[0], click, enabled=ans_1, draw_btn=draw_button,
                        blit_text=first_run):
            ans_1 = not ans_1
            draw_button = True
        elif check_button("Why is it?", *button_layout_4[1], click, enabled=ans_2, draw_btn=draw_button,
                          blit_text=first_run):
            ans_2 = not ans_2
            draw_button = True
        elif check_button("What is it?", *button_layout_4[2], click, enabled=ans_3, draw_btn=draw_button,
                          blit_text=first_run):
            ans_3 = not ans_3
            draw_button = True
        else:
            draw_button = False

        if round_button("S U B M I T", *button_layout_4[3], click):
            print(ans_1, ans_2, ans_3)
            if ans_1 and ans_2 and (not ans_3):
                display = True
                display_text("Correct!", 600, 400, text_color=GREEN, blit_text=display)
                pygame.time.wait(1000)
                break
            else:
                wrong += 1
                if wrong == 2:
                    display = True
                    display_text("You used your 2 attempts.", 600, 400, text_color=GREEN, blit_text=display)

        first_run = False
        pygame.display.update()
        clock.tick(60)


def handle_input(event):
    """
    Handle quitting events
    :param event: input from player
    """
    pressed_keys = pygame.key.get_pressed()
    alt_f4 = (event.type == KEYDOWN and event.key == K_F4
              and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
    if event.type == QUIT or alt_f4:
        config['chapter'] = chapter
        save_config()
        sys.exit()


def pause_menu_setup(background):
    SCREEN.blit(background, (0, 0))
    background = SCREEN.copy()
    text_surf, text_rect = text_objects('Pause Menu', MENU_TEXT, color=WHITE)
    text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 4))
    SCREEN.blit(text_surf, text_rect)
    pygame.display.update()
    return background


def pause_menu(player):
    paused = True
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((*BLACK, 160))
    background = pause_menu_setup(background)
    while paused:
        click = False
        pks = pygame.key.get_pressed()
        for event in pygame.event.get():
            handle_input(event)
            if event.type == KEYDOWN:
                right_key = event.key == K_RIGHT and not pks[K_d] or event.key == K_d and not pks[K_RIGHT]
                left_key = event.key == K_LEFT and not pks[K_a] or event.key == K_a and not pks[K_LEFT]
                if right_key:
                    player.go_right()
                elif left_key:
                    player.go_left()
                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    paused = False
                elif event.key == K_m:
                    return 'Main Menu'
                elif event.key == K_SPACE:
                    return 'Resume'
                elif event.key == K_q:
                    sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                click = True
            elif event.type == KEYUP:
                if event.key in (K_d, K_RIGHT, K_a, K_LEFT):
                    player.stop(pygame.key.get_pressed())
        if button('R E S U M E', *button_layout_4[0], click):
            return 'Resume'
        elif button('N E W G A M E', *button_layout_4[1], click):
            new_game()
            game()
        elif button('S E T T I N G S', *button_layout_4[2], click):
            settings_menu()
            pause_menu_setup(background)
        elif button('Q U I T  G A M E', *button_layout_4[3], click):
            sys.exit()
        pygame.display.update(button_layout_4)
        clock.tick(60)
    return 'Resume'


def end_game_setup(surface_copy=None):
    if surface_copy is not None:
        SCREEN.blit(surface_copy, (0, 0))
    else:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
        background.fill((255, 255, 255, 160))
        SCREEN.blit(background, (0, 0))
        text_surf, text_rect = text_objects('Game Over', MENU_TEXT)
        text_rect.center = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 4))
        SCREEN.blit(text_surf, text_rect)
        surface_copy = pygame.display.get_surface().copy()
    pygame.display.update()
    return surface_copy


def end_game():
    show_mouse()
    button_layout_3 = [(button_x_start, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    while True:
        click, pressed_keys = False, pygame.key.get_pressed()
        for event in pygame.event.get():
            handle_input(event)
            if event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_m):
                return 'Main Menu'
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_r):
                return 'Restart'
            elif event.type == MOUSEBUTTONDOWN:
                click = True
        if button('R E S T A R T', *button_layout_3[0], click):
            return 'Restart'
        elif button('M A I N  M E N U', *button_layout_3[1], click):
            main_menu()
            return 'Main Menu'
        pygame.display.update(button_layout_3)
        clock.tick(60)


def new_game():
    global chapter
    chapter = 0
    game()


if __name__ == '__main__':
    # Initialization
    if platform.system() == 'Windows':
        from ctypes import windll

        windll.user32.SetProcessDPIAware()
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
    pygame.mixer.init(frequency=44100, buffer=512)
    SELECT_SOUND = pygame.mixer.Sound('assets/audio/select.ogg')
    FOOTSTEP_SOUND = pygame.mixer.Sound('assets/audio/footstep_grass.ogg')

    chapter = config['chapter']
    music_playing = False
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = int(0.75 * pygame.display.Info().current_w), \
                                  int(0.75 * pygame.display.Info().current_h)
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    BUTTON_WIDTH = int(SCREEN_WIDTH * 0.625 // 3)
    BUTTON_HEIGHT = int(SCREEN_HEIGHT * 5 // 81)
    button_x_start = (SCREEN_WIDTH - BUTTON_WIDTH) // 2
    button_layout_4 = [(button_x_start, SCREEN_HEIGHT * 5 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    TOGGLE_WIDTH = int(BUTTON_WIDTH * 0.875)
    TOGGLE_ADJ = int(BUTTON_WIDTH * 0.075)

    MENU_TEXT = pygame.font.Font(FONT_LIGHT, int(110 / 1080 * SCREEN_HEIGHT))
    LARGE_TEXT = pygame.font.Font(FONT_REG, int(40 / 1080 * SCREEN_HEIGHT))
    MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, int(35 / 1440 * SCREEN_HEIGHT))
    SMALL_TEXT = pygame.font.Font(FONT_BOLD, int(25 / 1440 * SCREEN_HEIGHT))
    HUD_TEXT = pygame.font.Font(FONT_REG, int(40 / 1440 * SCREEN_HEIGHT))

    # # Load Icon
    # ICON = 'assets/sprites/adventurer_idle.png'
    # ICON = pygame.image.load(ICON)
    # pygame.display.set_icon(ICON)
    pygame.display.set_caption('HopeSTEM Game')
    clock = pygame.time.Clock()
    ticks = 0

    from sprites import *

    main_menu()
