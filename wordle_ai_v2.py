'''
Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI

Author: Kamron Cole kjc8084@rit.edu
'''
from itertools import product
import math

import numpy as np
from pynput.keyboard import Controller as K_CON
from pynput.mouse import Controller as M_CON

import wordle as w
import wordle_utils as wu
import wordle_ai_utils as utils


class WordleAI():
    '''
    Rudimentary AI to solve wordle puzzle, either from web GUI or internal CLI
    '''
    __slots__ = ['__hints_dict', '__wordle', '__word_weights_dict', '__next_guess',
                 '__guesses', '__verbose', '__probability_distribution']


    def __init__(self, game: w.Wordle, starting_word: str = 'proms', verbose = True) -> None:
        self.__hints_dict = {
            # Letters in the word
            'INCLUDED': set(),
            # Letters not in the word
            'EXCLUDED': set(),
            # Where included letters belong
            'CORRECT': set(),
            # Where included letters do not belong
            'GUESSED': set()
        }

        self.__wordle = game
        self.__word_weights_dict = dict(utils.WORD_WEIGHTS_LETTER_PROB)
        self.__next_guess = starting_word
        self.__guesses = 0
        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)
        self.__verbose = verbose


    def make_guess(self, raw_guess: str) -> w.Guess:
        '''
        Make a guess on an internal Wordle game
        '''
        return self.__wordle.make_guess(raw_guess)


    def read_report(self, guess: w.Guess) -> None:
        '''
        Read a guess's report and add letters to dict that will help solve
        for a word by removing invalid entries from the word list
        '''
        score_pattern = []
        feedback = guess.get_feedback()
        for i, token in enumerate(feedback):
            letter, result = token
            score_pattern.append(result)
            # If is correct letter and in correct position
            if result == wu.CORRECT_ALL:
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['CORRECT'].add((letter, i))
                # Backwards check to make sure letter is not included and excluded at the same time
                if letter in self.__hints_dict['EXCLUDED']:
                    self.__hints_dict['EXCLUDED'].remove(letter)
            # If is correct letter but in the wrong position
            if result == wu.CORRECT_LETTER:
                self.__hints_dict['INCLUDED'].add(letter)
                self.__hints_dict['GUESSED'].add((letter, i))
                # Backwards check to make sure letter is not included and excluded at the same time
                if letter in self.__hints_dict['EXCLUDED']:
                    self.__hints_dict['EXCLUDED'].remove(letter)
            # If letter not in the word and hasn't already been marked as included
            if result == wu.WRONG and letter not in self.__hints_dict['INCLUDED']:
                # Guesses with multiple letters will not put wrong repeated letters in EXCLUDED
                # if answer only has 1 of said letter. This attempts to fix that
                self.__hints_dict['GUESSED'].add((letter, i))
                self.__hints_dict['EXCLUDED'].add(letter)
        return tuple(score_pattern)


    def narrow_words(self) -> None:
        '''
        Using a dict of all feedback gained from previous guesses, remove words and
        their weight from from their respective list so that the remaining words meet
        the criteria of the answer
        '''
        if self.__next_guess in self.__word_weights_dict:
            self.__word_weights_dict.pop(self.__next_guess)

        self.__word_weights_dict = {word: self.__word_weights_dict[word]
                                    for word in self.__word_weights_dict.keys()
                                    if not utils.is_junk(word, self.__hints_dict)}

        weights = self.__word_weights_dict.values()
        self.__probability_distribution = np.array(list(weights)) / sum(weights)


    def run_cli(self):
        '''
        Attempt to solve CLI Wordle game by reading board state in from Wordle game and narrowing
        down word list from consecutive guesss' feedback
        '''
        guess = self.make_guess(self.__next_guess)
        score_pattern = guess.get_score_pattern()
        self.read_report(guess)
        self.narrow_words()
        return score_pattern


    def get_remaining_words(self) -> list:
        '''
        Get list of remaining words from words weight dict
        '''
        return list(self.__word_weights_dict.keys())


    def get_next_guess(self) -> str:
        '''
        Return current next guess
        '''
        return self.__next_guess


def tests():
    '''
    Run multiple iterations to get a rough guess of the AI's winrate,
    usually run between various changes to find optimal values
    '''
    progress = 1
    tot_words = len(utils.ALLOWED_FULL)
    data_dict = {}
    try:
        for raw_guess in sorted(utils.ALLOWED_FULL):
            print(f'trying "{raw_guess}" ({progress}/{tot_words})...')
            patterns = {combo: [0, 0] for combo in product([0, 10, 20], repeat=5)}
            for answer in w.ANSWERS:
                game = w.Wordle(answer)
                bot = WordleAI(game, raw_guess)
                score_pattern = bot.run_cli()
                p = len(bot.get_remaining_words())/tot_words # probability(pattern)
                info = -math.log2(p) # info (bits). How many times we reduced the words list by half
                patterns[score_pattern] = [p, info]
            data_dict[raw_guess] = {k: v for k, v in sorted(patterns.items(), key=lambda item: item[1][0], reverse=True)}
            progress += 1
            print(f'Done.\n')
    except KeyboardInterrupt:
        pass
    for word in data_dict:
        print(word, ':')
        for pattern in data_dict[word]:
            print(f'    {pattern}: {data_dict[word][pattern]}')
        print()



def main():
    '''
    Main
    '''
    tests()


if __name__ == '__main__':
    main()
