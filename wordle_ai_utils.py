import cv2
import numpy as np
import wordle

from PIL import ImageGrab
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

TOP = 291
BOTTOM = 691
LEFT = 795
RIGHT = 1125
WORDLE_GAME_BOX_1080P = [795, 291, 1125, 691]
COL_WIDTH = 62
ROW_HIGHT = 62
PADDING = 6
PADDING_COLOR = [19, 18, 18]
MAX_ROWS = 6
MAX_COLS = 5

# CORRECT ALL    = rgb( 83, 141, 78) or [ 78 141  83]
# CORRECT LETTER = rgb(180, 159, 59) or [ 59 159 180]
# WRONG          = rgb( 58,  58, 60) or [ 60  58  58]
SCORE_TO_COLOR = {
    wordle.CORRECT_ALL: [78, 141, 83],
    wordle.CORRECT_LETTER: [59, 159, 180],
    wordle.WRONG: [60, 58, 58]
}


def get_screen(bbox: list, color_space = cv2.COLOR_BGR2RGB):
    screen = np.array(ImageGrab.grab(bbox))
    screen = cv2.cvtColor(screen, color_space)
    return screen
    

def read_test_image():
    return cv2.imread('./assets/test_img_2.png')


def combine_horizontally_color(images, padding = 0):
    max_height = 0
    total_width = 0 
    for image in images:
        image_height = image.shape[0]
        image_width = image.shape[1]
        if image_height > max_height:
            max_height = image_height
        total_width += image_width
    final_image = np.zeros((max_height, (len(images) - 1) * padding + total_width, 3), dtype = np.uint8)
    current_x = 0
    for image in images:
        height = image.shape[0]
        width = image.shape[1]
        final_image[:height, current_x:width + current_x, :] = image
        current_x += width + padding
    return final_image


def combine_horizontally_bw(images, padding = 0):
    max_height = 0
    total_width = 0 
    for image in images:
        image_height = image.shape[0]
        image_width = image.shape[1]
        if image_height > max_height:
            max_height = image_height
        total_width += image_width
    final_image = np.zeros((max_height, (len(images) - 1) * padding + total_width), dtype = np.uint8)
    current_x = 0
    for image in images:
        height = image.shape[0]
        width = image.shape[1]
        final_image[:height, current_x:width + current_x] = image
        current_x += width + padding
    return final_image


def get_columns(image, crop_padding = 15):
    return [image[:, (COL_WIDTH * i) + (PADDING * i) + crop_padding:(COL_WIDTH * (i + 1)) + (PADDING * i) - crop_padding] for i in range(MAX_COLS)]


def get_rows(image, crop_padding = 15):
    return [image[(ROW_HIGHT * i) + (PADDING * i) + crop_padding:(ROW_HIGHT * (i + 1)) + (PADDING * i) - crop_padding] for i in range(MAX_ROWS)]


def get_words(screen) -> list:
    # Split board screenshot into columns and remove beginning/ending padding
    cols = get_columns(screen)
    # combine new columns horizontally
    final_image = combine_horizontally_bw(cols, -5)
    # read text from image
    text = pytesseract.image_to_string(final_image)
    return [list(word) for word in text.lower().split('\n')[:-1]]


def colors_equal(c1: list, c2: list, threshold:int = 1) -> bool:
    for i in range(len(c1)):
        if c1[i] not in range(c2[i] - threshold, c2[i] + threshold + 1):
            return False
    return True


def get_scores(row) -> list:
    scores = []
    new = list(np.array_split(row[0], 5))
    for array in new:
        array = list(filter(lambda color: list(color) != PADDING_COLOR, array))
        color = list(array[0])
        for score, dict_color in SCORE_TO_COLOR.items():
            if colors_equal(color, dict_color):
                scores.append(score)
    return scores


def remove_black_and_invert(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    thresh1 = cv2.threshold(s, 92, 255, cv2.THRESH_BINARY)[1]
    thresh2 = cv2.threshold(v, 128, 255, cv2.THRESH_BINARY)[1]
    thresh2 = 255 - thresh2
    mask = cv2.add(thresh1,thresh2)
    return mask


def make_game_board(letters: list, scores: list) -> wordle.Board:
    board = wordle.Board()
    for guess, score in zip(letters, scores):
        board.make_guess(wordle.Guess(list(zip(guess, score))))
    return board


def read_img_to_board(image) -> wordle.Board:
    scores = [get_scores(row) for row in get_rows(image)]
    new_image = remove_black_and_invert(image)
    letters = get_words(new_image)
    return make_game_board(letters, scores)


def main():
    screen = read_test_image()
    # screen = get_screen(WORDLE_GAME_BOX_1080P)
    board = read_img_to_board(screen)
    print(board.get_num_guesses())

if __name__ == '__main__':
    main()