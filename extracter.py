import pygame
import glob


def scale_image(image: pygame.Surface, scale_factor: float) -> pygame.Surface:
    """
    Scales and returns the given image
    :param image: the original pygame.Surface
    :param scale_factor: how much to scale the image by
    :return: the scaled image
    """
    if scale_factor == 1:
        return image
    width, height = image.get_rect().size[0], image.get_rect().size[1]
    return pygame.transform.scale(image, (int(width * scale_factor), int(height * scale_factor)))


def extract_platforms(source_path='assets/images/jungle tileset.png', scale_factor=1) -> list:
    """
    Extracts platform tiles from the tile sheet and returns them as a list
    NOTE: each tile is 16x16
    :param scale_factor:
    :param source_path: the relative path to the tile sheet
    :return:list of images for each platform tile
    """
    sheet = pygame.image.load(source_path).convert_alpha()
    platform_coords = [(0, 16, 27, 27), (26, 16, 27, 27), (53, 16, 27, 27)]  # left, centre, right
    return [scale_image(sheet.subsurface(coords), scale_factor) for coords in platform_coords]


def extract_vines(source_path='assets/images/jungle tileset.png', scale_factor=1):
    sheet = pygame.image.load(source_path).convert_alpha()
    vine_coords = [(21*16, 12*16, 24*16, 15 * 16)]  # big vine
    return [scale_image(sheet.subsurface(coords), scale_factor) for coords in vine_coords]


def extract_images(path: str, scale_factor=1) -> list:
    """
    Extracts images from a sprite sheet and returns them as a list

    :param scale_factor:
    :param path: relative path to sprite sheet
    :return: list of images of the sprite sheets
    """
    images = []
    for filename in glob.glob(path):
        im = pygame.image.load(filename)
        images.append(scale_image(im, scale_factor))
    return images

