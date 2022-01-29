from tkinter import RIGHT
from turtle import left
import cv2

import numpy as np

from PIL import ImageGrab
from pynput.keyboard import Controller
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

K_CON = Controller()

TOP = 291
BOTTOM = 691
LEFT = 795
RIGHT = 1125
WORDLE_GAME_BOX_1080P = [795, 291, 1125, 691]
COL_WIDTH = 62
ROW_HIGHT = 62
PADDING = 6

row_1 = [LEFT, TOP, RIGHT, TOP + ROW_HIGHT]

def get_pixels(screen):
    pixels = np.array([screen[row:(ROW_HIGHT * row) + (PADDING * row - 2), col:(COL_WIDTH * col) + (PADDING * col - 2)] for col in range(5) for row in range(6)])
    # images = screen[0:ROW_HIGHT, 0:COL_WIDTH]
    for image in pixels:
        cv2.imshow('image', image)
        cv2.waitKey(0)

def get_screen(bbox: list, color_space = cv2.COLOR_BGR2RGB):
    screen = np.array(ImageGrab.grab(bbox))
    screen = cv2.cvtColor(screen, color_space)
    return screen


def main():
    screen = get_screen(WORDLE_GAME_BOX_1080P)
    # cv2.imshow('image', screen)
    # cv2.waitKey(0)
    get_pixels(screen)
    # text = pytesseract.image_to_string(screen, nice=1)
    # print(text)
    print()

if __name__ == '__main__':
    main()