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
PRIMARY = 156, 152, 37
PRIMARY_LIGHT = 232, 227, 79

FONT_BOLD = 'assets/fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'assets/fonts/OpenSans-Regular.ttf'
FONT_LIGHT = 'assets/fonts/OpenSans-Light.ttf'
FONT_SCROLL = 'Assets/Fonts/yuweij.ttf'

CONFIG_FILE = 'config.json'
config = {'DEBUG': False, 'background_music': True, "chapter": 0, }
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


def button(text, x, y, w, h, click, inactive_color=PRIMARY, active_color=PRIMARY_LIGHT, text_color=WHITE):
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
        draw_circle(SCREEN, int(x), y + h // 4, h // 4, enabled_color)
    elif draw_btn:
        draw_circle(SCREEN, int(x), y + h // 4, h // 4, disabled_color)

    if blit_text:
        text_surf, text_rect = text_objects(text, MEDIUM_TEXT, color=text_color)
        text_rect.topleft = (x + h, y)
        SCREEN.blit(text_surf, text_rect)

    return x - h // 4 < mouse[0] < x + h // 4 and y < mouse[1] < y + h // 2 and click and pygame.time.get_ticks() > 100


def display_text(text, x, y, text_color=BLACK, blit_text=True, font=None):
    """
    Display text on Screen
    :param text: text need to display
    :param text_color: Black by default
    :param blit_text: improve quality by running once
    :return: None
    """
    if font is None:
        font = MEDIUM_TEXT
    if blit_text:
        text_surf, text_rect = text_objects(text, font, color=text_color)
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
                quit()

        if start_game:
            while start_game:
                start_game = game() == 'Restart'
            main_menu_setup()
        pygame.display.update(button_layout_4)
        clock.tick(60)


def settings_menu():
    global music_playing
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
        if toggle_btn('Background Music', *button_layout_4[0], click, enabled=music_playing,
                      draw_toggle=draw_bg_toggle, blit_text=first_run):
            music_playing = not music_playing
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

    player = Player()
    if chapter == 0:
        chapter_0(player)
        chapter = 1
    initial_chapter = floor(chapter)
    background = 'Assets/Images/background/background_{}.png'.format(str(chapter))
    SCREEN.fill(BLACK)

    if chapter > 2:
        enemy = Enemy(initial_chapter)
        wizard = Wizard(initial_chapter)

    game_zone = GameZone(background)
    command_zone = CommandZone()

    running = True

    while running:
        if chapter == 1:
            chapter_1(command_zone, game_zone)
            chapter = 2
            game()

        elif chapter == 2:
            chapter_2(command_zone, game_zone)
            chapter = 3
            game()

        elif chapter == 3:
            chapter_3(player, enemy, wizard, command_zone, game_zone)
        elif chapter == 3.2:
            chapter_3_2(command_zone)
            chapter = 0
            end_game()
        elif chapter == 3.3:
            chapter_3_3(background)
            chapter = 0
            end_game()

        pygame.display.update()
        clock.tick(40)


def chapter_3(player, enemy, wizard, command_zone, game_zone):
    global chapter
    mysterious_sound = pygame.mixer.Sound("Assets/Audio/mysterious.mp3")
    if music_playing:
        pygame.mixer.Channel(0).play(mysterious_sound, loops=-1)

    hurt_signal = True
    while True:
        click = False

        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
            if event.type == KEYDOWN and not command_zone.active:
                if event.key == K_ESCAPE or event.key == K_SPACE and not command_zone.active:
                    pygame.mixer.Channel(0).pause()
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'
                    if music_playing:
                        pygame.mixer.Channel(0).play(mysterious_sound, loops=-1)
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

        command_zone.update(SCREEN)
        game_zone.update(SCREEN)
        player.draw(SCREEN)
        player.update()
        if not enemy.dead:
            if round_button("R U N", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                            SCREEN_HEIGHT * 0.05, click):
                command_zone.exec_command()
            enemy.draw(SCREEN)
            enemy.update()
            if pygame.sprite.collide_rect(player, enemy):
                player.moving = False
                if player.animation_frame == 'attack':
                    print(player.attack_index)
                    if player.attack_index == 8 and hurt_signal:
                        enemy.count_hit += 1
                        enemy.animation_frame = 'hurt'
                        hurt_signal = False
                    if player.attack_index == 0:
                        hurt_signal = True

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
                    chapter = 3.2
                    game()
                elif trunk_chosen == 2:
                    chapter = 3.3
                    game()

        pygame.display.update()
        clock.tick(40)


def chapter_0(player):
    scroll_sound = pygame.mixer.Sound("Assets/Audio/scroll.ogg")
    if music_playing:
        pygame.mixer.Channel(0).play(scroll_sound, loops=-1)
    image = []
    index = 0

    for i in range(1, 49):
        source = 'Assets/scroll_0/scroll{}.jpg'.format(i)
        image.append(pygame.image.load(source))
        image[i - 1] = pygame.transform.smoothscale(image[i - 1], (SCREEN_WIDTH, SCREEN_HEIGHT))

    while index < 47:
        SCREEN.blit(image[index], (0, 0))
        index += 1
        pygame.display.update()
        clock.tick(15)

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
                    if music_playing:
                        pygame.mixer.Channel(0).play(scroll_sound, loops=-1)
            if event.type == MOUSEBUTTONDOWN:
                click = True

        SCREEN.blit(image[47], (0, 0))
        if round_button(" N E X T", int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.9), int(BUTTON_WIDTH * 0.5),
                        int(BUTTON_HEIGHT * 0.5), click, inactive_color=BLACK, active_color=GREY):
            break
        pygame.display.update()
        clock.tick(24)


def chapter_1(command_zone, game_zone):
    player = Player(False, False, 0.2, 0.55, 1.5)
    badge = Images("Assets/badge.png", (SCREEN_WIDTH / 3, SCREEN_HEIGHT / 3), scale=SCREEN_WIDTH / (3 * 484))
    scroll = Images("Assets/scroll_1.png", (SCREEN_WIDTH / 1.4, SCREEN_HEIGHT / 3), scale=SCREEN_WIDTH / (2.5 * 537))
    command_zone.set_up_chapter1()
    answer_1 = answer_2 = name = age = " "
    text_1 = "Before you go, you will prepare a badge."
    text_2 = "This badge represents you and your"
    text_3 = "kingdom."
    text_4 = "Type in your information as asked below "
    text_5 = "to inscribe those onto your badge."
    text_6 = "Think carefully!"
    fire_sound = pygame.mixer.Sound("Assets/Audio/fire-sound.ogg")
    fist_run = True
    part = 1

    if music_playing:
        pygame.mixer.Channel(0).play(fire_sound, loops=-1)

    while True:
        click = False
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
            command_zone.handle_input_1(event, part)
            if event.type == KEYDOWN and not command_zone.active:
                if event.key == K_ESCAPE or event.key == K_SPACE and not command_zone.active:
                    pygame.mixer.Channel(0).pause()
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'
                    if music_playing:
                        pygame.mixer.Channel(0).play(fire_sound, loops=-1)

        game_zone.update(SCREEN)
        command_zone.update(SCREEN)
        badge.draw(SCREEN)
        scroll.draw(SCREEN)
        if answer_1 == "Correct":
            if fist_run:
                command_zone.set_up_chapter1_2()
                part = 2
                fist_run = False
            txt_surf, txt_rect = text_objects(name, SCROLL_TEXT_LARGE)
            display_text(name, SCREEN_WIDTH / 3 - txt_rect.width / 2, SCREEN_HEIGHT / 3 - scroll.rect.height * 0.05,
                         text_color=WHITE, font=SCROLL_TEXT_LARGE)

            if answer_2 == "Correct":
                age_surf, age_rect = text_objects(age, SCROLL_TEXT_LARGE)
                display_text(age, SCREEN_WIDTH / 3 - age_rect.width / 2, SCREEN_HEIGHT / 3,
                             text_color=WHITE, font=SCROLL_TEXT_LARGE)
                if round_button("L E A V E", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                                SCREEN_HEIGHT * 0.05, click):
                    break
            else:
                if round_button("R U N", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                                SCREEN_HEIGHT * 0.05, click):
                    answer_2, age = command_zone.exec_chapter1(2)
                if answer_2 == "Not correct":
                    command_zone.error_message(SCREEN, "Your age is an Integer type")

        else:
            if round_button("R U N", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                            SCREEN_HEIGHT * 0.05, click):
                answer_1, name = command_zone.exec_chapter1(1)
            if answer_1 == "Not correct":
                command_zone.error_message(SCREEN, "First rule: Your name is a string so put it in \" \"")

        display_text(text_1, SCREEN_WIDTH / 1.4 - 0.32 * scroll.rect.width,
                     SCREEN_HEIGHT / 3 - scroll.rect.height * 0.26,
                     text_color=WHITE, font=SCROLL_TEXT)
        display_text(text_2, SCREEN_WIDTH / 1.4 - 0.32 * scroll.rect.width,
                     SCREEN_HEIGHT / 3 - scroll.rect.height * 0.20,
                     text_color=WHITE, font=SCROLL_TEXT)
        display_text(text_3, SCREEN_WIDTH / 1.4 - 0.32 * scroll.rect.width,
                     SCREEN_HEIGHT / 3 - scroll.rect.height * 0.14,
                     text_color=WHITE, font=SCROLL_TEXT)
        display_text(text_4, SCREEN_WIDTH / 1.4 - 0.32 * scroll.rect.width,
                     SCREEN_HEIGHT / 3 - scroll.rect.height * 0.08,
                     text_color=WHITE, font=SCROLL_TEXT)
        display_text(text_5, SCREEN_WIDTH / 1.4 - 0.32 * scroll.rect.width,
                     SCREEN_HEIGHT / 3 - scroll.rect.height * 0.02,
                     text_color=WHITE, font=SCROLL_TEXT)
        display_text(text_6, SCREEN_WIDTH / 1.4 - 0.32 * scroll.rect.width,
                     SCREEN_HEIGHT / 3 + scroll.rect.height * 0.04,
                     text_color=WHITE, font=SCROLL_TEXT)

        pygame.display.update()
        clock.tick(40)


def chapter_2(command_zone, game_zone):
    success_sound = pygame.mixer.Sound('Assets/Audio/success.ogg')
    ready_sound = pygame.mixer.Sound("Assets/Audio/ready.ogg")
    if music_playing:
        pygame.mixer.Channel(0).play(ready_sound, loops=-1)

    player = Player(False, False, 0.2, 0.55, 1.5)
    scroll_stage = 1
    scroll = Images('Assets/Scroll_2/1.png', (SCREEN_WIDTH / 1.4, SCREEN_HEIGHT / 3))

    next_img = Images('Assets/materials/next.png', (SCREEN_WIDTH / 1.4 + scroll.rect.width * 0.25,
                                                    SCREEN_HEIGHT / 3 + scroll.rect.height * 0.2))

    back_img = Images('Assets/materials/back.png', (SCREEN_WIDTH / 1.4 + scroll.rect.width * 0.25 - next_img.rect.width,
                                                    SCREEN_HEIGHT / 3 + scroll.rect.height * 0.2))

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
                    if music_playing:
                        pygame.mixer.Channel(0).play(ready_sound, loops=-1)
                    if event.key == K_LEFT:
                        player.go_left()
                    elif event.key == K_RIGHT:
                        player.go_right()
                elif event.type == KEYUP:
                    if event.key in (K_d, K_RIGHT, K_a, K_LEFT, K_RETURN):
                        player.stop(pygame.key.get_pressed())

            if next_img.is_clicked(event) and scroll_stage < 4:
                scroll_stage += 1
                scroll = Images('Assets/Scroll_2/{}.png'.format(str(scroll_stage)),
                                (SCREEN_WIDTH / 1.4, SCREEN_HEIGHT / 3))
            if back_img.is_clicked(event) and scroll_stage > 1:
                scroll_stage -= 1
                scroll = Images('Assets/Scroll_2/{}.png'.format(str(scroll_stage)),
                                (SCREEN_WIDTH / 1.4, SCREEN_HEIGHT / 3))

        command_zone.update(SCREEN)
        game_zone.update(SCREEN)
        player.draw(SCREEN)

        if not player.shield or not player.sword:
            player.update_idle()
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
        else:
            player.update()
            if round_button("L E A V E", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                            SCREEN_HEIGHT * 0.05, click):
                break

        if player.shield and player.sword and player.rect.left > SCREEN_WIDTH:
            break

        pygame.display.update()
        clock.tick(40)


def display_trunks(wizard):
    trunk_1 = Images("Assets/Images/treasure/trunk_1a.png", (SCREEN_WIDTH / 5,
                                                             SCREEN_HEIGHT / 2))

    trunk_2 = Images("Assets/Images/treasure/trunk_1b.png", (SCREEN_WIDTH / 2,
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
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                if trunk_1.rect.collidepoint(x, y):
                    chose = 1
                elif trunk_2.rect.collidepoint(x, y):
                    chose = 2
        pygame.display.update()
        clock.tick(60)
    return chose


def chapter_3_2(command_zone):
    """
    Micro-bit challenge
    Executive code in command_zone.exec_microbit() function
    """

    volcano_sound = pygame.mixer.Sound("Assets/Audio/volcano.mp3")
    if music_playing:
        pygame.mixer.Channel(0).play(volcano_sound, loops=-1)

    background = 'Assets/Images/background/background_3.2.png'
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
                    if music_playing:
                        pygame.mixer.Channel(0).play(volcano_sound, loops=-1)
        game_zone.update(SCREEN)
        player.draw(SCREEN)
        player.update_idle()
        command_zone.update(SCREEN)
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
        else:
            if round_button("L E A V E", SCREEN_WIDTH * 0.85, SCREEN_HEIGHT * 0.9, SCREEN_WIDTH * 0.12,
                            SCREEN_HEIGHT * 0.05, click):
                break

        pygame.display.update()
        clock.tick(24)


def chapter_3_3(background):
    """
    Answer giving question
    Break while loop by either answering correctly or 2 times wrong
    :return: None
    """

    img: pygame.Surface = pygame.transform.smoothscale(pygame.image.load(background).convert(),
                                                       (SCREEN_WIDTH, SCREEN_HEIGHT))
    SCREEN.blit(img, (0, 0))
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
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_SPACE:
                    pygame.mixer.Channel(0).pause()
                    if pause_menu(player) == 'Main Menu':
                        return 'Main Menu'

        player.draw(SCREEN)
        display_text("What does/do the character(s) that While loop and For loop have in common?",
                     button_x_start, SCREEN_HEIGHT * 3.5 // 13,
                     blit_text=first_run, text_color=WHITE)
        display_text("Check all the correct answers.", button_x_start, SCREEN_HEIGHT * 4 // 13,
                     blit_text=first_run, text_color=WHITE)
        if check_button("Can use `break` statement inside the loop.", *button_layout_4[0], click, enabled=ans_1,
                        draw_btn=draw_button, blit_text=first_run, text_color=WHITE):
            ans_1 = not ans_1
            draw_button = True
        elif check_button("Must know the number of iterations", *button_layout_4[1], click, enabled=ans_2,
                          draw_btn=draw_button,
                          blit_text=first_run, text_color=WHITE):
            ans_2 = not ans_2
            draw_button = True
        elif check_button("Can use `continue` statement inside the loop.", *button_layout_4[2], click, enabled=ans_3,
                          draw_btn=draw_button,
                          blit_text=first_run, text_color=WHITE):
            ans_3 = not ans_3
            draw_button = True
        else:
            draw_button = False

        if round_button("S U B M I T", *button_layout_4[3], click):
            if ans_1 and ans_3 and (not ans_2):
                display_text("Correct!", button_x_start + BUTTON_WIDTH + 40,
                             SCREEN_HEIGHT * 8 // 13 + BUTTON_HEIGHT // 2,
                             text_color=GREEN)
                break
            else:
                wrong += 1
                if wrong < 2:
                    display_text("Wrong, 1 attempt left", button_x_start + BUTTON_WIDTH + 40,
                                 SCREEN_HEIGHT * 8 // 13 + BUTTON_HEIGHT // 2, text_color=RED)
                if wrong == 2:
                    display_text("First answer and third answer were correct", button_x_start + BUTTON_WIDTH + 40,
                                 SCREEN_HEIGHT * 8 // 13 + BUTTON_HEIGHT // 2, text_color=RED)
                    break

        first_run = False
        pygame.display.update()
        clock.tick(40)


def handle_input(event):
    """
    Handle quitting events
    :param event: input from player
    """
    pressed_keys = pygame.key.get_pressed()
    alt_f4 = (event.type == KEYDOWN and event.key == K_F4
              and (pressed_keys[K_LALT] or pressed_keys[K_RALT]))
    if event.type == QUIT or alt_f4:
        quit()


def quit():
    config["chapter"] = chapter
    config["background_music"] = music_playing
    save_config()
    sys.exit()


def new_game():
    global chapter
    chapter = 0
    game()

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
        for event in pygame.event.get():
            handle_input(event)
            if event.type == KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    paused = False
                elif event.key == K_m:
                    return 'Main Menu'
                elif event.key == K_SPACE:
                    return 'Resume'
                elif event.key == K_q:
                    quit()
            elif event.type == MOUSEBUTTONDOWN:
                click = True
            elif event.type == KEYUP:
                if event.key in (K_d, K_RIGHT, K_a, K_LEFT):
                    player.stop(pygame.key.get_pressed())
        if button('R E S U M E', *button_layout_4[0], click):
            return 'Resume'
        elif button('N E W  G A M E', *button_layout_4[1], click):
            new_game()
            game()
        elif button('S E T T I N G S', *button_layout_4[2], click):
            settings_menu()
            pause_menu_setup(background)
        elif button('Q U I T  G A M E', *button_layout_4[3], click):
            quit()
        pygame.display.update(button_layout_4)
        clock.tick(60)
    return 'Resume'


def end_game():
    global chapter
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA, 32)
    background.fill((*BLACK, 160))
    SCREEN.blit(background, (0, 0))
    show_mouse()
    button_layout_3 = [(button_x_start, SCREEN_HEIGHT * 6 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 7 // 13, BUTTON_WIDTH, BUTTON_HEIGHT),
                       (button_x_start, SCREEN_HEIGHT * 8 // 13, BUTTON_WIDTH, BUTTON_HEIGHT)]
    while True:
        click = False
        for event in pygame.event.get():
            handle_input(event)
            if event.type == MOUSEBUTTONDOWN:
                click = True
        if button('R E S T A R T', *button_layout_3[0], click):
            chapter = 0
            game()
        elif button('Q U I T  G A M E', *button_layout_3[1], click):
            quit()
        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    # Initialization
    if platform.system() == 'Windows':
        from ctypes import windll

        windll.user32.SetProcessDPIAware()
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
    pygame.mixer.init(frequency=44100, buffer=512)
    SELECT_SOUND = pygame.mixer.Sound('assets/audio/select.ogg')
    FOOTSTEP_SOUND = pygame.mixer.Sound('assets/audio/footstep_grass.ogg')

    chapter = 3
    music_playing = config["background_music"]
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
    SCROLL_TEXT = pygame.font.Font(FONT_SCROLL, int(35 / 1440 * SCREEN_HEIGHT))
    SCROLL_TEXT_LARGE = pygame.font.Font(FONT_SCROLL, int(45 / 1440 * SCREEN_HEIGHT))

    # # Load Icon
    # ICON = 'assets/sprites/adventurer_idle.png'
    # ICON = pygame.image.load(ICON)
    # pygame.display.set_icon(ICON)
    pygame.display.set_caption('HopeSTEM Game')
    clock = pygame.time.Clock()
    ticks = 0

    from sprites import *

    main_menu()
