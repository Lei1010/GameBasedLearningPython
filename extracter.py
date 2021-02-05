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

