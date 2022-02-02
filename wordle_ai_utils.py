'''
Common tasks wordle_ai needs to reads image of Wordle board into a workable board.

Author: Kamron Cole kjc8084@rit.edu
'''
import functools
import json

from PIL import ImageGrab
from pynput.keyboard import Key

import numpy as np

import cv2
import pytesseract

import wordle
import wordle_utils as utils

# Uncomment below line and change path if tesseract.exe is not on your PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Game board location and spacing variables
TOP = 291
BOTTOM = 691
LEFT = 795
RIGHT = 1125
WORDLE_GAME_BOX_1080P = [LEFT, TOP, RIGHT, BOTTOM]
COL_WIDTH = 62
ROW_HIGHT = 62
PADDING = 6

# Colors
PADDING_COLOR = [19, 18, 18]
CORRECT_ALL_COLOR = [78, 141, 83]
CORRECT_LETTER_COLOR = [59, 159, 180]
WRONG_COLOR = [60, 58, 58]

SCORE_TO_COLOR = {
    utils.CORRECT_ALL: CORRECT_ALL_COLOR,
    utils.CORRECT_LETTER: CORRECT_LETTER_COLOR,
    utils.WRONG: WRONG_COLOR
}

# Game variables
MAX_ROWS = utils.MAX_GUESSES
MAX_COLS = utils.WORD_LEN


WORD_WEIGHTS_LETTER_PROB = None
with open('./assets/word_weights_letter_prob.json', 'r', encoding='utf-8') as file:
    WORD_WEIGHTS_LETTER_PROB = json.loads(file.read())

WORD_WEIGHT_WINRATE = None
with open('./assets/word_weights_winrate.json', 'r', encoding='utf-8') as file:
    WORD_WEIGHTS_LETTER_PROB = json.loads(file.read())

ALLOWED_FULL, WEIGHTS = list(zip(*WORD_WEIGHTS_LETTER_PROB.items()))

SCORE_THRESHOLD = 60
GUESS_THRESHOLD = utils.MAX_GUESSES - 1
WORDS_LEN_THRESHOLD = 3


def get_screen(bbox: list, color_space: int = cv2.COLOR_BGR2RGB) -> np.ndarray:
    '''
    Get screanshot of screen, crop it to bounding box, and convert it to specific color space
    '''
    screen = np.array(ImageGrab.grab(bbox))
    screen = cv2.cvtColor(screen, color_space)
    return screen


def read_image_from_file(filename) -> np.ndarray:
    '''
    Read image from file into a workable numpy array
    '''
    return cv2.imread(filename)


def combine_horizontally_bw(images: list[np.ndarray], padding: int = 0) -> np.ndarray:
    '''
    Combine a list of black and white images horizontally with some black padding between them
    if padding > 0
    '''
    max_height = 0
    total_width = 0
    # get final images size
    for image in images:
        image_height = image.shape[0]
        image_width = image.shape[1]
        if image_height > max_height:
            max_height = image_height
        total_width += image_width
    # make empty array that will contain combined image
    final_image = np.zeros((max_height, (len(images) - 1) * padding + total_width),
                           dtype=np.uint8)
    current_x = 0
    # combine images
    for image in images:
        height = image.shape[0]
        width = image.shape[1]
        final_image[:height, current_x:width + current_x] = image
        current_x += width + padding
    return final_image


def calc_col_x_begin(col_number, crop_padding):
    '''
    Calculate beginning of column with pixels cropped off
    '''
    return (COL_WIDTH * col_number) + (PADDING * col_number) + crop_padding


def calc_col_x_end(col_number, crop_padding):
    '''
    Calculate end of column with pixels cropped off
    '''
    return (COL_WIDTH * (col_number + 1)) + (PADDING * col_number) - crop_padding


def calc_row_y_begin(row_number, crop_padding):
    '''
    Calculate beginning of column with pixels cropped off
    '''
    return (ROW_HIGHT * row_number) + (PADDING * row_number) + crop_padding


def calc_row_y_end(row_number, crop_padding):
    '''
    Calculate end of column with pixels cropped off
    '''
    return (ROW_HIGHT * (row_number + 1)) + (PADDING * row_number) - crop_padding


def get_columns(image: np.ndarray, crop_padding: int = 15) -> list[np.ndarray]:
    '''
    Split image of Wordle game board into separate columns, cropping them horizontally,
    and return a list of images by column
    '''
    return [image[:, calc_col_x_begin(i, crop_padding):calc_col_x_end(i, crop_padding)]
            for i in range(MAX_COLS)]


