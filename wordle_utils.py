"""
Helper functions used by Wordle
"""
# Colours used in output
RED = '\033[1;31m'
GREEN = '\033[1;32m'
WHITE = '\033[0m'
YELLOW = '\033[1;33m'

# Game Constants
WORD_LEN = 5
MAX_GUESSES = 6
ASSETS_PATH = '/assets'
ALLOWED_GUESSES_PATH = f'.{ASSETS_PATH}/wordle-allowed-guesses.txt'
NEW_ALLOWED_GUESSES_PATH = f'.{ASSETS_PATH}/wordle_nyt_allowed_guesses.txt'
POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle-answers.txt'
NEW_POSSIBLE_ANSWERS_PATH = f'.{ASSETS_PATH}/wordle_nyt_answers.txt'

# Numerical values too handle guess results easier
CORRECT_ALL = 20 # correct letter and position.
CORRECT_LETTER = 10 # correct letter wrong position.
WRONG = 0 # Wrong letter and position.
MAX_SCORE = CORRECT_ALL * WORD_LEN # Correct guess score

# Assign colour to guess result
GUESS_RESULT_DICT = {
    CORRECT_ALL: GREEN,
    CORRECT_LETTER: YELLOW,
    WRONG: WHITE
}


def clear_screen():
    """
    Clear terminal based on operating system
    """
    print(chr(27) + "[2J")


def values_from_result(result: list[str, int]) -> tuple:
    """
    Get raw guess word and score of a guess from result list
    """
    guess = ''
    score = 0
    score_pattern = []
    for letter, value in result:
        guess += letter
        score += value
        score_pattern.append(score)
    return guess, score, tuple(score_pattern)


def remove_flag_from_dict(flag, result, answer_dict):
    """
    Goes back in results list and changes score in first instance
    of flag (list[letter, score]) to the proper value.
    """
    if flag in result:
        for _, value in enumerate(result):
            if value == flag:
                # if there the letter in the word and all the same letter havent been parsed yet
                if len(answer_dict[flag[0]]) > 1:
                    value[1] = CORRECT_LETTER
                else:
                    value[1] = WRONG
                break
