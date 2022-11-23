"""
Common tasks wordle_ai needs to reads image of Wordle board into a workable board.

Author: Kamron Cole kjc8084@rit.edu
"""
import functools
import json
import time

import numpy as np

import wordle
import wordle_utils as utils

# Game variables
MAX_ROWS = utils.MAX_GUESSES
MAX_COLS = utils.WORD_LEN

with open('./assets/nyt_word_weights_letter_prob.json', 'r', encoding='utf-8') as file_1:
    WORD_WEIGHTS_LETTER_PROB = json.loads(file_1.read())

# with open('./assets/word_weights_winrate.json', 'r', encoding='utf-8') as file_2:
#     WORD_WEIGHT_WINRATE = json.loads(file_2.read())

ALLOWED_FULL, WEIGHTS = list(zip(*WORD_WEIGHTS_LETTER_PROB.items()))

SCORE_THRESHOLD = 60
GUESS_THRESHOLD = utils.MAX_GUESSES - 1
WORDS_LEN_THRESHOLD = 3

def make_game_board(letters: list[str], scores: list[int]) -> wordle.Board:
    """
    Make game board given list of guesses and list of scores.
    Both lists should be the same shape
    """
    board = wordle.Board()
    for guess, score in zip(letters, scores):
        board.make_guess(wordle.Guess(list(zip(guess, score))))
    return board

def is_junk(word: str, hints_dict: dict) -> bool:
    """
    Given various hints about a word from previous guesses,
    check whether a falls within the hint's condition
    """
    for letter, index in hints_dict['CORRECT']:
        if word[index] != letter:
            return True
    for letter in hints_dict['INCLUDED']:
        if letter not in word:
            return True
    for letter in hints_dict['EXCLUDED']:
        if letter in word:
            return True
    for letter, index in hints_dict['GUESSED']:
        if word[index] == letter:
            return True
    return False

def find_words_with_most_unique_letters(unique_letters: set) -> set:
    """
    Find set of words that have the unique letters in common,
    if no word exists with all unique letter in common,
    remove a unique letter and try again
    """
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
    """
    Rebuild a weighted words dict with the unique words
    Choose a random word from the weighted words dict
    """
    common_word_weights = {}
    for word in unique_words:
        common_word_weights[word] = WORD_WEIGHTS_LETTER_PROB[word]
    prob_dist = np.array(list(common_word_weights.values())) / sum(common_word_weights.values())
    return np.random.choice(list(common_word_weights.keys()), 1, False, prob_dist)[0]

def main():
    """
    Manual Tests
    """
    pass


if __name__ == '__main__':
    main()