def get_rows(image: np.ndarray, crop_padding: int = 15) -> list[np.ndarray]:
    '''
    Split image of Wordle game board into separate rows, cropping them vertically,
    and return a list of images by row
    '''
    return [image[calc_row_y_begin(i, crop_padding):calc_row_y_end(i, crop_padding)]
            for i in range(MAX_ROWS)]


def get_words(screen: np.ndarray) -> list[str]:
    '''
    Read words from game board image into a list of words whose index is what number guess it was
    '''
    # Split board screenshot into columns and remove beginning/ending padding
    cols = get_columns(screen)
    # combine new columns horizontally
    final_image = combine_horizontally_bw(cols, -5)
    # read text from image
    text = pytesseract.image_to_string(final_image)
    return [list(word) for word in text.lower().split('\n')[:-1]]


def colors_equal(c_1: list, c_2: list, threshold: int = 1) -> bool:
    '''
    Check if bgr colors are equal within a sertain threshold of each other
    '''
    for i, value in enumerate(c_1):
        if value not in range(c_2[i] - threshold, c_2[i] + threshold + 1):
            return False
    return True


def get_scores(row: np.ndarray) -> list[int]:
    '''
    Get a single guesses scores given an image of a single guess
    '''
    scores = []
    new = list(np.array_split(row[0], 5))
    for array in new:
        array = list(filter(lambda color: list(color) != PADDING_COLOR, array))
        if not array:
            raise AttributeError('invalid letter or scores found from image.')
        color = list(array[0])
        for score, dict_color in SCORE_TO_COLOR.items():
            if colors_equal(color, dict_color):
                scores.append(score)
    return scores


def remove_black_and_invert(image: np.ndarray) -> np.ndarray:
    '''
    Set threshold on saturation and value channels
    then combine them as a mask then invert and return black/white image
    '''
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    _, sat, val = cv2.split(hsv)
    thresh1 = cv2.threshold(sat, 92, 255, cv2.THRESH_BINARY)[1]
    thresh2 = cv2.threshold(val, 128, 255, cv2.THRESH_BINARY)[1]
    thresh2 = 255 - thresh2
    mask = cv2.add(thresh1, thresh2)
    return mask


def make_game_board(letters: list[str], scores: list[int]) -> wordle.Board:
    '''
    Make game board given list of guesses and list of scores.
    Both lists should be the same shape
    '''
    board = wordle.Board()
    for guess, score in zip(letters, scores):
        board.make_guess(wordle.Guess(list(zip(guess, score))))
    return board


def read_img_to_board(image: np.ndarray) -> wordle.Board:
    '''
    Read an image of a Wordle game board into a workable wordle.Board
    '''
    scores = [get_scores(row) for row in get_rows(image)]
    new_image = remove_black_and_invert(image)
    letters = get_words(new_image)
    if not scores[0]:
        raise AttributeError('invalid letter or scores found from image.')
    return make_game_board(letters, scores)


def type_guess(keyboard, guess: str) -> None:
    '''
    Type a guess into the web GUI wordle game
    '''
    for letter in guess:
        keyboard.press(letter)
        keyboard.release(letter)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


def find_words_with_most_unique_letters(unique_letters: set) -> set:
    '''
    Find set of words that have the unique letters in common,
    if no word exists with all unique letter in common,
    remove a unique letter and try again
    '''
    all_words_left = []
    for letter in unique_letters:
        words_left = [word for word in ALLOWED_FULL if letter in word]
        all_words_left.append(words_left)
    words = functools.reduce(lambda x, y: set(x) & set(y), all_words_left)
    while not words:
        all_words_left.pop()
        words = functools.reduce(lambda x, y: set(x) & set(y), all_words_left)
    return words


def choose_word_from_unique_words(unique_words: set) -> str:
    '''
    Rebuild a weighted words dict with the unique words
    Choose a random word from the weighted words dict
    '''
    common_word_weights = {}
    for word in unique_words:
        common_word_weights[word] = WORD_WEIGHTS_LETTER_PROB[word]
    prob_dist = np.array(list(common_word_weights.values())) / sum(common_word_weights.values())
    return np.random.choice(list(common_word_weights.keys()), 1, False, prob_dist)[0]


def main():
    '''
    Manual Tests
    '''
    test_file_1 = './assets/test_img.png'
    # test_file_2 = './assets/test_img_2.png'
    screen = read_image_from_file(test_file_1)
    # screen = get_screen(WORDLE_GAME_BOX_1080P)
    board = read_img_to_board(screen)
    print(board.get_guesses_num())


if __name__ == '__main__':
    main()
